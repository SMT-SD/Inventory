# -*- coding: utf-8 -*-
{
    'name': "Bulx brand category APi",

    'summary': """
        Brand Category order Customer product""",

    'description': """
        Integration API
    """,

    'author': "My Company",
    'website': "http://www.technic.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'stock', 'product_brand', 'product_category_codes'],

    # always loaded
    'data': [
        # 'security/contact.xml',
        'security/ir.model.access.csv',
        'views/bulx_city.xml',
        'views/bulx_address.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/product.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
