# -*- coding: utf-8 -*-
from odoo import fields, models

# 在'ir.actions.act_window.view'欄位中增加一項
class ActWindowView(models.Model): 
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[
        ('gallery', "Awesome Gallery")
    ],  ondelete={'gallery': 'cascade'})
