# -*- coding: utf-8 -*-
{
    "name": "會計系統-報表",
    "summary": """
        會計系統報表"
    """,
    "description": """
        會計系統報表"
    """,
    "version": "0.1",
    "application": True,
    "category": "Accounting",
    "installable": True,
    "depends": [
        "base",
        "account",
        "sale",
        "account_check_printing",
        "base_account_budget",
        "analytic",
    ],
    # 順序是有意義的
    "data": [
        "security/ir.model.access.csv",
        "data/account_financial_report_data.xml",
        "wizard/general_ledger.xml",
        "report/general_ledger_report.xml",
        "report/report_financial.xml",
        "report/report.xml",
        "views/accounting_menu.xml",
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'card_reader/static/src/**/*',
    #     ],
    # },
    "license": "AGPL-3",
}
