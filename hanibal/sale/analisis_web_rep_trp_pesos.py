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

# ARNEGSIS

from openerp import fields,models, api
import cx_Oracle


#-----------------------------------
#- * REPORTE ANALISIS DE CAPACIDAD DE CAMIONES * -
#-----------------------------------    
class analisis_web_rep_trp_pesos(models.Model):
    
    _name = 'analisis.web.rep.trp.pesos'
    _order = 'fecha desc'
   # _rec_name = 'placa'
    
    compania = fields.Char(string='Compania')
    placa = fields.Char(string='Placa')
    fecha = fields.Date(string='Fecha')
    mes = fields.Char(string='Mes')
    anio = fields.Char(string='Anio')
    pla_numvia = fields.Char(string='Pla_numvia')
    tipo = fields.Char(string='Tipo')
    capacidad = fields.Float(string='Capacidad',group_operator="sum")
    peso = fields.Float(string='Peso',group_operator="sum")
    utilizacion = fields.Float(string='Utilizacion',group_operator="avg")
    recomendacion = fields.Char(string='Recomendacion')
    tipo_transporte = fields.Char(string='Tipo Transporte')


    @api.multi
    def fechafor(self,dt):
        FCH = dt[6:10]+'-'+dt[3:5]+'-'+dt[0:2]
	return FCH

    @api.multi
    def mes_cnv(self,psc):
	#dct=['01 Enero','02 Febrero','03 Marzo','04 Abril','05 Mayo','06 Junio','07 Julio','08 Agosto','09 Septiembre','10 Octubre','11 Noviembre','12 Diciembre']
	dct=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
	return dct[int(psc)-1]
  
    @api.multi
    def import_data(self,):
	print 'Importar analisis guia---------------------------------------'
	self._cr.execute("TRUNCATE TABLE ANALISIS_WEB_REP_TRP_PESOS")
	self._cr.commit()
	dct = {}
	conn_str='openside/masejo072431@172.16.1.251:1521/proqimsa'
	db_conn = cx_Oracle.connect(conn_str)
	cursor = db_conn.cursor()
	cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'")
	cursor.execute('SELECT COMPANIA,PLACA,FECHA,ANIO,MES,PLA_NUMVIA,TIPO,CAPACIDAD,PESO,UTILIZACION,RECOMENDACION,TIPO_TRANSPORTE FROM openside.WEB_REP_TRP_PESOS')
	registros = cursor.fetchall()
	for r in registros:
            mi_lista = list(r)
            dct = {'compania':mi_lista[0], 
                   'placa':mi_lista[1],
		   'fecha':self.fechafor(mi_lista[2]),
		   'anio':mi_lista[3],
		   'mes':self.mes_cnv(mi_lista[4]),
		   'pla_numvia':mi_lista[5],
		   'tipo':mi_lista[6],
		   'capacidad':mi_lista[7],			
		   'peso':mi_lista[8],
                   'utilizacion':mi_lista[9],
                   'recomendacion':mi_lista[10],
                   'tipo_transporte':mi_lista[11]
		}
									    
            self.create(dct)
	return True


