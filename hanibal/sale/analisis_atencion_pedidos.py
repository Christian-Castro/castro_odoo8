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

#--------------------------------------bitacora

class analisis_bitacora_pedidos(models.Model):

    
    _name = 'analisis.bitacora.pedidos'
    ##_order = 'codigo_ped , indice_det'
    ##_rec_name = 'pedido'

    clase = fields.Char(string='Clase')
    codigo = fields.Char(string='Articulo')
    descripcion = fields.Char(string='Descripcion')
    dia = fields.Date(string='Fecha')
    pedido = fields.Char(string='Pedido')
    vendedor= fields.Char(string='Vendedor')
    cli_des = fields.Char(string='Cliente')
    cerrado = fields.Char(string='Cerrado')
    cantidad = fields.Float(string='Cant Ini')
    estado = fields.Char(string='Estado Ini')
    bodega = fields.Char(string='Bodega')
    total = fields.Float(string='Total')
    disponible_cia = fields.Float(string='Disp')
    reservado_cia = fields.Float(string='Res')     
    disponible_bod  = fields.Float(string='Dis Bod')
    reservado_bod = fields.Float(string='Res Bod')
    pedidos_id = fields.Many2one('analisis.pedidos',string="Pedidos",requrired="True",ondelete="cascade")
    cia = fields.Char(string='Compañia')
    periodo =  fields.Char(string='Periodo')
    vendedor_cod = fields.Char(string='Cod Vend')
    cantidadpedida = fields.Float(string='Can Pedida')
    cantidadfacturada = fields.Float(string='Can Facturada')
    estadofinal = fields.Char(string='Estado Final')
    es_venta_perdida = fields.Char(string='Es venta perdida')
    inicio = fields.Datetime(string='Inicio')
    fin = fields.Datetime(string='Fin')
    horas = fields.Float(string='Horas')
    calificacion = fields.Char(string='Calificacion')
    user_id = fields.Many2one(string='usuario')
    motivo_cierre= fields.Char(string='Motivo Cierre')


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
    def _busca_pedido_cab(self,cod):

	query = "select id from analisis_pedidos where pedido = '"+str(cod)+"' "
	self._cr.execute(query)
	res = self._cr.dictfetchall()
	if res != []:
	   iden = res[0]['id']
	else:
	   iden = False
	return iden

    @api.multi
    def fecha(self,dt):
        if dt != None:
	  FCH = dt[6:10]+'-'+dt[3:5]+'-'+dt[0:2]+' '+dt[11:19]
	  return FCH
        if dt is None: 
          FCH = ''
          return dt#FCH


    @api.multi
    def fecha2(self,dt):
        if dt != None:
	  FCH = dt[6:10]+'-'+dt[3:5]+'-'+dt[0:2]
	  return FCH
        if dt is None: 
          FCH = ''
          return dt#FCH


    @api.multi
    def import_data_bit(self,):

	self._cr.execute("TRUNCATE TABLE analisis_bitacora_pedidos cascade")#
	self._cr.commit()
	dct = {}
	conn_str='openside/masejo072431@172.16.1.251:1521/proqimsa'
	db_conn = cx_Oracle.connect(conn_str)
	cursor = db_conn.cursor()
	cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'")

	


	cursor.execute('select CLASE,CODIGO,DECRIPCION,DIA,PEDIDO,VENDEDOR,CLI_DES,CERRADO,CANTIDAD,ESTADO,BODEGA,TOTAL,DISPONIBLE_CIA,RESERVADO_CIA,DISPONIBLE_BOD,RESERVADO_BOD,CIA,PERIODO,VENDEDOR_COD,CANTIDADPEDIDA,CANTIDADFACTURADA,ESTADOFINAL,ES_VENTA_PERDIDA,INICIO,FIN,HORAS,CALIFICACION,MOTIVO_CIERRE from WEB_SIDE_BIT_PED t')


	registros = cursor.fetchall()

	for r in registros:
            mi_lista = list(r)

            dct = {'clase':mi_lista[0], 
                   'codigo':mi_lista[1], 
                   'descripcion':mi_lista[2],
                   'dia':self.fecha2(mi_lista[3]),
                   'pedido':mi_lista[4],
                   'vendedor':mi_lista[5],
                   'cli_des':mi_lista[6],
                   'cerrado':mi_lista[7],
                   'cantidad':mi_lista[8],
                   'estado':mi_lista[9],
                   'bodega':mi_lista[10],
                   'total':mi_lista[11],
                   'disponible_cia':mi_lista[12],
                   'reservado_cia':mi_lista[13],
                   'disponible_bod':mi_lista[14],
                   'reservado_bod':mi_lista[15],
                   'pedidos_id':int(self._busca_pedido_cab(mi_lista[4])),
		   'cia':mi_lista[16], 
                   'periodo':mi_lista[17], 
                   'vendedor_cod':mi_lista[18], 
                   'cantidadpedida':mi_lista[19],
                   'cantidadfacturada':mi_lista[20], 
                   'estadofinal':mi_lista[21], 
                   'es_venta_perdida':mi_lista[22],
                   'inicio':self.fecha(mi_lista[23]), 
                   'fin':self.fecha(mi_lista[24]), 
                   'horas':mi_lista[25], 
                   'calificacion':mi_lista[26],
                   'user_id': int(self._busca_usuario(mi_lista[18])) or False,
                   'motivo_cierre':mi_lista[27],





		}
									    
            self.create(dct)
	return True


