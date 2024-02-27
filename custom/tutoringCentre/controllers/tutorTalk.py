from odoo.http import request, route, Controller
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.tools import replace_exceptions
from markupsafe import Markup
from odoo.exceptions import UserError
from werkzeug.exceptions import NotFound
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class TutorTalkController(Controller):
    def _get_guest_name(self):
        return _("Visitor")

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/buildChat",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    @add_guest_to_context
    def create_chat(
        self,
        channel_id,
        channel_name,
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
        # 待解決 -- 似乎曾有未知錯誤 channel_vals 為boolean?
        if not channel_vals:
            _logger.warning("channel_vals is False")
            return False
        channel_vals["name"] = channel_name
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
        "/tutoringCentre/api/tutorTalk/livechat/fetch_channel",
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
        "/tutoringCentre/api/tutorTalk/livechat/fetch_announce_channel",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    def _fetch_announce_channel(self, im_livechat_ids):
        im_livechat = request.env["im_livechat.channel"].sudo().browse(im_livechat_ids)
        if not im_livechat:
            return False
        announce_channel_ids = []
        for record in im_livechat:
            if record.announcementChannel.id:
                announce_channel_ids.append(record.announcementChannel.id)

        return announce_channel_ids

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/send_message",
        type="json",
        auth="public",
    )
    def send_message_to_livechat(self, channel_id, message, message_type="comment"):
        channel = (
            request.env["discuss.channel"]
            .sudo()
            .search([("id", "=", channel_id)], limit=1)
        )
        if channel and channel.channel_type == "livechat":
            channel.message_post(
                body=(
                    Markup(f"<p>{message}</p>")
                    if message_type == "comment"
                    else message
                ),
                author_id=request.env.user.partner_id.id,
                message_type=message_type,
                subtype_xmlid="mail.mt_comment" if message_type == "comment" else None,
            )
            user_values = {
                field: channel[field]
                for field in request.env["discuss.channel"]._fields
            }
            return user_values
        else:
            return {"success": False, "error": "Invalid LiveChat channel"}

    # @route(
    #     "/tutoringCentre/api/tutorTalk/livechat/fetch_channels",
    #     type="json",
    #     auth="public",
    # )
    # def _fetch_livechat_channels(self):
    #     livechat_channels = (
    #         request.env["im_livechat.channel"]
    #         .sudo()
    #         .search([("category", "in", ["tutoringCentre"])])
    #     )

    #     livechat_channels_values = [
    #         {
    #             "name": record.name,
    #             "id": record.id,
    #             "create_uid": record.create_uid,
    #             "image": record.image_128,
    #             "user_ids": record.user_ids,
    #             "course": record.course.read()[0],
    #         }
    #         for record in livechat_channels
    #     ]

    #     return livechat_channels_values

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/fetch_channels",
        type="json",
        auth="public",
    )
    def _fetch_channels(self, channel_ids):
        channels = request.env["discuss.channel"].sudo().browse(channel_ids).read()
        if not channels:
            return False

        return channels

    @route(
        "/tutoringCentre/api/announcement/fetch_announcement_messages",
        type="json",
        auth="public",
    )
    def _fetch_announcement_messages(self, course_id):
        course = request.env["tutoring_centre.course"].sudo().browse(course_id)
        if not course:
            return False
        messages = course.get_announcement_messages()
        return messages
