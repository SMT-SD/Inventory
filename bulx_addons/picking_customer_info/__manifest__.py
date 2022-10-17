# -*- coding: utf-8 -*-
{
    'name': "Picking Customer Information Report",

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
    'depends': ['base','mail','account','purchase','sale_management','stock','inventory_product_api'],

    # always loaded
    'data': [
        'security/contact.xml',
        # 'security/ir.model.access.csv',
        # 'views/picking_customer_info.xml',
        'views/hide_apply_button.xml',
        'views/hide_taxes.xml',
        'views/invoice_customer_data.xml',
        'views/picking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}