# -*- coding: utf-8 -*-

import time
import datetime

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc


class is_motif_retour(osv.osv_memory):
    _name = 'is.motif.retour'
    _description = u"Motif de retour à l'étape rédaction"
    
    _columns = {
        'date': fields.datetime('Date/Heure', required=True, readonly=True),
        'user_id': fields.many2one('res.users', 'Utilisateur', required=True, readonly=True),
        'motif': fields.text('Motif de retour', required=True),
    }
    
    _defaults = {
        'date': fields.datetime.now,
        'user_id': lambda obj, cr, uid, context: uid,
    }
    
    def valider_reponse(self, cr, uid, ids, context=None):
        ei_obj = self.pool.get('is.ei')
        is_motif_obj = self.pool.get('is.motif.retour.ei')
        
        ei = ei_obj.browse(cr, uid, context.get(('active_ids'), []), context=context)
        data = self.browse(cr, uid , ids[0], context=context)
        is_motif_obj.create(cr, uid, {'date': data.date,
                                      'user_id': data.user_id.id,
                                      'description': data.motif,
                                      'ei_id1': ei.id}, context=context)
        
        ei_obj.write(cr, uid, ei.id, {'state': 'draft'}, context=context)

        template_id=ei_obj.getId(cr, uid, ids, 'email_template_ei_vers_redaction')
        print "template_id=",template_id,ids[0]
        if template_id:
            self.pool.get('email.template').send_mail(cr, uid, template_id, ei.id, force_send=True, context=context)
        return

                    
