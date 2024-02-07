from odoo.http import request, route, Controller
from odoo.tools.translate import _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.tools import replace_exceptions
from markupsafe import Markup
from odoo.exceptions import UserError
from werkzeug.exceptions import NotFound
import logging
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import threading

_logger = logging.getLogger(__name__)


class TutoringCentreController(Controller):
    @route(
        ["/tutoringCentre/app", "/tutoringCentre/app/<path:subpath>"],
        auth="public",
        website=True,
    )
    def _render_tutoringCentre(self, config_id=None):
        return request.render(
            "tutoringCentre.root",
            {
                "session_info": request.env["ir.http"].get_frontend_session_info(),
            },
        )

    @add_guest_to_context
    @route(
        "/tutoringCentre/api/userInfo",
        type="json",
        auth="public",
    )
    def _get_user_info(self):
        return request.env.user.read()[0]

    @route(
        "/tutoringCentre/api/createMember",
        type="json",
        auth="public",
    )
    def _create_member(self, userID, studentName):
        new_member = (
            request.env["tutoring_centre.member"]
            .sudo()
            .create_member(str(userID), studentName)
        )
        new_member_values = {field: new_member[field] for field in new_member._fields}
        return new_member_values

    @route(
        "/tutoringCentre/api/memberInfo",
        type="json",
        auth="public",
    )
    def _get_member_info(self, userID):
        member = (
            request.env["tutoring_centre.member"]
            .sudo()
            .search([("portal_user", "=", userID)], limit=1)
        )

        if not member.read():
            return False

        member_values = member.read()[0]
        student_data = member.student.read()
        member_values["student"] = student_data[0] if student_data else None

        return member_values

    def _get_guest_name(self):
        return _("Visitor")

    @route(
        "/tutoringCentre/TutorTalk/api/livechat/buildChat",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    @add_guest_to_context
    def create_chat(
        self,
        channel_id,
        anonymous_name,
        previous_operator_id=None,
        chatbot_script_id=None,
        persisted=True,
        **kwargs,
    ):
        user_id = request.env.user.id
        country_id = None
        if request.session.uid:
            user_id = request.env.user.id
            country_id = request.env.user.country_id.id
        else:
            if request.geoip.country_code:
                country = (
                    request.env["res.country"]
                    .sudo()
                    .search([("code", "=", request.geoip.country_code)], limit=1)
                )
                if country:
                    country_id = country.id

        if previous_operator_id:
            previous_operator_id = int(previous_operator_id)

        chatbot_script = False
        if chatbot_script_id:
            frontend_lang = request.httprequest.cookies.get(
                "frontend_lang", request.env.user.lang or "en_US"
            )
            chatbot_script = (
                request.env["chatbot.script"]
                .sudo()
                .with_context(lang=frontend_lang)
                .browse(chatbot_script_id)
            )
        channel_vals = (
            request.env["im_livechat.channel"]
            .with_context(lang=False)
            .sudo()
            .browse(channel_id)
            ._get_livechat_discuss_channel_vals(
                anonymous_name,
                previous_operator_id=previous_operator_id,
                chatbot_script=chatbot_script,
                user_id=user_id,
                country_id=country_id,
                lang=request.httprequest.cookies.get("frontend_lang"),
            )
        )
        if not channel_vals:
            _logger.warning("channel_vals is False")
            return False
        if not persisted:
            operator_partner = (
                request.env["res.partner"]
                .sudo()
                .browse(channel_vals["livechat_operator_id"])
            )
            display_name = (
                operator_partner.user_livechat_username or operator_partner.display_name
            )
            return {
                "name": channel_vals["name"],
                "chatbot_current_step_id": channel_vals["chatbot_current_step_id"],
                "state": "open",
                "operator_pid": (operator_partner.id, display_name.replace(",", "")),
                "chatbot_script_id": chatbot_script.id if chatbot_script else None,
            }
        channel = (
            request.env["discuss.channel"]
            .with_context(mail_create_nosubscribe=False)
            .sudo()
            .create(channel_vals)
        )
        with replace_exceptions(UserError, by=NotFound()):
            _logger.warning("進入with replace_exception")
            __, guest = channel.sudo()._find_or_create_persona_for_channel(
                guest_name=self._get_guest_name(),
                country_code=request.geoip.country_code,
                timezone=request.env["mail.guest"]._get_timezone_from_request(request),
                post_joined_message=False,
            )
        channel = channel.with_context(guest=guest)
        if not channel_vals:
            _logger.warning("channel_vals is 2.00000Faslse")
            return False
        if (
            not chatbot_script
            or chatbot_script.operator_partner_id != channel.livechat_operator_id
        ):
            channel._broadcast([channel.livechat_operator_id.id])
        channel_info = channel._channel_info()[0]
        if guest:
            channel_info["guest_token"] = guest._format_auth_cookie()

        return {
            "channel_info": channel_info,
            "channel": channel,
        }

    @route(
        "/tutoringCentre/TutorTalk/api/livechat/fetchChannel",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    def _fetch_channel(self, channel_uuid):
        channel = (
            request.env["discuss.channel"].sudo().search([("uuid", "=", channel_uuid)])
        )
        if not channel:
            return
        return channel.read()[0]

    @route(
        "/tutoringCentre/TutorTalk/api/livechat/send_message",
        type="json",
        auth="public",
    )
    def send_message_to_livechat(self, channel_uuid, message):
        channel = (
            request.env["discuss.channel"]
            .sudo()
            .search([("uuid", "=", channel_uuid)], limit=1)
        )
        if channel and channel.channel_type == "livechat":
            channel.message_post(
                body=Markup(
                    f'<div class="o_mail_notification o_hide_author">{message}</div>'
                ),
                author_id=request.env.user.partner_id.id,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
            user_values = {
                field: channel[field]
                for field in request.env["discuss.channel"]._fields
            }
            return user_values
        else:
            return {"success": False, "error": _("Invalid LiveChat channel")}
