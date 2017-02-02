# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

import uuid
from appy.pod.renderer import Renderer
import os
from openerp import SUPERUSER_ID

from pytz import timezone
import pytz

import base64

#Importation des listes de selections communes à plusieurs objets
from selection import AutoriteControle, OuiNon
#from selection import AutoriteControle

#OuiNon=[('oui', 'Oui'),('non', 'Non')]
#AutoriteControle=[('ars', 'ARS'),('cd', 'CD'),('ars_cd', 'ARS+CD')]


class is_destinataire (osv.osv):
    _name = 'is.destinataire'
    _description = u"Destinataire"
    _columns = {
        'name': fields.char('Nom' , required=True),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]
    _defaults = {
    }


class is_auteur (osv.osv):
    _name = 'is.auteur'
    _description = u"Auteur"
    _columns = {
        'name': fields.char('Nom' , required=True),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]
    _defaults = {
    }


class is_departement(osv.osv):
    _name = 'is.departement'
    _description = u"Département"
    _order = "name"
    
    _columns = {
        'name': fields.char('Nom du département' , required=True),
        'code': fields.char('Code du département', required=True),
        'mail_ars': fields.char('Mail ARS'),
        'mail_cg':  fields.char('Mail CD', help="Mail du Conseil Départemental"),
        'mail_ase': fields.char('Mail ASE'),
    }
    
    _sql_constraints = [
        ('code_uniq', 'unique(code)', u"Le code du département doit être unique !"),
        ('name_uniq', 'unique(name)', u"Le nom du département doit être unique !"),
    ]
    
    _defaults = {
    }





class is_etablissement(osv.osv):
    _name = 'is.etablissement'
    _description = u"Établissement"
    _order = "name"

    _columns = {
        'name': fields.char('Nom', required=True),
        'identifiant': fields.char('Identifiant', required=True),
        'departement_id': fields.many2one('is.departement', 'Département', required=True),
        'director_id': fields.many2one('res.users', 'Directeur', readonly=False, required=True),
        'responsible_id': fields.many2one('res.users', 'Responsable', required=True),

        'responsable_ids': fields.many2many('res.users', 'is_etablissement_responsables_rel', 'etablissement_id', 'user_id', 'Autres responsables'),

        #'traiteur_ids': fields.many2many('res.users', 'is_etablissement_users_rel', 'user_id', 'etablissement_id', 'Traiteurs'),
        'membre_ids': fields.many2many('res.users', 'is_etablissement_membres_rel', 'etablissement_id', 'user_id', 'Membres'),

        'autorite_controle': fields.selection(AutoriteControle, 'Autorité de Contrôle'),


        'adresse1': fields.char('Adresse', required=False),
        'adresse2': fields.char('Adresse (suite)', required=False),
        'cp': fields.char('CP', required=False),
        'ville': fields.char('Ville', required=False),
        'finess': fields.char('Finess', required=False),
        'telephone': fields.char('Téléphone', required=False),
        'fax': fields.char('Fax', required=False),
    }
    
    _sql_constraints = [
        ('identifiant_uniq', 'unique(identifiant)', u"L'identifiant de l'établissement doit être unique !"),
    ]
    
    _defaults = {
        'director_id': lambda obj, cr, uid, context: uid,
    }
            
    
class is_manip_fields(osv.osv):
    _name = 'is.manip.fields'
    _description = u"Caractéristiques des champs"
    
    _columns = {
        'fields_id': fields.many2one('ir.model.fields', 'Champs', ondelete='cascade', required=True, select=1),
        'field_visible': fields.boolean('Visible'),
        'field_required': fields.boolean('Obligatoire'),
        'type_event_id': fields.many2one('is.type.evenement', 'Type evenement'),
        'is_eig': fields.boolean('EIG'),
        'is_eig_auteur': fields.boolean('Auteur'),
        'is_eig_temoin': fields.boolean('Temoin'),
        'is_eig_victim': fields.boolean('Victim'),
        'is_eig_infos': fields.boolean('Infos'),
    }
    
    _defaults = {
        'is_eig': False,
        'is_eig_auteur': False,
        'is_eig_temoin': False,
        'is_eig_victim': False,
        'is_eig_infos': False,
    }
    



class is_type_evenement_mail(osv.osv):
    _name = 'is.type.evenement.mail'
    _description = 'is.type.evenement.mail'
    
    _columns = {
        'autorite_controle': fields.selection(AutoriteControle  , 'Autorité de Contrôle'),
        'mail_destination':  fields.selection(AutoriteControle  , 'Mail de destination du département'),
        'type_evenement_id': fields.many2one('is.type.evenement', 'Type d’événement'),
    }




class is_type_evenement(osv.osv):
    _name = 'is.type.evenement'
    _description = u"Type d’événement"
    
    _columns = {
        'code': fields.char('Code'),
        'name': fields.char('Nom', required=True),

        'mail_destination_ids': fields.one2many('is.type.evenement.mail', 'type_evenement_id', 'Mail de destination'),

        'onglet_faits':                  fields.boolean(u'Afficher onglet Faits'),
        'onglet_auteurs':                fields.boolean(u'Afficher onglet Auteurs'),
        'onglet_temoins':                fields.boolean(u'Afficher onglet Témoins'),
        'onglet_victimes':               fields.boolean(u'Afficher onglet Victimes'),
        'onglet_mesures':                fields.boolean(u'Afficher onglet Mesures'),
        'onglet_infos':                  fields.boolean(u'Afficher onglet Infos'),
        'onglet_element_complementaire': fields.boolean(u'Afficher onglet Eléments complémentaires'),

        'fields_eig_id': fields.one2many('is.manip.fields', 'type_event_id', 'Caractéristiques des champs EIG', domain=[('is_eig', '=', True)]),
        'fields_auteur_id': fields.one2many('is.manip.fields', 'type_event_id', 'Caractéristiques des champs Auteur', domain=[('is_eig_auteur', '=', True)]),
        'fields_victim_id': fields.one2many('is.manip.fields', 'type_event_id', 'Caractéristiques des champs Victime', domain=[('is_eig_victim', '=', True)]),
        'fields_temoin_id': fields.one2many('is.manip.fields', 'type_event_id', 'Caractéristiques des champs Témoins', domain=[('is_eig_temoin', '=', True)]),
        'fields_info_id': fields.one2many('is.manip.fields', 'type_event_id', 'Caractéristiques des champs ', domain=[('is_eig_infos', '=', True)]),    

    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le Type d'évènement doit être unique !"),
    ]
    
    
    #Cette fonction permet de recharger les éventuelles modifications dans is_default_type_event -->
    def onchange_type_event(self, cr, uid, ids, name, context=None):
        default_obj = self.pool.get('is_default_type_event')
        lst_eig        = default_obj.get_fields_eig_properties(cr, uid, True, context=context)
        lst_eig_auteur = default_obj.get_fields_auteur_properties(cr, uid, True, context=context)
        lst_eig_victim = default_obj.get_fields_victim_properties(cr, uid, True, context=context)
        lst_eig_temoin = default_obj.get_fields_temoin_properties(cr, uid, True, context=context)
        lst_eig_infos  = default_obj.get_fields_infos_properties(cr, uid, True, context=context)
        
        return {'value': {'fields_eig_id': lst_eig, 
                          'fields_auteur_id': lst_eig_auteur,
                          'fields_victim_id': lst_eig_victim, 
                          'fields_temoin_id': lst_eig_temoin,
                          'fields_info_id': lst_eig_infos}}
        
        
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals and vals['code']:
            value = self.pool.get('is_default_type_event').update_vals_create(cr, uid, vals['code'], context=context)
            vals.update(value)
        return super(is_type_evenement, self).create(cr, uid, vals, context=context)
        
    def update_one2many_fields(self, cr, uid, object, eig_id, lst_fields, context=None):
        field_ids = object.search(cr, uid, [('is_eig_id','=',eig_id)], context=context)
        if field_ids:
            for field_id in field_ids:
                for item in lst_fields:
                    field_vsb = str('related_vsb_'+item.fields_id.name)
                    field_rqr = str('related_rqr_'+item.fields_id.name)
                    object.write(cr, uid, field_id, {field_vsb:False, field_rqr:False}, context=context)
                    vals = {}
                    if item.field_visible :
                        field = str('related_vsb_'+item.fields_id.name)
                        vals.update({field: True})
                        if item.field_required:
                            field = str('related_rqr_'+item.fields_id.name)
                            vals.update({field: True})
                    if vals:
                        object.write(cr, uid, field_id, vals, context=context)
        return True

                
    def write(self, cr, uid, ids, vals, context=None):
        res = super(is_type_evenement, self).write(cr, uid, ids, vals, context=context)
        #if 'fields_eig_id' in vals or 'fields_auteur_id' in vals or 'fields_victim_id' in vals or 'fields_temoin_id' in vals or 'fields_info_id' in vals:
        type_event = self.browse(cr, uid, ids[0], context=context)
        """ Mettre à jour les EIG utilisant ce type d'evenement """
        eig_obj = self.pool.get('is.eig')
        eig_ids = eig_obj.search(cr, uid, [('type_event_id','=', ids[0])], context=context)
        if eig_ids:
            for eig_id in eig_ids:
                value = eig_obj.onchange_type_event(cr, uid, [eig_id], ids[0], context=context)['value']
                eig_obj.write(cr, uid, eig_id, value, context=context)
                
                auteur_obj = self.pool.get('is.eig.auteur')
                temoin_obj = self.pool.get('is.eig.temoin')
                victim_obj = self.pool.get('is.eig.victime')
                infos_obj = self.pool.get('is.infos.communication')
                self.update_one2many_fields(cr, uid, auteur_obj, eig_id, type_event.fields_auteur_id, context)
                self.update_one2many_fields(cr, uid, temoin_obj, eig_id, type_event.fields_temoin_id, context)
                self.update_one2many_fields(cr, uid, victim_obj, eig_id, type_event.fields_victim_id, context)
                self.update_one2many_fields(cr, uid, infos_obj, eig_id, type_event.fields_info_id, context)
        return res

            
    
