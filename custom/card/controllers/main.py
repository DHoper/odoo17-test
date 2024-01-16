# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class CardHaloTest(http.Controller):
    @http.route(["/halo"], type="json", auth="public", method=["POST"])
    def get_halo(self):
        employees = request.env["hr.employee"].sudo().search([])

        # 获取 hr.employee 的所有字段名
        employee_fields = request.env["hr.employee"]._fields.keys()

        # 将记录转换为字典列表，动态获取所有字段的值
        employee_data = [
            {field: getattr(employee, field) for field in employee_fields}
            for employee in employees
        ]

        data = {
            "status": 200,
            "response": employee_data,
            "message": "All Employees Returned",
        }
        return data
