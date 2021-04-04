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
from . import crear_informe_orden_pago_excel
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

class account_invoice(models.Model):
    _inherit= "account.journal"

    codigo_transaccion_banco = fields.Char(string="Codigo Transaccional Banco")
    exigir_codigo = fields.Boolean(string="Exigir Codigo")

    @api.constrains('exigir_codigo')
    def valida_check(self):
        if self.exigir_codigo==True:
            if len(self.codigo_transaccion_banco)==0:
                raise osv.except_osv(('Alerta'),("Ingresar el Codigo Transaccional Banco."))

class res_partner_bank(models.Model):
    _inherit= "res.partner.bank"

    codigo_proveedor = fields.Char(string="Codigo Proveedor",size=16)

class account_voucher(models.Model):
    _inherit= "account.voucher"

    enviado = fields.Boolean(string="Enviado")
    veces_descarga = fields.Integer(string="# Descargado")
    egreso = fields.Char('Egreso', readonly=True, copy=False)
    res_partner_bank_id = fields.Many2one('res.partner.bank',string="Banco")
    cod_proveedor = fields.Char(related='res_partner_bank_id.bank_bic',string="Codigo de Proveedor en el Banco")
    partner_id_related = fields.Many2one(related='partner_id',string="Proveedir")


    @api.multi
    def default_banco_ids(self, partner_id_related):
        obj_datos=self.env['res.partner.bank'].search([('partner_id','=',partner_id_related)])
        if len(obj_datos)==1:
            return {
                'value': {
                    'res_partner_bank_id': obj_datos.id,
                    }
                }
    

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('account.voucher') or '/'
        vals['egreso'] = seq
        a = super(account_voucher, self).create(vals)
        return a

class res_partner_detalle(models.Model):
    _inherit = "res.partner"

    voucher_line=fields.One2many('account.voucher.detalle','voucher_id',string="Relacion")

class account_voucher_detalle(models.Model):
    _name = "account.voucher.detalle"
    
    voucher_id =fields.Many2one('res.partner',string="Relacion")
    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)
    company_id = fields.Many2one(related='usuario_id.company_id',string="Compañia")
    res_partner_bank_id = fields.Many2one('res.partner.bank',string="Banco Fuente")#,domain="[('company_id', '=', company_id)]")
    codigo_proveedor = fields.Char(string="Codigo Proveedor",size=16)



#----------------------------------------------------------
#        Creacion de campos para la pantalla              -
#----------------------------------------------------------

class ReporteCaja(models.Model):
    _name="reporte.orden_pago_detalle"

    id_relacion = fields.Many2one('reporte.orden_pago',string="Cabecera")
    id_proveedor = fields.Many2one('res.partner',string='Proveedor')
    journal_id = fields.Many2one('account.journal',string="Metodo de Pago")
    date =fields.Date(string='Fecha')
    res_partner_bank_id = fields.Many2one('res.partner.bank',string="Banco")
    amount = fields.Float(string="Total")
    id_pago = fields.Many2one('account.voucher',string="Pago")
    pagar = fields.Boolean(string="Pagar",default=True)



class ReporteCaja(models.Model):
    _name="reporte.orden_pago"
    _rec_name = 'titulo'

    orden_line=fields.One2many('reporte.orden_pago_detalle','id_relacion',string="Relacion")
    titulo=fields.Char(string="Titulo",default='Reporte de Orden de Pago')
    fecha_desde = fields.Date(string="Fecha desde")
    fecha_hasta = fields.Date(string="Fecha hasta")
    journal_ids=fields.Many2many('account.journal',string='Metodo de Pagos')
    partner_id=fields.Many2one('res.partner',string='Proveedor')
    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)
    fecha_emision = fields.Date(string="Fecha Emision")
    estado_pagos =fields.Selection( (('draft','Borrador'),
                               ('posted','Contabilizado')),string='Estados de Pagos', required=False)
    tipo_reporte =fields.Selection( (('1','PDF - EXCEL'),
                               ('2','BIZ')),string='Tipo de Reporte', required=True,default='1')
    active = fields.Boolean(string="Activo",default=False)
    submotivo_pago = fields.Selection((('RPA','Orden de pago'),
                                        ('VIA','Viáticos'),
                                        ('TRA','Transporte'),
                                        ('COM','Comisiones'),
                                        ('HON','Honorarios'),
                                        ('ANT','Anticipo'),
                                        ('PRE','Préstamo'),
                                        ('UTI','Utilidades'),
                                        ('REE','Rembolso'),
                                        ('BON','Bono')),string="Sub Motivo de pago")

    filename=fields.Char(string="Nombre de archivo")
    archivo_xls=fields.Binary(string='Archivo Excel')
    filename_pdf=fields.Char(string="Nombre de archivo")
    archivo_pdf=fields.Binary(string='Archivo PDF')
    filename_txt=fields.Char(string="Nombre de archivo")
    archivo_txt=fields.Binary(string='Archivo BIZ')

    _defaults = {
        'fecha_emision': fields.datetime.now(),
    }

    def normalize(self,s):
        replacements = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
        )
        for a, b in replacements:
            s = s.replace(a, b).replace(a.upper(), b.upper())
        return s

    @api.constrains('fecha_desde','fecha_hasta','tipo_reporte')
    def validar_reporte(self):
        if self.tipo_reporte=='2':
            self.active=True
        else:
            self.active=False