class is_nature_evenement(osv.osv):
    _name = 'is.nature.evenement'
    _description = u"Nature d'événement"
    
    _columns = {
        'name': fields.char('Nature', required=True),
    }
    

class is_type_risque(osv.osv):
    _name = 'is.type.risque'
    _description = "Type de risque"
    
    _columns = {
        'name': fields.char('Type', required=True),
    }
    

class is_nature_risque(osv.osv):
    _name = 'is.nature.risque'
    _description = "Nature de risque"
    
    _columns = {
        'name': fields.char('Nature', required=True),
    }
    
    

class is_qualite(osv.osv):
    _name = 'is.qualite'
    _description = u'Qualité'
    
    _columns = {
        'name': fields.char(u'Qualité', required=True),
    }
    

class is_sexe(osv.osv):
    _name = 'is.sexe'
    _description = 'Sexe'
    
    _columns = {
        'name': fields.char('Sexe', required=True),
    }
    
    
class is_disposition_prise(osv.osv):
    _name = 'is.disposition.prise'
    _description = 'disposition prises'
    
    _columns = {
        'name': fields.char('Nom de dispostion', required=True),
    }   
    
    
class is_consequence(osv.osv):
    _name = 'is.consequence'
    _description = u"Conséquences"
    
    _columns = {
        'name': fields.char(u'Conséquence', required=True),
    }
    
    
class is_eig_auteur(osv.osv):
    _name = 'is.eig.auteur'
    _description = 'Auteur'
    
    _columns = {
        'identifie': fields.boolean(u'Identifié'),
        'related_vsb_identifie': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_identifie': fields.boolean(u'Champs technique - Obligation'),
        
        'name': fields.char('Nom'),
        'related_vsb_name': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_name': fields.boolean(u'Champs technique - Obligation'),
        
        'prenom': fields.char('Prénom'),
        'related_vsb_prenom': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_prenom': fields.boolean(u'Champs technique - Obligation'),
        
        'birthdate': fields.date('Date de naissance'),
        'related_vsb_birthdate': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_birthdate': fields.boolean(u'Champs technique - Obligation'),
        
        'qualite_id': fields.many2one('is.qualite', u'Qualité'),
        'related_vsb_qualite_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_qualite_id': fields.boolean(u'Champs technique - Obligation'),
        

        'sexe_id': fields.many2one('is.sexe', 'Sexe'),
        'related_vsb_sexe_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_sexe_id': fields.boolean(u'Champs technique - Obligation'),

        'disposition_id': fields.many2one('is.disposition.prise', 'Disposition prises'),
        'related_vsb_disposition_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_disposition_id': fields.boolean(u'Champs technique - Obligation'),
        
        'adresse': fields.char('Adresse'),
        'related_vsb_adresse': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_adresse': fields.boolean(u'Champs technique - Obligation'),

        'is_eig_id': fields.many2one('is.eig', 'EIG'),
    }     
    
    
class is_eig_temoin(osv.osv):
    _name = 'is.eig.temoin'
    _description = u'Témoins'
    
    _columns = {
        'identifie': fields.boolean(u'Identifié'),
        'related_vsb_identifie': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_identifie': fields.boolean(u'Champs technique - Obligation'),
        
        'name': fields.char('Nom'),
        'related_vsb_name': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_name': fields.boolean(u'Champs technique - Obligation'),
        
        'prenom': fields.char('Prénom'),
        'related_vsb_prenom': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_prenom': fields.boolean(u'Champs technique - Obligation'),

        'sexe_id': fields.many2one('is.sexe', 'Sexe'),
        'related_vsb_sexe_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_sexe_id': fields.boolean(u'Champs technique - Obligation'),

        'address': fields.char('Adresse'),
        'related_vsb_address': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_address': fields.boolean(u'Champs technique - Obligation'),
        
        'birthdate': fields.date('Date de naissance'),
        'related_vsb_birthdate': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_birthdate': fields.boolean(u'Champs technique - Obligation'),
        
        'qualite_id': fields.many2one('is.qualite', u'Qualité'),
        'related_vsb_qualite_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_qualite_id': fields.boolean(u'Champs technique - Obligation'),
        
        'disposition_id': fields.many2one('is.disposition.prise', 'Disposition prises'),
        'related_vsb_disposition_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_disposition_id': fields.boolean(u'Champs technique - Obligation'),
        
        'is_eig_id': fields.many2one('is.eig', 'EIG'),
    }