analisis_bitacora_pedidos()
#-----------------------------------------------




#-----------------------------------
#- * REPORTE ANALISIS DE PEDIDOS * -
#-----------------------------------   
class analisis_pedidos_det(models.Model):

    
    _name = 'analisis.pedidos.det'
    ##_order = 'codigo_ped , indice_det'
    ##_rec_name = 'pedido'

    codigo_ped = fields.Char(string='CODIGO_PED')
    estado_linea = fields.Char(string='Est')
    articulo = fields.Char(string='Articulo')
    descripcion = fields.Char(string='Descripcion')
    bodega = fields.Char(string='Bod')
    unidad = fields.Char(string='Un')
    cantidad = fields.Float(string='Cant')
    precio = fields.Float(string='Precio')
    total_art = fields.Float(string='Total')
    existencia_actual = fields.Float(string='Existencia')
    indice_det = fields.Float(string='Indice')
    pedidos_id = fields.Many2one('analisis.pedidos',string="Pedidos",requrired="True",ondelete="cascade")

    @api.multi
    def _busca_pedido_cab(self,cod):

	query = "select id from analisis_pedidos where pedido = '"+str(cod)+"' "
	self._cr.execute(query)
	res = self._cr.dictfetchall()
	if res != []:
	   iden = res[0]['id']
	else:
	   iden = False
	return iden

    @api.multi
    def import_data_det(self,):

	self._cr.execute("TRUNCATE TABLE analisis_pedidos_det cascade")#
	self._cr.commit()
	dct = {}
	conn_str='openside/masejo072431@172.16.1.251:1521/proqimsa'
	db_conn = cx_Oracle.connect(conn_str)
	cursor = db_conn.cursor()
	cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'")

	


	cursor.execute('SELECT CODIGO_PED,ESTADO_LINEA,ARTICULO,DESCRIPCION,BODEGA,UNIDAD,CANTIDAD,PRECIO,TOTAL_ART,EXISTENCIA_ACTUAL,INDICE_DET FROM openside.WEB_REP_ATENCION_PEDIDOS_DET')


	registros = cursor.fetchall()

	for r in registros:
            mi_lista = list(r)

            dct = {'codigo_ped':mi_lista[0], 
		   'estado_linea':mi_lista[1],
		   'articulo':mi_lista[2],
		   'descripcion':mi_lista[3],
		   'bodega':mi_lista[4],
		   'unidad':mi_lista[5],
		   'cantidad':mi_lista[6],
		   'precio':mi_lista[7],
		   'total_art':mi_lista[8],
		   'existencia_actual':mi_lista[9],
		   'indice_det':mi_lista[10],
		   'pedidos_id':int(self._busca_pedido_cab(mi_lista[0]))
		}
									    
            self.create(dct)
	return True


analisis_pedidos_det()

