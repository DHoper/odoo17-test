# -*- coding: utf-8 -*-
from odoo import fields, models

# 在'ir.ui.view'欄位中增加一項
class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('gallery', "Awesome Gallery")])
