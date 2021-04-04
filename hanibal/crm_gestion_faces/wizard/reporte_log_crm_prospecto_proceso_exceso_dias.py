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
    _name = "reporte.log.crm.prospecto.proceso.exceso.dias"
    _description = "Dias excedidos"
    _auto = False
    _rec_name = 'fecha_iniciativa'

    _columns = {
        'orden':fields.float('Orden', readonly=False,),
        'estado': fields.char('estado', readonly=True),
        'tipo': fields.char('Iniciativa / Prospecto', readonly=True),
        'comercial': fields.char('Comercial', readonly=True),
        'ciudad': fields.char('Ciudad', readonly=True),
        'prospecto': fields.char('prospecto', readonly=True),
        'fecha_iniciativa': fields.datetime('Fecha iniciativa', readonly=True),
        'dias_estado': fields.float('Dias', readonly=True,group_operator="sum"),
        'titulo': fields.char('Titulo', readonly=True),  
        'periodo_iniciativa': fields.char('Periodo', readonly=True),      
        'dias_exceso': fields.float('Exceso', readonly=True,group_operator="sum"),
        'observado': fields.char('Observado', readonly=True),
        'ganado': fields.char('Ganado', readonly=True),

    }
    _order = 'orden desc'

    
    def _tabla(self):
        group_by_strxx1 = """
               select 1 orden, ini.id id,
                    '1 Identificar'  estado,
                    ini.type tipo, ven.name comercial,ciu.name ciudad,cli.name prospecto, 
                    fecha_iniciativa,  
                    coalesce(dias_identificar,0) dias_estado,
                    ini.name titulo,
                    to_char(fecha_iniciativa, 'yyyymm') periodo_iniciativa,
		    case 
		       when coalesce(dias_identificar,0) <=   (select tr.d_identificar 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 0
		       when coalesce(dias_identificar,0) >   (select tr.d_identificar 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	coalesce(dias_identificar,0) - (select tr.d_identificar 
			                  from   crm_tiempos_procesos_conf as tr)	
		    end dias_exceso,
		    case 
		       when coalesce(dias_identificar,0) <=   (select tr.d_identificar 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 'NO'
		       when coalesce(dias_identificar,0) >   (select tr.d_identificar 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	'SI'	
		    end observado,
           case when cs.name = 'New' then 'Proceso' 
                when cs.name = 'Lost' then 'No' 
                when cs.name = 'Won' then 'Si' 
            else cs.name 
           end ganado


                  from          crm_lead as ini
                     left join    res_users as usr on (ini.user_id = usr.id )
                     left join    res_partner as ven on ( usr.partner_id = ven.id)
                     inner join   res_partner as cli on (ini.partner_id = cli.id )
                     left join   log_crm_gestion as ges on (ini.id = ges.registro_id )
                     left join     ciudades as ciu on (ciu.id = ini.ciudad_id )
                     left join     crm_case_stage cs on (ini.stage_id = cs.id)
                     
                    where ini.user_id = usr.id and 
                          usr.partner_id = ven.id and
                          ini.partner_id = cli.id 

union all 
                   select 2 orden, ini.id id,
                    '2 Preparar' estado,
                    ini.type tipo, ven.name comercial,ciu.name ciudad,cli.name prospecto, 
                    fecha_iniciativa,  

                    coalesce(dias_preparar,0) dias_estado,
                    ini.name titulo,
                    to_char(fecha_iniciativa, 'yyyymm') periodo_iniciativa,
		    case 
		       when coalesce(dias_preparar,0) <=   (select tr.d_preparar 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 0
		       when coalesce(dias_preparar,0) >   (select tr.d_preparar 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	coalesce(dias_preparar,0) - (select tr.d_preparar 
			                  from   crm_tiempos_procesos_conf as tr)	
		    end dias_exceso,
		    case 
		       when coalesce(dias_preparar,0) <=   (select tr.d_preparar 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 'NO'
		       when coalesce(dias_preparar,0) >   (select tr.d_preparar 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	'SI'	
		    end Observado,
           case when cs.name = 'New' then 'Proceso' 
                when cs.name = 'Lost' then 'No' 
                when cs.name = 'Won' then 'Si' 
            else cs.name 
           end ganado

                  from          crm_lead as ini
                     left join    res_users as usr on (ini.user_id = usr.id )
                     left join    res_partner as ven on ( usr.partner_id = ven.id)
                     inner join   res_partner as cli on (ini.partner_id = cli.id )
                     left join   log_crm_gestion as ges on (ini.id = ges.registro_id )
                     left join     ciudades as ciu on (ciu.id = ini.ciudad_id )
                     left join     crm_case_stage cs on (ini.stage_id = cs.id)
                     
                    where ini.user_id = usr.id and 
                          usr.partner_id = ven.id and
                          ini.partner_id = cli.id
                union all 
                   select 3 orden,ini.id id,
                    '3 Primera Visita' estado,
                    ini.type tipo, ven.name comercial,ciu.name ciudad,cli.name prospecto, 
                    fecha_iniciativa,  

                    coalesce(dias_primera_visita,0) dias_estado,
                    ini.name titulo,
                    to_char(fecha_iniciativa, 'yyyymm') periodo_iniciativa,
		    case 
		       when coalesce(dias_primera_visita,0) <=   (select tr.d_primera_visita
			                  from   crm_tiempos_procesos_conf as tr) 
			then 0
		       when coalesce(dias_primera_visita,0) >   (select tr.d_primera_visita 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	coalesce(dias_preparar,0) - (select tr.d_preparar 
			                  from   crm_tiempos_procesos_conf as tr)	
		    end dias_exceso,
		    case 
		       when coalesce(dias_primera_visita,0) <=   (select tr.d_primera_visita 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 'NO'
		       when coalesce(dias_primera_visita,0) >   (select tr.d_primera_visita 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	'SI'	
		    end Observado ,
           case when cs.name = 'New' then 'Proceso' 
                when cs.name = 'Lost' then 'No' 
                when cs.name = 'Won' then 'Si' 
            else cs.name 
           end ganado                   

                  from          crm_lead as ini
                     left join    res_users as usr on (ini.user_id = usr.id )
                     left join    res_partner as ven on ( usr.partner_id = ven.id)
                     inner join   res_partner as cli on (ini.partner_id = cli.id )
                     left join   log_crm_gestion as ges on (ini.id = ges.registro_id )
                     left join     ciudades as ciu on (ciu.id = ini.ciudad_id )
                     left join     crm_case_stage cs on (ini.stage_id = cs.id)
                     
                    where ini.user_id = usr.id and 
                          usr.partner_id = ven.id and
                          ini.partner_id = cli.id 

union all 
                   select 4 orden,ini.id id,
                    '4 Seguimiento' estado,
                    ini.type tipo, ven.name comercial,ciu.name ciudad,cli.name prospecto, 
                    fecha_iniciativa,  

                    coalesce(dias_seguimiento,0) dias_estado,
                    ini.name titulo,
                    to_char(fecha_iniciativa, 'yyyymm') periodo_iniciativa,
		    case 
		       when coalesce(dias_seguimiento,0) <=   (select tr.d_seguimiento 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 0
		       when coalesce(dias_seguimiento,0) >   (select tr.d_seguimiento 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	coalesce(dias_seguimiento,0) - (select tr.d_seguimiento 
			                  from   crm_tiempos_procesos_conf as tr)	
		    end dias_exceso,
		    case 
		       when coalesce(dias_seguimiento,0) <=   (select tr.d_seguimiento 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 'NO'
		       when coalesce(dias_seguimiento,0) >   (select tr.d_seguimiento 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	'SI'	
		    end Observado,
           case when cs.name = 'New' then 'Proceso' 
                when cs.name = 'Lost' then 'No' 
                when cs.name = 'Won' then 'Si' 
            else cs.name 
           end ganado

                  from          crm_lead as ini
                     left join    res_users as usr on (ini.user_id = usr.id )
                     left join    res_partner as ven on ( usr.partner_id = ven.id)
                     inner join   res_partner as cli on (ini.partner_id = cli.id )
                     left join   log_crm_gestion as ges on (ini.id = ges.registro_id )
                     left join     ciudades as ciu on (ciu.id = ini.ciudad_id )
                     left join     crm_case_stage cs on (ini.stage_id = cs.id)
                     
                    where ini.user_id = usr.id and 
                          usr.partner_id = ven.id and
                          ini.partner_id = cli.id 
union all 
                   select 5 orden,ini.id id,
                    '5 Pruebas' estado,
                    ini.type tipo, ven.name comercial,ciu.name ciudad,cli.name prospecto, 
                    fecha_iniciativa,  

                    coalesce(dias_pruebas,0) dias_estado,
                    ini.name titulo,
                    to_char(fecha_iniciativa, 'yyyymm') periodo_iniciativa,
		    case 
		       when coalesce(dias_pruebas,0) <=   (select tr.d_pruebas 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 0
		       when coalesce(dias_pruebas,0) >   (select tr.d_pruebas 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	coalesce(dias_pruebas,0) - (select tr.d_pruebas 
			                  from   crm_tiempos_procesos_conf as tr)	
		    end dias_exceso,
		    case 
		       when coalesce(dias_pruebas,0) <=   (select tr.d_pruebas 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 'NO'
		       when coalesce(dias_pruebas,0) >   (select tr.d_pruebas 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	'SI'	
		    end Observado,
           case when cs.name = 'New' then 'Proceso' 
                when cs.name = 'Lost' then 'No' 
                when cs.name = 'Won' then 'Si' 
            else cs.name 
           end ganado

                  from          crm_lead as ini
                     left join    res_users as usr on (ini.user_id = usr.id )
                     left join    res_partner as ven on ( usr.partner_id = ven.id)
                     inner join   res_partner as cli on (ini.partner_id = cli.id )
                     left join   log_crm_gestion as ges on (ini.id = ges.registro_id )
                     left join     ciudades as ciu on (ciu.id = ini.ciudad_id )
                     left join     crm_case_stage cs on (ini.stage_id = cs.id)
                     
                    where ini.user_id = usr.id and 
                          usr.partner_id = ven.id and
                          ini.partner_id = cli.id 

union all 
                   select 6 orden,ini.id id,
                    '6 Oferta' estado,
                    ini.type tipo, ven.name comercial,ciu.name ciudad,cli.name prospecto, 
                    fecha_iniciativa,   
                    coalesce(dias_oferta,0) dias_estado,
                    ini.name titulo,
                    to_char(fecha_iniciativa, 'yyyymm') periodo_iniciativa,
		    case 
		       when coalesce(dias_oferta,0) <=   (select tr.d_oferta 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 0
		       when coalesce(dias_oferta,0) >   (select tr.d_oferta 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	coalesce(dias_oferta,0) - (select tr.d_oferta 
			                  from   crm_tiempos_procesos_conf as tr)	
		    end dias_exceso,
		    case 
		       when coalesce(dias_oferta,0) <=   (select tr.d_oferta 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 'NO'
		       when coalesce(dias_oferta,0) >   (select tr.d_oferta 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	'SI'	
		    end Observado,
           case when cs.name = 'New' then 'Proceso' 
                when cs.name = 'Lost' then 'No' 
                when cs.name = 'Won' then 'Si' 
            else cs.name 
           end ganado

                  from          crm_lead as ini
                     left join    res_users as usr on (ini.user_id = usr.id )
                     left join    res_partner as ven on ( usr.partner_id = ven.id)
                     inner join   res_partner as cli on (ini.partner_id = cli.id )
                     left join   log_crm_gestion as ges on (ini.id = ges.registro_id )
                     left join     ciudades as ciu on (ciu.id = ini.ciudad_id )
                     left join     crm_case_stage cs on (ini.stage_id = cs.id)
                     
                    where ini.user_id = usr.id and 
                          usr.partner_id = ven.id and
                          ini.partner_id = cli.id and 
                          ges.estado = 'Oferta'

union all 
                   select 7 orden,ini.id id,
                    '7 Negociacion'estado,
                    ini.type tipo, ven.name comercial,ciu.name ciudad,cli.name prospecto, 
                    fecha_iniciativa,
                    coalesce(dias_negociacion,0) dias_estado,
                    ini.name titulo,
                    to_char(fecha_iniciativa, 'yyyymm') periodo_iniciativa,

		    case 
		       when coalesce(dias_negociacion,0) <=   (select tr.d_negociacion 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 0
		       when coalesce(dias_negociacion,0) >   (select tr.d_negociacion 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	coalesce(dias_negociacion,0) - (select tr.d_negociacion 
			                  from   crm_tiempos_procesos_conf as tr)	
		    end dias_exceso,
		    case 
		       when coalesce(dias_negociacion,0) <=   (select tr.d_negociacion 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 'NO'
		       when coalesce(dias_negociacion,0) >   (select tr.d_negociacion 
			                  from   crm_tiempos_procesos_conf as tr) 
			then 	'SI'	
		    end Observado,
           case when cs.name = 'New' then 'Proceso' 
                when cs.name = 'Lost' then 'No' 
                when cs.name = 'Won' then 'Si' 
            else cs.name 
           end ganado

                  from          crm_lead as ini
                     left join    res_users as usr on (ini.user_id = usr.id )
                     left join    res_partner as ven on ( usr.partner_id = ven.id)
                     inner join   res_partner as cli on (ini.partner_id = cli.id )
                     left join   log_crm_gestion as ges on (ini.id = ges.registro_id )
                     left join     ciudades as ciu on (ciu.id = ini.ciudad_id )
                     left join     crm_case_stage cs on (ini.stage_id = cs.id)
                     
                    where ini.user_id = usr.id and 
                          usr.partner_id = ven.id and
                          ini.partner_id = cli.id

                order by 7,1       
  """

        return group_by_strxx1

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            )""" % (self._table, self._tabla()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
