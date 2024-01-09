# -*- coding: utf-8 -*-
{
    'name': "讀卡機裝置",
    'summary': """
        讀卡機裝置管理系統"
    """,

    'description': """
        讀卡機裝置管理系統"
    """,

    'version': '0.1',
    'application': True,
    'category': 'Device/',
    'installable': True,
    'depends': ['base'],
    # 順序是有意義的
    'data': [
        'security/ir.model.access.csv',
        'views/card_reader.xml',
        'views/menus.xml',
        ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'card_reader/static/src/**/*',
    #     ],
    # },
    'license': 'LGPL-3'
}