#----------------------------------------------------------
#                     Obtencion de datos                  -
#---------------------------------------------------------- 
    @api.multi
    def consultar(self):
        self.env.cr.execute("delete from reporte_orden_pago_detalle where id_relacion={0}".format(self.id))
        lista_id=''
        if self.tipo_reporte=='2':
            self.active=True
        else:
            self.active=False
        if self.tipo_reporte!='':
            if self.fecha_desde and self.fecha_hasta and self.journal_ids and self.estado_pagos:
                for j in self.journal_ids:
                    if lista_id!='':
                        lista_id=lista_id+','+str(j.id)
                    else:
                        lista_id=str(j.id)
                sql="""SELECT id from account_voucher where date between '{0}' AND '{1}' and journal_id in ({2}) and state in ('{3}') and  type='payment' order by id,date,number asc""".format(self.fecha_desde,self.fecha_hasta,lista_id,self.estado_pagos)
            elif self.fecha_desde and self.fecha_hasta and len(self.journal_ids)==0 and self.estado_pagos== False:
                sql="""SELECT id from account_voucher where date between '{0}' AND '{1}' and  type='payment' order by id,date,number asc""".format(self.fecha_desde,self.fecha_hasta)
            elif self.fecha_desde and self.fecha_hasta and self.journal_ids and self.estado_pagos==False:
                for j in self.journal_ids:
                    if lista_id!='':
                        lista_id=lista_id+','+str(j.id)
                    else:
                        lista_id=str(j.id)            
                sql="""SELECT id from account_voucher where date between '{0}' AND '{1}' and journal_id in ({2}) and  type='payment' order by id,date,number asc""".format(self.fecha_desde,self.fecha_hasta,lista_id)
            elif self.fecha_desde and self.fecha_hasta and len(self.journal_ids)==0 and self.estado_pagos:
                sql="""SELECT id from account_voucher where date between '{0}' AND '{1}' and state in ('{2}') and  type='payment' order by id,date,number asc""".format(self.fecha_desde,self.fecha_hasta,self.estado_pagos)
        else:
            if self.fecha_desde and self.fecha_hasta and self.journal_ids and self.partner_id:
                for j in self.journal_ids:
                    if lista_id!='':
                        lista_id=lista_id+','+str(j.id)
                    else:
                        lista_id=str(j.id)
                sql="""SELECT id from account_voucher where date between '{0}' AND '{1}' and journal_id in ({2}) and partner_id={3} and state='posted' and  type='payment' order by id,date,number asc""".format(self.fecha_desde,self.fecha_hasta,lista_id,self.partner_id.id)
            elif self.fecha_desde and self.fecha_hasta and len(self.journal_ids)==0 and self.partner_id:
                sql="""SELECT id from account_voucher where date between '{0}' AND '{1}' and partner_id={2} and state='posted' and  type='payment' order by id,date,number asc""".format(self.fecha_desde,self.fecha_hasta,self.partner_id.id)
        self.env.cr.execute(sql)
        lista_facturas=self.env.cr.dictfetchall()
        lista_facturas_id = [value['id'] for value in lista_facturas]
        obj_datos=self.env['account.voucher'].search([('id','in',lista_facturas_id)])
        dic={}
        lista_datos=[]
        descripcion=''
        for l in obj_datos:
            obj_line = self.env['reporte.orden_pago_detalle'].create({
                'id_relacion':self.id,
                'id_proveedor':l.partner_id.id,
                'journal_id':l.journal_id.id,
                'date':l.date,
                'res_partner_bank_id': l.res_partner_bank_id.id,
                'amount':l.amount,
                'id_pago':l.id
                })
            #INTEGRACION: SE CAMBIA POR PEDIDO DE CAMBIO DE NUMERO
            number=''
            if l.numerofac=='' or l.numerofac == False :
                number='Borrador'
            else:
                number=l.numerofac
            print(str(l.journal_id.code),'str(l.journal_id.code)')
            vat_1=''
            if l.partner_id.vat!= False:
                vat_1=l.partner_id.vat
            else:
                vat_1='NA'
            dic={
            'id_pago':l.id,
            'fecha_emision':l.date,
            'egreso':l.egreso,
            'cheque':number,
            'beneficiario':l.partner_id.name,
            'observacion':l.narration,
            'valor':l.amount,
            'partner_id':l.partner_id.id,
            'nit':vat_1,
            'partner_name':l.partner_id.name,
            'journal_id':str(l.journal_id.code),
            'cod_banco':l.res_partner_bank_id.bank_bic,
            'cod_proveedor':l.res_partner_bank_id.codigo_proveedor
            }
            lista_datos.append(dic)

            if l.enviado== False:
                l.enviado= True
                l.veces_descarga=1
            else:
                l.veces_descarga=l.veces_descarga+1


        cadena=''
        for fil in self.journal_ids:
            obj_move_line=self.env['account.journal'].search([('id','=',fil.id)])
            if cadena=='':
                cadena=obj_move_line.name
            else:
                cadena=cadena+' ,'+obj_move_line.name

        if cadena=='':
            cadena='Todos los metodos de pago'

        if self.estado_pagos==False:
            cadena1="Todos"
        elif self.estado_pagos=='draft':
            cadena1="Borrador"
        else:
            cadena1="Contabilizado"

        datos={
            'lista':lista_datos,
            'cant':len(obj_datos),
            'filtro':cadena,
            'filtro1':cadena1,
        }

        return datos

