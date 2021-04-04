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
from . import crear_informe_cobranza_excel
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
from openerp.tools import ustr, DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.safe_eval import safe_eval

#----------------------------------------------------------
#        Creacion de campos Tipo                          -
#---------------------------------------------------------- 
class account_invoice(models.Model):
    _inherit= "account.journal"

    tipo_reporte = fields.Char(string="Siglas")


#----------------------------------------------------------
#        Creacion de campos para la pantalla              -
#---------------------------------------------------------- 

class ReporteCobranza(models.TransientModel):
    _name = "reporte.cobranza"
    _inherit = "reporte.utileria"
    _rec_name = 'jornada_id'

    fecha_desde = fields.Date(string="Fecha desde")
    fecha_hasta = fields.Date(string="Fecha hasta")
    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    # saldo = fields.Boolean(string="Presentar Saldo",default=False)
    # total = fields.Boolean(string="Presentar Total",default=False)
    # facturas_saldos = fields.Selection( (('S','SI'),
    #                            ('N','NO'),
    #                            ('T','TODAS')),default='T' ,string='Facturas con Saldos')
    #total_grupos = fields.Boolean(string="Total por grupos",default=False)
    journal_ids = fields.Many2many('account.journal',string='Diario')
    usuario_id = fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)

    filename=fields.Char(string="Nombre de archivo")
    archivo_xls=fields.Binary(string='Archivo Excel')
    filename_pdf=fields.Char(string="Nombre de archivo")
    archivo_pdf=fields.Binary(string='Archivo PDF')
    tipo_reporte = fields.Selection(
        string='Tipo De Reporte',
        selection=[
            ('reporte_financiero', 'Informe Financiero'),
            ('reporte_gestion_cobranza', 'Informe Gestión Cobranzas'),
            ('reporte_tutor', 'Informe Tutor Sin Valores'),
            ('reporte_tutor_resumido', 'Informe Tutor Resumido'),
            ('reporte_alumno', 'Resumen Cuentas Por Cobrar'),
            ]
    )
    

    _defaults = {
        'fecha_emision': fields.datetime.now(),
    }

    @api.onchange('jornada_id')
    def onchange_jornada(self):
        for l in self:
            if l.jornada_id:
                l.seccion_id=False
                l.curso_id= False
                l.paralelo_id = False

    @api.onchange('seccion_id')
    def onchange_seccion(self):
        for l in self:
            if l.seccion_id:
                l.curso_id= False
                l.paralelo_id = False

    @api.onchange('curso_id')
    def onchange_curso(self):
        for l in self:
            if l.curso_id:
                l.paralelo_id = False

    def strToDatetime(self, strdate):
        return datetime.strptime(strdate, DEFAULT_SERVER_DATE_FORMAT)


