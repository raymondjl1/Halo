# -*- coding: utf-8 -*-
{
    'name': "HALO_App_Connector",

    'summary': """
        HALO App Connector""",

    'description': """
        HALO App Connector
    """,

    'author': "Halo Solutions Inc",
    'website': "http://www.haloai.us",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/18.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'mail'],


    'data': [
        'security/ir.model.access.csv',
        'views/halo_menus.xml',
        'views/product_views.xml',
        'views/halo_subscriptions.xml',
        'views/halo_groups.xml',
        'views/halo_app_updates.xml',
        'data/email_template.xml',
        
        
    ],
    'installable': True,
    'application': True,
}
