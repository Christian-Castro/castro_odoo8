# -*- coding: utf-8 -*-
from openerp import api
from openerp.osv import fields, osv

import logging
from datetime import datetime, timedelta

import base64

import io

import time

import commands
import os
import reporte_excel
import reporte_pdf
_logger = logging.getLogger(__name__)

class Libro_Mayor(osv.osv_memory):
    _name = "reporte.libro.mayor.ans"
    _rec_name = "chart_account_id"
    _columns = {
        'chart_account_id': fields.many2one('account.account', string='Plan de Cuentas', required=True,domain = [('parent_id','=',False)]),
        'fiscalyear_id': fields.many2one('account.fiscalyear', string='Año Fiscal'),
        'target_move': fields.selection([('posted', 'Asiento Contabilizados'),
                                         ('all', 'Todos los Asientos'),
                                         ], 'Seleccionar Asientos', required=True),
        'journal_ids': fields.many2many('account.journal', string='Diarios', required=True),
        'date_from': fields.date("Fecha Desde",required=True),
        'date_to': fields.date("Fecha Hasta",required=True),
        'filter': fields.selection([('filter_no', 'No Filtros'), ('filter_date', 'Fecha')],
                                   "Filtrado Por:", required=True),
        'display_account': fields.selection([('all', 'Todos'), ('movement', 'Con Movimientos'),
                                             ], 'Mostrar Cuentas', required=True),
        'jornada': fields.many2one('jornada', string='Jornada', help='Seleccione su jornada',
                                    required=False),
        'seleccion':fields.boolean(),
        'seccion': fields.many2one('seccion', string='Seccion', help='Seleccione su jornada',
                                   required=False),
        'curso': fields.many2one('curso', string="Curso", help='Seleccione su jornada',
                                 required=False),
        'cuentas': fields.many2many('account.account', string="Cuenta Contable", required=True),
        'nombre_xls': fields.char(),
        'binario_txt': fields.binary("Archivo Pdf Factura"),
        'binario_xls': fields.binary('Archivo Excel a Generar'),
        'nombre_txt': fields.char(),
    }
    @api.multi
    def consultar(self,sheet_libromayor,alignment_title,fuente_cabecera,reporte):
        hoja = 9
        hoja_intro = 10
        hoja_cuerpo = 10
        cuentas_existentes = [l.id for l in self.cuentas]
        total = 0
        sub_deudor = 0
        sub_acreedor = 0
        i = 0
        for l in self.cuentas:
            if l.type == "view":
                hijos = self.hijos_cuentas(l.id)
                for k in hijos:
                    if k in cuentas_existentes:
                        continue
                    cuenta = self.env['account.account'].search([('id','=',k)])
                    saldo = self.traer_ultimo_saldo(self.date_from,k)
                    lista = self.traer_movimiento(k)
                    for c in cuenta:
                        cuenta_name = u' '.join((c.code,c.name)).encode('utf-8').strip()# str(c.code) +" "+str(c.name)
                    hojas = self.ingresar(lista,cuenta_name,saldo,hoja,hoja_intro,hoja_cuerpo,sheet_libromayor,alignment_title,fuente_cabecera,reporte)
                    hoja = hojas[0]
                    hoja_intro = hojas[1]
                    hoja_cuerpo = hojas[2]
                    _logger.info(cuenta_name[0])
                    if int(cuenta_name[0]) == 1:
                        sub_deudor += hojas[3]
                    else:
                        sub_acreedor += hojas[3]
            else:
                lista = self.traer_movimiento(l.id)
                saldo = self.traer_ultimo_saldo(self.date_from,l.id)
                hojas = self.ingresar(lista, str(l.code) + " " + str(l.name), saldo, hoja,
                                      hoja_intro, hoja_cuerpo, sheet_libromayor, alignment_title, fuente_cabecera,
                                      reporte)
                hoja = hojas[0]
                hoja_intro = hojas[1]
                hoja_cuerpo = hojas[2]
                if int(l.code[0]) == 1:
                    sub_deudor += hojas[3]
                else:
                    sub_acreedor += hojas[3]

            if i < len(self.cuentas):
                #_logger.info("sub_deudor "+str(sub_deudor) + " sub_acreedor "+str(sub_acreedor))
                total = sub_deudor - sub_acreedor
                if reporte == 1:
                    reporte_excel.totalizado_cuentas(sheet_libromayor,hoja_cuerpo,alignment_title,fuente_cabecera,total)
                else:
                    reporte_pdf.totalizado_cuentas(sheet_libromayor,hoja_cuerpo,alignment_title,fuente_cabecera,total)
            i += 1

    def ingresar(self,lista,cuenta,saldo,hoja,hoja_intro,hoja_cuerpo,sheet_libromayor,alignment_title,fuente_cabecera,reporte):
        total = 0
        if lista['datos']:
            entered_date = datetime.strptime(self.date_from, '%Y-%m-%d')
            entered_date = entered_date.date()
            ayer = entered_date - timedelta(days=1)
            fuente = {'cuenta': cuenta, 'detalle': lista['datos'],
                      'documento': lista['documentos'], 'ultimo_saldo': saldo, 'fecha': ayer}
            if reporte == 1:
                hojas = reporte_excel.cuerpo_reporte(sheet_libromayor, alignment_title, fuente_cabecera, fuente, hoja,
                                                     hoja_intro, hoja_cuerpo)
                hoja = hojas['cuerpo'] + 2
                hoja_intro = hoja + 2
                hoja_cuerpo = hoja_intro + 1
                total = hojas['total']
            else:
                hojas = reporte_pdf.cuerpo_reporte(sheet_libromayor, alignment_title, fuente_cabecera, fuente, hoja,
                                                   hoja_intro, hoja_cuerpo)
                hoja = hojas['cuerpo'] + 2
                hoja_intro = hoja + 2
                hoja_cuerpo = hoja_intro + 1
                total = hojas['total']
        return [hoja,hoja_intro,hoja_cuerpo,total]


    def hijos_cuentas(self,id):
        id_traer = []
        id_consultar = []
        obj = self.env['account.account'].search([('parent_id','=',id)])
        for l in obj:
            if l.type == "view":
                id_consultar.append(l.id)
            else:
                id_traer.append(l.id)
        for k in id_consultar:
            obj1 = self.env['account.account'].search([('parent_id', '=', k)])
            for j in obj1:
                if j.type == "view":
                    id_consultar.append(j.id)
                else:
                    id_traer.append(j.id)
        #_logger.info("lista traer_id = "+str(id_traer)+" lista consultar = "+str(id_consultar))
        return id_traer



    def saldo_inicial_reporte(self):
        debito = 0
        credito = 0
        obj_datos = self.env['account.move.line'].search([('move_id.date','<',self.date_from), ])
        for l in obj_datos:
            debito += l.debit
            credito += l.tax_amount
        contador = debito - credito

        return contador

    def traer_ultimo_saldo(self,date,account):
        if date and account:
            obj_datos = self.env['account.move.line'].search([('account_id.id', '=', account), ('move_id.date', '<', str(date))])
            acumulador = 0
            debito = 0
            credito = 0
            for l in obj_datos:
                debito += l.debit
                credito += l.tax_amount
            acumulador = debito - credito
        return acumulador

    def traer_movimiento(self,account):
        if self.chart_account_id and self.fiscalyear_id:
            obj_datos = None
            lista_id = [j.id for j in self.journal_ids]
            if self.journal_ids:
                documento = []
                where = ('move_id.state','=','posted') if self.target_move == 'posted' else  ('move_id.state', '!=', '')

                where_2 = ('seccion','=',self.seccion.id) if self.seccion else ('seccion', '!=', '')
                where_3 = ('curso','=',self.curso.id) if self.curso else ('curso', '!=', '')
                where_4 = ('jornada', '=', self.jornada.id) if self.jornada else ('jornada', '!=', '')


                obj_validacion = self.env['account.move.line'].search([('account_id.id', '=', account)
                                                                     , ('move_id.date', '>=', str(self.date_from))
                                                                     , ('move_id.date', '<=', str(self.date_to))
                                                                     , ('account_id.company_id', '=', self.chart_account_id.id)
                                                                     , ('journal_id','in',lista_id)
                                                                     , where_2,where_3,where_4
                                                                     , where
                                                                     ],
                                                                 order='date')
                if obj_validacion and self.display_account == "movement":

                    obj_datos = self.env['account.move.line'].search([('account_id.id', '=', account)
                                                                         , ('move_id.date', '>=', str(self.date_from))
                                                                         , ('move_id.date', '<=', str(self.date_to))
                                                                         , ('account_id.company_id', '=', self.chart_account_id.id)
                                                                         , ('journal_id','in',lista_id)
                                                                         , where
                                                                         ],
                                                                     order='date')

                    for j in obj_datos:
                        datos = self.env['account.invoice.line'].search([('invoice_id.move_id','=',j.move_id.id)])
                        descripcion = ""
                        if datos:
                            for a in datos:
                                if a.name:
                                    if descripcion == "":
                                        descripcion = str(a.name)
                                    else:
                                        descripcion += "," + str(a.name)
                                    documento.append(descripcion)
                else:
                    obj_datos = self.env['account.move.line'].search([('account_id.id', '=', account)
                                                                         , ('move_id.date', '>=', str(self.date_from))
                                                                         , ('move_id.date', '<=', str(self.date_to))
                                                                         , ('account_id.company_id', '=',
                                                                            self.chart_account_id.id)
                                                                         , ('journal_id', 'in', lista_id)
                                                                         , where
                                                                      ],
                                                                     order='date')



            else:
                _logger.info("Hay campos vacios")
        return {'datos':obj_datos,'documentos':documento}


    def _get_account(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1)
        return accounts and accounts[0] or False

    @api.one
    def clear_record_data(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [inv.id], {'cuentas': [(5,)]}, context=context)
        return True



    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<=', now), ('date_stop', '>=', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    def _get_all_journal(self, cr, uid, context=None):
        return self.pool.get('account.journal').search(cr, uid ,[])

    def _get_all_cuenta(self, cr, uid, context=None):
        return self.pool.get('account.account').search(cr, uid ,[])

    def ajustes_hoja(self,sheet,flag,celda,value,value2):
        if (flag == 0):
            sheet.column_dimensions[celda].width = value2
        if (flag == 1):
            sheet.row_dimensions[int(celda)].height = value


    @api.multi
    def generar_excell(self):
        fp = io.BytesIO()
        dic = {
            'fecha_desde': self.date_from,
            'fecha_hasta': self.date_to,
            'plan_cuenta': self.chart_account_id,
            'usuario': self.env.user.name,
            'inicial': self.saldo_inicial_reporte(),
        }
        workbook = reporte_excel.crear_reporte_excell()
        reporte_excel.crear_encabezado(dic,workbook['sheet'],workbook['alineacion'],workbook['fuente'])
        self.consultar(workbook['sheet'], workbook['alineacion'], workbook['fuente'],1)
        workbook['libro'].save(fp)
        filename = 'Reporte Libro Mayor' + '.xlsx'
        self.nombre_xls = filename
        self.binario_xls = base64.b64encode(fp.getvalue())
        return True

    @api.multi
    def generar_pdf(self):
        fp = io.BytesIO()
        dic = {
            'fecha_desde': self.date_from,
            'fecha_hasta': self.date_to,
            'plan_cuenta': self.chart_account_id,
            'usuario': self.env.user.name,
            'inicial': self.saldo_inicial_reporte(),
        }
        workbook = reporte_pdf.crear_reporte_pdf()
        reporte_pdf.crear_encabezado(dic, workbook['sheet'], workbook['alineacion'], workbook['fuente'])
        self.consultar(workbook['sheet'], workbook['alineacion'], workbook['fuente'], 0)
        workbook['libro'].save(fp)
        filename_pdf = 'Informe'+'.xlsx'
        archivo_pdf = base64.b64encode(fp.getvalue())
        obj=self.env['ir.attachment']
        obj_xls = obj.create({'res_model': self.id, 'name': filename_pdf
                                 , 'datas': archivo_pdf, 'type': 'binary',
                              'datas_fname': filename_pdf})
        direccion_xls = obj._get_path(obj_xls.datas)[1]
        direccion = obj._get_path(obj_xls.datas)[0]
        nombre_bin = obj_xls.store_fname
        nombre_archivo = obj_xls.datas_fname
        separa = direccion_xls.rstrip(direccion)
        os.chdir(separa)
        os.rename(nombre_bin, nombre_archivo)
        commands.getoutput(""" libreoffice --headless --convert-to pdf *.xlsx""")
        with open(direccion_xls.rstrip(direccion) + '/' + nombre_archivo.split('.')[0] + '.pdf', "rb") as f:
            data = f.read()
            file = data.encode("base64")
        self.write({'nombre_txt': nombre_archivo.split('.')[0] + '.pdf', 'binario_txt': file})
        os.rename(nombre_archivo, nombre_bin)
        obj_xls.unlink()

        return True

    _defaults = {
        'chart_account_id': _get_account,
        'filter': 'filter_no',
        'target_move': 'posted',
        'journal_ids':_get_all_journal,
        'date_from':fields.date.today(),
        'date_to': fields.date.today(),

    }


