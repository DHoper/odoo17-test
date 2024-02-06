# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreMemberModel(models.Model):
    _name = "tutoring_centre.member"
    _description = "補習班系統-會員"

    is_active = fields.Boolean(string="帳號狀態", required=True, default=True)
    # parent = fields.One2many(
    #     "tutoring_centre.member_parent", "id", string="家長", required=True
    # )
    student = fields.Many2many("tutoring_centre.member_student", string="學生")
    portal_user = fields.Selection(
        selection=lambda self: self._get_useable_website_user_selections(),
        string="使用者帳號",
        required=True,
    )

    @api.model
    def create_member(self, userID, studentName):
        new_student = self.env["tutoring_centre.member_student"].create(
            {"name": studentName}
        )

        # new_member.write({"student": [(4, new_student.id, 0)]})

        new_member = self.create(
            {
                "is_active": True,
                "portal_user": userID,
                "student": [(6, 0, [new_student.id])],
            }
        )

        if not new_member:
            return False

        return new_member

    def _get_useable_website_user_selections(self):
        usable_website_user_records = self.env["res.users"].search(
            [("share", "=", "True")]
        )
        return [
            (str(record.id), record.login) for record in usable_website_user_records
        ]
