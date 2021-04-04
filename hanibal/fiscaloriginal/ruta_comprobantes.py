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

class ruta_comprobantes(osv.osv):
    _name = 'ruta.comprobantes'
    
    _columns = {
        'name':fields.char('Descripcion',required=True),
        'active': fields.boolean('Habilitado'),
        'tipo':fields.selection(
                                (('f','Facturas'),
                                 ('g','Guias de remisión'),
                                 ('nc','Notas de credito'),
                                 ('nd','Notas de debito'),
                                 ('r','Retención'),
                                 ('li','Liquidacion de Compras'),
                                 ),'Tipo',required=True),
        #=======================================================================
        # ACTUALIZADO 13-06-2017
        #=======================================================================
        ################# 'comp_id':fields.many2one('res.company','Compañia',required=True),
        'comp_id':fields.many2one('compania.sis','Compañia',required=True),
        #=======================================================================
        # ACTUALIZADO 13-06-2017
        #=======================================================================
        'folios_id':fields.many2one('folios.configuracion','Ruta comprobantes',ondelete='cascade')
    }

    _defaults = {
        'active':True    
    }

ruta_comprobantes()
