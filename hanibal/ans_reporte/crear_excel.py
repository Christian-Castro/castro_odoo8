# -*- coding: utf-8 -*-
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
from . import crear_informe_excel
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

class ReportProjectInforme(models.Model):
    _inherit = "reporte.escuela"

    @api.multi
    def generar_excel(self):
        fp =io.BytesIO()
        workbook = self.crear_excel_info()
        workbook.save(fp)
        fecha_a = datetime.strptime(self.fecha_emision, '%Y-%m-%d %H:%M:%S')
        fecha_a = fecha_a - timedelta(hours=5)
        fecha_actual = datetime.strftime(fecha_a, '%d-%m-%Y_%H_%M_%S')
        self.filename = 'Informe.xlsx'#'Informe-'+str(fecha_actual)+'.xlsx'
        self.archivo_xls=base64.b64encode(fp.getvalue())      
        return True

    @api.multi
    def generar_pdf(self):
        filename_pdf=''
        filename_pdf=''
        fp =io.BytesIO()
        workbook = self.crear_excel_info_pdf()
        workbook.save(fp)
        fecha_a = datetime.strptime(self.fecha_emision, '%Y-%m-%d %H:%M:%S')
        fecha_a = fecha_a - timedelta(hours=5)
        fecha_actual = datetime.strftime(fecha_a, '%d-%m-%Y_%H_%M_%S')
        filename_pdf = 'Informe.xlsx'#'Informe-'+str(fecha_actual)+'.xlsx'
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
        #self.write({'filename_pdf':filename_pdf,'archivo_pdf':archivo_pdf})
        os.rename(nombre_archivo,nombre_bin)
        obj_xls.unlink()
        
        return True

    def crear_excel_info(self):
        wb = crear_informe_excel.crear_wb_informe()
        self.crear_informe(wb)
        return wb 

    def crear_excel_info_pdf(self):
        wb = crear_informe_excel.crear_wb_informe()
        self.crear_informe_pdf(wb)
        return wb 
    
    @api.multi
    def consultar(self):

        if self.jornada_id:
            if self.seccion_id:
                if self.curso_id:
                    if self.paralelo_id:
                        obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('paralelo_id','=',self.paralelo_id.id),('active','in',(True,False))])
                    else:
                        obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('active','in',(True,False))])
                else:
                    obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('active','in',(True,False))])
            else:
                obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('active','in',(True,False))])
        orden=1
        lista_alumnos=[]
        lista_detalle=[]
        dicc={}
        dicct={}
        direccion=''
        self.cant_estudiante=len(obj_datos)
        for datos in obj_datos:
            dicc={}
            dicct={}
            direccion=''
            if datos.parent_id.street:
                if datos.parent_id.street2:
                    direccion=str(datos.parent_id.street+' '+datos.parent_id.street2)
                else:
                    direccion=datos.parent_id.street
            dicct={
                'orden':orden,
                'codigo':datos.codigo_alumno,
                'alumno':datos.name,
                'representante':datos.parent_id.name,
                'correo':datos.parent_id.email,
                'direccion':direccion,
                'telefono':datos.parent_id.phone,
                'cedula':datos.parent_id.vat,
                'state':'A',
                'jornada_id':datos.jornada_id.id,
                'seccion_id':datos.seccion_id.id,
                'curso_id':datos.curso_id.id,
                'paralelo_id':datos.paralelo_id.id,
            }
            lista_detalle.append(dicct)
            orden=orden+1

        self.env.cr.execute("""delete from reporte_escuela_detalle""")


        obj_detalle=self.env['reporte.escuela.detalle']
        for detalle in lista_detalle:
            obj_detalle.create({
                    'orden':detalle['orden'],
                    'codigo':detalle['codigo'],
                    'alumno':detalle['alumno'],
                    'representante':detalle['representante'],
                    'correo':detalle['correo'],
                    'direccion':detalle['direccion'],
                    'telefono':detalle['telefono'],
                    'cedula':detalle['cedula'],
                    'state':detalle['state'],
                    'reporte_id':self.id,
                    'jornada_id':detalle['jornada_id'],
                    'seccion_id':detalle['seccion_id'],
                    'curso_id':detalle['curso_id'],
                    'paralelo_id':detalle['paralelo_id'],
                })

    def consultar_excel(self):
        if self.jornada_id:
            if self.seccion_id:
                if self.curso_id:
                    if self.paralelo_id:
                        obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('paralelo_id','=',self.paralelo_id.id)])
                    else:
                        obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id)])
                else:
                    obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id)])
            else:
                obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id)])
        orden=1
        lista_alumnos=[]
        lista_detalle=[]
        dicc={}
        dicct={}
        direccion=''
        self.cant_estudiante=len(obj_datos)
        for datos in obj_datos:
            dicc={}
            dicct={}
            direccion=''
            if datos.parent_id.street:
                if datos.parent_id.street2:
                    direccion=str(datos.parent_id.street+' '+datos.parent_id.street2)
                else:
                    direccion=datos.parent_id.street
            dicc={
                'orden':orden,
                'codigo':datos.codigo_alumno,
                'alumno':datos.name,
                'representante':datos.parent_id.name,
                'correo':datos.parent_id.email,
                'direccion':direccion,
                'telefono':datos.parent_id.phone,
                'cedula':datos.parent_id.vat,
                'state':'A',
                'jornada_id':datos.jornada_id.name,
                'seccion_id':datos.seccion_id.name,
                'curso_id':datos.curso_id.name,
                'codigo_curso':datos.curso_id.codigo,
                'paralelo_id':datos.paralelo_id.codigo,
            }
            lista_alumnos.append(dicc)

        cant_alumno=len(lista_alumnos)
        dic_filt={}
        lista_filt=[]
        for lista in lista_alumnos:
            dic_filt={
                'jornada_id':lista['jornada_id'],
                'seccion_id':lista['seccion_id'],
                'curso_id':lista['curso_id'],
                'paralelo_id':lista['paralelo_id'],
            }
            lista_filt.append(dic_filt)

        lista_nueva = []
        for i in lista_filt:
            if i not in lista_nueva:
                lista_nueva.append(i)

        dic_final = {}
        lista_final = []
        dic_final = {}
        lista_final = []
        lista_aux=[]
        lista_total=[]
        for lista_pri in lista_nueva:
            lista_aux=[]
            dic_final = {}
            for lista_sec in lista_alumnos:
                if lista_pri['jornada_id'] == lista_sec['jornada_id'] and lista_pri['seccion_id'] == lista_sec['seccion_id'] and lista_pri['curso_id'] == lista_sec['curso_id'] and lista_pri['paralelo_id'] == lista_sec['paralelo_id']:
                    dic_detalle = {}
                    dic_detalle={
                        'orden':lista_sec['orden'],
                        'codigo':lista_sec['codigo'],
                        'alumno':lista_sec['alumno'],
                        'representante':lista_sec['representante'],
                        'correo':lista_sec['correo'],
                        'direccion':lista_sec['direccion'],
                        'telefono':lista_sec['telefono'],
                        'cedula':lista_sec['cedula'],
                        'state':lista_sec['state'],
                        'jornada_id':lista_sec['jornada_id'],
                        'seccion_id':lista_sec['seccion_id'],
                        'curso_id':lista_sec['curso_id'],
                        'codigo_curso':lista_sec['codigo_curso'],
                        'paralelo_id':lista_sec['paralelo_id'],
                    }
                    lista_aux.append(dic_detalle)
                    dic_final={
                        'jornada_id':lista_sec['jornada_id'],
                        'seccion_id':lista_sec['seccion_id'],
                        'curso_id':lista_sec['curso_id'],
                        'codigo_curso':lista_sec['codigo_curso'],
                        'paralelo_id':lista_sec['paralelo_id'],
                        'lista_detalle':lista_aux,
                    }
                    
            lista_final.append(dic_final)

        datos={
            'lista':lista_final,
            'cant':cant_alumno,
        }

        return datos

    def crear_informe(self, wb):
        self.consultar()
        fecha_a = datetime.strptime(self.fecha_emision, '%Y-%m-%d %H:%M:%S')
        fecha_a = fecha_a - timedelta(hours=5)
        fecha_actual = datetime.strftime(fecha_a, '%d-%m-%Y %H:%M:%S')
        dic ={
            'jornada_id':self.jornada_id.name,
            'seccion_id':self.seccion_id.name,
            'curso_id':self.curso_id.name,
            'curso_codigo':self.curso_id.codigo,
            'paralelo_id':self.paralelo_id.codigo,
            'usuario_id':self.usuario_id.name,
            'company_id':self.usuario_id.company_id.name,
            'fecha':fecha_actual,
        }

        lista_alumnos=[]
        cant_alumno=0
        datos=self.consultar_excel()
        lista_alumnos=datos['lista']
        cant_alumno=datos['cant']

        sheet_info = crear_informe_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "70"
        sheet_view.zoomScaleNormal = "70"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "70"
        crear_informe_excel.Informe(sheet_info, dic,lista_alumnos,cant_alumno)

    def crear_informe_pdf(self, wb):
        self.consultar()
        fecha_a = datetime.strptime(self.fecha_emision, '%Y-%m-%d %H:%M:%S')
        fecha_a = fecha_a - timedelta(hours=5)
        fecha_actual = datetime.strftime(fecha_a, '%d-%m-%Y %H:%M:%S')
        dic ={
            'jornada_id':self.jornada_id.name,
            'seccion_id':self.seccion_id.name,
            'curso_id':self.curso_id.name,
            'curso_codigo':self.curso_id.codigo,
            'paralelo_id':self.paralelo_id.codigo,
            'usuario_id':self.usuario_id.name,
            'company_id':self.usuario_id.company_id.name,
            'fecha':fecha_actual,
        }

        lista_alumnos=[]
        cant_alumno=0
        datos=self.consultar_excel()
        lista_alumnos=datos['lista']
        cant_alumno=datos['cant']
        # contador=0
        # for dat in lista_alumnos:
        #     contador+=1
        #     #cantidad=0

        # cant_hojas=int(contador/5)+1


        sheet_info = crear_informe_excel.crea_hoja_info_pdf(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "70"
        sheet_view.zoomScaleNormal = "70"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "70"
        crear_informe_excel.Informe_pdf(sheet_info, dic,lista_alumnos,cant_alumno)


