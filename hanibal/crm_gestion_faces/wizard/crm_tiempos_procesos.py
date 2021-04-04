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
from openerp import tools
from openerp.osv import fields, osv

class crm_tiempos_procesos_conf(osv.osv):
    _name = "crm.tiempos.procesos.conf"
    _description = "Tiempos de Procesos"
   # _auto = False
   # _rec_name = 'name'

    _columns = {
        'name':fields.char('Name'),
        'd_identificar': fields.float('Identificar'),
        'd_preparar': fields.float('Preparar'),
        'd_primera_visita': fields.float('Primera Visita'),
        'd_seguimiento': fields.float('Seguimiento'),
        'd_pruebas': fields.float('Pruebas'),
        'd_oferta': fields.float('Oferta'),
        'd_negociacion': fields.float('Negociacion'),


    }
   # _order = 'd_identificar'

    _defaults = {  
        'name':'Tiempos',
        'd_identificar': 0,  
        'd_preparar': 0,  
        'd_primera_visita': 0,  
        'd_segimiento': 0,  
        'd_pruebas': 0,  
        'd_oferta': 0,  
        'd_negociacion': 0,  
        }
        
crm_tiempos_procesos_conf()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
