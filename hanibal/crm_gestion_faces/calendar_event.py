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

class calendar_event(osv.Model):
    """ Model for Calendar Event """
    
    _name = 'calendar.event'
    _inherit = 'calendar.event'
    
    _columns = {
        'primera_visita':fields.boolean('Es primera visita?'),
        'otras_visitas':fields.selection( (('S','Seguimiento'),),'Tipo de reunion' ),
        'lead_id':fields.many2one('crm.lead','Oportunidad',help="Este campo indica cual es la oportunidad de donde se generan las reuniones"),
    }
    