#-------------------------------------------------------------------------------------------------------------------
#                     CREACION DE TXT                                                                              -
#-------------------------------------------------------------------------------------------------------------------
    @api.multi
    def generar_txt(self):
        contenido=""
        nombre=""
        A1=5
        A2=6
        A3=18
        A4=1
        A5=14
        A6=60
        A7=3
        A8=3
        A9=2
        A10=2
        A11=20
        A12=1
        A13=15
        A14=60
        A15=15
        A16=15
        A17=15
        A18=20
        A19=10
        A20=50
        A21=50
        A22=20
        A23=3
        A24=10
        A25=10
        A26=10
        A27=1
        A28=5
        A29=6
        A30=3
        A31=10

        secuencial=1
        for l in self.orden_line:
            A_1=''
            A_2=''
            A_3=''
            A_4=''
            A_5=''
            A_6=''
            A_7=''
            A_8='001'
            A_9=''
            A_10=''
            A_11=''
            A_12='1'
            A_13=''
            A_14=''
            A_15=''
            A_16=''
            A_17=''
            A_18=''
            A_19='          '
            A_20='                                                  '
            A_21='                                                  '
            A_22='                    '
            A_23='TER'
            A_24='          '
            A_25='          '
            A_26='          '
            A_27=' '
            A_28=''
            A_29='      '
            A_30=''
            A_31=''
            if l.pagar==True:
                A_1='BZDET'
                fun='%0{0}d'.format(A2)
                A_2=fun % secuencial
                val=str(l.id_pago.res_partner_bank_id.bank_bic).split(' ')
                fun='%0{0}d'.format(A3)
                if len(val)>1:
                    val=0.0
                    val=(val[0])
                    A_3=fun % (val)
                else:
                    A_3=fun % int(l.id_pago.res_partner_bank_id.bank_bic)
                ###  VALIDACION DE IDENTIFICACION
                if l.id_proveedor.vat!= False:
                    A_5=l.id_proveedor.vat
                else:
                    A_5='NA'
                if len(l.id_proveedor.vat)==10:
                    A_4='C'
                elif len(l.id_proveedor.vat)==13:           
                    A_4='R'
                else:
                    A_4='P'
                if len(l.id_proveedor.name)>=60:
                    A_6 =l.id_proveedor.name
                else:
                    A_6 =l.id_proveedor.name
                
                ### VALIDACION DEL METODO DE PAGO
                A_7=str(l.id_pago.journal_id.code)

                text1 = l.id_pago.narration
                lista_metodos = ['EFE','CHE','IMP','PEF']
                pago=''
                if str(l.id_pago.journal_id.code)in lista_metodos and l.id_pago.journal_id.exigir_codigo==False:
                   A_9='000'
                elif str(l.id_pago.journal_id.code) not in lista_metodos and l.id_pago.journal_id.exigir_codigo==False:
                   raise osv.except_osv(('Alerta'),("Configurar de manera correcta el Diario."))
                else:
                   A_9=l.id_pago.res_partner_bank_id.bank.bic

                if A_9==False:
                    A_9=''

                A_10=l.id_pago.res_partner_bank_id.state
                A_11=l.id_pago.res_partner_bank_id.acc_number

                ### VALIDACION DE MONTO
                A_13=''
                valor=str(l.id_pago.amount).split('.')
                if len(valor[1])==1:
                    cant=len(valor[0])
                    val=''
                    for i in range(cant, 13):
                        val=str(val)+'0'

                    A_13=str(val)+str(valor[0])+'00'
                else:
                    cant=len(valor[0])
                    val=''
                    for i in range(cant, 13):
                        val=str(val)+'0'

                    A_13=str(val)+str(valor[0])+str(valor[1])

                A_14=l.id_pago.narration
                if l.id_pago.number=='' or l.id_pago.number == False :
                    A_15='Borrador'
                else:
                    A_15=l.id_pago.number
                fun='%0{0}d'.format(A16)
                A_16=fun % 0
                fun='%0{0}d'.format(A17)
                A_17=fun % 0
                fun='%0{0}d'.format(A18)
                A_18=fun % 0

                if (l.id_proveedor.street)!=False:
                    A_21=str(l.id_proveedor.street)+' '+str(l.id_proveedor.street2)

                if (l.id_proveedor.phone)!=False:
                    A_22=str(l.id_proveedor.phone)

                A_30=str(self.submotivo_pago)

                contenido = contenido +str(A_1)+str(A_2)+str(A_3) + str(A_4) + str(A_5) + str(A_6) +  str(A_7) + str(A_8) + str(A_9.strip()) + str(A_10) + str(A_11)+ str(A_12) + str(A_13) + str(A_14) + str(A_15) + str(A_16) + str(A_17) + str(A_18) + str(A_19) + str(A_20)+ str(A_21) + str(A_22) + str(A_23) + str(A_24)+ str(A_25)+ str(A_26)+ str(A_27)+ str(A_28)+ str(A_29)+ str(A_30)+ str(A_31)
                contenido = contenido + str('\n')
                secuencial=secuencial+1

        now = datetime.now()
        anio = now.strftime('%Y')
        mes = now.strftime('%m')
        dia = now.strftime('%d')
        nombre=str(self.partner_id.name) + str(anio) + str(mes) + str(dia) + ".BIZ"
        contenido2 = contenido.encode('utf-8')
        self.write({'filename_txt': nombre, 'archivo_txt': bytes(base64.b64encode(contenido2))})
        return True


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
        wb = crear_informe_orden_pago_excel.crear_wb_informe()
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

        sheet_info = crear_informe_orden_pago_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "130"
        sheet_view.zoomScaleNormal = "130"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "130"
        crear_informe_orden_pago_excel.Informe(sheet_info, dic,lista_datos,cant_datos,filtro,filtro1)

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
        wb = crear_informe_orden_pago_excel.crear_wb_informe()
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
        filtro1=datos['filtro1']
        sheet_info = crear_informe_orden_pago_excel.crea_hoja_info_pdf(wb, 'Informe ',0)
        #sheet_info = crear_informe_cobranza_excel.crea_hoja_info(wb, 'Informe ',0)
        sheet_view = openpyxl.worksheet.SheetView()
        sheet_view.zoomScale = "70"
        sheet_view.zoomScaleNormal = "70"
        sheet_info.sheet_view = sheet_view
        sheet_info.zoomScale = "70"
        crear_informe_orden_pago_excel.Informe_pdf(sheet_info, dic,lista_datos,cant_datos,filtro,filtro1)