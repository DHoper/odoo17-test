from odoo.http import request, route, Controller
from odoo.tools.translate import _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.tools import replace_exceptions
from markupsafe import Markup
from odoo.exceptions import UserError
from werkzeug.exceptions import NotFound
import logging


_logger = logging.getLogger(__name__)


class YourController(Controller):
    @route("/tutoringCentre/parentPortal", auth="public", website=True)
    def parentPortal(self):
        return request.render(
            "tutoringCentre.parentPortal",
            {
                "session_info": request.env["ir.http"].get_frontend_session_info(),
            },
        )

    def _get_guest_name(self):
        return _("Visitor")

    @route(
        "/tutoringCentre/parentPortal/buildChat",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    @add_guest_to_context
    def get_chat_session(
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

        # current_user_id = request.env.user.id
        # new_channel = request.env["discuss.channel"].create(
        #     {
        #         "name": "Your Channel Name",
        #         "description": "Your Channel Description",
        #         "channel_type": "livechat",
        #         "channel_member_ids": [
        #             (
        #                 0,
        #                 0,
        #                 {
        #                     "partner_id": 2,
        #                     "is_pinned": False,
        #                 },
        #                 {"partner_id": current_user_id},
        #             )
        #         ],
        #     }
        # )

        return channel_info

    @route("/tutoringCentre/livechat/send_message", type="json", auth="public")
    def send_message_to_livechat(self, channel_uuid, message):
        channel = (
            request.env["discuss.channel"]
            .sudo()
            .search([("uuid", "=", channel_uuid)], limit=1)
        )

        _logger.info(
            f"============================================================>{request.env.user.partner_id.id}"
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
            return {"success": True}
        else:
            return {"success": False, "error": _("Invalid LiveChat channel")}

    @route(
        "/tutoringCentre/parentPortal/get_channel_messages", type="json", auth="public"
    )
    def channel_fetch_messages(self, channel_uuid, last_id=None, limit=20):
        try:
            channel = (
                request.env["discuss.channel"]
                .sudo()
                .search([("uuid", "=", channel_uuid)], limit=1)
            )
            if not channel:
                return {"error": "找不到該頻道"}

            messages = channel.sudo()._channel_fetch_message(
                last_id=int(last_id) if last_id else False, limit=int(limit)
            )

            return {"messages": messages}
        except Exception as e:
            return {"error": str(e)}

    @route("/tutoringCentre/parentPortal/send_bus_message", type="json", auth="public")
    def send_bus_message(self, channel_uuid, message):
        bus = request.env["bus.bus"]
        channel_info = (
            request.env["discuss.channel"]
            .sudo()
            .search([("uuid", "=", channel_uuid)], limit=1)
        )
        if channel_info:
            bus._sendone(
                "tutoringCentre_channel",
                {
                    "channel_uuid": channel_uuid,
                    "message": message,
                },
            )
            return {"success": True}
        else:
            return {"success": False, "error": _("Invalid channel")}

        @route(
            "/tutoringCentre/ABC/<int:channel_id>",
            methods=["GET"],
            type="http",
            auth="public",
            csrf=True,
        )
        @add_guest_to_context
        def discuss_channel(self, channel_id):
            channel = request.env["discuss.channel"].search([("id", "=", channel_id)])
            if not channel:
                raise NotFound()
            return self._response_discuss_public_template(channel)

        def _response_discuss_public_template(
            self, channel, discuss_public_view_data=None
        ):
            discuss_public_view_data = discuss_public_view_data or {}
            return request.render(
                "mail.discuss_public_channel_template",
                {
                    "data": {
                        "channelData": channel._channel_info()[0],
                        "discussPublicViewData": dict(
                            {
                                "shouldDisplayWelcomeViewInitially": channel.default_display_mode
                                == "video_full_screen",
                            },
                            **discuss_public_view_data,
                        ),
                    },
                    "session_info": channel.env["ir.http"].session_info(),
                },
            )
