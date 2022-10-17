# -*- coding: utf-8 -*-
{
    'name': "Product Serial",

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
    'depends': ['base','mail','product_expiry','stock','product_brand','sale_management','purchase','report_csv'],

    # always loaded
    'data': [
        'security/contact.xml',
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/product_moves_report.xml',
        'views/cycling_count.xml',
        'views/serial_lots.xml',
        'views/moves.xml',
        'views/po_lines.xml',
        'views/location.xml',
        'reports/lots_serial_numbers.xml',
        'reports/product_moves_analysis.xml',
        'reports/templates.xml',
        'wizard/sync_all_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}