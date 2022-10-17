# -*- coding: utf-8 -*-
{
    'name': "Logistics",

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
    'depends': ['base','mail','stock'],

    # always loaded
    'data': [
        'security/contact.xml',
        'security/ir.model.access.csv',
        'views/hub.xml',
        'views/logistics_data.xml',
        'views/partners.xml',
        # 'reports/product_moves_analysis.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}