class is_eig_victime(osv.osv):
    _name = 'is.eig.victime'
    _description = 'Victime'
    
    _columns = {
        'identifie': fields.boolean(u'Identifié'),
        'related_vsb_identifie': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_identifie': fields.boolean(u'Champs technique - Obligation'),

        'name': fields.char('Nom'),
        'related_vsb_name': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_name': fields.boolean(u'Champs technique - Obligation'),
        
        'prenom': fields.char('Prénom'),
        'related_vsb_prenom': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_prenom': fields.boolean(u'Champs technique - Obligation'),

        'sexe_id': fields.many2one('is.sexe', 'Sexe'),
        'related_vsb_sexe_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_sexe_id': fields.boolean(u'Champs technique - Obligation'),

        'address': fields.char('Adresse'),
        'related_vsb_address': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_address': fields.boolean(u'Champs technique - Obligation'),
        
        'birthdate': fields.date('Date de naissance'),
        'related_vsb_birthdate': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_birthdate': fields.boolean(u'Champs technique - Obligation'),

        'ecole': fields.char('École fréquentée'),
        'related_vsb_ecole': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_ecole': fields.boolean(u'Champs technique - Obligation'),

        'qualite_id': fields.many2one('is.qualite', u'Qualité'),
        'related_vsb_qualite_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_qualite_id': fields.boolean(u'Champs technique - Obligation'),
        
        'disposition_id': fields.many2one('is.disposition.prise', 'Disposition prises'),
        'related_vsb_disposition_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_disposition_id': fields.boolean(u'Champs technique - Obligation'),
        
        'consequence_id': fields.many2one('is.consequence', u'Conséquences'),
        'related_vsb_consequence_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_consequence_id': fields.boolean(u'Champs technique - Obligation'),
        
        'nom_pere': fields.char('Nom Père'),
        'related_vsb_nom_pere': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_nom_pere': fields.boolean(u'Champs technique - Obligation'),
        
        'prenom_pere': fields.char(u'Prénom Père'),
        'related_vsb_prenom_pere': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_prenom_pere': fields.boolean(u'Champs technique - Obligation'),
        
        'address_pere': fields.char('Adresse Père'),
        'related_vsb_address_pere': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_address_pere': fields.boolean(u'Champs technique - Obligation'),
        
        'nom_mere': fields.char('Nom Mère'),
        'related_vsb_nom_mere': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_nom_mere': fields.boolean(u'Champs technique - Obligation'),
        
        'prenom_mere': fields.char(u'Prénom Mère'),
        'related_vsb_prenom_mere': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_prenom_mere': fields.boolean(u'Champs technique - Obligation'),
        
        'address_mere': fields.char('Adresse Mère'),
        'related_vsb_address_mere': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_address_mere': fields.boolean(u'Champs technique - Obligation'),
        
        'is_eig_id': fields.many2one('is.eig', 'EIG'),
    }
    

class is_infos_communication(osv.osv):
    _name = 'is.infos.communication'
    _description = "Information communication"
    
    _columns = {
        'date': fields.datetime('Date heure'),
        'related_vsb_date': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_date': fields.boolean(u'Champs technique - Obligation'),
        
        'user_id': fields.many2one('is.destinataire', 'Destinataire', help=u"Indiquer qui a été saisi par une information concernant l'EIG (exemple : la presse a été saisie par un personnel de la structure)"),
        'related_vsb_user_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_user_id': fields.boolean(u'Champs technique - Obligation'),
        
        'responsible_id': fields.many2one('is.auteur', 'Auteur', help=u"Indiquer qui est à l'origine de cette information (par exemple : la famille d'un usager a informé le procureur)"),
        'related_vsb_responsible_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_responsible_id': fields.boolean(u'Champs technique - Obligation'),
        
        'support': fields.char('Support', help=u"Permet d'indiquer le support de communication (courrier, presse écrite, internet, journal interne)"),
        'related_vsb_support': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_support': fields.boolean(u'Champs technique - Obligation'),
        
        'info_cible': fields.char('Information cible', help=u"Indiquer la nature des événements communiqués"),
        'related_vsb_info_cible': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_info_cible': fields.boolean(u'Champs technique - Obligation'),
        
        'impact': fields.boolean(u'Impact médiatique', help=u"A cocher si l'événement est susceptible d'avoir un impact médiatique"),
        'related_vsb_impact': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_impact': fields.boolean(u'Champs technique - Obligation'),
        
        'is_eig_id': fields.many2one('is.eig', 'EIG'),
    }
    
    


class is_motif_retour_eig(osv.osv):
    _name = 'is.motif.retour.eig'
    _description = u"Motifs de retour EIG"
    
    _columns = {
        'date': fields.datetime('Date/Heure'),
        'user_id': fields.many2one('res.users', 'Auteur'),
        'action': fields.char('Action'),
        'description': fields.text('Motif'),
        'eig_id1': fields.many2one('is.eig', 'EIG', readonly=True),
    }





