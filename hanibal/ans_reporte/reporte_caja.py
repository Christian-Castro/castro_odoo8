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
from . import crear_informe_caja_excel
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

class ReporteCaja(models.TransientModel):
    _name="reporte.caja"
    _rec_name = 'titulo'

    titulo=fields.Char(string="Titulo",default='Reporte de Caja')
    fecha_desde = fields.Date(string="Fecha desde")
    fecha_hasta = fields.Date(string="Fecha hasta")
    journal_ids=fields.Many2many('account.journal',string='Caja')
    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)
    fecha_emision = fields.Date(string="Fecha Emision")

    filename=fields.Char(string="Nombre de archivo")
    archivo_xls=fields.Binary(string='Archivo Excel')
    filename_pdf=fields.Char(string="Nombre de archivo")
    archivo_pdf=fields.Binary(string='Archivo PDF')

    _defaults = {
        'fecha_emision': fields.datetime.now(),
    }


#----------------------------------------------------------
#                     Obtencion de datos                  -
#---------------------------------------------------------- 
    @api.multi
    def consultar(self):
        lista_id=''
        if self.fecha_desde and self.fecha_hasta and self.journal_ids:
            for j in self.journal_ids:
                if lista_id!='':
                    lista_id=lista_id+','+str(j.id)
                else:
                    lista_id=str(j.id)
            sql="""SELECT id from account_voucher where date between '{0}' AND '{1}' and account_journal_caja_id in ({2}) and state in ('posted')  order by id,date,number asc""".format(self.fecha_desde,self.fecha_hasta,lista_id)
        self.env.cr.execute(sql)
        lista_facturas=self.env.cr.dictfetchall()
        lista_facturas_id = [value['id'] for value in lista_facturas]
        obj_datos=self.env['account.voucher'].search([('id','in',lista_facturas_id)])
        dic={}
        lista_datos=[]
        descripcion=''
        for l in obj_datos:
            for det in l.line_cr_ids:
                dic={}
                if det.amount!=0.0:
                    obj_move_line=self.env['account.move.line'].search([('id','=',det.move_line_id.id)])
                    obj_invoice=self.env['account.invoice'].search([('number','=',obj_move_line.ref)])
                    dic={
                    'tipo':l.account_journal_caja_id.categoria_reporte,
                    'numero':l.number,
                    'fecha_pago':l.date,
                    #INTEGRACION: SE CAMBIA POR PEDIDO DE CAMBIO DE NUMERO
                    #'factura':obj_invoice.number,
                    'factura':obj_invoice.numerofac,
                    'monto':det.amount,
                    'cliente':obj_invoice.alumno_id.name,
                    'banco':l.banco_id.name,
                    'documento':l.documento,
                    'fecha_ch':l.fecha_ch,
                    'comentario':l.narration
                    }
                    lista_datos.append(dic)
            
        lista_tipo=[]
        for tipos in lista_datos:
            if tipos['tipo'] not in lista_tipo:
                lista_tipo.append(tipos['tipo'])

        #-------------------------------------------------------------------------------------------------------------------
        #                     AGRUPAR LAS CABECERAS                                                                        -
        #  SE AGRUPA LAS JORNADAS,SECCION,CURSO,PARALELO PARA TENER UNA SOLA LISTA DE TODAS SI DUPLICADOS                  -
        #-------------------------------------------------------------------------------------------------------------------
        lista_cabecera=[]
        dic_cab={}
        for m in lista_datos:
            dic_cab={
            'tipo':m['tipo'],
            }
            if dic_cab not in lista_cabecera:
                lista_cabecera.append(dic_cab)


        #-------------------------------------------------------------------------------------------------------------------
        #                     AGRUPAR LAS CABECERAS Y DETALLE                                                              -
        #  CON LA CABECERAS AGRUPADAS SOLO SE LES AGREGA UNA LISTA CON LOS DETALLES DE LOS ALUMNOS                         -
        #-------------------------------------------------------------------------------------------------------------------
        lista_completa=[]
        for n in lista_cabecera:
            dic_cab={
            'tipo':n['tipo'],
            }
            detalle={}
            lista_detalle=[]
            for deta in lista_datos:
                if deta['tipo'] == n['tipo']:
                    detalle={
                    'numero':deta['numero'],
                    'fecha_pago':deta['fecha_pago'],
                    'factura':deta['factura'],
                    'monto':deta['monto'],
                    'cliente':deta['cliente'],
                    'banco':deta['banco'],
                    'documento':deta['documento'],
                    'fecha_ch':deta['fecha_ch'],
                    'comentario':deta['comentario'],
                    }
                    lista_detalle.append(detalle)
            lista_detalle_ordenada=sorted(lista_detalle, key = lambda user: user['numero'])

            dic_det={
            'tipo':n['tipo'],
            'detalle':lista_detalle_ordenada,
            }
            lista_completa.append(dic_det)

        cadena=''
        for fil in self.journal_ids:
            obj_move_line=self.env['account.journal'].search([('id','=',fil.id)])
            if cadena=='':
                cadena=obj_move_line.name
            else:
                cadena=cadena+' ,'+obj_move_line.name

        datos={
            'lista':lista_completa,
            'cant':len(obj_datos),
            'filtro':cadena,
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
        wb = crear_informe_caja_excel.crear_wb_informe()
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

        sheet_info = crear_informe_caja_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "130"
        sheet_view.zoomScaleNormal = "130"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "130"
        crear_informe_caja_excel.Informe(sheet_info, dic,lista_datos,cant_datos,filtro)

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
        wb = crear_informe_caja_excel.crear_wb_informe()
        self.crear_informe_pdf(wb)
        return wb 

    def crear_informe_pdf(self, wb):
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
        sheet_info = crear_informe_caja_excel.crea_hoja_info_pdf(wb, 'Informe ',0)
        #sheet_info = crear_informe_cobranza_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "70"
        sheet_view.zoomScaleNormal = "70"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "70"
        crear_informe_caja_excel.Informe_pdf(sheet_info, dic,lista_datos,cant_datos,filtro)