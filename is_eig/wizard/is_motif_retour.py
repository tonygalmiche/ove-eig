# -*- coding: utf-8 -*-

import time
import datetime

from openerp.osv import fields,osv
from openerp.tools.translate import _
from openerp import netsvc,api
from openerp import SUPERUSER_ID


class is_motif_retour_redaction_eig(osv.osv_memory):
    _name = 'is.motif.retour.redaction.eig'
    _description = u"Motif de retour à l'étape rédaction d'un EIG"
    
    _columns = {
        'date': fields.datetime('Date/Heure', required=True, readonly=True),
        'user_id': fields.many2one('res.users', 'Utilisateur', required=True, readonly=True),
        'operation': fields.char('Opération', readonly=True),
        'operation_id': fields.char('Opération Id', readonly=True),
        'motif': fields.text('Motif de retour', required=True),
    }
    
    _defaults = {
        'date': fields.datetime.now,
        'user_id': lambda obj, cr, uid, context: uid,
    }

    @api.model
    def default_get(self, fields):
        context = self._context
        context = context or {}
        res = super(is_motif_retour_redaction_eig, self).default_get(fields)
        operation_id=context["operation_id"]
        res["operation_id"]=operation_id
        if operation_id=="retour_redaction":
            res["operation"]=u"retour Rédaction"
        if operation_id=="retour_completer":
            res["operation"]=u"retour Compléter"
        return res


    def valider_reponse(self, cr, uid, ids, context=None):
        eig_obj = self.pool.get('is.eig')
        is_motif_obj = self.pool.get('is.motif.retour.eig')
        eig = eig_obj.browse(cr, uid, context.get(('active_ids'), []), context=context)
        data = self.browse(cr, uid , ids[0], context=context)
        is_motif_obj.create(cr, uid, {'date': data.date,
                                      'user_id': data.user_id.id,
                                      'action': data.operation,
                                      'description': data.motif,
                                      'eig_id1': eig.id}, context=context)

        if data.operation_id=="retour_redaction":
            eig_obj.write(cr, SUPERUSER_ID, eig.id, {'state': 'draft', 'related_group_motif_retour': True}, context=context)
            template_id=eig_obj.getId(cr, uid, ids, 'email_template_redige_vers_redaction')
        if data.operation_id=="retour_completer":
            eig_obj.write(cr, SUPERUSER_ID, eig.id, {'state': 'complet', 'related_group_motif_retour': True}, context=context)
            template_id=eig_obj.getId(cr, uid, ids, 'email_template_valide_vers_a_completer')
        if template_id:
            self.pool.get('email.template').send_mail(cr, uid, template_id, eig.id, force_send=True, context=context)
        return




                    