class is_eig(osv.osv):
    _name = 'is.eig'
    _description = u"Événements Indésirables Graves"
    #_rec_name = "etablissement_id"
    _order = "name desc"



    # Btn Rédaction => Rédigé
    def _btn_rediger_eig(self, cr, uid, ids, names, arg, context=None):
            res = {}
            for obj in self.browse(cr, uid, ids, context=context):
                r=False
                if obj.state=="draft":
                    if  uid == SUPERUSER_ID \
                        or self.pool['res.users'].has_group(cr, uid, 'is_eig.group_is_traiteur') \
                        or uid==obj.etablissement_id.director_id.id \
                        or uid==obj.etablissement_id.responsible_id.id \
                        or uid==obj.redacteur_id.id:
                        r=True
                res[obj.id] = r
            return res


    # Btn Rédigé => Validé
    def _btn_valider_eig(self, cr, uid, ids, names, arg, context=None):
            res = {}
            for obj in self.browse(cr, uid, ids, context=context):
                r=False
                if obj.state=="redige":
                    if  uid == SUPERUSER_ID \
                        or self.pool['res.users'].has_group(cr, uid, 'is_eig.group_is_traiteur') \
                        or uid==obj.etablissement_id.director_id.id:
                        r=True
                res[obj.id] = r
            return res


    # Btn Rédigé => Rédaction
    def _btn_retour_redaction(self, cr, uid, ids, names, arg, context=None):
            res = {}
            for obj in self.browse(cr, uid, ids, context=context):
                r=False
                if obj.state=="redige":
                    if  uid == SUPERUSER_ID \
                        or self.pool['res.users'].has_group(cr, uid, 'is_eig.group_is_traiteur') \
                        or uid==obj.redacteur_id.id \
                        or uid==obj.etablissement_id.director_id.id:
                        r=True
                res[obj.id] = r
            return res


    # Btn Completer
    def _btn_completer_eig(self, cr, uid, ids, names, arg, context=None):
            res = {}
            for obj in self.browse(cr, uid, ids, context=context):
                r=False
                if obj.state=="valide":
                    if  uid == SUPERUSER_ID \
                        or self.pool['res.users'].has_group(cr, uid, 'is_eig.group_is_traiteur'):
                        r=True
                res[obj.id] = r
            return res


    # Btn Completer => Valider
    def _btn_completer_vers_valider_eig(self, cr, uid, ids, names, arg, context=None):
            res = {}
            for obj in self.browse(cr, uid, ids, context=context):
                r=False
                if obj.state=="complet":
                    if  uid == SUPERUSER_ID \
                        or self.pool['res.users'].has_group(cr, uid, 'is_eig.group_is_traiteur') \
                        or uid==obj.etablissement_id.director_id.id:
                        r=True
                res[obj.id] = r
            return res


    _columns = {
        'btn_rediger_eig':               fields.function(_btn_rediger_eig               , type='boolean'),
        'btn_valider_eig':               fields.function(_btn_valider_eig               , type='boolean'),
        'btn_retour_redaction':          fields.function(_btn_retour_redaction          , type='boolean'),
        'btn_completer_eig':             fields.function(_btn_completer_eig             , type='boolean'),
        'btn_completer_vers_valider_eig':fields.function(_btn_completer_vers_valider_eig, type='boolean'),
        'state': fields.selection([
            ('draft', u'Rédaction'),
            ('redige', u'Rédigé'),
            ('valide', u'Validé'),
            ('complet', u'A compléter'),
            ('done', u'Traité'),
            ('non_declarable', u'Non déclarable')
        ], 'Statut', readonly=True, select=True),
        'name': fields.char('N°'),
        'etablissement_id': fields.many2one('is.etablissement', u'Établissement', required=True, help=u'ESMS concerné par un EIG. Ce choix détermine le formulaire départemental qui sera généré et envoyé aux autorités de tutelles.'),
        'redacteur_id': fields.many2one('res.users', u'Rédacteur', readonly=True),
        'valideur_id': fields.many2one('res.users', 'Valideur', readonly=True),

        'date_validation': fields.datetime(u'Date de validation'),

        #'traiteur_ids': fields.many2many('res.users', 'is_eig_users_rel', 'user_id', 'eig_id', 'Traiteurs', readonly=True, required=True),
        'type_event_id': fields.many2one('is.type.evenement', u"Type d'événement", required=True, help=u"Grandes catégories d'EIG. Pour tout EIG concernant un ou plusieurs mineurs relevant de l'ASE, il est nécessaire de sélectionner « Mineur relevant de l'ASE ». Ce choix détermine également le formulaire départemental qui sera généré et envoyé aux autorités de tutelles."),
        'nature_event_id': fields.many2one('is.nature.evenement', u"Nature d'événement", required=True, help=u"Préciser le type d'événement à déclarer."),


        'nature_precision': fields.char('Précision nature évènement'),
        'related_vsb_nature_precision': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_nature_precision': fields.boolean(u'Champs technique - Obligation'),


        'type_risq_id': fields.many2one('is.type.risque', "Type de risque", required=False, help=u"Permet de préciser sur quel temps du parcours de l'usager est apparu l'EIG."),
        'nature_risq_id': fields.many2one('is.nature.risque', "Nature de risque", required=True, help=u"Permet d'identifier la nature du risque afin d'alimenter la cartographie des risques de la fondation OVE"),
        
        'signalement_autorites': fields.boolean(u'Signalement aux autorités judiciaires'),

        'start_date': fields.datetime(u'Date heure de début', help=u"Date connue de début de l'événement. En cas de maladie il s'agit de la date connue de déclaration des symptômes chez le premier malade."),
        'related_vsb_start_date': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_start_date': fields.boolean(u'Champs technique - Obligation'),
        
        'end_date': fields.datetime('Date heure de fin', help=u"Date connue de fin de l'événement. En cas de maladie il s'agit de la date connue de déclaration des symptômes chez le dernier malade."),
        'related_vsb_end_date': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_end_date': fields.boolean(u'Champs technique - Obligation'),
        
        'description_faits': fields.text('Description des faits', help=u"Permet de décrire de manière exhaustive et détaillée les faits survenus dans votre établissement. En cas de maladie il est nécessaire de préciser de quelle maladie ou contamination il s'agit en l'espèce."),
        'related_vsb_description_faits': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_description_faits': fields.boolean(u'Champs technique - Obligation'),
        


        'risque_reproductivite': fields.selection(OuiNon, 'Risque de reproductivité'),
        'related_vsb_risque_reproductivite': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_risque_reproductivite': fields.boolean(u'Champs technique - Obligation'),

        'risque_extension': fields.selection(OuiNon, "Risque d'extension"),
        'related_vsb_risque_extension': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_risque_extension': fields.boolean(u'Champs technique - Obligation'),

        'risque_contentieux': fields.selection(OuiNon, "Risque de contentieux immédiat"),
        'related_vsb_risque_contentieux': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_risque_contentieux': fields.boolean(u'Champs technique - Obligation'),

        'evenement_maitrise': fields.selection(OuiNon, "L'événement semble t-il maîtrisé"),
        'related_vsb_evenement_maitrise': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_evenement_maitrise': fields.boolean(u'Champs technique - Obligation'),

        'si_non_maitrise': fields.text("Si non maîtrisé, précisez pourquoi"),
        'related_vsb_si_non_maitrise': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_si_non_maitrise': fields.boolean(u'Champs technique - Obligation'),

        'lieu_faits': fields.char('Lieu', help=u"Permet d'indiquer le lieu de déroulement des faits"),
        'related_vsb_lieu_faits': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_lieu_faits': fields.boolean(u'Champs technique - Obligation'),
        
        'element_faits': fields.text(u'Eléments préoccupants'),
        'related_vsb_element_faits': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_element_faits': fields.boolean(u'Champs technique - Obligation'),
        
        'cause_faits': fields.boolean(u'Cause identifiée', help="Cet item est obligatoire en cas de « maladie » ou d'« atteinte à l'intégrité des usagers » dans la partie « Type de risque »."),
        'related_vsb_cause_faits': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_cause_faits': fields.boolean(u'Champs technique - Obligation'),
        



        'reunion_debriefing': fields.selection(OuiNon, "Une première réunion de débriefing a-t-elle été organisée"),
        'related_vsb_reunion_debriefing': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_reunion_debriefing': fields.boolean(u'Champs technique - Obligation'),

        'si_reunion_debriefing': fields.text("Si oui, quelles sont les premières conclusions"),
        'related_vsb_si_reunion_debriefing': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_si_reunion_debriefing': fields.boolean(u'Champs technique - Obligation'),


        'causes_profondes': fields.selection(OuiNon, "Une recherche des causes profondes est-elle prévue le cas échéant"),
        'related_vsb_causes_profondes': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_causes_profondes': fields.boolean(u'Champs technique - Obligation'),

        'si_causes_profondes': fields.text("Si oui, quelle est la méthodologie utilisée"),
        'related_vsb_si_causes_profondes': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_si_causes_profondes': fields.boolean(u'Champs technique - Obligation'),


        'enseignements_a_tirer': fields.selection(OuiNon, "Enseignements à tirer", help="Y a-t-il des enseignements à tirer au niveau de l’établissement, ou au niveau régional, de l’événement pour prévenir sa reproduction"),
        'related_vsb_enseignements_a_tirer': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_enseignements_a_tirer': fields.boolean(u'Champs technique - Obligation'),

        'si_enseignements_a_tirer': fields.text("Si oui, lesquels"),
        'related_vsb_si_enseignements_a_tirer': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_si_enseignements_a_tirer': fields.boolean(u'Champs technique - Obligation'),


        'mesure_organisation': fields.text('Organisationnelles', help=u"Permet d'indiquer les mesures prises au niveau du fonctionnement de l'établissement pour répondre à cet EIG"),
        'related_vsb_mesure_organisation': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_mesure_organisation': fields.boolean(u'Champs technique - Obligation'),
        





        'mesure_personnel': fields.text(u'Personnel établissement', help=u"Permet d'indiquer les mesures prises (accompagnement, dialogue interne, disciplinaires...) à l'égard d'un ou de plusieurs membres du personnel suite à la déclaration de cet EIG."),
        'related_vsb_mesure_personnel': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_mesure_personnel': fields.boolean(u'Champs technique - Obligation'),
        
        'mesure_usagers': fields.text('Autres usagers', help=u"Permet d'indiquer les mesures prises à l'égard des usagers non directement touchés par cet EIG"),
        'related_vsb_mesure_usagers': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_mesure_usagers': fields.boolean(u'Champs technique - Obligation'),
        
        'mesure_autres': fields.text('Autres', help=u"Permet d'indiquer les mesures prises à l'égard des autres personnes potentiellement impliquées (famille, professionnels extérieurs, structure partenaire...) suite à la déclaration de cet EIG."),
        'related_vsb_mesure_autres': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_mesure_autres': fields.boolean(u'Champs technique - Obligation'),
        
        'note': fields.text('Note'),
        'related_vsb_note': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_note': fields.boolean(u'Champs technique - Obligation'),
        
        'attachment_ids': fields.many2many('ir.attachment', 'is_eig_attachment_rel', 'eig_id', 'attachment_id', u'Pièces jointes', help=u"Permet d'ajouter, si besoin, tout élément complémentaire susceptible d'aider à la compréhension de l'EIG (chrono, rapport éducatif,...). Pour rappel : il est inutile de surcharger l'information."),
        'related_vsb_attachment_ids': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_attachment_ids': fields.boolean(u'Champs technique - Obligation'),
        
        'auteur_ids': fields.one2many('is.eig.auteur', 'is_eig_id', 'Auteur'),
        'related_vsb_auteur_ids': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_auteur_ids': fields.boolean(u'Champs technique - Obligation'),
        
        'temoin_ids': fields.one2many('is.eig.temoin', 'is_eig_id', u'Témoins'),
        'related_vsb_temoin_ids': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_temoin_ids': fields.boolean(u'Champs technique - Obligation'),
        
        'victim_ids': fields.one2many('is.eig.victime', 'is_eig_id', 'Victime'),
        'related_vsb_victim_ids': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_victim_ids': fields.boolean(u'Champs technique - Obligation'),
        



        'intervention_police': fields.selection(OuiNon, "Intervention de la police"),
        'related_vsb_intervention_police': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_intervention_police': fields.boolean(u'Champs technique - Obligation'),


        'depot_plainte': fields.selection(OuiNon, "Dépôt de plainte par la famille"),
        'related_vsb_depot_plainte': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_depot_plainte': fields.boolean(u'Champs technique - Obligation'),



        'infos_ids': fields.one2many('is.infos.communication', 'is_eig_id', 'Information communication'),
        'related_vsb_infos_ids': fields.boolean(u'Champs technique - Visibilité'),
        'related_rqr_infos_ids': fields.boolean(u'Champs technique - Obligation'),

        'motif_ids': fields.one2many('is.motif.retour.eig', 'eig_id1', 'Motif de retour', readonly=True),




                
        'related_aut_vsb_identifie': fields.boolean(u'Champs technique - Visibilité'),
        'related_aut_rqr_identifie': fields.boolean(u'Champs technique - Obligation'),
        'related_aut_vsb_name': fields.boolean(u'Champs technique - Visibilité'),
        'related_aut_rqr_name': fields.boolean(u'Champs technique - Obligation'),
        'related_aut_vsb_prenom': fields.boolean(u'Champs technique - Visibilité'),
        'related_aut_rqr_prenom': fields.boolean(u'Champs technique - Obligation'),
        'related_aut_vsb_birthdate': fields.boolean(u'Champs technique - Visibilité'),
        'related_aut_rqr_birthdate': fields.boolean(u'Champs technique - Obligation'),
        'related_aut_vsb_qualite_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_aut_rqr_qualite_id': fields.boolean(u'Champs technique - Obligation'),
        'related_aut_vsb_disposition_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_aut_rqr_disposition_id': fields.boolean(u'Champs technique - Obligation'),
        'related_aut_vsb_sexe_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_aut_rqr_sexe_id': fields.boolean(u'Champs technique - Obligation'),

        'related_aut_vsb_adresse': fields.boolean(u'Champs technique - Visibilité'),
        'related_aut_rqr_adresse': fields.boolean(u'Champs technique - Obligation'),

        'related_tem_vsb_identifie': fields.boolean(u'Champs technique - Visibilité'),
        'related_tem_rqr_identifie': fields.boolean(u'Champs technique - Obligation'),
        'related_tem_vsb_name': fields.boolean(u'Champs technique - Visibilité'),
        'related_tem_rqr_name': fields.boolean(u'Champs technique - Obligation'),
        'related_tem_vsb_prenom': fields.boolean(u'Champs technique - Visibilité'),
        'related_tem_rqr_prenom': fields.boolean(u'Champs technique - Obligation'),
        'related_tem_vsb_sexe_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_tem_rqr_sexe_id': fields.boolean(u'Champs technique - Obligation'),
        'related_tem_vsb_address': fields.boolean(u'Champs technique - Visibilité'),
        'related_tem_rqr_address': fields.boolean(u'Champs technique - Obligation'),
        'related_tem_vsb_birthdate': fields.boolean(u'Champs technique - Visibilité'),
        'related_tem_rqr_birthdate': fields.boolean(u'Champs technique - Obligation'),
        'related_tem_vsb_qualite_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_tem_rqr_qualite_id': fields.boolean(u'Champs technique - Obligation'),
        'related_tem_vsb_disposition_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_tem_rqr_disposition_id': fields.boolean(u'Champs technique - Obligation'),
        
        'related_vict_vsb_identifie': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_identifie': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_name': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_name': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_prenom': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_prenom': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_sexe_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_sexe_id': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_address': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_address': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_ecole': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_ecole': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_birthdate': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_birthdate': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_qualite_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_qualite_id': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_disposition_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_disposition_id': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_consequence_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_consequence_id': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_nom_pere': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_nom_pere': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_prenom_pere': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_prenom_pere': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_address_pere': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_address_pere': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_nom_mere': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_nom_mere': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_prenom_mere': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_prenom_mere': fields.boolean(u'Champs technique - Obligation'),
        'related_vict_vsb_address_mere': fields.boolean(u'Champs technique - Visibilité'),
        'related_vict_rqr_address_mere': fields.boolean(u'Champs technique - Obligation'),
        
        'related_inf_vsb_date': fields.boolean(u'Champs technique - Visibilité'),
        'related_inf_rqr_date': fields.boolean(u'Champs technique - Obligation'),
        'related_inf_vsb_user_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_inf_rqr_user_id': fields.boolean(u'Champs technique - Obligation'),
        'related_inf_vsb_responsible_id': fields.boolean(u'Champs technique - Visibilité'),
        'related_inf_rqr_responsible_id': fields.boolean(u'Champs technique - Obligation'),
        'related_inf_vsb_support': fields.boolean(u'Champs technique - Visibilité'),
        'related_inf_rqr_support': fields.boolean(u'Champs technique - Obligation'),
        'related_inf_vsb_info_cible': fields.boolean(u'Champs technique - Visibilité'),
        'related_inf_rqr_info_cible': fields.boolean(u'Champs technique - Obligation'),
        'related_inf_vsb_impact': fields.boolean(u'Champs technique - Visibilité'),
        'related_inf_rqr_impact': fields.boolean(u'Champs technique - Obligation'),


        'related_onglet_faits': fields.boolean(u'Champs technique - Onglet Faits'),
        'related_onglet_auteurs': fields.boolean(u'Champs technique - Onglet Auteurs'),
        'related_onglet_temoins': fields.boolean(u'Champs technique - Onglet Témoins'),
        'related_onglet_victimes': fields.boolean(u'Champs technique - Onglet Victimes'),
        'related_onglet_mesures': fields.boolean(u'Champs technique - Onglet Mesures'),
        'related_onglet_infos': fields.boolean(u'Champs technique - Onglet Infos'),
        'related_onglet_element_complementaire': fields.boolean(u'Champs technique - Onglet Eléments complémentaires'),

        'related_group_motif_retour': fields.boolean(u'Champs technique - Tableau motif retour'),

    }
    
    _defaults = {
        'name': '',
        'redacteur_id': lambda obj, cr, uid, context: uid,
        'state': 'draft',
    }




    
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
    
    def onchange_type_event(self, cr, uid, ids, type_event_id, context=None):
        vals = {}
        #On commencer par décocher toutes les cases à cocher techniques
        vals.update({

                    'related_onglet_faits':  False,
                    'related_onglet_auteurs':  False,
                    'related_onglet_temoins':  False,
                    'related_onglet_victimes':  False,
                    'related_onglet_mesures':  False,
                    'related_onglet_infos':  False,
                    'related_onglet_element_complementaire':  False,
                    'related_group_motif_retour':  False,

                    'related_vsb_nature_precision':  False,
                    'related_rqr_nature_precision':  False,
                    'related_vsb_start_date':  False,
                    'related_rqr_start_date':  False,
                    'related_vsb_end_date':  False,
                    'related_vsb_description_faits':  False,
                    'related_rqr_description_faits':  False,

                    'related_vsb_risque_reproductivite':  False,
                    'related_rqr_risque_reproductivite':  False,

                    'related_vsb_risque_extension':  False,
                    'related_rqr_risque_extension':  False,

                    'related_vsb_risque_contentieux':  False,
                    'related_rqr_risque_contentieux':  False,

                    'related_vsb_evenement_maitrise':  False,
                    'related_rqr_evenement_maitrise':  False,

                    'related_vsb_si_non_maitrise':  False,
                    'related_rqr_si_non_maitrise':  False,

                    'related_vsb_lieu_faits':  False,
                    'related_rqr_lieu_faits':  False,
                    'related_vsb_element_faits':  False,
                    'related_rqr_element_faits':  False,
                    'related_vsb_cause_faits':  False,
                    'related_rqr_cause_faits':  False,

                    'related_vsb_reunion_debriefing':  False,
                    'related_rqr_reunion_debriefing':  False,

                    'related_vsb_si_reunion_debriefing':  False,
                    'related_rqr_si_reunion_debriefing':  False,

                    'related_vsb_causes_profondes':  False,
                    'related_rqr_causes_profondes':  False,

                    'related_vsb_si_causes_profondes':  False,
                    'related_rqr_si_causes_profondes':  False,

                    'related_vsb_enseignements_a_tirer':  False,
                    'related_rqr_enseignements_a_tirer':  False,

                    'related_vsb_si_enseignements_a_tirer':  False,
                    'related_rqr_si_enseignements_a_tirer':  False,

                    'related_vsb_mesure_organisation':  False,
                    'related_rqr_mesure_organisation':  False,
                    'related_is_ref_fournisseur':  False,
                    'related_vsb_mesure_personnel':  False,
                    'related_rqr_mesure_personnel':  False,
                    'related_delai_fabrication':  False,
                    'related_vsb_mesure_usagers':  False,
                    'related_rqr_mesure_usagers': False,
                    'related_vsb_mesure_autres': False,
                    'related_rqr_mesure_autres': False,
                    'related_vsb_note': False,
                    'related_rqr_note': False,
                    'related_vsb_attachment_ids': False,
                    'related_rqr_attachment_ids': False,
                    #-------------------------- 'related_vsb_auteur_ids': False,
                    #-------------------------- 'related_rqr_auteur_ids': False,
                    #-------------------------- 'related_vsb_temoin_ids': False,
                    #-------------------------- 'related_rqr_temoin_ids': False,
                    #-------------------------- 'related_vsb_victim_ids': False,
                    #-------------------------- 'related_rqr_victim_ids': False,
                    #--------------------------- 'related_vsb_infos_ids': False,
                    #--------------------------- 'related_rqr_infos_ids': False,
                    

                    'related_vsb_intervention_police':  False,
                    'related_rqr_intervention_police':  False,

                    'related_vsb_depot_plainte':  False,
                    'related_rqr_depot_plainte':  False,


                    'related_aut_vsb_identifie': False,
                    'related_aut_rqr_identifie': False,
                    'related_aut_vsb_name': False,
                    'related_aut_rqr_name': False,
                    'related_aut_vsb_prenom': False,
                    'related_aut_rqr_prenom': False,
                    'related_aut_vsb_birthdate': False,
                    'related_aut_rqr_birthdate': False,
                    'related_aut_vsb_qualite_id': False,
                    'related_aut_rqr_qualite_id': False,
                    'related_aut_vsb_sexe_id': False,
                    'related_aut_rqr_sexe_id': False,
                    'related_aut_vsb_disposition_id': False,
                    'related_aut_rqr_disposition_id': False,
                    'related_aut_vsb_adresse': False,
                    'related_aut_rqr_adresse': False,

                    
                    'related_tem_vsb_identifie': False,
                    'related_tem_rqr_identifie': False,
                    'related_tem_vsb_name': False,
                    'related_tem_rqr_name': False,
                    'related_tem_vsb_prenom': False,
                    'related_tem_rqr_prenom': False,
                    'related_tem_vsb_sexe_id': False,
                    'related_tem_rqr_sexe_id': False,
                    'related_tem_vsb_address': False,
                    'related_tem_rqr_address': False,
                    'related_tem_vsb_birthdate': False,
                    'related_tem_rqr_birthdate': False,
                    'related_tem_vsb_qualite_id': False,
                    'related_tem_rqr_qualite_id': False,
                    'related_tem_vsb_disposition_id': False,
                    'related_tem_rqr_disposition_id': False,
                    
                    'related_vict_vsb_identifie': False,
                    'related_vict_rqr_identifie': False,
                    'related_vict_vsb_name': False,
                    'related_vict_rqr_name': False,
                    'related_vict_vsb_prenom': False,
                    'related_vict_rqr_prenom': False,
                    'related_vict_vsb_sexe_id': False,
                    'related_vict_rqr_sexe_id': False,
                    'related_vict_vsb_address': False,
                    'related_vict_rqr_address': False,
                    'related_vict_vsb_ecole': False,
                    'related_vict_rqr_ecole': False,
                    'related_vict_vsb_birthdate': False,
                    'related_vict_rqr_birthdate': False,
                    'related_vict_vsb_qualite_id': False,
                    'related_vict_rqr_qualite_id': False,
                    'related_vict_vsb_disposition_id': False,
                    'related_vict_rqr_disposition_id': False,
                    'related_vict_vsb_consequence_id': False,
                    'related_vict_rqr_consequence_id': False,
                    'related_vict_vsb_nom_pere': False,
                    'related_vict_rqr_nom_pere': False,
                    'related_vict_vsb_prenom_pere': False,
                    'related_vict_rqr_prenom_pere': False,
                    'related_vict_vsb_address_pere': False,
                    'related_vict_rqr_address_pere': False,
                    'related_vict_vsb_nom_mere': False,
                    'related_vict_rqr_nom_mere': False,
                    'related_vict_vsb_prenom_mere': False,
                    'related_vict_rqr_prenom_mere': False,
                    'related_vict_vsb_address_mere': False,
                    'related_vict_rqr_address_mere': False,
                    
                    'related_inf_vsb_date': False,
                    'related_inf_rqr_date': False,
                    'related_inf_vsb_user_id': False,
                    'related_inf_rqr_user_id': False,
                    'related_inf_vsb_responsible_id': False,
                    'related_inf_rqr_responsible_id': False,
                    'related_inf_vsb_support': False,
                    'related_inf_rqr_support': False,
                    'related_inf_vsb_info_cible': False,
                    'related_inf_rqr_info_cible': False,
                    'related_inf_vsb_impact': False,
                    'related_inf_rqr_impact': False,
        })
        if type_event_id:
            type_event_obj = self.pool.get('is.type.evenement')
            type_event =  type_event_obj.browse(cr, uid, type_event_id, context=context)

            vals.update({
                'related_onglet_faits': type_event.onglet_faits,
                'related_onglet_auteurs': type_event.onglet_auteurs,
                'related_onglet_temoins': type_event.onglet_temoins,
                'related_onglet_victimes': type_event.onglet_victimes,
                'related_onglet_mesures': type_event.onglet_mesures,
                'related_onglet_infos': type_event.onglet_infos,
                'related_onglet_element_complementaire': type_event.onglet_element_complementaire,
            })

            for item in type_event.fields_eig_id:
                if item.field_visible :
                    field = str('related_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_rqr_'+item.fields_id.name)
                        vals.update({field: True})
                        
            for item in type_event.fields_auteur_id:
                if item.field_visible :
                    field = str('related_aut_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_aut_rqr_'+item.fields_id.name)
                        vals.update({field: True})
                        
            for item in type_event.fields_temoin_id:
                if item.field_visible :
                    field = str('related_tem_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_tem_rqr_'+item.fields_id.name)
                        vals.update({field: True})
                        
            for item in type_event.fields_victim_id:
                if item.field_visible :
                    field = str('related_vict_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_vict_rqr_'+item.fields_id.name)
                        vals.update({field: True})
                        
            for item in type_event.fields_info_id:
                if item.field_visible :
                    field = str('related_inf_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_inf_rqr_'+item.fields_id.name)
                        vals.update({field: True})
        
        return {'value': vals}
        
    
    def create(self, cr, uid, vals, context=None):

        #if vals.get('name', '/') == '/':
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'eig.number') or ''

        if 'etablissement_id' in vals and vals['etablissement_id']:
            etablissement = self.pool.get('is.etablissement').browse(cr, uid, vals['etablissement_id'], context=context)
            #if etablissement.director_id.id != uid and etablissement.responsible_id.id != uid:
            #    raise osv.except_osv(_("Avertissement"), _(u"Vous n'êtes pas autorisé à créer un document, Seul le directeur ou le responsable de l'établissement peut créer un document!"))
                
            res = self.get_valideur_traiteurs(cr, uid, vals['etablissement_id'], context)
            vals.update({'valideur_id': res['valideur_id']})
            #if res['traiteur_ids']:
            #    vals.update({'traiteur_ids': [(6, 0, res['traiteur_ids'])]})
                        
        return super(is_eig, self).create(cr, uid, vals, context=context)
    

    def copy(self, cr, uid, id, default=None, context=None):
        if not context:
            context = {}
        default.update({
            'redacteur_id': uid,
            'date_validation': False,
        })
        return super(is_eig, self).copy(cr, uid, id, default=default, context=context)




    def action_rediger_eig(self, cr, uid, ids, context=None):
        template_id=self.getId(cr, uid, ids, 'email_template_redaction_vers_redige')
        if template_id:
            self.pool.get('email.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
        self.write(cr, uid, ids, {'state': 'redige'}, context=context)


    def action_non_declarable(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'state': 'non_declarable'}, context=context)
            vals = {
                'etablissement_id'   : obj.etablissement_id.id,
                'type_event_id'      : 15,
                'destinataire_id'    : 4,
                'nature_event_id'    : 46,
                'date_faits'         : obj.start_date,
                'mesure_amelioration': ' ',
                'mesure_immediat'    : ' ',
                'mesure_autre'       : ' ',
                'consequence_faits'  : ' ',
                'lieu_faits'         : ' ',
                'description_faits'  : ' ',

            }
            id = self.pool.get('is.ei').create(cr, uid, vals, context=context)
            return {
                'name': "Incident",
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'is.ei',
                'type': 'ir.actions.act_window',
                'res_id': id,
                'domain': '[]',
            }








    def key2val(self,key,liste):
        for l in liste:
            if key==l[0]:
                return l[1]

    def get_mail(self, doc, key):
        mail=False
        if key=="ars":
            mail = doc.etablissement_id.departement_id.mail_ars
        if key=="cd":
            mail = doc.etablissement_id.departement_id.mail_cg
        if not mail:
            val=self.key2val(key,AutoriteControle)
            raise osv.except_osv("", "Mail "+str(val)+" non trouvé pour le département de cet établissement !")
        return mail

    def action_valider_eig(self, cr, uid, ids, context=None):
        doc = self.browse(cr, uid, ids[0], context=context)
        if not doc.type_risq_id:
            raise osv.except_osv("", "Champ 'Type de risque' obligatoire !")

        autorite_controle=doc.etablissement_id.autorite_controle
        if not autorite_controle:
            raise osv.except_osv("", "Autorité de contôle non renseigné pour cet établissement !")

        mail_destination_ids=doc.type_event_id.mail_destination_ids
        if not mail_destination_ids:
            raise osv.except_osv("", "Destinataires des mails (ARS ou CD) non renseignés pour ce type d'évènement !")

        test=False
        mail=[]
        for lig in doc.type_event_id.mail_destination_ids:
            if lig.autorite_controle==autorite_controle:
                if not lig.mail_destination:
                    val=self.key2val(autorite_controle,AutoriteControle)
                    raise osv.except_osv("", "Mail de destination non renseigné pour ce type d'évènement et pour l'autorité de contrôle "+str(val)+" !")

                if lig.mail_destination=="ars" or lig.mail_destination=="ars_cd":
                    mail.append(self.get_mail(doc, "ars"))
                if lig.mail_destination=="cd" or lig.mail_destination=="ars_cd":
                    mail.append(self.get_mail(doc, "cd"))
                test=True
                break

        if not test:
            val=self.key2val(autorite_controle,AutoriteControle)
            raise osv.except_osv("", "Autorité de contrôle de l'établissement ("+str(val)+") non trouvée pour ce type d'évènement !")

        mail_ars_cd=",".join(mail)

        # Enregistrement de la date de validation car celle-ci est utilisée dans le modèle
        vals={
            'date_validation': fields.datetime.now(),
        }
        self.write(cr, SUPERUSER_ID, ids, vals, context=context)

        # Generation du PDF
        self.generation_pdf(cr, uid, ids)

        # Mail au traiteur
        template_id=self.getId(cr, uid, ids, 'email_template_redige_vers_valide_traiteur')
        if template_id:
            self.pool.get('email.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)

        # Mais ARS avec pièce jointe
        template_id=self.getId(cr, uid, ids, 'email_template_redige_vers_valide_ars')
        if template_id:
            obj = self.pool.get('ir.attachment')

            # Recherche des fichiers PDF attachés à l'EIG
            attachment_ids = obj.search(cr, uid, [('res_model', '=', 'is.eig'),('res_id', '=', ids[0]),('name','like','%pdf'),('name','not ilike','%signalement%')], context=context)

            #print "Pieces jointes à envoyer par mail", attachment_ids
            email_obj = self.pool.get('email.template')
            email = email_obj.browse(cr, uid, template_id)

            #Enregistrement des destinataires du mail
            email_obj.write(cr, uid, template_id, {'email_to': mail_ars_cd})

            # Ajout des pieces jointes de l'onglet 'Elements complémentaire'
            if doc.attachment_ids:
                for x in doc.attachment_ids:
                    attachment_ids.append(x.id)

            #Ajout des pièces jointes au modèle
            email_obj.write(cr, uid, template_id, {'attachment_ids': [(6, 0, attachment_ids)]})


            # Envoi du mail (avec les pièces jointes)
            email_obj.send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
            # Suppression des pièces jointes du modèle
            email_obj.write(cr, uid, template_id, {'attachment_ids': [(6, 0, [])]})

        vals={
            'state': 'valide',
        }
        self.write(cr, SUPERUSER_ID, ids, vals, context=context)





    def action_completer_vers_valider_eig(self, cr, uid, ids, context=None):
        template_id=self.getId(cr, uid, ids, 'email_template_a_completer_vers_valide')
        if template_id:
            self.pool.get('email.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
        vals={
            'state': 'valide',
            'date_validation': fields.datetime.now(),
        }
        self.write(cr, uid, ids, vals, context=context)




    #def action_completer_eig(self, cr, uid, ids, context=None):
    #    self.write(cr, uid, ids, {'state': 'complet'}, context=context)
    #    template_id=self.getId(cr, uid, ids, 'email_template_valide_vers_a_completer')
    #    if template_id:
    #        self.pool.get('email.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)

    def action_terminer_eig(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)


    def getId(self, cr, uid, ids, external_id, context=None):
        obj = self.pool.get('ir.model.data')
        ids = obj.search(cr, uid, [('module', '=', 'is_eig'),('name', '=', external_id)], context=context)
        id=False;
        if ids:
            for l in obj.read(cr, uid, ids, ['res_id','name'], context=context):
                print str(l)
                id=l["res_id"]
        return id


    def get_signup_url(self, cr, uid, ids, context=None):
        url="https://eig.fondation-ove.fr/web#id="+str(ids[0])+"&view_type=form&model=is.eig"
        return url

#        assert len(ids) == 1
#        document = self.browse(cr, uid, ids[0], context=context)
#        contex_signup = dict(context, signup_valid=True)
#        return self.pool['res.partner']._get_signup_url_for_action(
#            cr, uid, [document.valideur_id.partner_id.id], action='mail.action_mail_redirect',
#            model=self._name, res_id=document.id, context=contex_signup,
#        )[document.valideur_id.partner_id.id]


    def get_traiteurs(self, cr, uid, ids, context=None):
        obj = self.pool.get('ir.model.data')
        data_ids = obj.search(cr, uid, [('module', '=', 'is_eig'),('name', '=', 'group_is_traiteur')], context=context)
        mail=""
        id=0
        if ids:
            for o in obj.read(cr, uid, data_ids, ['res_id','name'], context=context):
                id=o["res_id"]
        if id:
            ctx=self.pool.get('res.groups')
            for g in ctx.browse(cr, uid, id, context=context):
                l=[]
                for u in g.users:
                    l.append(u.email)
                mail=",".join(l)

        #mail="tony.galmiche.div@free.fr"
        return mail




    # ** Convertir une date/heure string utc en date/heure string localisée ****
    def h(self, date):
        if date==False:
            return ""
        # Timezone en UTC
        utc = pytz.utc
        # DateTime à partir d'une string avec ajout de la timezone
        utc_dt  = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=utc)
        # Timezone Europe/Paris
        europe = timezone('Europe/Paris')
        # Convertion de la datetime utc en datetime localisée
        loc_dt = utc_dt.astimezone(europe)
        # Retour de la datetime localisée en string
        return loc_dt.strftime('%d/%m/%Y %H:%M')


    # ** Convertir une date string utc en date string localisée ****************
    def d(self, date):
        if date==False:
            return ""
        # Timezone en UTC
        utc = pytz.utc
        # DateTime à partir d'une string avec ajout de la timezone
        utc_dt  = datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=utc)
        # Timezone Europe/Paris
        europe = timezone('Europe/Paris')
        # Convertion de la datetime utc en datetime localisée
        loc_dt = utc_dt.astimezone(europe)
        # Retour de la datetime localisée en string
        return loc_dt.strftime('%d/%m/%Y')


    def t(self, txt):
        if txt==False:
            return ""
        return txt




    def checkbox(self, val):
        html="Bonjour le monde : " + "<p>Ligne 1" + str(val) + "</p>" + "<p>Ligne 2" + str(val) + "</p>"
        html='<table><tr><td>toto</td><td>tutu</td><td><INPUT type="checkbox" />glace vanille</td></tr></table>'
        return html


    def f1(self, val):
        val=str(val)
        if (val=="1" or val=="t" or val=="True" or val=="true"):
            r="☑"
        else:
            r="□"
        return r

    def f2(self,val):
        if (self.nature_event_id.id == val):
            r="☑"
        else:
            r="□"
        return r


    def f3(self,val):
        r=0
        for lig in self.infos_ids:
            if lig.user_id.id == val:
                r=1
        return r


    def f4(self,val):
        for lig in self.infos_ids:
            if(lig.user_id.id == val):
                #print "=> date=",lig.date
                return str(lig.date)
        return False


    def f5(self,val):
        for lig in self.infos_ids:
            if(lig.user_id.id == val):
                return lig.support or ''
        return ""


    def generation_odt(self, cr, uid, ids, context=None):
        #obj = self.browse(cr, uid, ids[0], context=context)
        #obj.f4(3)
        self.generation_document(cr, uid, ids, context, "ODT")
        return True


    def generation_pdf(self, cr, uid, ids, context=None):
        self.generation_document(cr, uid, ids, context, "PDF")
        return True


    def generation_document(self, cr, uid, ids, context=None, type="ODT"):
        v = {}
        for rec in self.browse(cr, uid, ids, context=context):
            v["o"] = rec
            id = rec.id
            # ** Signalement aux autorités judiciaires *************************
            if rec.signalement_autorites:
                print "Signalement aux autorités judiciaires"
                obj = self.pool.get('res.company')
                company_ids = obj.search(cr, uid, [('id', '=', 1)], context=context)
                if company_ids:
                    company = obj.browse(cr, uid, company_ids[0], context=context)
                    print company.name
                    obj = self.pool.get('ir.attachment')
                    attachment_ids = obj.search(cr, uid, [('res_model', '=', 'res.company'),('res_id', '=', company_ids[0])], context=context)
                    if attachment_ids:
                        for l in obj.read(cr, uid, attachment_ids, ['name','datas'], context=context):
                            self.generation_document_par_nom(cr, uid, id, context, type, v, l["datas"], l["name"])
            # ** Recherche des modeles associés au département *****************
            etablissement_id = rec.etablissement_id.id
            departement_id = rec.etablissement_id.departement_id.id
            obj = self.pool.get('ir.attachment')
            attachment_ids = obj.search(cr, uid, [('res_model', '=', 'is.departement'),('res_id', '=', departement_id)], context=context)
            if attachment_ids:
                for l in obj.read(cr, uid, attachment_ids, ['name','datas'], context=context):
                    self.generation_document_par_nom(cr, uid, id, context, type, v, l["datas"], l["name"])
            # ******************************************************************
        return True


    def generation_document_par_nom(self, cr, uid, id, context=None, type="ODT", v=[], contenu="", nom=""):
        alea=str(uuid.uuid4())
        appy_model    = "/tmp/appy_model_"+alea+".odt"
        appy_dest     = "/tmp/appy_dest_"+alea+".odt"
        appy_dest_pdf = "/tmp/appy_dest_"+alea+".pdf"
        f = open(appy_model,'wb')
        #f.write(l["datas"].decode('base64'))
        f.write(contenu.decode('base64'))
        f.close()

        # ** Génération du fichier avec Appy ***********************
        renderer = Renderer(appy_model, v, appy_dest)
        renderer.run()
        # **********************************************************

        # ** Transformation en PDF *********************************
        if type=="PDF":
            cde="soffice --headless   --convert-to pdf:writer_pdf_Export "+appy_dest+" --outdir /tmp"
            os.system(cde)
        #***********************************************************

        # ** Recherche si une pièce jointe est déja associèe *******
        name=nom[:-4]
        if type=="PDF":
            name=name+".pdf"
        else:
            name=name+".odt"
        obj = self.pool.get('ir.attachment')
        model=str(self)
        ids = obj.search(cr, uid, [('res_model','=',model),('res_id','=',id),('name','=',name)], context=context)
        # **********************************************************

        # ** Creation ou modification de la pièce jointe ***********
        #r = open(appy_dest,'rb').read().encode('base64')
        dest=appy_dest
        if type=="PDF":
            dest=appy_dest_pdf
        r = open(dest,'rb').read().encode('base64')

        vals = {
            'name':        name,
            'datas_fname': name,
            'type':        'binary',
            'res_model':   model,
            'res_id':      id,
            'datas':       r,
        }
        if ids:
            obj.write(cr, SUPERUSER_ID, ids[0], vals, context=context)
            print "Modification ir.attachment id="+str(ids[0])
        else:
            id = obj.create(cr, SUPERUSER_ID, vals, context=context)
            print "Création ir.attachment id="+str(id)
        os.system("rm -f "+appy_model)
        os.system("rm -f "+appy_dest)
        os.system("rm -f "+appy_dest_pdf)
        #***********************************************************************



