# -*- coding: utf-8 -*-
{
    'name': "Stock Return",

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
    'depends': ['base','mail','account','inventory_product_serials','stock_transfer','purchase','stock_picking_return_refund_option','picking_customer_info','stock'],

    # always loaded
    'data': [
        'security/contact.xml',
        'security/ir.model.access.csv',
        'reports/return_report.xml',
        'views/stock_return.xml',
        'views/return_reason.xml',
        'views/credit_note.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}