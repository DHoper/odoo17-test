# -*- coding: utf-8 -*-
{
    "name": "補習班",
    "summary": """
        補習班"
    """,
    "description": """
        補習班"
    """,
    "author": "FJBC",
    "parentPortal": "",
    "category": "補習班/",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "web", "http_routing", "mail", "crm"],
    "application": True,
    "installable": True,
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "tutoringCentre.assets_parentPortal": [
            # bootstrap
            ("include", "web._assets_helpers"),
            "web/static/src/scss/pre_variables.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            # required for fa icons
            # "web/static/src/libs/fontawesome/css/font-awesome.css",
            # include base files from framework
            ("include", "web._assets_bootstrap"),
            ("include", "web._assets_core"),
            # remove some files that we do not use to create a minimal bundle
            # ("remove", "web/static/src/core/**/*"),
            # ("remove", "web/static/lib/luxon/luxon.js"),
            "web/static/src/core/registry.js",
            "web/static/src/libs/pdfjs.js",
            "web/static/src/views/fields/file_handler.*",
            # "web/static/src/core/assets.js",
            # "mail/static/src/discuss/**/common/**/*",
            "mail/static/src/**/common/**/*",
            # "web/static/src/core/utils/functions.js",
            # "web/static/src/core/browser/browser.js",
            "bus/static/src/**/*",
            "tutoringCentre/static/src/**/*",
        ],
    },
    "license": "AGPL-3",
}
