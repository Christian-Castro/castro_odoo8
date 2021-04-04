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
from openerp import api
import datetime


class res_partner(osv.osv):
    
    _inherit = 'res.partner'
    
    _columns = {
        'prospectos':fields.boolean('Prospectos', required=False, help='Para declarar prospectos en el proceso de ventas'), 
        'actividad_economica':fields.char('Actividad', required=False, help='Actividad Economica'),
        'monto_mensual':fields.float('Monto Mensual Compra', required=False, help='Monto Mensual Compra'),
        'monto_anual':fields.float('Monto Anual Venta', required=False, help='Monto Anual Venta'),
        'ciudad_id': fields.many2one('ciudades', 'Ciudad', ondelete='cascade', select=True),
                    }
    
res_partner()
