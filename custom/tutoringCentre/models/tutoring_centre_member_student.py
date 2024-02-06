from odoo import fields, models, api


class TutoringCentreMemberModel(models.Model):
    _name = "tutoring_centre.member_student"
    _description = "補習班系統-會員-學生"

    name = fields.Char(string="姓名")
    birthdate = fields.Date(string="生日")

    # member_id = fields.Many2one(
    #     "tutoring_centre.member.student",
    #     required=True,
    #     ondelete="cascade",
    # )
