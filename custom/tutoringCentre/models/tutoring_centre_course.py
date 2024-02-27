# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions, Command
from datetime import datetime
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreCourseModel(models.Model):
    _name = "tutoring_centre.course"
    _description = "補習班系統-班級"

    name = fields.Char(string="班級名稱", required=True)
    student = fields.Many2many("tutoring_centre.member_student", string="學生")
    teacher = fields.Many2many("tutoring_centre.teacher", string="教師")
    im_livechat_id = fields.Many2one("im_livechat.channel", string="客服頻道")

    def create(self, values):
        course = super(TutoringCentreCourseModel, self).create(values)
        im_livechat_values = {
            "name": course.name,
            "category": "tutoringCentre",
            "user_ids": [
                (6, 0, [teacher.portal_user.id for teacher in course.teacher])
            ],
        }
        im_livechat = self.env["im_livechat.channel"].create(im_livechat_values)
        course.im_livechat_id = im_livechat.id
        if course.student:
            self._handle_new_student_addition(course)

        return course

    def _handle_new_student_addition(self, course):
        self._create_live_channel(course.student, course)
        for record in course.student:
            partner_id = record.member_id.portal_user.partner_id.id
            if partner_id:
                course.im_livechat_id.announcementChannel.add_members(
                    partner_ids=partner_id, post_joined_message=False
                )

    def unlink(self):
        for course in self:
            if course.im_livechat_id:
                course.im_livechat_id.unlink()
        return super(TutoringCentreCourseModel, self).unlink()

    def write(self, vals):
        _logger.info(777777777777777777777777777777)
        _logger.info(vals)
        if "student" in vals:
            original_student = self.student
            res = super(TutoringCentreCourseModel, self).write(vals)
            new_records = self.student - original_student
            deleted_records = original_student - self.student

            new_students = self.env["tutoring_centre.member_student"].browse(
                new_records.ids
            )
            if deleted_records:
                self._remove_live_channel(deleted_records)
                deleted_ids = [
                    record.member_id.portal_user.partner_id.id
                    for record in deleted_records
                ]
            student_member_ids = self.student.mapped("member_id").ids

            deleted_ids = [
                record.member_id.portal_user.partner_id.id
                for record in deleted_records
                if record.member_id.id not in student_member_ids
            ]
            if deleted_ids:
                self._remove_members_from_channel_member(deleted_ids)

            if new_records:
                self._create_live_channel(new_students)
                for record in new_students:
                    partner_id = record.member_id.portal_user.partner_id.id
                    if partner_id:
                        self.im_livechat_id.announcementChannel.add_members(
                            partner_ids=partner_id, post_joined_message=False
                        )
            return res
        else:
            return super(TutoringCentreCourseModel, self).write(vals)

    def _remove_members_from_channel_member(self, ids):
        for id in ids:
            channel_member = self.env["discuss.channel.member"].search(
                [
                    ("partner_id", "=", id),
                    ("channel_id", "=", self.im_livechat_id.announcementChannel.id),
                ]
            )
            if channel_member:
                channel_member.unlink()

    def _create_live_channel(self, new_students, course=False):
        self_record = course if course else self
        if not self_record.im_livechat_id:
            return False

        for record in new_students:
            if any(
                self_record.im_livechat_id == channel.livechat_channel_id
                for channel in record.active_channels
            ):
                return
            member_to_add = [
                Command.create(
                    {
                        "partner_id": record.member_id.portal_user.partner_id.id,
                        "is_pinned": False,
                    }
                ),
            ]
            for teacher in self_record.teacher:
                member_to_add.append(
                    Command.create(
                        {
                            "partner_id": teacher.portal_user.partner_id.id,
                            "is_pinned": False,
                        }
                    )
                )
            channel_vals = {
                "channel_member_ids": member_to_add,
                "channel_type": "livechat",
                "livechat_active": True,
                "livechat_operator_id": self_record.teacher[
                    0
                ].portal_user.partner_id.id,
                "livechat_channel_id": self_record.im_livechat_id.id,
                "chatbot_current_step_id": False,
                "anonymous_name": False,
                "country_id": False,
                "name": f"{record.name}-{self_record.name}",
            }
            live_channel = (
                self_record.env["discuss.channel"]
                .with_context(mail_create_nosubscribe=False)
                .sudo()
                .create(channel_vals)
            )
            im_channel = (
                self_record.env["im_livechat.channel"]
                .sudo()
                .browse(self_record.im_livechat_id)
            )
            im_channel.id.write({"channel_ids": [(4, live_channel.id)]})
            live_channel.message_post(body=f"(小朋友 : {record.name}) -- 頻道已建立")
            record.write({"active_channels": [(4, live_channel.id)]})

    def _remove_live_channel(self, removed_students):
        if not self.im_livechat_id:
            return False

        for record in removed_students:
            live_channels = self.env["discuss.channel"].search(
                [
                    (
                        "livechat_channel_id",
                        "=",
                        self.im_livechat_id.id,
                    ),
                    ("id", "in", record.active_channels.ids),
                ],
            )
            if live_channels:
                record.write({"active_channels": [(3, live_channels)]})
                for channel in live_channels:
                    channel.write({"active": False})

    @api.model
    def roll_call(self, course_id, students):
        current_partner_id = self.env.user.partner_id
        course = self.sudo().browse(course_id)
        _logger.info(f"---------------------------------------{course}------------")
        for student in students:
            domain = [
                (
                    "livechat_channel_id",
                    "=",
                    course.im_livechat_id.id,
                ),
                (
                    "id",
                    "in",
                    student.active_channels.ids,
                ),
                (
                    "id",
                    "!=",
                    course.im_livechat_id.announcementChannel.id,
                ),
            ]
            channel = self.env["discuss.channel"].search(domain)
            message = f"爸爸媽媽您好<br>{student.name}弟弟/妹妹已經在我們 [{course.name}] 班上完成點名<br>請您放心。"
            channel.message_post(
                body=Markup(f"<p>{message}</p>"),
                author_id=current_partner_id.id,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
