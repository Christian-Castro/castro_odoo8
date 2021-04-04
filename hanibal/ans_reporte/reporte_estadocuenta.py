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
from . import crear_informe_estadocuenta_excel
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
#        Creacion de campos Tipo                          -
#---------------------------------------------------------- 
class account_invoice(models.Model):
    _inherit= "res.partner"

    status = fields.Boolean(string="Estado",default=True)

#----------------------------------------------------------
#        Creacion de campos para la pantalla              -
#---------------------------------------------------------- 

class ReporteEstadoCuenta(models.TransientModel):
    _name="reporte.estadocuenta"
    _rec_name = 'jornada_id'

    fecha_desde = fields.Date(string="Fecha desde")
    fecha_hasta = fields.Date(string="Fecha hasta")
    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)
    alumno_id = fields.Many2one('res.partner',string="Alumno")
    filename=fields.Char(string="Nombre de archivo")
    archivo_xls=fields.Binary(string='Archivo Excel')
    filename_pdf=fields.Char(string="Nombre de archivo")
    archivo_pdf=fields.Binary(string='Archivo PDF')
    fecha_emision= fields.Datetime('Fecha', readonly=True, copy=False,select=True,)

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


#----------------------------------------------------------
#                     Obtencion de datos                  -
#---------------------------------------------------------- 
    @api.multi
    def consultar(self):
        lista_facturas=[]
        if self.alumno_id:
            if self.jornada_id:
                if self.seccion_id:
                    if self.curso_id:
                        if self.paralelo_id:
                            sql="""SELECT id,alumno_id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} and paralelo_id={5} and alumno_id={6} order by id""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,self.paralelo_id.id,self.alumno_id.id)
                        else:
                            sql="""SELECT id,alumno_id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} and alumno_id={5} order by id""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,self.alumno_id.id)
                    else:
                        sql="""SELECT id,alumno_id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and seccion_id={3} and alumno_id={4} order by id""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.alumno_id.id)
                else:
                    sql="""SELECT id,alumno_id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and alumno_id={3} order by id""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.alumno_id.id)
        else:
            if self.jornada_id:
                if self.seccion_id:
                    if self.curso_id:
                        if self.paralelo_id:
                            sql="""SELECT id,alumno_id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} and paralelo_id={5} order by id""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,self.paralelo_id.id)
                        else:
                            sql="""SELECT id,alumno_id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and seccion_id={3} and curso_id={4} order by id""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id,self.curso_id.id)
                    else:
                        sql="""SELECT id,alumno_id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} and seccion_id={3} order by id""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id,self.seccion_id.id)
                else:
                    sql="""SELECT id,alumno_id from account_invoice where date_invoice between '{0}' AND '{1}' and escuela=True and state in ('open','paid') and
                                    jornada_id={2} order by id""".format(self.fecha_desde,self.fecha_hasta,self.jornada_id.id)

        self.env.cr.execute(sql)
        lista_facturas=self.env.cr.dictfetchall()

        lista_facturas_id = [value['id'] for value in lista_facturas]
        lista_alumno_id = [value['alumno_id'] for value in lista_facturas]
        if len(lista_facturas_id)==0:
            datos={
            'lista':[],
            'cant':0,
            }
            return datos

        # Lista de alumnos sin repetidos
        filtrar_alumnos=[]
        for lis_a in lista_alumno_id:
            if lis_a:
                if lis_a not in filtrar_alumnos:
                    filtrar_alumnos.append(lis_a)
        concantena_id=''
        for j in filtrar_alumnos:
            if concantena_id!='':
                concantena_id=concantena_id+','+str(j)
            else:
                concantena_id=str(j)
        sql_1=''
        if self.jornada_id:
            if self.seccion_id:
                if self.curso_id:
                    if self.paralelo_id:
                        sql_1="""SELECT id,alumno_id from account_invoice where date_invoice<'{0}' and alumno_id in ({1}) and escuela=True and state in ('open','paid') and
                                jornada_id={2} and seccion_id={3} and curso_id={4} and paralelo_id={5} order by id""".format(self.fecha_desde,concantena_id,self.jornada_id.id,self.seccion_id.id,self.curso_id.id,self.paralelo_id.id)
                    else:
                        sql_1="""SELECT id,alumno_id from account_invoice where date_invoice<'{0}' and alumno_id in ({1}) and escuela=True and state in ('open','paid') and
                                jornada_id={2} and seccion_id={3} and curso_id={4} order by id""".format(self.fecha_desde,concantena_id,self.jornada_id.id,self.seccion_id.id,self.curso_id.id)
                else:
                    sql_1="""SELECT id,alumno_id from account_invoice where date_invoice <'{0}' and alumno_id in ({1}) and escuela=True and state in ('open','paid') and
                                jornada_id={2} and seccion_id={3} order by id""".format(self.fecha_desde,concantena_id,self.jornada_id.id,self.seccion_id.id)
            else:
                sql_1="""SELECT id,alumno_id from account_invoice where date_invoice<'{0}' and alumno_id in ({1}) and escuela=True and state in ('open','paid') and
                                jornada_id={2} order by id""".format(self.fecha_desde,concantena_id,self.jornada_id.id)


        self.env.cr.execute(sql_1)
        lista_facturas_antes=self.env.cr.dictfetchall()
        lista_facturas_antes_id = [value['id'] for value in lista_facturas_antes]
        lista_alumnos_saldos=[]
        for alum_a in filtrar_alumnos:
            obj_facturas_antes=self.env['account.invoice'].search([('id','in',lista_facturas_antes_id),('alumno_id','=',alum_a)],order='alumno_id')
            saldos=0.0
            for d in obj_facturas_antes:
                saldos=saldos+d.residual
            dic_antes={
                'alumno_id':alum_a,
                'cargos':saldos,
            }
            lista_alumnos_saldos.append(dic_antes)


        obj_datos=self.env['account.invoice'].search([('id','in',lista_facturas_id)],order='alumno_id')
        dic={}
        lista_datos=[]
        descripcion=''
        for l in obj_datos:
            objDate = datetime.strptime(l.date_invoice, '%Y-%m-%d')
            fecha_emision = datetime.strftime(objDate, '%d/%m/%Y')
            movil=''
            celular=''
            if l.alumno_id.parent_id.phone:
                celular=l.alumno_id.parent_id.phone
            if l.alumno_id.parent_id.mobile:
                movil=l.alumno_id.parent_id.mobile
            telefono=str(celular+'-'+movil)
            cargo=0.0
            for al in lista_alumnos_saldos:
                if l.alumno_id.id==al['alumno_id']:
                    cargo=al['cargos']
            direccion=''
            if l.alumno_id.parent_id.street:
                if l.alumno_id.parent_id.street2:
                    direccion=str(l.alumno_id.parent_id.street+' '+l.alumno_id.parent_id.street2)
                else:
                    direccion=l.alumno_id.parent_id.street
            status=''
            if l.alumno_id.status:
                status='A'
            else:
                status='I'
            comentarios=''
            if l.comment==False:
                comentarios=''
            alumnos=''
            if l.alumno_id.name:
                alumnos=str('('+l.alumno_id.codigo_alumno.encode('utf-8')+' ) '+l.alumno_id.name.encode('utf-8'))

            dic={
            'tipo':l.journal_id.tipo_reporte,
            #INTEGRACION: SE CAMBIA POR PEDIDO DE CAMBIO DE NUMERO
            #'numero':l.number,
            'numero':l.numerofac,
            'emision':fecha_emision,
            'status':status,
            'alumno':alumnos,
            'representante':l.alumno_id.parent_id.name,
            'direccion':direccion,
            'cedula':l.alumno_id.parent_id.vat,
            'telefono':telefono,
            'jornada':l.jornada_id.name,
            'seccion':l.seccion_id.name,
            'curso':l.curso_id.name,
            'paralelo':l.paralelo_id.codigo,
            'cargos':l.amount_total,
            'total':0.0,
            'comentario':comentarios,
            'cargo':cargo
            }
            lista_datos.append(dic)
            for pag in l.payment_ids:
                objDates = datetime.strptime(pag.date, '%Y-%m-%d')
                fecha = datetime.strftime(objDates, '%d/%m/%Y')
                pagos=self.env['account.voucher'].search([('date','=',pag.date),('journal_id','=',pag.journal_id.id)])
                numero=''
                comentario=''
                for d in pagos:
                    numer=str(d.number).replace('/','')
                    if numer==pag.ref:
                        numero=d.number
                        if d.narration!=False:
                            comentario=d.narration
                        break
                dic={
                'tipo':pag.journal_id.tipo_reporte,
                'numero':numero,
                'emision':fecha,
                'status':status,
                'alumno':l.alumno_id.name,
                'representante':l.alumno_id.parent_id.name,
                'direccion':direccion,
                'cedula':l.alumno_id.parent_id.vat,
                'telefono':telefono,
                'jornada':l.jornada_id.name,
                'seccion':l.seccion_id.name,
                'curso':l.curso_id.name,
                'paralelo':l.paralelo_id.codigo,
                'cargos':0.0,
                'total':pag.credit,
                'comentario':comentario,
                'cargo':cargo
                }
                lista_datos.append(dic)
                dic={}

            dic={}
        #-------------------------------------------------------------------------------------------------------------------
        #                     AGRUPAR LAS CABECERAS                                                                        -
        #  SE AGRUPA LAS JORNADAS,SECCION,CURSO,PARALELO PARA TENER UNA SOLA LISTA DE TODAS SI DUPLICADOS                  -
        #-------------------------------------------------------------------------------------------------------------------
        lista_cabecera=[]
        dic_cab={}
        for m in lista_datos:
            dic_cab={
            'alumno':m['alumno'],
            'representante':m['representante'],
            'direccion':m['direccion'],
            'telefono':m['telefono'],
            'cedula':m['cedula'],
            'jornada':m['jornada'],
            'seccion':m['seccion'],
            'curso':m['curso'],
            'paralelo':m['paralelo'],
            'status':m['status'],
            }
            if dic_cab not in lista_cabecera:
                lista_cabecera.append(dic_cab)
        #-------------------------------------------------------------------------------------------------------------------
        #                     AGRUPAR LAS CABECERAS Y DETALLE                                                              -
        #  CON LA CABECERAS AGRUPADAS SOLO SE LES AGREGA UNA LISTA CON LOS DETALLES DE LOS ALUMNOS                         -
        #-------------------------------------------------------------------------------------------------------------------
        lista_completa=[]
        for n in lista_cabecera:
            
            detalle={}
            lista_detalle=[]
            for deta in lista_datos:
                if deta['jornada'] == n['jornada'] and deta['seccion'] == n['seccion'] and deta['curso'] == n['curso'] and deta['paralelo'] == n['paralelo'] and deta['alumno'] == n['alumno'] and deta['representante'] == n['representante'] and deta['direccion'] == n['direccion'] and deta['telefono'] == n['telefono'] and deta['cedula'] == n['cedula']:
                    detalle={
                    'tipo':deta['tipo'],
                    'numero':deta['numero'],
                    'emision':deta['emision'],
                    'comentario':deta['comentario'],
                    'cargos':deta['cargos'],
                    'total':deta['total'],
                    }
                    lista_detalle.append(detalle)
            dic_det={
            'alumno':n['alumno'],
            'representante':n['representante'],
            'direccion':n['direccion'],
            'telefono':n['telefono'],
            'cedula':n['cedula'],
            'jornada':n['jornada'],
            'seccion':n['seccion'],
            'curso':n['curso'],
            'paralelo':n['paralelo'],
            'cargo':deta['cargo'],
            'status':n['status'],
            'detalle':lista_detalle,
            }
            lista_completa.append(dic_det)

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
        self.archivo_xls=base64.b64encode(fp.getvalue())      
        return True

    def crear_excel_info(self):
        wb = crear_informe_estadocuenta_excel.crear_wb_informe()
        self.crear_informe(wb)
        return wb 


    def crear_informe(self, wb):
        fecha_a = datetime.strptime(self.fecha_emision, '%Y-%m-%d %H:%M:%S')
        fecha_a = fecha_a - timedelta(hours=5)
        fecha_actual = datetime.strftime(fecha_a, '%d/%m/%Y %H:%M:%S')
        fecha_d = datetime.strptime(self.fecha_desde, '%Y-%m-%d')
        fecha_desde = datetime.strftime(fecha_d, '%d/%b/%Y')
        fecha_h = datetime.strptime(self.fecha_hasta, '%Y-%m-%d')
        fecha_hasta = datetime.strftime(fecha_h, '%d/%b/%Y')
        dic ={
            'jornada_id':self.jornada_id.name,
            'seccion_id':self.seccion_id.name,
            'curso_id':self.curso_id.name,
            'curso_codigo':self.curso_id.codigo,
            'paralelo_id':self.paralelo_id.codigo,
            'usuario_id':self.usuario_id.name,
            'fecha_corte':fecha_actual,
            'fecha_desde':fecha_desde,
            'fecha_hasta':fecha_hasta,
            'company_id':self.usuario_id.company_id.name,
            #'fecha':fecha_actual,
        }

        lista_alumnos=[]
        cant_alumno=0
        datos=self.consultar()
        lista_datos=datos['lista']
        cant_datos=datos['cant']

        sheet_info = crear_informe_estadocuenta_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "100"
        sheet_view.zoomScaleNormal = "100"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "100"
        crear_informe_estadocuenta_excel.Informe(sheet_info, dic,lista_datos,cant_datos)

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
        wb = crear_informe_estadocuenta_excel.crear_wb_informe()
        self.crear_informe_pdf(wb)
        return wb 

    def crear_informe_pdf(self, wb):
        fecha_a = datetime.strptime(self.fecha_emision, '%Y-%m-%d %H:%M:%S')
        fecha_a = fecha_a - timedelta(hours=5)
        fecha_actual = datetime.strftime(fecha_a, '%d/%m/%Y %H:%M:%S')
        fecha_d = datetime.strptime(self.fecha_desde, '%Y-%m-%d')
        fecha_desde = datetime.strftime(fecha_d, '%d/%b/%Y')
        fecha_h = datetime.strptime(self.fecha_hasta, '%Y-%m-%d')
        fecha_hasta = datetime.strftime(fecha_h, '%d/%b/%Y')
        dic ={
            'jornada_id':self.jornada_id.name,
            'seccion_id':self.seccion_id.name,
            'curso_id':self.curso_id.name,
            'curso_codigo':self.curso_id.codigo,
            'paralelo_id':self.paralelo_id.codigo,
            'usuario_id':self.usuario_id.name,
            'fecha_corte':fecha_actual,
            'fecha_desde':fecha_desde,
            'fecha_hasta':fecha_hasta,
            'company_id':self.usuario_id.company_id.name,
            #'fecha':fecha_actual,
        }

        lista_alumnos=[]
        cant_alumno=0
        datos=self.consultar()
        lista_datos=datos['lista']
        cant_datos=datos['cant']
        sheet_info = crear_informe_estadocuenta_excel.crea_hoja_info_pdf(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "70"
        sheet_view.zoomScaleNormal = "70"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "70"
        crear_informe_estadocuenta_excel.Informe_pdf(sheet_info, dic,lista_datos,cant_datos)