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


class analisis_rotacion_inventario_usd(models.Model):
    
    _name = 'analisis.rotacion.inventario.usd'
    _order = 'bodega, codigo,fechahistorico'
    #_rec_name = 'pedido'
    
    bodega = fields.Char(string='Bodega')
    tipoclasificacion = fields.Char(string='Tipo')
    valorclasificacion = fields.Char(string='Clase')
    codigo = fields.Char(string='Codigo')
    descripcion = fields.Char(string='Descripcion')
    existenciaactual = fields.Float(string='Existencia')     
    fechahistorico = fields.Date(string='Fecha') 
    periodo = fields.Char(string='periodo')    
    unidadmedida = fields.Char(string='unidadmedida') 
    saldofinalperiodo = fields.Float(stcring='Saldo')   
    ventasnetas = fields.Float(string='ventasnetas')  
    costopromedio = fields.Float(string='costopromedio') 
    rotacion = fields.Float(string='rotacion')
    diasmes = fields.Float(string='diasmes')
    diasrec = fields.Float(string='diasrec')
    compania = fields.Char(string='compania')
    inventario = fields.Char(string='inventario')
    promsaldo = fields.Float(string='promsaldo')
    acmfacturado = fields.Float(string='acmfacturado')
    calificacion = fields.Char(string='calificacion')
    tipoanalisis = fields.Char(string='tipoanalisis')


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
       # print '***************************************'
       # print  dt
       # print dt[0:3]
       # print '***************************************'
	FCH =  dt[6:10]+'-'+dt[3:5]+'-'+dt[0:2] ##2015-04-01 00:00:00

        #FCH =  dt[0:3]+'-'+dt[5:6]+'-'+dt[8:9] ##2015-04-01 00:00:00

	return FCH

    @api.multi
    def mes_cnv(self,psc):
	dct=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
	return dct[int(psc)-1]
  
    @api.multi
    def import_data(self,):
	print 'Importar rotacion inventario'
	self._cr.execute("TRUNCATE TABLE analisis_rotacion_inventario_usd")
	self._cr.commit()
	dct = {}
	conn_str='openside/masejo072431@172.16.1.251:1521/proqimsa'

	db_conn = cx_Oracle.connect(conn_str)

	cursor = db_conn.cursor()
	cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'")
	cursor.execute('SELECT BODEGA,TIPOCLASIFICACION,VALORCLASIFICACION,CODIGO,DECRIPCION,EXISTENCIAACTUAL,FECHAHISTORICO,PERIODO,UNIDADMEDIDA,SALDOFINALPERIODO, VENTASNETAS, COSTOPROMEDIO, ROTACION, DIASMES,DIASREC, COMPANIA,INVENTARIO, PROMSALDO, ACMFACTURADO,CALIFICACION,tipoanalisis from OPENSIDE.WEB_ROTACION_INV_BOD_USD_1')
	registros = cursor.fetchall()



	for r in registros:
            mi_lista = list(r)
            dct = {'bodega':mi_lista[0],
		   'tipoclasificacion':mi_lista[1],
		   'valorclasificacion':mi_lista[2],
		   'codigo':mi_lista[3],
		   'descripcion':mi_lista[4],
		   'existenciaactual':mi_lista[5],
                   'fechahistorico':self.fecha(mi_lista[6]) or False ,
		   'periodo':mi_lista[7],
		   'unidadmedida':mi_lista[8],
		   'saldofinalperiodo':mi_lista[9],
		   'ventasnetas':mi_lista[10],
		   'costopromedio':mi_lista[11],
		   'rotacion':mi_lista[12],
		   'diasmes':mi_lista[13],
		   'diasrec':mi_lista[14],
                   'compania':mi_lista[15],
                   'inventario':mi_lista[16],
                   'promsaldo':mi_lista[17] ,
                   'acmfacturado':mi_lista[18],
                   'calificacion':mi_lista[19] ,
                   'tipoanalisis':mi_lista[20]#,
                  

		}
									    
            self.create(dct)
	return True


