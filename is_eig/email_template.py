# -*- coding: utf-8 -*-


from openerp.osv import osv, fields


# Cela permet de supprimer le mécanisme de traduction des mails qui n'est pas utilisé
# => Mais cela ne fonctionne pas car la valeur False n'est pas prise en compte
# => J'ai du modifier directement email.template
#class email_template(osv.osv):
#    _inherit = 'email.template'
#    _columns = {
#        'subject':   fields.char("Subject", translate=False),
#        'body_html': fields.html("Body"   , translate=False),

#    }

