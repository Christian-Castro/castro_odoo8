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

class log_reporte(osv.osv):
    _name = "log.crm.analisis.precios"
    _description = "Analisis de Precios"
    _auto = False
    _rec_name = 'fecha'

    _columns = {
        'id': fields.char('id', readonly=True),
        'comercial': fields.char('Comercial', readonly=True),
        'prospecto': fields.char('prospecto', readonly=True),
        'fecha':  fields.date('Fecha de prospecto', readonly=True), 
        'tipo': fields.char('Tipo', readonly=True),
        'producto_cod': fields.char('Codigo', readonly=True),
        'producto_des': fields.char('Descripcion', readonly=True),
        'precio_unitario': fields.float('Precio', readonly=True,group_operator="sum"),
        'titulo':fields.char('Titulo', readonly=True),
        
    }
    _order = 'fecha desc'

    