# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

class is_ei(osv.osv):
    _name = 'is.ei'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = u"Gestion des Événements Indésirables"
    _order = "name desc"
    #_rec_name = "etablissement_id"
    
    _columns = {
        'name': fields.char('N°'),
        'etablissement_id': fields.many2one('is.etablissement', u'Établissement', required=True),
        'redacteur_id': fields.many2one('res.users', u'Rédacteur', readonly=True, required=True),
        'valideur_id': fields.many2one('res.users', 'Valideur', readonly=True, required=True),
        #'traiteur_ids': fields.many2many('res.users', 'is_ei_users_rel', 'user_id', 'ei_id', 'Traiteurs'), 
        'type_event_id': fields.many2one('is.type.evenement.ei', u"Type d'événement", required=True),
        'nature_event_id': fields.many2one('is.nature.evenement.ei', u"Nature d'événement", required=True),
        'date_faits': fields.datetime('Date/heure', required=True),
        'description_faits': fields.text('Description des faits', required=True),

        #'consequence_faits': fields.many2one('is.consequence', u'Conséquences', required=True),
        'consequence_faits': fields.text('Conséquences', required=True),

        'lieu_faits': fields.char('Lieu', required=True),
        'victime_ids': fields.one2many('is.victime.ei', 'ei_id', 'Victime'),
        'mesure_immediat': fields.text(u'Mesures immédiates', required=True),
        'mesure_amelioration': fields.text(u"mesures d'amélioration éventuelles", required=True),
        'mesure_autre': fields.text('Autres', required=True),
        'info_date': fields.datetime('Date/heure'),

        #'destinataire_id': fields.many2one('res.users', 'Destinataire', required=True),
        'destinataire_id': fields.many2one('is.destinataire', 'Destinataire', required=True),

        'auteur_id': fields.many2one('res.users', 'Auteur (responsable de la diffusion)'),
        'attachment_ids': fields.many2many('ir.attachment', 'is_ei_attachment_rel', 'ei_id', 'attachment_id', u'Pièces jointes'),
        'motif_ids': fields.one2many('is.motif.retour.ei', 'ei_id1', 'Motif de retour', readonly=True),
        'state': fields.selection([('draft', u'Rédaction'),
                                  ('redige', u'Rédigé'),
                                  ('valide', u'Validé')], 'État', readonly=True, select=True),
    }
    
    _defaults = {
        'name': '',
        'redacteur_id': lambda obj, cr, uid, context: uid,
        'state': 'draft',
    }
    
    def get_signup_url(self, cr, uid, ids, context=None):
        url="https://eig.fondation-ove.fr/web#id="+str(ids[0])+"&view_type=form&model=is.ei"
        return url

