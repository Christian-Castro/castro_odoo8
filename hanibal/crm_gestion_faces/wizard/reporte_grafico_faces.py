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
    _rec_name = 'fecha_prospecto'

    _columns = {
        #'id': fields.float('N idd', readonly=True),
        'estado': fields.char('estado', readonly=True),
        'tipo': fields.char('Iniciativa / Prospecto', readonly=True),
        'iniciativa': fields.float('N Iniciativa', readonly=True),
        'comercial': fields.char('Comercial', readonly=True),
        'ciudad': fields.char('Ciudad', readonly=True),
        'prospecto': fields.char('prospecto', readonly=True),
        'fecha_prospecto':  fields.datetime('Fecha de prospecto', readonly=True), 
        'fecha_iniciativa': fields.datetime('Fecha de iniciativa', readonly=True),
        'identificar': fields.char('Identificar', readonly=True),

        'fecha_contacto': fields.datetime('Fecha de contacto', readonly=True),
        'preparar': fields.char('Preparar', readonly=True),

        'fecha_reunion': fields.datetime('Fecha de reunion', readonly=True),
        'fecha_contacto_pv': fields.datetime('Fecha de contacto PV', readonly=True),
        'p_visita': fields.char('p_visita1', readonly=True),

        'fecha_pllamada': fields.datetime('Fecha primera llamada', readonly=True),
        'fecha_preunion': fields.datetime('Fecha primera reunion', readonly=True),
        'seguimiento': fields.char('seguimiento', readonly=True),


        'fecha_reu_marc_prueba': fields.datetime('fecha_reu_marc_prueba', readonly=True),
        'fecha_llamada_seg_sa': fields.datetime('fecha_llamada_seg_sa', readonly=True),
        'pruebas': fields.char('Pruebas', readonly=True),

        'fecha_oferta_final': fields.datetime('fecha_oferta_final', readonly=True),
        'fecha_reunion_pruebas': fields.datetime('fecha_llamada_seg_sa', readonly=True),
        'oferta': fields.char('oferta', readonly=True),
        'fecha_gan_perd': fields.datetime('fecha_gan_perd', readonly=True),
        'negociacion': fields.char('negociacion', readonly=True),
        
    }
    _order = 'fecha_iniciativa desc'

    
    def _tabla(self):
        group_by_strxx1 = """
                    select ini.id id,
                    ges.estado,
                    ini.type tipo, ini.id iniciativa,ven.name comercial,ciu.name ciudad,cli.name prospecto, 
                    fecha_prospecto,fecha_iniciativa, 1 identificar,
                    fecha_contacto,preparar,

                    fecha_reunion, fecha_contacto_pv,p_visita,
                    fecha_pllamada,fecha_preunion,seguimiento,
                    fecha_reu_marc_prueba, fecha_llamada_seg_sa,pruebas,
                    fecha_oferta_final,fecha_reunion_pruebas,oferta,
                    fecha_gan_perd,negociacion


                    from          crm_lead as ini
                     left join    res_users as usr on (ini.user_id = usr.id )
                     left join    res_partner as ven on ( usr.partner_id = ven.id)
                     inner join   res_partner as cli on (ini.partner_id = cli.id )
                     left join   log_crm_gestion as ges on (ini.id = ges.registro_id )
                     left join     ciudades as ciu on (ciu.id = ini.ciudad_id )
                     
                    where ini.user_id = usr.id and 
                          usr.partner_id = ven.id and
                          ini.partner_id = cli.id 
        """
        return group_by_strxx1

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            )""" % (self._table, self._tabla()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
