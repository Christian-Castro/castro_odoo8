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
#- * REPORTE ANALISIS DE PEDIDOS * -
#-----------------------------------    
class analisis_rotacion_cartera(models.Model):
    
    _name = 'analisis.rotacion.cartera'
    _order = 'sal_fecha asc'
    #_rec_name = 'pedido'
    
    compania = fields.Char(string='Compañia')
    cliente_codigo = fields.Char(string='CLIENTE CODIGO')
    cliente_descripcion = fields.Char(string='CLIENTE DESCRIPCION')
    cliente_diacre = fields.Float(string='D.Cre',group_operator="sum")
    mes = fields.Char(string='Mes')
    anio = fields.Char(string='Año')
##    sal_mes = fields.Float(string='Sal',group_operator="avg")
    sal_mes = fields.Float(string='Sal',group_operator="sum")
    fac_mes = fields.Float(string='Fact',group_operator="sum")
  ##  prom_saldos = fields.Float(string='P. Sal.',group_operator="avg")
    prom_saldos = fields.Float(string='P. Sal.',group_operator="sum")
    facturado = fields.Float(string='T. Fac',group_operator="sum")
    dias = fields.Float(string='Días',group_operator="sum") 
    rotacion = fields.Float(string='Rotacion',group_operator="avg") 
    en_problemas = fields.Char(string='En problemas')
    cod_vendedor = fields.Char(string='Vendedor')
    user_id = fields.Many2one(string='usuario')
    periodo = fields.Char(string='Período')
    cliente_limite = fields.Float(string='Crédito',group_operator="sum") 
    ##dr = fields.Float(string='D.Recuperacion',group_operator="avg")
    dr = fields.Float(string='D.Recuperacion',group_operator="sum")  
    sal_fecha = fields.Date(string='Fecha') 
    grupo = fields.Char(string='Grupo')



    @api.multi
    def _busca_usuario(self,cod):

	query = "select id from res_users where codigo = '"+str(cod)+"' "
	self._cr.execute(query)
	res = self._cr.dictfetchall()
	if res != []:
	   iden = res[0]['id']
	else:
	   iden = False
	return iden

    @api.multi
    def fecha(self,dt):

	FCH =  dt[6:10]+'-'+dt[3:5]+'-'+dt[0:2] ##2015-04-01 00:00:00

        #FCH =  dt[0:3]+'-'+dt[5:6]+'-'+dt[8:9] ##2015-04-01 00:00:00

	return FCH

    @api.multi
    def mes_cnv(self,psc):
	dct=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
	return dct[int(psc)-1]
  
    @api.multi
    def import_data(self,):
	print 'Importar Cartera'
	self._cr.execute("TRUNCATE TABLE analisis_rotacion_cartera")
	self._cr.commit()
	dct = {}
	conn_str='openside/masejo072431@172.16.1.251:1521/proqimsa'
        #conn_str='openside/anibal@192.168.234.129:1521/rossi'
	db_conn = cx_Oracle.connect(conn_str)

	cursor = db_conn.cursor()
	cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'")
	cursor.execute('SELECT COMPANIA,CLIENTE_CODIGO,CLIENTE_DESCRIPCION,CLIENTE_DIACRE,MES,ANIO,SAL_MES,FAC_MES,PROM_SALDOS,FACTURADO,DIAS,ROTACION,EN_PROBLEMAS,COD_VENDEDOR,CLI_LIMITE,DR,SAL_FECHA,GRUPO from WEB_ANALISIS_CARTERA')
	registros = cursor.fetchall()

	for r in registros:
            mi_lista = list(r)
            dct = {'compania':mi_lista[0],
		   'cliente_codigo':mi_lista[1],
		   'cliente_descripcion':mi_lista[2],
		   'cliente_diacre':mi_lista[3],
		   'mes':self.mes_cnv(mi_lista[4]),
		   'anio':mi_lista[5],
		   'sal_mes':mi_lista[6],
		   'fac_mes':mi_lista[7],
		   'prom_saldos':mi_lista[8],
		   'facturado':mi_lista[9],
		   'dias':mi_lista[10],
		   'rotacion':mi_lista[11],
		   'en_problemas':mi_lista[12],
		   'cod_vendedor':mi_lista[13],
		   'user_id':int(self._busca_usuario(mi_lista[13])) or False,
                   'periodo':mi_lista[5]+mi_lista[4],
                   'cliente_limite':mi_lista[14],
                   'dr':mi_lista[15] ,
                   'sal_fecha':self.fecha(mi_lista[16]) or False,
                   'grupo':mi_lista[17]


		}
									    
            self.create(dct)
	return True