#        assert len(ids) == 1
#        document = self.browse(cr, uid, ids[0], context=context)
#        contex_signup = dict(context, signup_valid=True)
#        return self.pool['res.partner']._get_signup_url_for_action(
#            cr, uid, [document.valideur_id.partner_id.id], action='mail.action_mail_redirect',
#            model=self._name, res_id=document.id, context=contex_signup,
#        )[document.valideur_id.partner_id.id]
    





    def get_valideur_traiteurs(self, cr, uid, etablissement_id, context=None):
        etablissement_obj = self.pool.get('is.etablissement')
        etablissement = etablissement_obj.browse(cr, uid, etablissement_id, context=context)
        return {'valideur_id': etablissement.director_id.id,
                #'traiteur_ids': etablissement.traiteur_ids and [e.id for e in  etablissement.traiteur_ids]
        }
        
    
    def onchange_etablissement_id(self, cr, uid, ids, etablissement_id, context=None):
        vals = {}
        if etablissement_id:
            vals = self.get_valideur_traiteurs(cr, uid, etablissement_id, context)
        return {'value': vals}
    
    


    def create(self, cr, uid, vals, context=None):
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'ei.number') or ''
        if 'etablissement_id' in vals and vals['etablissement_id']:
            res = self.get_valideur_traiteurs(cr, uid, vals['etablissement_id'], context)
            vals.update({'valideur_id': res['valideur_id']})
        return super(is_ei, self).create(cr, uid, vals, context=context)


    def copy(self, cr, uid, id, default=None, context=None):
        if not context:
            context = {}
        default.update({
            'redacteur_id': uid,
        })
        return super(is_ei, self).copy(cr, uid, id, default=default, context=context)



    
    
    def action_rediger_ei(self, cr, uid, ids, context=None):
        """ transaction de rédaction vers redigé """
        ei = self.browse(cr, uid, ids[0], context=context)
        self.write(cr, uid, ids, {'state': 'redige'}, context=context)
        template_id=self.getId(cr, uid, ids, 'email_template_ei_vers_redige')
        if template_id:
            self.pool.get('email.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
        
    def action_valider_eig(self, cr, uid, ids, context=None):
        """ transaction de redigé vers validé """
        ei = self.browse(cr, uid, ids[0], context=context)
        self.write(cr, uid, ids, {'state': 'valide'}, context=context)
        template_id=self.getId(cr, uid, ids, 'email_template_ei_vers_valide')
        if template_id:
            self.pool.get('email.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)

    
    def action_rediger_eig(self, cr, uid, ids, context=None):
        """ transaction de validé vers redigé """
        return self.write(cr, uid, ids, {'state': 'redige'}, context=context)




        
    def action_send_manual_ei(self, cr, uid, ids, context=None):
        """ Envoi manuel d'email """
        return self.action_ei_manual_send(cr, uid, ids, 'email_template_edi_is_ei', context)
    


    def getId(self, cr, uid, ids, external_id, context=None):
        obj = self.pool.get('ir.model.data')
        ids = obj.search(cr, uid, [('module', '=', 'is_ei'),('name', '=', external_id)], context=context)
        id=False;
        if ids:
            for l in obj.read(cr, uid, ids, ['res_id','name'], context=context):
                id=l["res_id"]
        return id



#    def action_ei_send(self, cr, uid, ids, email_template, user_id, context=None):
#        '''
#        This function opens a window to compose an email
#        '''
#        #assert len(ids) == 1, 'This option should only be used for a single id at a time.'
#        ir_model_data = self.pool.get('ir.model.data')
#        try:
#            template_id = ir_model_data.get_object_reference(cr, uid, 'is_ei', email_template)[1]
#        except ValueError:
#            template_id = False
#        #try:
#        #    compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
#        #except ValueError:
#        #    compose_form_id = False 
#        #ctx = dict()
#        #ctx.update({
#        #    'default_model': 'is.ei',
#        #    'default_res_id': ids[0],
#        #    'default_use_template': bool(template_id),
#        #    'default_template_id': template_id,
#        #    'default_composition_mode': 'comment',
#        #    'mark_so_as_sent': True
#        #})
#        print 'template ------', template_id
#        #print 'compose_form_id -----', compose_form_id
#        #return self.pool.get('email.template').send_mail(cr, uid, template_id, user_id, force_send=True, context=context)
#        #return self.pool.get('email.template').send_mail(cr, uid, 4, 1, force_send=True, context=context)
#        return
  
    def action_ei_manual_send(self, cr, uid, ids, email_template, context=None):
        '''
        This function opens a window to compose an email
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'is_ei', email_template)[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        ctx.update({
            'default_model': 'is.ei',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        print 'template ------', template_id
        print 'compose_form_id -----', compose_form_id
        return {
             'type': 'ir.actions.act_window',
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'mail.compose.message',
             'views': [(compose_form_id, 'form')],
             'view_id': compose_form_id,
             'target': 'new',
             'context': ctx,
         }

    
    def imprimer_rapport(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        return self.pool['report'].get_action(cr, uid, ids, 'is_ei.report_is_ei', context=context)


class is_type_evenement_ei(osv.osv):
    _name = 'is.type.evenement.ei'
    _description = u"Type d'évènement"
    
    _columns = {
        'name': fields.char(u"Type d'évènement", required=True),
    }
    

class is_nature_evenement_ei(osv.osv):
    _name = 'is.nature.evenement.ei'
    _description = u"Nature d'évènement"
    
    _columns = {
        'name': fields.char(u"Nature d'évènement", required=True),
    }

class is_victime_ei(osv.osv):
    _name = 'is.victime.ei'
    _description = 'Victime'
    
    _columns = {
        'name': fields.char('Nom'),
        'prenom': fields.char(u'Prénom'),
        'date_naissance': fields.date('Date de naissance'),
        'qualite_id': fields.many2one('is.qualite', u'Qualité'),
        'sexe_id': fields.many2one('is.sexe', 'Sexe'),
        'ei_id': fields.many2one('is.ei', 'EI', readonly=True),
    }
    
    
class is_motif_retour_ei(osv.osv):
    _name = 'is.motif.retour.ei'
    _description = u"Motifs de retour à l'étape Rédigé"
    
    _columns = {
        'date': fields.datetime('Date/Heure'),
        'user_id': fields.many2one('res.users', 'Auteur'),
        'description': fields.text('Motif'),
        'ei_id1': fields.many2one('is.ei', 'EI', readonly=True),
    }
    
    
