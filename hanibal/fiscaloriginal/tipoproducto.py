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

class fiscal_tipoproducto(osv.osv):
    _name = 'fiscal.tipoproducto'
    _description = 'Tipos de Producto'
 
    _columns = {
        'codigofiscal':fields.char('Codigo Fiscal', 10, required=True),
        'name':fields.char('Nombre', 100, required=True),
	    'habilitado':fields.boolean('Habilitado', requiered=True),
        'reglaretencion_id':fields.one2many('fiscal.reglaretencion','tipoproducto_id'),  
        #Folios

        'folios_id':fields.many2one('folios.configuracion','Tipos de Productos',ondelete='cascade')
        
        }

    _defaults = {
        'habilitado':True    
    }
   
fiscal_tipoproducto()