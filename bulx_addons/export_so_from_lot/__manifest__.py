# -*- coding: utf-8 -*-
{
    'name': "Export SO from Lots",

    'summary': """
        Bulx""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','stock','sale_stock'],

    # always loaded
    'data': [
        # 'security/contact.xml',
        # 'security/ir.model.access.csv',
        'views/so_export.xml',
        # 'views/zone.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}