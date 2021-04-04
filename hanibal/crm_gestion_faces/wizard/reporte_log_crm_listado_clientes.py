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
    _name = "crm.listado.clientes"
    _description = "Listado de Clientes"
    _auto = False
    _rec_name = 'cliente'

    _columns = {
        'id': fields.float('Id', readonly=True),
        'cliente': fields.char('Cliente', readonly=True),
        'comercial': fields.char('Comercial', readonly=True),
        'ciudad': fields.char('Direccion', readonly=True),
        'direccion': fields.char('Direccion', readonly=True),
        'ruc': fields.char('Ruc', readonly=True),
        'telefono': fields.char('Telefono', readonly=True),
        'celular': fields.char('Mobil', readonly=True),
        'correo': fields.char('Correo', readonly=True),

    }
    _order = 'cliente'

    
    def _tabla(self):
        group_by_strxx1 = """
                select  
                        cli.id id,
                        cli.name cliente,
                        ven.name comercial,
                        cli.city  ciudad,
                        cli.street direccion,
                        cli.vat  ruc,
                        cli.phone telefono,
                        cli.mobile celular,
                        cli.email  correo
                from     res_partner  cli  
	                left join    res_users as usr on (cli.user_id = usr.id )
	                left join    res_partner as ven on ( usr.partner_id = ven.id)
                   where  usr.partner_id = ven.id and 
                           cli.is_company = 't'
                   order by 1,2,3
         """
        return group_by_strxx1

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            )""" % (self._table, self._tabla()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
