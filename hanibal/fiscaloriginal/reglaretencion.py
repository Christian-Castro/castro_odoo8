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

from openerp.osv import fields, osv

class fiscal_reglaretencion(osv.osv):
    _name = 'fiscal.reglaretencion'
    
    _columns = {
        'name':fields.char('Descripcion',15),
        'habilitado': fields.boolean('Habilitado'),
        'posicionfiscal_id': fields.many2one('account.fiscal.position','Posicion Fiscal'),
        'tipoproducto_id':fields.many2one('fiscal.tipoproducto','Tipo de Producto'),
        'tax_id':fields.many2one('account.tax','Retenciones')
	}

    _defaults = {
        'habilitado':True    
    }

fiscal_reglaretencion()