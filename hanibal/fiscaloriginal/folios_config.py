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

from openerp.osv import osv,fields

class folios_configuracion(osv.osv):
    _name = 'folios.configuracion'
    _description="Folios Configuracion"
    
    _columns = {
   
            'company_id': fields.many2one('res.company', 'Compañia'),
            'sus_tributario':fields.one2many('fiscal.sustentotributario','folios_id','Sustento Tributario'),
            'tipo_documento':fields.one2many('fiscal.tipodocumento','folios_id','Tipo Documento'),
            'tipo_producto':fields.one2many('fiscal.tipoproducto','folios_id','Tipo de Productos'),
            'tipo_identificacion':fields.one2many('fiscal.tipoidentificacion','folios_id','Tipo de Identificacion'),
            'tipo_pago':fields.one2many('fiscal.tipopago','folios_id','Tipo de Pago'),
            'forma_pago':fields.one2many('fiscal.formapago','folios_id','Forma de Pago'),
            'name':fields.char('Descripcion'),
            'ruta_comp':fields.one2many('ruta.comprobantes','folios_id','Ruta comprobantes'),
            
        }
    
    _defaults={
        'name':'Folios Configuracion'
               }
        
folios_configuracion()