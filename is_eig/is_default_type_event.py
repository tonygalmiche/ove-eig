# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

class is_default_type_event(osv.osv):
    _name = 'is_default_type_event'
    
    
    def get_eig_fields(self, cr, uid, context=None):
        field_obj = self.pool.get('ir.model.fields')
        field_ids = field_obj.search(cr, uid, [('model', '=', 'is.eig'), ('name','in', ('start_date',
                                                                                        'end_date',
                                                                                        'nature_precision'
                                                                                        'description_faits',
                                                                                        'lieu_faits',
                                                                                        'element_faits',
                                                                                        'cause_faits',
                                                                                        'mesure_organisation',
                                                                                        'mesure_personnel',
                                                                                        'mesure_usagers',
                                                                                        'mesure_autres',
                                                                                        'note',
                                                                                        'attachment_ids'
                                                                                        # ,'auteur_ids'
                                                                                        # ,'temoin_ids'
                                                                                        # ,'victim_ids'
                                                                                        # ,'infos_ids'
                                                                                        ))], context=context)
        return field_ids
    
    def get_auteur_fields(self, cr, uid, context=None):
        field_obj = self.pool.get('ir.model.fields')
        field_ids = field_obj.search(cr, uid, [('model', '=', 'is.eig.auteur'), ('name','in', ('identifie',
                                                                                               'name',
                                                                                               'adresse',
                                                                                               'prenom',
                                                                                               'birthdate',
                                                                                               'qualite_id',
                                                                                               'sexe_id',
                                                                                               'disposition_id'))], context=context)
        return field_ids
        
    
    def get_victim_fields(self, cr, uid, context=None):
        field_obj = self.pool.get('ir.model.fields')
        field_ids = field_obj.search(cr, uid, [('model', '=', 'is.eig.victime'), ('name','in', ('identifie',
                                                                                                'name',
                                                                                                'prenom',
                                                                                                'address',
                                                                                                'ecole',
                                                                                                'birthdate',
                                                                                                'sexe_id',
                                                                                                'qualite_id',
                                                                                                'disposition_id',
                                                                                                'consequence_id',
                                                                                                'nom_pere',
                                                                                                'prenom_pere',
                                                                                                'address_pere',
                                                                                                'nom_mere',
                                                                                                'prenom_mere',
                                                                                                'address_mere'))], context=context)
        return field_ids
    
    
    def get_temoin_fields(self, cr, uid, context=None):
        field_obj = self.pool.get('ir.model.fields')
        field_ids = field_obj.search(cr, uid, [('model', '=', 'is.eig.temoin'), ('name','in', ('identifie',
                                                                                               'name',
                                                                                               'prenom',
                                                                                               'sexe_id',
                                                                                               'address',
                                                                                               'birthdate',
                                                                                               'qualite_id',
                                                                                               'disposition_id'))], context=context)
        return field_ids
    
    def get_infos_fields(self, cr, uid, context=None):
        field_obj = self.pool.get('ir.model.fields')
        field_ids = field_obj.search(cr, uid, [('model', '=', 'is.infos.communication'), ('name','in', ('date',
                                                                                                        'user_id',
                                                                                                        'responsible_id',
                                                                                                        'support',
                                                                                                        'info_cible',
                                                                                                        'impact'))], context=context)
        return field_ids
    
    def get_fields_eig_properties(self, cr, uid, visible=False, context=None):
        field_ids = self.get_eig_fields(cr, uid, context)
        lst = []
        for field_id in field_ids:
            lst.append({'fields_id': field_id, 'field_visible': visible, 'field_required': False, 'is_eig': True})
        return lst
    
    def get_fields_auteur_properties(self, cr, uid, visible=False, context=None):
        field_ids = self.get_auteur_fields(cr, uid, context)
        lst = []
        for field_id in field_ids:
            lst.append({'fields_id': field_id, 'field_visible': visible, 'field_required': False, 'is_eig_auteur': True})
        return lst
    
    def get_fields_victim_properties(self, cr, uid, visible=False, context=None):
        field_ids = self.get_victim_fields(cr, uid, context)
        lst = []
        for field_id in field_ids:
            lst.append({'fields_id': field_id, 'field_visible': visible, 'field_required': False, 'is_eig_victim': True})
        return lst
    
    def get_fields_temoin_properties(self, cr, uid, visible=False, context=None):
        field_ids = self.get_temoin_fields(cr, uid, context)
        lst = []
        for field_id in field_ids:
            lst.append({'fields_id': field_id, 'field_visible': visible, 'field_required': False, 'is_eig_temoin': True})
        return lst
    
    def get_fields_infos_properties(self, cr, uid, visible=False, context=None):
        field_ids = self.get_infos_fields(cr, uid, context)
        lst = []
        for field_id in field_ids:
            lst.append({'fields_id': field_id, 'field_visible': visible, 'field_required': False, 'is_eig_infos': True})
        return lst
    
    def manip_type_evenement1(self, cr, uid, context=None):
        field_obj = self.pool.get('ir.model.fields')
        eig_lst = []
        fields_eig_ids = self.get_eig_fields(cr, uid, context)
        for field in field_obj.browse(cr, uid, fields_eig_ids, context=context):
            if field.name == 'nature_precision':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'start_date':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'end_date':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': False, 'is_eig': True}])
            if field.name == 'description_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'lieu_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'element_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'cause_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'mesure_organisation':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'mesure_personnel':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'mesure_usagers':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'mesure_autres':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'note':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'attachment_ids':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
        
        
        victim_lst = []
        default_victim_lst = self.get_fields_victim_properties(cr, uid, False, context)
        for item in default_victim_lst:
            item.update({'field_visible': True})
            victim_lst.append([0,False, item])
            
        auteur_lst = []
        default_auteur_lst = self.get_fields_auteur_properties(cr, uid, False, context)
        for item in default_auteur_lst:
            auteur_lst.append([0,False, item])
        
        temoin_lst = []   
        default_temoin_lst = self.get_fields_temoin_properties(cr, uid, False, context)
        for item in default_temoin_lst:
            temoin_lst.append([0,False, item])
        
        infos_lst = []    
        default_infos_lst = self.get_fields_infos_properties(cr, uid, False, context)
        for item in default_infos_lst:
            infos_lst.append([0,False, item])
        
        return {'eig': eig_lst, 'auteur': auteur_lst, 'temoin': temoin_lst, 'victim': victim_lst, 'infos': infos_lst}
    
    def manip_type_evenement2(self, cr, uid, context=None):
        field_obj = self.pool.get('ir.model.fields')
        eig_lst = []
        fields_eig_ids = self.get_eig_fields(cr, uid, context)
        for field in field_obj.browse(cr, uid, fields_eig_ids, context=context):
            if field.name == 'nature_precision':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'start_date':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'end_date':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'description_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'lieu_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'element_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'cause_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'mesure_organisation':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'mesure_personnel':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'mesure_usagers':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'mesure_autres':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'note':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'attachment_ids':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
        
        victim_lst = []
        default_victim_lst = self.get_fields_victim_properties(cr, uid, False, context)
        for item in default_victim_lst:
            item.update({'field_visible': True})
            victim_lst.append([0,False, item])
            
            
        auteur_lst = []
        default_auteur_lst = self.get_fields_auteur_properties(cr, uid, False, context)
        for item in default_auteur_lst:
            auteur_lst.append([0,False, item])
        
        temoin_lst = []   
        default_temoin_lst = self.get_fields_temoin_properties(cr, uid, False, context)
        for item in default_temoin_lst:
            temoin_lst.append([0,False, item])
        
        infos_lst = []    
        default_infos_lst = self.get_fields_infos_properties(cr, uid, False, context)
        for item in default_infos_lst:
            infos_lst.append([0,False, item])
        
        return {'eig': eig_lst, 'auteur': auteur_lst, 'temoin': temoin_lst, 'victim': victim_lst, 'infos': infos_lst}

    
    def manip_type_evenement3(self, cr, uid, context=None):
        field_obj = self.pool.get('ir.model.fields')
        eig_lst = []
        fields_eig_ids = self.get_eig_fields(cr, uid, context)
        for field in field_obj.browse(cr, uid, fields_eig_ids, context=context):
            if field.name == 'nature_precision':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'start_date':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'end_date':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': False, 'is_eig': True}])
            if field.name == 'description_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'lieu_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'element_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'cause_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'mesure_organisation':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'mesure_personnel':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'mesure_usagers':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'mesure_autres':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'note':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'attachment_ids':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
        
        
        victim_lst = []
        default_victim_lst = self.get_fields_victim_properties(cr, uid, False, context)
        for item in default_victim_lst:
            item.update({'field_visible': True})
            victim_lst.append([0,False, item])
        
        auteur_lst = []
        default_auteur_lst = self.get_fields_auteur_properties(cr, uid, False, context)
        for item in default_auteur_lst:
            item.update({'field_visible': True, 'field_required': True})
            auteur_lst.append([0,False, item])
        
        temoin_lst = []   
        fields_temoin_ids = self.get_temoin_fields(cr, uid, context)
        for field in field_obj.browse(cr, uid, fields_temoin_ids, context=context):
            if field.name == 'identifie':
                temoin_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_temoin': True}])
            if field.name == 'name':
                temoin_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_temoin': True}])
            if field.name == 'prenom':
                temoin_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_temoin': True}])
            if field.name == 'address':
                temoin_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_temoin': True}])
            if field.name == 'birthdate':
                temoin_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_temoin': True}])
            if field.name == 'qualite_id':
                temoin_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_temoin': True}])

            if field.name == 'disposition_id':
                temoin_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_temoin': True}])

            if field.name == 'sexe_id':
                temoin_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_temoin': True}])




        infos_lst = []    
        default_infos_lst = self.get_fields_infos_properties(cr, uid, False, context)
        for item in default_infos_lst:
            item.update({'field_visible': True, 'field_required': True})
            infos_lst.append([0,False, item])
        
        return {'eig': eig_lst, 'auteur': auteur_lst, 'temoin': temoin_lst, 'victim': victim_lst, 'infos': infos_lst}
    
    def update_vals_create(self, cr, uid, code, context=None):
        vals = {}
        if code == 'E1':
            properties = self.manip_type_evenement1(cr, uid, context)
            vals.update({'fields_eig_id': properties['eig'],
                         'fields_auteur_id': properties['auteur'],
                         'fields_victim_id': properties['victim'],
                         'fields_temoin_id': properties['temoin'],
                         'fields_info_id': properties['infos']
                        })
            return vals
        
        if code == 'E2':
            properties = self.manip_type_evenement2(cr, uid, context)
            vals.update({'fields_eig_id': properties['eig'],
                         'fields_auteur_id': properties['auteur'],
                         'fields_victim_id': properties['victim'],
                         'fields_temoin_id': properties['temoin'],
                         'fields_info_id': properties['infos']
                        })
            return vals
        
        if code in ('E3','E4','E5'):
            properties = self.manip_type_evenement3(cr, uid, context)
            vals.update({'fields_eig_id': properties['eig'],
                         'fields_auteur_id': properties['auteur'],
                         'fields_victim_id': properties['victim'],
                         'fields_temoin_id': properties['temoin'],
                         'fields_info_id': properties['infos']
                        })
            return vals
