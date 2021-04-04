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
#25-02-2018
from openerp.tools.translate import _
#25-02-2018
class sale_order(osv.osv):
    
    _name="sale.order"
    _inherit = "sale.order"
    
    _columns = {
        
        'venta_id': fields.many2one('crm.lead', 'Oportunidad', ondelete='cascade', select=True),
	'tipo':fields.selection(  (('ini','Inicial'),('fin','Final'),('uni','Unica')),'Tipo' ),
	
    }

   

   
#25-02-2018
