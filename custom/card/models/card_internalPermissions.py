# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
import logging
import random


_logger = logging.getLogger(__name__)


class CardInternalPermissions(models.Model):
    _name = "card.internal_permissions"
    _description = "內部卡片群組管理-許可權限"

    group_permission_id = fields.Many2one(
        "card.internal_group", string="權限ID(群組)", ondelete="cascade"
    )
    permission_id = fields.Many2one(
        "card.internal_management", string="權限ID", ondelete="cascade"
    )

    useable_card_reader = fields.Selection(
        selection=lambda self: self._get_useable_card_reader_selections(),
        string="讀卡機",
        tracking=True,
    )
    useable_time_permissions = fields.Many2many(
        "card.internal_time_config",
        string="許可時間",
        required=True,
    )
    color = fields.Integer("標籤顏色", default=0)
    display_name = fields.Char(
        string="顯示名稱", compute="_compute_display_name", store=True
    )

    @api.depends("useable_card_reader")
    def _compute_display_name(self):
        readerList = self.env["card_reader"].search([("device_mode", "=", "Write")])
        for record in self:
            if record.useable_card_reader:
                found_item = next(
                    (
                        item
                        for item in readerList
                        if item.id == int(record.useable_card_reader)
                    ),
                    None,
                )
                record.display_name = found_item.device_name

    def _get_useable_card_reader_selections(self):
        usable_cardReader_records = self.env["card_reader"].search(
            [("device_mode", "=", "Write")]
        )
        return [
            (str(record.id), record.device_name) for record in usable_cardReader_records
        ]

    readOnly = fields.Boolean(
        string="根據上下文設定的字段",
        compute="_compute_context_dependent_field",
        store=False,
    )

    @api.depends_context("readOnly")
    def _compute_context_dependent_field(self):
        for record in self:
            context_value = self.env.context.get("readOnly", False)
            if context_value is not None:
                record.readOnly = context_value
