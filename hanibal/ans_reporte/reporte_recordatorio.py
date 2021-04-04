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
from . import crear_informe_recordatorio_excel
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

class Reporte_recordatorio(models.Model):
    _inherit= "recordatorio"

    filename=fields.Char(string="Nombre de archivo")
    archivo_xls=fields.Binary(string='Archivo Excel')
    filename_pdf=fields.Char(string="Nombre de archivo")
    archivo_pdf=fields.Binary(string='Archivo PDF')
    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)


#----------------------------------------------------------
#                     Obtencion de datos                  -
#---------------------------------------------------------- 
    @api.multi
    def consultar(self):
        lista_datos=[]
        orden=0
        for l in self.recordatorio_detalle:
            orden=orden+1
            dic={
            'orden':orden,
            'sequence':self.sequence,
            'descripcion':l.descripcion,
            'jornada':l.jornada_id.name,
            'seccion':l.seccion_id.name,
            'curso':l.curso_id.name,
            'paralelo':l.paralelo_id.codigo,
            'alumno':l.alumno_id.name,
            'representante':l.representante_id.name,
            'correo':l.correo_repres,
            'numero_factura':l.factura_id.numerofac,
            'fecha_factura':l.fecha_factura,
            'concepto':l.concepto,
            'monto':l.monto,
            'saldo':l.saldo,
            'notificaciones':l.cant_notificacion,
            'fecha_envio_correo':l.fecha_envio_correo
            }
            lista_datos.append(dic)

        

        datos={
            'lista':lista_datos,
            'cant':len(self.recordatorio_detalle),
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
        ahora = datetime.now()
        dia=ahora.day
        mes=ahora.month
        anio=ahora.year
        self.filename = 'Recordatorio_%s_%s_%s.xlsx' % (str(dia),str(mes),str(anio))
        self.archivo_xls=base64.b64encode(fp.getvalue())      
        return True

    def crear_excel_info(self):
        wb = crear_informe_recordatorio_excel.crear_wb_informe()
        self.crear_informe(wb)
        return wb 


    def crear_informe(self, wb):
        now = datetime.now()
        dic ={
            'fecha_desde':self.fecha_desde,
            'fecha_hasta':self.fecha_hasta,
            'company_id':self.usuario_id.company_id.name,
            'usuario_id':self.usuario_id.name,
            'fecha_emision':now,
            'jornada':self.jornada_id.name,
            'seccion':self.seccion_id.name,
            'curso':self.curso_id.name,
            'paralelo':self.paralelo_id.codigo,
            'representante': self.representante_id.name,
            'alumno': self.alumno_id.name
        }

        lista_alumnos=[]
        cant_alumno=0
        datos=self.consultar()
        lista_datos=datos['lista']
        cant_datos=datos['cant']
        sheet_info = crear_informe_recordatorio_excel.crea_hoja_info(wb, 'Recordatorio ',0)
        #sheet_info = crear_informe_cobranza_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "130"
        sheet_view.zoomScaleNormal = "130"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "130"
        crear_informe_recordatorio_excel.Informe(sheet_info, dic,lista_datos)

#-------------------------------------------------------------------------------------------------------------------
#                     CREACION DE PDF                                                                              -
#-------------------------------------------------------------------------------------------------------------------
    @api.multi
    def generar_pdf(self):
        filename_pdf=''
        fp =io.BytesIO()
        workbook = self.crear_excel_info_pdf()
        workbook.save(fp)
        ahora = datetime.now()
        dia=ahora.day
        mes=ahora.month
        anio=ahora.year
        filename_pdf = 'Recordatorio_%s_%s_%s.xlsx' % (str(dia),str(mes),str(anio))
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
        wb = crear_informe_recordatorio_excel.crear_wb_informe()
        self.crear_informe_pdf(wb)
        return wb 

    def crear_informe_pdf(self, wb):
        now = datetime.now()
        # fecha_a = datetime.strptime(now, '%Y-%m-%d')
        # fecha_actual = datetime.strftime(fecha_a, '%d/%b/%Y')
        dic ={
            'fecha_desde':self.fecha_desde,
            'fecha_hasta':self.fecha_hasta,
            'company_id':self.usuario_id.company_id.name,
            'usuario_id':self.usuario_id.name,
            'fecha_emision':now,
            'jornada':self.jornada_id.name,
            'seccion':self.seccion_id.name,
            'curso':self.curso_id.name,
            'paralelo':self.paralelo_id.codigo,
            'representante': self.representante_id.name,
            'alumno': self.alumno_id.name
        }

        lista_alumnos=[]
        cant_alumno=0
        datos=self.consultar()
        lista_datos=datos['lista']
        cant_datos=datos['cant']
        sheet_info = crear_informe_recordatorio_excel.crea_hoja_info_pdf(wb, 'Recordatorio ',0)
        #sheet_info = crear_informe_cobranza_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "50"
        sheet_view.zoomScaleNormal = "50"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "50"
        crear_informe_recordatorio_excel.Informe_pdf(sheet_info, dic,lista_datos)