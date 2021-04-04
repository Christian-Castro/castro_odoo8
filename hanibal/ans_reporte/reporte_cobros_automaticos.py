# -*- coding: utf-8 -*-
# -*- coding: latin-1 -*-
from openerp.osv import fields, osv
from openerp import models, fields, api, _
from datetime import datetime,timedelta,date
from dateutil import parser
import logging
from datetime import datetime, date, timedelta
import calendar
import base64  
import itertools
import requests
import json
from io import StringIO
import io  
from . import crear_informe_cobros_automaticos_excel
import math
import time
import pytz
import openpyxl
from openpyxl import Workbook
import openpyxl.worksheet
import unicodedata
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
from openpyxl.styles.borders import Border, Side
from openpyxl.drawing.image import Image
import commands
import os


#----------------------------------------------------------
#        Creacion de campos para la pantalla              -
#---------------------------------------------------------- 

class Reporte_cobros(models.Model):
    _inherit= "pagos.automaticos"

    filename=fields.Char(string="Nombre de archivo")
    archivo_xls=fields.Binary(string='Archivo Excel')
    filename_pdf=fields.Char(string="Nombre de archivo")
    archivo_pdf=fields.Binary(string='Archivo PDF')


#----------------------------------------------------------
#                     Obtencion de datos                  -
#---------------------------------------------------------- 
    @api.multi
    def consultar(self):
        lista_datos=[]
        for l in self.pagos_line:
            for f in l.factura_id:
                lista_pagos = [value.ref for value in f.payment_ids]
                cont_num=''
                lis=0.0
                for n in lista_pagos:
                    lis=lis+1
                    if lis<len(lista_pagos):
                        cont_num=cont_num+n+','
                    else:
                        cont_num=cont_num+n
                obser=''
                for d in f.invoice_line:
                    obser=obser+d.name

                dic={
                'tipo':f.journal_id.tipo_reporte,
                #INTEGRACION: SE CAMBIA POR PEDIDO DE CAMBIO DE NUMERO
                #'numero_factura':f.number,
                'numero_factura':f.numerofac,
                'alumno':f.alumno_id.name,
                'codigo_alumno':f.alumno_id.codigo_alumno,
                'observacion':obser,
                'valor':f.amount_total,
                'numero_pago':cont_num,
                'jornada':f.jornada_id.codigo,
                'curso':f.curso_id.name,
                'paralelo':f.paralelo_id.codigo,
                'fecha_factura':f.date_invoice
                }
                lista_datos.append(dic)

        

        datos={
            'lista':lista_datos,
            'cant':len(self.pagos_line),
        }

        return datos

#-------------------------------------------------------------------------------------------------------------------
#                     CREACION DE EXCEL                                                                            -
#-------------------------------------------------------------------------------------------------------------------

    @api.multi
    def generar_excel(self):
        fp =io.BytesIO()
        workbook = self.crear_excel_info()
        workbook.save(fp)
        self.filename = 'Informe.xlsx'
        self.archivo_xls=base64.b64encode(fp.getvalue())      
        return True

    def crear_excel_info(self):
        wb = crear_informe_cobros_automaticos_excel.crear_wb_informe()
        self.crear_informe(wb)
        return wb 


    def crear_informe(self, wb):
        fecha_a = datetime.strptime(self.fecha_emision, '%Y-%m-%d')
        fecha_actual = datetime.strftime(fecha_a, '%d/%b/%Y')
        dic ={
            'fecha_desde':self.fecha_desde,
            'fecha_hasta':self.fecha_hasta,
            'usuario_id':self.usuario_id.name,
            'fecha_corte':fecha_actual,
            'company_id':self.usuario_id.company_id.name,
        }

        lista_alumnos=[]
        cant_alumno=0
        datos=self.consultar()
        lista_datos=datos['lista']
        cant_datos=datos['cant']
        filtro=datos['filtro']
        filtro1=datos['filtro1']

        sheet_info = crear_informe_cobros_automaticos_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "130"
        sheet_view.zoomScaleNormal = "130"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "130"
        crear_informe_cobros_automaticos_excel.Informe(sheet_info, dic,lista_datos)

#-------------------------------------------------------------------------------------------------------------------
#                     CREACION DE PDF                                                                              -
#-------------------------------------------------------------------------------------------------------------------
    @api.multi
    def generar_pdf(self):
        filename_pdf=''
        filename_pdf=''
        fp =io.BytesIO()
        workbook = self.crear_excel_info_pdf()
        workbook.save(fp)
        filename_pdf = 'Informe.xlsx'
        archivo_pdf=base64.b64encode(fp.getvalue())
        obj=self.env['ir.attachment']
        obj_xls=obj.create({'res_model':self.id,'name':filename_pdf,'datas':archivo_pdf,'type':'binary','datas_fname':filename_pdf})
        direccion_xls=obj._get_path(obj_xls.datas)[1]
        direccion=obj._get_path(obj_xls.datas)[0]
        nombre_bin=obj_xls.store_fname
        nombre_archivo=obj_xls.datas_fname
        separa = direccion_xls.rstrip(direccion)
        os.chdir(separa)
        os.rename(nombre_bin,nombre_archivo)
        commands.getoutput(""" libreoffice --headless --convert-to pdf *.xlsx""") 
        with open(direccion_xls.rstrip(direccion)+'/'+nombre_archivo.split('.')[0]+'.pdf', "rb") as f:
            data = f.read()
            file= data.encode("base64")
        self.write({'filename_pdf':nombre_archivo.split('.')[0]+'.pdf','archivo_pdf':file})
        os.rename(nombre_archivo,nombre_bin)
        obj_xls.unlink()
        
        return True

    def crear_excel_info_pdf(self):
        wb = crear_informe_cobros_automaticos_excel.crear_wb_informe()
        self.crear_informe_pdf(wb)
        return wb 

    def crear_informe_pdf(self, wb):
        estado=''
        if self.estado=='0':
            estado='Borrador'
        else:
            estado='Validado'
        now = datetime.now()
        # fecha_a = datetime.strptime(now, '%Y-%m-%d')
        # fecha_actual = datetime.strftime(fecha_a, '%d/%b/%Y')
        dic ={
            'codigo':self.banco_id.bank_bic,
            'banco':self.banco_id.bank_name,
            'met_pago':self.journal_id.name,
            'fecha_creacion':self.fecha_creacion,
            'cuenta_bancaria':self.cuenta_banco,
            'caja':self.account_journal_caja_id.name,
            'fecha_cobro':self.fecha_cobro,
            'estado':estado,
            'company_id':self.usuario_id.company_id.name,
            'usuario_id':self.usuario_id.name,
            'fecha_emision':now
        }

        lista_alumnos=[]
        cant_alumno=0
        datos=self.consultar()
        lista_datos=datos['lista']
        cant_datos=datos['cant']
        sheet_info = crear_informe_cobros_automaticos_excel.crea_hoja_info_pdf(wb, 'Informe ',0)
        #sheet_info = crear_informe_cobranza_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "70"
        sheet_view.zoomScaleNormal = "70"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "70"
        crear_informe_cobros_automaticos_excel.Informe_pdf(sheet_info, dic,lista_datos)