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
    _name = "log.crm.prospecto.procesos.cantidad"
    _description = "Numero de Prospectos por Proceso"
    _auto = False
    _rec_name = 'fecha_iniciativa'

    _columns = {
        #'id': fields.float('N idd', readonly=True),
        'estado': fields.char('Estado', readonly=True),
        'tipo': fields.char('Iniciativa / Prospecto', readonly=True),
        'iniciativa': fields.float('N Iniciativa', readonly=True),
        'comercial': fields.char('Comercial', readonly=True),
        'ciudad': fields.char('Ciudad', readonly=True),
        'prospecto': fields.char('Prospecto', readonly=True),
        'fecha_iniciativa': fields.datetime('Fecha iniciativa', readonly=True),
        'periodo_iniciativa': fields.char('Periodo', readonly=True),   
        'titulo': fields.char('Titulo', readonly=True)
    }
    _order = 'fecha_iniciativa desc'

    
    def _tabla(self):
        group_by_strxx1 = """
                    select ini.id id,
                    case 
                      when ges.estado = 'Identificar' then '1 Identificar'
                      when ges.estado = 'Preparar' then '2 Preparar'
                      when ges.estado = 'Primera Visita' then '3 Primera Visita'
                      when ges.estado = 'Seguimiento' then '4 Seguimiento'
                      when ges.estado = 'Pruebas' then '5 Pruebas'
                      when ges.estado = 'Oferta' then '6 Oferta'
                      when ges.estado = 'Negociacion' then '7 Negociacion'
                    end estado,
                    ini.type tipo, ini.id iniciativa,ven.name comercial,ciu.name ciudad,cli.name prospecto, 
                    fecha_iniciativa,-- dias_identificar identificar,

                    to_char(fecha_iniciativa, 'yyyymm') periodo_iniciativa,
                    ini.name titulo

                    from          crm_lead as ini
                     left join    res_users as usr on (ini.user_id = usr.id )
                     left join    res_partner as ven on ( usr.partner_id = ven.id)
                     inner join   res_partner as cli on (ini.partner_id = cli.id )
                     left join   log_crm_gestion as ges on (ini.id = ges.registro_id )
                     left join     ciudades as ciu on (ciu.id = ini.ciudad_id )
                     
                    where ini.user_id = usr.id and 
                          usr.partner_id = ven.id and
                          ini.partner_id = cli.id """
        return group_by_strxx1

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            )""" % (self._table, self._tabla()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
