# -*- coding: utf-8 -*-
{
    'name': 'PaaS Management',
    'version': '1.0',
    'category': 'Management',
    'summary': 'Manage Odoo instances from a PaaS',
    'description': """
        This module allows you to track and manage Odoo instances
        retrieved from an external PaaS API.
    """,
    'author': 'Aureofy',
    'website': 'https://aureofy.com',
    'depends': ['base', 'contacts', 'account', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/paas_views.xml',
        'views/res_partner_views.xml',
        'data/paas_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