class analisis_pedidos(models.Model):
    
    _name = 'analisis.pedidos'
    _order = 'fecha_digita_pedido asc'
    _rec_name = 'pedido'
    
    compania = fields.Char(string='COMPAÑIA')
    pedido = fields.Char(string='NUMERO PEDIDO')# coidgo del pedido
    fecha_digita_pedido = fields.Datetime(string='FECHA INGRESO PEDIDO')
    
    mes = fields.Char(string='MES')
    anio = fields.Char(string='AÑO')
    
    cliente_codigo = fields.Char(string='CLIENTE CODIGO')
    cliente_descripcion = fields.Char(string='CLIENTE DESCRIPCION')
    estado_pedido = fields.Char(string='ESTADO PEDIDO')
    vendedor = fields.Char(string='VENDEDOR')
    cod_vendedor = fields.Char(string='CODIGO VENDEDOR')
    localidad = fields.Char(string='LOCALIDAD')
    #fecha_pedido = fields.Date(string='FECHA PEDIDO')    

    dias_limite = fields.Char(string='DIAS LIMITE')
    eficiencia = fields.Float(string='A tiempo',group_operator="avg")
    no_eficiencia = fields.Float(string='Fuera de tiempo',group_operator="avg")
    fecha_ultima_factura = fields.Datetime(string='ULTIMA FACTURA')
    fecha_ultima_guia = fields.Date(string='ULTIMA GUIA')
    fecha_ultima_planificacion = fields.Date(string='ULTIMA PLANIFICACION')
    diferencia = fields.Char(string='DIFERENCIA')
    atencion = fields.Char(string='ATENCION')
    user_id = fields.Many2one(string='usuario')
    refacturado = fields.Char(string='REFACTURADO')
    oficina = fields.Char(string='OFICINA')
    line_id = fields.One2many('analisis.pedidos.det','pedidos_id',string="Detalle")
    line_id_bit = fields.One2many('analisis.bitacora.pedidos','pedidos_id',string="Bitacora")
    subtotal = fields.Float(string='Subtotal')
    iva = fields.Float(string='Iva')
    total = fields.Float(string='Total')
    motivo_cierre = fields.Char(string='Motivo Cierre')
    estado_cerrado = fields.Char(string='Cerrado')

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
        if dt != None:
	  FCH = dt[6:10]+'-'+dt[3:5]+'-'+dt[0:2]+' '+dt[11:19]
	  return FCH
        if dt is None: 
          FCH = ''
          return FCH

    @api.multi
    def mes_cnv(self,psc):
	dct=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
	return dct[int(psc)-1]
  
    @api.multi
    def import_data(self,):
	print 'Importar pedidos'
	self._cr.execute("TRUNCATE TABLE analisis_pedidos cascade")
	self._cr.commit()
	dct = {}
	conn_str='openside/masejo072431@172.16.1.251:1521/proqimsa'
	db_conn = cx_Oracle.connect(conn_str)
	cursor = db_conn.cursor()
	cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'")
        print 'ñññññññññññññññññññññññññññññññ'
        print 'ñññññññññññññññññññññññññññññññ'
        print 'ñññññññññññññññññññññññññññññññ'
        print 'ñññññññññññññññññññññññññññññññ'
        print 'ñññññññññññññññññññññññññññññññ'
        print 'ñññññññññññññññññññññññññññññññ'
        print 'ñññññññññññññññññññññññññññññññ'
	cursor.execute('SELECT compania,pedido,fecha_digitacion_pedido,mes,anio,cliente_codigo,cliente_descripcion,estado_pedido,estado_cerrado,vendedor,cod_vendedor, localidad,dias_limite,eficiencia,no_eficiencia,fecha_ultimafactura,  fecha_ultimaguia,fecha_ultimaplanificacion,diferencia,a_tiempo,refacturado,oficina,subtotal,iva,total,motivo_cierre FROM openside.WEB_REP_ATENCION_PEDIDOS_2')

	#registros = cursor.dictfetchall()
       # print '|||||||||||||||||||||||||||||||||||||'
       # print '|||||||||||||||||||||||||||||||||||||'
       # print '|||||||||||||||||||||||||||||||||||||'
       # print '|||||||||||||||||||||||||||||||||||||'
       # print '|||||||||||||||||||||||||||||||||||||'
       # print '|||||||||||||||||||||||||||||||||||||'
	registros = cursor.fetchall()
	for r in registros:
            mi_lista = list(r)
            dct = {'compania':mi_lista[0],
		    'pedido':mi_lista[1],
		    'fecha_digita_pedido':self.fecha(mi_lista[2]),
		    'mes':self.mes_cnv(mi_lista[3]),
		    'anio':mi_lista[4],
		    'cliente_codigo':mi_lista[5],
		    'cliente_descripcion':mi_lista[6],
		    'estado_pedido':mi_lista[7],
		    'estado_cerrado':mi_lista[8],
		    'vendedor':mi_lista[9],
		    'cod_vendedor':mi_lista[10],
		    'localidad':mi_lista[11],
		   # 'fecha_pedido':mi_lista[12],
		    'dias_limite':mi_lista[12],
		    'eficiencia':mi_lista[13],
		    'no_eficiencia':mi_lista[14],
		    'fecha_ultima_factura':self.fecha(mi_lista[15]) or False,
		    'fecha_ultima_guia':self.fecha(mi_lista[16]) or False,
		    'fecha_ultima_planificacion':self.fecha(mi_lista[17]) or False,
		    'diferencia':mi_lista[18],
		    'atencion':mi_lista[19],
		    'user_id': int(self._busca_usuario(mi_lista[10])) or False,
                    'refacturado':mi_lista[20],
                    'oficina':mi_lista[21],
                    'subtotal':mi_lista[22],
                    'iva':mi_lista[23],
                    'total':mi_lista[24],
                    'motivo_cierre':mi_lista[25],
		}
            print 'kkkkkkkkkkkkkkkkkkkkkk'							    
	    print 'kkkkkkkkkkkkkkkkkkkkkk'							    
            print 'kkkkkkkkkkkkkkkkkkkkkk'							    
	    print 'kkkkkkkkkkkkkkkkkkkkkk'	
            print 'kkkkkkkkkkkkkkkkkkkkkk'							    
	    print 'kkkkkkkkkkkkkkkkkkkkkk'							    
            print 'kkkkkkkkkkkkkkkkkkkkkk'							    
	    print 'kkkkkkkkkkkkkkkkkkkkkk'	
						    
            self.create(dct)
        
	#analisis.pedidos.det()
        #import  analisis_pedidos_det
	obj = self.env['analisis.pedidos.det']
	obj.import_data_det()
        obj2 = self.env['analisis.bitacora.pedidos']
        obj2.import_data_bit()


	return True
analisis_pedidos()

