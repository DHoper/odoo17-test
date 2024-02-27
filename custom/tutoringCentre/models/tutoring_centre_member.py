# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreMemberModel(models.Model):
    _name = "tutoring_centre.member"
    _description = "補習班系統-會員"

    is_active = fields.Boolean(string="帳號狀態", required=True, default=True)
    student = fields.One2many(
        "tutoring_centre.member_student", "member_id", string="學生"
    )
    portal_user = fields.Many2one(
        "res.users",
        string="使用者帳號",
        domain=[("share", "=", True)],
        required=True,
    )
    # activeChannels = fields.Many2many(
    #     "discuss.channel", string="啟用頻道", required=True, readonly=True
    # )
    # channelInfo = fields.Text("頻道資料", readonly=True)

    @api.model
    def create_member(self, user_id, studentName, course_ids, channel_ids):
        new_student = self.env["tutoring_centre.member_student"].create(
            {"name": studentName, "courses": course_ids}
        )

        new_member = self.create(
            {
                "is_active": True,
                "portal_user": user_id,
                "student": [(6, 0, [new_student.id])],
                "activeChannels": channel_ids,
            }
        )

        self.env["tutoring_centre.course"].browse(course_ids).write(
            {
                "student": [(4, new_student.id)],
            }
        )

        if not new_member:
            return False

        return new_member

    @api.model
    def add_active_channels(self, member_id, channel_ids):
        record = self.browse(member_id)
        if record:
            channels_to_add = [(4, channel_id) for channel_id in channel_ids]
            record.activeChannels = channels_to_add
            return True
        return False

    def _get_useable_im_channel_selections(self):
        usable_im_channel_records = self.env["discuss.channel"].search(
            [("channel_type", "=", "livechat")]
        )
        return [(str(record.id), record.name) for record in usable_im_channel_records]

    # def send_group_message(self, message, ids):
    #     if not message:
    #         raise exceptions.UserError("Message cannot be empty.")

    #     for channel_id in ids:
    #         channel = self.env["discuss.channel"].browse(channel_id)
    #         channel.message_post(
    #             body=Markup(f"<p>{message}</p>"),
    #             author_id=2,
    #             message_type="comment",
    #             subtype_xmlid="mail.mt_comment",
    #         )
