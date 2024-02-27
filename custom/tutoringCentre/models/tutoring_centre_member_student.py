from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreStudentModel(models.Model):
    _name = "tutoring_centre.member_student"
    _description = "補習班系統-會員-學生"

    name = fields.Char(string="姓名")
    courses = fields.Many2many("tutoring_centre.course", string="班級", readonly=True)
    birthdate = fields.Date(string="生日")
    member_id = fields.Many2one("tutoring_centre.member", string="會員", required=True)
    active_channels = fields.Many2many(
        "discuss.channel", string="啟用頻道", readonly=True
    )

    # def write(self, vals):
    #     if vals.get("courses"):
    #         res = super(TutoringCentreStudentModel, self).write(vals)
    #         self.ensure_one()
    #         _logger.info(f"----------------------->{self}--------{self.courses}")
    #         self.courses.write({"student": self})
    #         return res
    #     else:
    #         return super(TutoringCentreStudentModel, self).write(vals)