#----------------------------------------------------------
#                     Obtencion de datos                  -
#---------------------------------------------------------- 
    @api.multi
    def consultar(self):
        # lista_id=''
        # if self.journal_ids:
        #     for j in self.journal_ids:
        #         if lista_id!='':
        #             lista_id=lista_id+','+str(j.id)
        #         else:
        #             lista_id=str(j.id)
        # print(lista_id)

        model_invoice = self.env['account.invoice']
        cliente_id = "[('partner_id', '=', %s)]" %(self.cliente_id) if self.cliente_id else "[]"
        alumno_id = "[('alumno_id', '=', %s)]" %(self.alumno_id.id) if self.alumno_id else "[]"
        journal_ids = "[('journal_id', 'in', %s)]" %(self.journal_ids.ids) if self.journal_ids else "[]"

        invoice_ids = model_invoice.search(
            [
                ('type', '=', 'out_invoice'),
            ] + safe_eval(cliente_id)+safe_eval(alumno_id)+safe_eval(journal_ids),
        )

        if 'T' == 'T':
            if self.jornada_id:
                if self.seccion_id:
                    if self.curso_id:
                        if self.paralelo_id:
                            self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} and paralelo_id={5} and id in {6}""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,self.paralelo_id.id, str(tuple(invoice_ids.ids))))
                            lista_facturas=self.env.cr.dictfetchall()
                        else:
                            self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} and id in {5}""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,str(tuple(invoice_ids.ids))))
                            lista_facturas=self.env.cr.dictfetchall()
                    else:
                        self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and seccion_id={3} and id in {4}""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,str(tuple(invoice_ids.ids))))
                        lista_facturas=self.env.cr.dictfetchall()
                else:
                    self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and id in {3}""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,str(tuple(invoice_ids.ids))))
                    lista_facturas=self.env.cr.dictfetchall()
        elif self.facturas_saldos == 'S':
            if self.jornada_id:
                if self.seccion_id:
                    if self.curso_id:
                        if self.paralelo_id:
                            self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and residual is not null and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} and paralelo_id={5} and journal_id in ({6})""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,self.paralelo_id.id,invoice_ids))
                            lista_facturas=self.env.cr.dictfetchall()
                        else:
                            self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and residual is not null and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} and journal_id in ({5})""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,invoice_ids))
                            lista_facturas=self.env.cr.dictfetchall()
                    else:
                        self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and residual is not null and
                                    jornada_id={2} and seccion_id={3} and journal_id in ({4})""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,invoice_ids))
                        lista_facturas=self.env.cr.dictfetchall()
                else:
                    self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and residual is not null and
                                    jornada_id={2} and journal_id in ({3})""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,invoice_ids))
                    lista_facturas=self.env.cr.dictfetchall()
        elif self.facturas_saldos == 'N':
            if self.jornada_id:
                if self.seccion_id:
                    if self.curso_id:
                        if self.paralelo_id:
                            self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and residual is null and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} and paralelo_id={5} and journal_id in ({6})""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,self.paralelo_id.id,invoice_ids))
                            lista_facturas=self.env.cr.dictfetchall()
                        else:
                            self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and residual is NULL and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} and journal_id in ({5})""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,invoice_ids))
                            lista_facturas=self.env.cr.dictfetchall()
                    else:
                        self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and residual is null and
                                    jornada_id={2} and seccion_id={3} and journal_id in ({4})""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,invoice_ids))
                        lista_facturas=self.env.cr.dictfetchall()
                else:
                    self.env.cr.execute("""SELECT id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and residual is null and
                                    jornada_id={2} and journal_id in ({3})""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,invoice_ids))
                    lista_facturas=self.env.cr.dictfetchall()


        lista_facturas_id = [value['id'] for value in lista_facturas]
        obj_datos=self.env['account.invoice'].search([('id','in',lista_facturas_id)],order='jornada_id')
        dic = {}
        lista_datos = []
        descripcion = ''
        for l in obj_datos:
            descripcion = ''
            for det in l.invoice_line:
                descripcion = descripcion+' '+det.name
            objDate = datetime.strptime(l.date_invoice, '%Y-%m-%d')
            fecha_emision = datetime.strftime(objDate, '%d/%m/%Y')

            dic = {
            'tipo':l.journal_id.tipo_reporte,
            "codigo_alumno": l.alumno_id.codigo_alumno,
            'numero':l.numerofac,
            'emision':fecha_emision,
            "vencimiento": l.date_due,
            "dias_mora": (datetime.now() - self.strToDatetime(l.date_due)).days,
            'alumno':l.alumno_id.name,
            'jornada':l.jornada_id.name,
            'seccion':l.seccion_id.name,
            'curso':l.curso_id.name,
            'paralelo':l.paralelo_id.codigo,
            'saldo':l.residual,
            'total':l.amount_total,
            "pagos": sum(line.credit for line in (l.filtered(
                        lambda diario: diario.journal_id.cheques_postfechados == False)).payment_ids),
            "cheques_postfechados": sum(line.credit for line in (l.filtered(
                        lambda diario: diario.journal_id.cheques_postfechados == True)).payment_ids),
            'comentario':descripcion
            }
            lista_datos.append(dic)
            dic = {}
        #-------------------------------------------------------------------------------------------------------------------
        #                     AGRUPAR LAS CABECERAS                                                                        -
        #  SE AGRUPA LAS JORNADAS,SECCION,CURSO,PARALELO PARA TENER UNA SOLA LISTA DE TODAS SI DUPLICADOS                  -
        #-------------------------------------------------------------------------------------------------------------------
        lista_cabecera=[]
        dic_cab={}
        for m in lista_datos:
            dic_cab={
            'jornada':m['jornada'],
            'seccion':m['seccion'],
            'curso':m['curso'],
            'paralelo':m['paralelo'],
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
            'jornada':n['jornada'],
            'seccion':n['seccion'],
            'curso':n['curso'],
            'paralelo':n['paralelo'],
            }
            detalle={}
            lista_detalle=[]
            for deta in lista_datos:
                if deta['jornada'] == n['jornada'] and deta['seccion'] == n['seccion'] and deta['curso'] == n['curso'] and deta['paralelo'] == n['paralelo']:
                    detalle={
                    'tipo':deta['tipo'],
                    "codigo_alumno": deta["codigo_alumno"],
                    "vencimiento": deta["vencimiento"],
                    "dias_mora": deta["dias_mora"],
                    "pagos": deta["pagos"],
                    "cheques_postfechados": deta["cheques_postfechados"],
                    'numero':deta['numero'],
                    'emision':deta['emision'],
                    'alumno':deta['alumno'],
                    'comentario':deta['comentario'],
                    'saldo':deta['saldo'],
                    'total':deta['total'],
                    }
                    lista_detalle.append(detalle)
            dic_det={
            'jornada':n['jornada'],
            'seccion':n['seccion'],
            'curso':n['curso'],
            'paralelo':n['paralelo'],
            'detalle':lista_detalle,
            }
            lista_completa.append(dic_det)

        for d in lista_completa:
            print(d['jornada'],'   ',d['seccion'],'   ',d['curso'],'     ',d['paralelo'],'     ',len(d['detalle']))

        datos={
            'lista':lista_completa,
            'cant':len(obj_datos),
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
        self.archivo_xls = base64.b64encode(fp.getvalue())
        return True

    def crear_excel_info(self):
        wb = crear_informe_cobranza_excel.crear_wb_informe()
        self.crear_informe(wb)
        return wb 


    def crear_informe(self, wb):
        fecha_a = datetime.strptime(self.fecha_hasta, '%Y-%m-%d')
        fecha_actual = datetime.strftime(fecha_a, '%d/%b/%Y')
        dic ={
            'jornada_id':self.jornada_id.name,
            'seccion_id':self.seccion_id.name,
            'curso_id':self.curso_id.name,
            'curso_codigo':self.curso_id.codigo,
            'paralelo_id':self.paralelo_id.codigo,
            'usuario_id':self.usuario_id.name,
            'fecha_corte':fecha_actual,
            #'fecha':fecha_actual,
        }

        datos=self.consultar()
        lista_datos=datos['lista']
        cant_datos=datos['cant']

        sheet_info = crear_informe_cobranza_excel.crea_hoja_info_pdf(wb, 'Informe ',0)
        # sheet_view = openpyxl.worksheet.views.SheetView()
        # sheet_view.zoomScale = "70"
        # sheet_view.zoomScaleNormal = "70"
        # sheet_info.sheet_view = sheet_view
        # sheet_info.zoomScale = "70"
        crear_informe_cobranza_excel.Informe_financiero(sheet_info, dic,lista_datos, cant_datos, self.saldo, self.total)

#-------------------------------------------------------------------------------------------------------------------
#                     CREACION DE PDF                                                                              -
#-------------------------------------------------------------------------------------------------------------------
    @api.multi
    def generar_pdf(self):
        filename_pdf=''
        filename_pdf=''
        fp = io.BytesIO()
        workbook = self.crear_excel_info_pdf()
        workbook.save(fp)
        filename_pdf = 'Informe.xlsx'
        archivo_pdf = base64.b64encode(fp.getvalue())
        obj=self.env['ir.attachment']
        obj_xls = obj.create({'res_model':self.id,'name':filename_pdf,'datas':archivo_pdf,'type':'binary','datas_fname':filename_pdf})
        direccion_xls = obj._get_path(obj_xls.datas)[1]
        direccion = obj._get_path(obj_xls.datas)[0]
        nombre_bin = obj_xls.store_fname
        nombre_archivo = obj_xls.datas_fname
        separa = direccion_xls.rstrip(direccion)
        # separa = "/home/rrojas/.local/share/Odoo/filestore/ans_escuela_01-12-2020"
        os.chdir(separa)
        os.rename(nombre_bin,nombre_archivo)
        commands.getoutput(""" libreoffice --headless --convert-to pdf *.xlsx""") 
        with open(separa+'/'+nombre_archivo.split('.')[0]+'.pdf', "rb") as f:
            data = f.read()
            file= data.encode("base64")
        self.write({'filename_pdf': nombre_archivo.split('.')[0]+'.pdf','archivo_pdf': file})
        os.rename(nombre_archivo,nombre_bin)
        obj_xls.unlink()
        
        return True

    def crear_excel_info_pdf(self):
        wb = crear_informe_cobranza_excel.crear_wb_informe()
        self.crear_informe_pdf(wb)
        return wb 

    def crear_informe_pdf(self, wb):
        fecha_a = datetime.strptime(self.fecha_hasta, '%Y-%m-%d')
        fecha_actual = datetime.strftime(fecha_a, '%d/%b/%Y')
        dic ={
            'jornada_id':self.jornada_id.name,
            'seccion_id':self.seccion_id.name,
            'curso_id':self.curso_id.name,
            'curso_codigo':self.curso_id.codigo,
            'paralelo_id':self.paralelo_id.codigo,
            'usuario_id':self.usuario_id.name,
            'fecha_corte':fecha_actual,
        }

        datos=self.consultar()
        lista_datos=datos['lista']
        cant_datos=datos['cant']
        sheet_info = crear_informe_cobranza_excel.crea_hoja_info_pdf(wb, 'Informe ',0)
        # sheet_info = crear_informe_cobranza_excel.crea_hoja_info(wb, 'Informe ',0)
        # sheet_view = openpyxl.worksheet.views.SheetView()
        # sheet_view.zoomScale = "70"
        # sheet_view.zoomScaleNormal = "70"
        # sheet_info.sheet_view = sheet_view
        # sheet_info.zoomScale = "70"
        crear_informe_cobranza_excel.Informe_financiero(sheet_info, dic, lista_datos, cant_datos, self.saldo, self.total)
    
    ##Archivos tutor
    @api.multi
    def generar_excel_tutor(self):
        fp = io.BytesIO()
        workbook = self.crear_excel_info_tutor()
        workbook.save(fp)
        return self.download_file(fp, 'Informe Tutor.xlsx')
    
    @api.multi
    def generar_pdf_tutor(self):
        fp = io.BytesIO()
        workbook = self.crear_excel_info_tutor()
        workbook.save(fp)
        return self.download_file(fp, 'Informe Tutor.xlsx', True)

    def crear_excel_info_tutor(self):
        wb = crear_informe_cobranza_excel.crear_wb_informe()
        self.crear_informe_tutor_xlsx(wb)
        return wb

    def crear_informe_tutor_xlsx(self, wb):
        fecha_a = datetime.strptime(self.fecha_hasta, '%Y-%m-%d')
        fecha_actual = datetime.strftime(fecha_a, '%d/%b/%Y')
        dic = {
            'jornada_id':self.jornada_id.name,
            'seccion_id':self.seccion_id.name,
            'curso_id':self.curso_id.name,
            'curso_codigo':self.curso_id.codigo,
            'paralelo_id':self.paralelo_id.codigo,
            'usuario_id':self.usuario_id.name,
            'fecha_corte':fecha_actual,
        }

        datos = self.consultar()
        lista_datos = datos['lista']
        cant_datos = datos['cant']
        sheet_info = crear_informe_cobranza_excel.crea_hoja_info_pdf(wb, 'Informe Tutor', 0, True)
        crear_informe_cobranza_excel.Informe_financiero(sheet_info, dic, lista_datos, cant_datos, 0, 0, True)#self.saldo, self.total, True)
    