# -*- coding: utf-8 -*-
{
    'name': "HALO_template",

    'summary': """
        HALO customizations to mail""",

    'description': """
        HALO customizations to maiol
    """,

    'author': "Halo Solutions Inc",
    'website': "http://www.haloai.us",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail'],


    # always loaded
    'data': [
        #'views/HALO_sales_dashboards.xml',
        #'views/HALO_dashboards_menus.xml', #depends on dashboard
        #'data/default_records.xml', # must be loaded after all models
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    
    'installable': True,
    'application': True,
}
