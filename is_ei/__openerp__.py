# -*- coding: utf-8 -*-
{
    'name': 'EI OVE',
    'version': '1.0',
    'category': 'InfoSaône',
    'description': """
OVE - Gestion des incidents
""",
    'author': 'Tony GALMICHE',
    'maintainer': 'InfoSaone',
    'website': 'http://www.infosaone.com',
    'depends': ['base', 'is_eig'],
    'data': [
        'security/is_ei_security.xml',
        'security/ir.model.access.csv',
        'assets.xml',                       # Permet d'ajouter les .css et .js
        'is_ei_action_data.xml',
        'wizard/is_motif_retour_view.xml',
        'is_ei_view.xml',
        'is_access_data.xml',
        'is_ei_report.xml',
        'views/report_is_ei.xml',
        'data/sequence.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
