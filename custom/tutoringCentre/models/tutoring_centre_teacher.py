# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreTeacherModel(models.Model):
    _name = "tutoring_centre.teacher"
    _description = "補習班系統-老師"

    name = fields.Char(string="姓名", required=True)
    is_active = fields.Boolean(string="帳號狀態", required=True, default=True)
    courses = fields.Many2many("tutoring_centre.course", string="負責班級")
    portal_user = fields.Many2one(
        "res.users",
        string="使用者帳號",
        domain=[("share", "=", False)],
        required=True,
    )
