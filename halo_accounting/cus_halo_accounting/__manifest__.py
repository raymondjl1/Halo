# -*- coding: utf-8 -*-
{
    'name': 'Halo Accounting Customizations',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Custom accounting module for Halo: bank reconciliation and financial reports',
    'description': """
        Halo Accounting Customizations for Odoo 18
        ==========================================
        - Custom bank statement reconciliation widget
        - Manual proposition support with account/partner resolution
        - Auto-matching via reconciliation rules
        - Unreconcile functionality with manual move cleanup
        - Profit & Loss report with date filtering
        - Balance Sheet report with date filtering
        - Rainbow Man completion effect (OWL 18 compliant)
        - Budget model batch-create fix
    """,
    'author': 'Halo',
    'depends': [
        'account',
        'account_accountant',
        'base_accounting_kit',
        'base_account_budget',
        'dynamic_accounts_report',
    ],
    'data': [
        'views/account_bank_statement_views.xml',
        'views/financial_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cus_halo_accounting/static/src/xml/account_reconciliation.xml',
            'cus_halo_accounting/static/src/js/reconciliation_model.js',
            'cus_halo_accounting/static/src/js/reconciliation_renderer.js',
            'cus_halo_accounting/static/src/js/reconciliation.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
