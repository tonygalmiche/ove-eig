# -*- coding: utf-8 -*-

{
    'name': 'EIG OVE',
    'version': '1.0',
    'category': 'InfoSaône',
    'description': """
OVE Événements Indésirables Graves
""",
    'author': 'Tony GALMICHE',
    'maintainer': 'InfoSaone',
    'website': 'http://www.infosaone.com',
    'depends': ['base', 'document', 'email_template'],
    'data': ['security/is_eig_security.xml',
             'security/ir.model.access.csv',
             'is_eig_action_data.xml',
             'wizard/is_motif_retour_view.xml',
             'menu.xml',
             'is_eig_data.xml',
             'is_eig_view.xml',
             'is_access_data.xml',
             'data/sequence.xml',
             'views/webclient_templates.xml',
            ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
