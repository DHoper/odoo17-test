# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreCourseModel(models.Model):
    _name = "tutoring_centre.course"
    _description = "補習班系統-課程"

    name = fields.Char(string="課程名稱", required=True)
    # classes = fields.One2many(
    #     "tutoring_centre.course_class", string="班級", required=True
    # )
    # tutoringCentre_id = fields.Many2one(
    #     "tutoring_centre.course",
    #     required=True,
    #     ondelete="cascade",
    # )
