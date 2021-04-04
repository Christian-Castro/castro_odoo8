# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
@attention: Objeto que guardara todo lo que suceda en diferentes objetos
"""

from openerp.osv import fields, osv 

class log_crm_gestion(osv.osv):
    
    _name = 'log.crm.gestion'
    
    _columns = {
        'registro_id':fields.integer('Clave'),    # id de la iniciativa 
        'usuario_crea':fields.integer('Usuario'), # usuario que crea la iniciativa
	'estado':fields.char('Estado'),#esstado de la bitacora
        
        'fecha_prospecto':fields.datetime('Fecha Prospecto'), # creacion del prospecto
        'fecha_iniciativa':fields.datetime('Fecha de iniciativa'), # fecha de creacion de iniciativa 
        'identificar':fields.char('Identificar'),# resultado de la diferencia
	'dias_identificar':fields.float('Dias de identificar'),
        
        'fecha_contacto':fields.datetime('Fecha de creacion de Contacto para preparar'), # fecha de creacion de fecha de contacto?
        'preparar':fields.char('Preparar'),# porque es char?  no es la diferencia de fechas... deveria ser datetime
	'dias_preparar':fields.float('Dias de Preparar'),
        
        'fecha_reunion':fields.datetime('Fecha de la Reunion de primera visita'),# de cual de todas? de pruebas, primera visita? 
        'fecha_contacto_pv':fields.datetime('Fecha de creacion Contacto menor o igual a la reunion'),# que es?
        'p_visita':fields.char('Primera Visita'), # fecha de primera visita ... verdad?
	'dias_primera_visita':fields.float('Dias de primera visita'),
        
        'fecha_pllamada':fields.datetime('Fecha Primera Llamada de seguimiento'),  # que es ?
        'fecha_preunion':fields.datetime('Fecha Primera Reunion de seguimiento'), # fecha de primera reunion.
        'seguimiento':fields.char('Seguimiento'), # las reuniones de seguimiento no participan o como lo visualizas?
	'dias_seguimiento':fields.float('Dias de seguimiento'),

	'fecha_reu_marc_prueba':fields.datetime('Fecha de reunion marcada como prueba'),
	'fecha_llamada_seg_sa':fields.datetime('Fecha de ultima llamada de seguimiento saliente'),
	'pruebas':fields.char('Diferencia de pruebas'),
	'dias_pruebas':fields.float('Dias de pruebas'),

	'fecha_oferta_final':fields.datetime('Fecha de oferta final'),
	'fecha_reunion_pruebas':fields.datetime('fecha de ultima reunion de pruebas antes de reunion'),
	'oferta':fields.char('Oferta'),
	'dias_oferta':fields.float('Dias de oferta'),

	'fecha_gan_perd':fields.datetime('Fecha ganada o perdidad de la oportunidad'),
	'negociacion':fields.char('Negociacion'),
	'dias_negociacion':fields.float('Dias de negociacion'),
					
    }
         
    
log_crm_gestion() 
