# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import io
from datetime import datetime, date
from openerp.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)
try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')

class ReporteVentas(models.TransientModel):
    _name = "reporte.ventas"
    _inherit = "reporte.utileria"


    name = fields.Char(default="Reporte Ventas")
    fecha_inicio = fields.Date(string='Fecha Inicio',)
    fecha_fin = fields.Date(string='Fecha Fin',)
    cliente_id = fields.Many2one(
        string='Cliente',
        comodel_name='res.partner',
    )
    alumno_id = fields.Many2one(
        string='Alumno',
        comodel_name='res.partner',
    )
    jornada_id = fields.Many2one(
        string='Jornada',
        comodel_name='jornada',
    )
    seccion_id = fields.Many2one(
        string='Sección',
        comodel_name='seccion',
    )
    curso_id = fields.Many2one(
        string='Curso',
        comodel_name='curso',
    )
    paralelo_id = fields.Many2one(
        string='Paralelo',
        comodel_name='paralelo',
    )
    
    @api.multi
    def generar_archivo_xlsx(self):
        fp = self.generar_archivo()
        return self.download_file(fp, "Reporte Ventas.xlsx")

    @api.multi
    def generar_archivo_pdf(self):
        fp = self.generar_archivo()
        return self.download_file(fp, "Reporte Ventas.xlsx", True)

    def generar_archivo(self):
        wb, ws, fp = self.crear_workbook('VENTAS')
        self.setear_ancho_columna(ws)
        self.setear_tamano_hoja(ws, 9)
        self.setear_hoja_orientacion(ws, True)
        # self.mostrar_paginas_derecha_cabecera(ws)
        self.ocultar_lineas_xlsx(ws)
        data_ventas, lista_resumen = self.construir_data()
        self.dibujar_cabecera(wb, ws)
        self.dibujar_cabecera_tabla(wb, ws)
        self.dibujar_cuerpo_tabla(wb, ws, data_ventas, lista_resumen)
        # # self.repetir_fila_en_cada_hoja(ws, 1, 6)
        self.ajustar_pagina_a_n_columnas(ws)
        wb.close()
        return fp

    def setear_ancho_columna(self, ws):
        ws.set_column('A:A', 10.43)
        ws.set_column('B:B', 11)
        ws.set_column('C:C', 14.86)
        ws.set_column('D:D', 34)
        ws.set_column('E:E', 34)
        ws.set_column('F:F', 11)
        ws.set_column('G:G', 12.71)
        ws.set_column('H:H', 18.86)
        ws.set_column('I:I', 11.57)
        ws.set_column('J:J', 8)
        ws.set_column('K:K', 8)
        ws.set_column('L:L', 8)
        ws.set_column('M:M', 8)
        ws.set_column('N:N', 7.14)
        ws.set_column('O:O', 6.86)
        ws.set_column('P:P', 11)
        # ws.set_column(1, 23, 15) #desde la B hasta Z ancho 15

    def construir_data(self):
        model_invoice = self.env["account.invoice"]

        jornada = "('jornada_id', '=', %s)," %(self.jornada_id.id) if self.jornada_id else ""
        seccion = "('seccion_id', '=', %s)," %(self.seccion_id.id) if self.seccion_id else ""
        curso = "('curso_id', '=', %s)," %(self.curso_id.id) if self.curso_id else ""
        paralelo = "('paralelo_id', '=', %s)," %(self.paralelo_id.id) if self.paralelo_id else ""
        tipo_factura = "[('escuela', '=', True), %s%s%s%s]" %(jornada, seccion, curso, paralelo)

        cliente = "[('partner_id', '=', %s),]" %(self.cliente_id.id) if self.cliente_id else "[]"
        alumno = "[('alumno_id', '=', %s),]" %(self.alumno_id.id) if self.alumno_id else "[]"

        invoice_ids = model_invoice.search(
            [
                ("state", "in", ["open", "paid", "cancel"]),
                ("date_invoice", ">=", self.fecha_inicio),
                ("date_invoice", "<=", self.fecha_fin),
                ("type", "in", ["out_invoice", "out_refund"]),#factura cliente
                ("escuela", "=", True),
            ] + safe_eval(tipo_factura)+safe_eval(cliente)+safe_eval(alumno)
        )

        lista_establecimiento = sorted(list(set(invoice_ids.mapped('establecimiento'))))
        lista_punto_emision = sorted(list(set(invoice_ids.mapped('puntoemision'))))
        #resumen
        total_facturas = len(invoice_ids)
        total_anuladas = len(invoice_ids.filtered(lambda invoice: invoice.state == 'cancel'))
        total_devoluciones = invoice_ids.filtered(lambda invoice: invoice.type == 'out_refund' and invoice.tipo == 'nota_credito_cliente')
        invoice_reembolso_ids = invoice_ids.filtered(lambda invoice: invoice.journal_id.reembolso)
        lista_con_iva = []
        lista_sin_iva = []
        lista_descuento = []
        lista_iva = []
        for invoice in invoice_reembolso_ids:
            lista_con_iva.append(sum([(line.price_unit * line.quantity) for line in invoice.invoice_line.filtered(
                        lambda line_invoice: line_invoice.invoice_line_tax_id and line_invoice.invoice_line_tax_id.amount != 0)]))
            lista_sin_iva.append(sum([(line.price_unit * line.quantity) for line in invoice.invoice_line.filtered(
                        lambda line_invoice: not line_invoice.invoice_line_tax_id or line_invoice.invoice_line_tax_id.amount == 0)]))
            lista_descuento.append(sum([line.descuento or 0 for line in invoice.invoice_line]))
            lista_iva.append(invoice.amount_tax)

        total_iva_devoluciones = []
        tarifa = 0
        con_iva = 0
        descuento = 0
        for invoice in total_devoluciones:
            tarifa = sum([(line.price_unit * line.quantity) for line in invoice.invoice_line.filtered(
                    lambda line_invoice: not line_invoice.invoice_line_tax_id or line_invoice.invoice_line_tax_id.amount == 0)])
            con_iva = sum([(line.price_unit * line.quantity) for line in invoice.invoice_line.filtered(
                    lambda line_invoice: line_invoice.invoice_line_tax_id and line_invoice.invoice_line_tax_id.amount != 0)])
            descuento = sum([line.descuento or 0 for line in invoice.invoice_line])
            total_iva_devoluciones.append(invoice.amount_tax)
        lista_resumen = [{
            'total_facturas': total_facturas,
            'total_anuladas': total_anuladas,
            'total_devoluciones': len(total_devoluciones),
            'total_tarifa_devoluciones': tarifa,
            'total_con_iva_devoluciones': con_iva,
            'total_iva_devoluciones': sum(total_iva_devoluciones),
            'total_descuento_devoluciones': descuento,
            'reembolso_con_iva': sum(lista_con_iva),
            'reembolso_sin_iva': sum(lista_sin_iva),
            'reembolso_descuento': sum(lista_descuento),
            'reembolso_iva': sum(lista_iva),
        }]
        #serie
        lista_serie = []
        for esta in lista_establecimiento:
            for punto in  lista_punto_emision:
                dic_serie = {
                    'establecimiento': esta,
                    'punto_emision': punto,
                }
                lista_serie.append(dic_serie)

        #diario
        # list_journal_ids = sorted(list(set(invoice_ids.mapped('journal_id.id'))))
        
        lista_detalle_serie = []
        lista_detalle_diario = []
        # for diario_id in list_journal_ids:
        for serie in lista_serie:
            name_pto_emision = ''
            for invoice in invoice_ids.filtered(lambda invoice: invoice.establecimiento == serie['establecimiento']
                and invoice.puntoemision == serie['punto_emision']):# and invoice.journal_id.id == diario_id):
                tarifa = sum([(line.price_unit * line.quantity) for line in invoice.invoice_line.filtered(
                        lambda line_invoice: not line_invoice.invoice_line_tax_id or line_invoice.invoice_line_tax_id.amount == 0)])
                con_iva = sum([(line.price_unit * line.quantity) for line in invoice.invoice_line.filtered(
                        lambda line_invoice: line_invoice.invoice_line_tax_id and line_invoice.invoice_line_tax_id.amount != 0)])
                descuento = sum([line.descuento or 0 for line in invoice.invoice_line])
                dic_detalle_serie = {
                    'comprobante': invoice.number,
                    'fecha_emision': invoice.date_invoice,
                    'documento': invoice.numerofac,
                    'cliente': invoice.partner_id.name,
                    'alumno': invoice.alumno_id.name,
                    'jornada': invoice.jornada_id.display_name,
                    'seccion': invoice.seccion_id.display_name,
                    'curso': invoice.curso_id.display_name,
                    'paralelo': invoice.paralelo_id.display_name,
                    'tarifa': tarifa,
                    'con_iva': con_iva,
                    'descuento': descuento,
                    'total_sin_iva': (tarifa + con_iva) - descuento,
                    'iva': invoice.amount_tax,
                    'contado': 0,
                    'credito': ((tarifa + con_iva) - descuento) + invoice.amount_tax,
                }
                lista_detalle_serie.append(dic_detalle_serie)
                name_pto_emision = invoice.puntoemision_id.name if invoice.puntoemision_id else ''
            serie['name_pto_emision'] = name_pto_emision
            dic_detalle_diraio = {
                # 'diario': invoice.journal_id.display_name,
                'serie': serie,
                'detalle': sorted(lista_detalle_serie, key=lambda detalle: detalle['documento']),
            }
            lista_detalle_diario.append(dic_detalle_diraio)
        return lista_detalle_diario, lista_resumen

    def dibujar_cabecera(self, wb, ws):
        ws.merge_range(
            "A1:E1",
            "VENTAS POR FECHAS (del %s al %s)" %(self.fecha_inicio, self.fecha_fin),
            self.format_bold_left(wb)
        )
        ws.merge_range(
            "O1:P1",
            "Módulo de Compras".decode("utf-8"),
            self.format_bold_right(wb)
        )
        ws.merge_range(
            "A2:D2",
            self.env.user.company_id.display_name,
            self.format_bold_left(wb)
        )
        ws.merge_range(
            "A3:D3",
            datetime.now(),
            self.format_bold_date_left(wb)
        )

    def dibujar_cabecera_tabla(self, wb, ws):
        ws.merge_range(
            "A6:A7",
            "No. COMPRO",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "B6:B7",
            "F. EMISION",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "C6:C7",
            "No. DOCUMENTO",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "D6:D7",
            "NOMBRE CLIENTE",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "E6:E7",
            "NOMBRE ALUMNO",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "F6:F7",
            "JORNADA",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "G6:G7",
            "SECCION",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "H6:H7",
            "CURSO",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "I6:I7",
            "PARALELO",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "J6:K6",
            "SUBTOTAL",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "J7",
            "TARIFA",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "K7",
            "CON IVA",
            self.format_bold_center_border(wb)
        )
        ws.merge_range(
            "L6:L7",
            "DESCTO",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "M6:M7",
            "TOTAL",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "N6:N7",
            "IVA",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "O6:P6",
            "VENTAS AL",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "O7",
            "CONTADO",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "P7",
            "CREDITO",
            self.format_bold_center_border(wb)
        )

    def dibujar_cuerpo_tabla(self, wb, ws, data_ventas, lista_resumen):
        # total_tipo_tarifa = 0
        # total_tipo_con_iva = 0
        # total_tipo_descuento = 0
        # total_tipo_sin_iva = 0
        # total_tipo_iva = 0
        # total_tipo_credito = 0

        total_general_tarifa = 0
        total_general_con_iva = 0
        total_general_descuento = 0
        total_general_sin_iva = 0
        total_general_iva = 0
        total_general_credito = 0
        lista_serie = []
        row = 8
        # nombre_diario = ''
        for venta in data_ventas:
            # if nombre_diario != venta['diario']:
            #     if nombre_diario:
            #         dic_total_tipo = dict(
            #             total_tipo_tarifa=total_tipo_tarifa,
            #             total_tipo_con_iva=total_tipo_con_iva,
            #             total_tipo_descuento=total_tipo_descuento,
            #             total_tipo_sin_iva=total_tipo_sin_iva,
            #             total_tipo_iva=total_tipo_iva,
            #             total_tipo_credito=total_tipo_credito,
            #         )
            #         row = self.dibujar_total_tipo(ws, wb, row, dic_total_tipo)

            #         total_tipo_tarifa = 0
            #         total_tipo_con_iva = 0
            #         total_tipo_descuento = 0
            #         total_tipo_sin_iva = 0
            #         total_tipo_iva = 0
            #         total_tipo_credito = 0

            #     ws.write(
            #         "A"+str(row),
            #         "TIPO",
            #         self.format_bold_left(wb),
            #     )
            #     ws.merge_range(
            #         "B"+str(row)+":D"+str(row),
            #         venta['diario'],
            #         self.format_bold_left(wb),
            #     )
            #     row += 1
            #     nombre_diario = venta['diario']

            # for serie in venta['serie']:
            ws.write(
                "A"+str(row),
                "SERIE:",
                self.format_bold_left(wb),
            )
            ws.merge_range(
                "B"+str(row)+":D"+str(row),
                # str(venta['serie']['establecimiento'])+'-'+str(venta['serie']['punto_emision']),
                venta['serie']['name_pto_emision'],
                self.format_bold_left(wb),
            )
            lista_serie.append(venta['serie']['name_pto_emision'])
            row += 1
            total_tarifa = 0
            total_con_iva = 0
            total_descuento = 0
            total_sin_iva = 0
            total_iva = 0
            total_credito = 0
            for line in venta['detalle']:
                ws.write(
                    'A'+str(row),
                    line['comprobante'],
                    self.format_left(wb),
                )
                ws.write(
                    'B'+str(row),
                    line['fecha_emision'],
                    self.format_left(wb),
                )
                ws.write(
                    'C'+str(row),
                    line['documento'] or '',
                    self.format_left(wb),
                )
                ws.write(
                    'D'+str(row),
                    line['cliente'] or '',
                    self.format_left(wb),
                )
                ws.write(
                    'E'+str(row),
                    line['alumno'] or '',
                    self.format_left(wb),
                )
                ws.write(
                    'F'+str(row),
                    line['jornada'] or '',
                    self.format_left(wb),
                )
                ws.write(
                    'G'+str(row),
                    line['seccion'] or '',
                    self.format_left(wb),
                )
                ws.write(
                    'H'+str(row),
                    line['curso'] or '',
                    self.format_left(wb),
                )
                ws.write(
                    'I'+str(row),
                    line['paralelo'] or '',
                    self.format_left(wb),
                )
                ws.write(
                    'J'+str(row),
                    line['tarifa'] or '',
                    self.format_amount_right(wb),
                )
                total_tarifa += line['tarifa']
                ws.write(
                    'K'+str(row),
                    line['con_iva'] or '',
                    self.format_amount_right(wb),
                )
                total_con_iva += line['con_iva']
                ws.write(
                    'L'+str(row),
                    line['descuento'] or '',
                    self.format_amount_right(wb),
                )
                total_descuento += line['descuento']
                ws.write(
                    'M'+str(row),
                    line['total_sin_iva'] or '',
                    self.format_amount_right(wb),
                )
                total_sin_iva += line['total_sin_iva']
                ws.write(
                    'N'+str(row),
                    line['iva'] or '',
                    self.format_amount_right(wb),
                )
                total_iva += line['iva']
                ws.write(
                    'O'+str(row),
                    line['contado'] or '',
                    self.format_amount_right(wb),
                )
                ws.write(
                    'P'+str(row),
                    line['credito'] or '',
                    self.format_amount_right(wb),
                )
                total_credito += line['credito']
                row += 1
            #total por serie
            ws.write(
                'I'+str(row),
                'TOTAL POR SERIE:',
                self.format_bold_right_border(wb),
            )
            ws.write(
                'J'+str(row),
                total_tarifa,
                self.format_amount_bold__bordertop_right(wb),
            )
            ws.write(
                'K'+str(row),
                total_con_iva,
                self.format_amount_bold__bordertop_right(wb),
            )
            ws.write(
                'L'+str(row),
                total_descuento,
                self.format_amount_bold__bordertop_right(wb),
            )
            ws.write(
                'M'+str(row),
                total_sin_iva,
                self.format_amount_bold__bordertop_right(wb),
            )
            ws.write(
                'N'+str(row),
                total_iva,
                self.format_amount_bold__bordertop_right(wb),
            )
            ws.write(
                'O'+str(row),
                0,
                self.format_amount_bold__bordertop_right(wb),
            )
            ws.write(
                'P'+str(row),
                total_credito,
                self.format_amount_bold__bordertop_right(wb),
            )
            #acumulador total por tipo
            # total_tipo_tarifa += total_tarifa
            # total_tipo_con_iva += total_con_iva
            # total_tipo_descuento += total_descuento
            # total_tipo_sin_iva += total_sin_iva
            # total_tipo_iva += total_iva
            # total_tipo_credito += total_credito
            #acumulador total general
            total_general_tarifa += total_tarifa
            total_general_con_iva += total_con_iva
            total_general_descuento += total_descuento
            total_general_sin_iva += total_sin_iva
            total_general_iva += total_iva
            total_general_credito += total_credito
            row += 1
        #total por tipo
        # dic_total_tipo = dict(
        #     total_tipo_tarifa=total_tipo_tarifa,
        #     total_tipo_con_iva=total_tipo_con_iva,
        #     total_tipo_descuento=total_tipo_descuento,
        #     total_tipo_sin_iva=total_tipo_sin_iva,
        #     total_tipo_iva=total_tipo_iva,
        #     total_tipo_credito=total_tipo_credito,
        # )
        # row = self.dibujar_total_tipo(ws, wb, row, dic_total_tipo)
        #total general
        ws.write(
            'I'+str(row),
            'TOTAL GENERAL:',
            self.format_bold_right_border(wb),
        )
        ws.write(
            'J'+str(row),
            total_general_tarifa,
            self.format_amount_bold__bordertop_right(wb),
        )
        ws.write(
            'K'+str(row),
            total_general_con_iva,
            self.format_amount_bold__bordertop_right(wb),
        )
        ws.write(
            'L'+str(row),
            total_general_descuento,
            self.format_amount_bold__bordertop_right(wb),
        )
        ws.write(
            'M'+str(row),
            total_general_sin_iva,
            self.format_amount_bold__bordertop_right(wb),
        )
        ws.write(
            'N'+str(row),
            total_general_iva,
            self.format_amount_bold__bordertop_right(wb),
        )
        ws.write(
            'O'+str(row),
            0,
            self.format_amount_bold__bordertop_right(wb),
        )
        ws.write(
            'P'+str(row),
            total_general_credito,
            self.format_amount_bold__bordertop_right(wb),
        )
        row += 2
        #Resumen
        ws.merge_range(
            "A"+str(row)+":F"+str(row),
            'R E S U M E N',
            self.format_bold_center(wb, 10),
        )
        row += 2
        ws.merge_range(
            "A"+str(row)+":B"+str(row),
            'VENTAS POR SERIE',
            self.format_bold_left(wb, 10),
        )
        row_serie = row + 1
        for serie in lista_serie:
            ws.write(
                "A"+str(row_serie),
                serie,
                self.format_left(wb, 10),
            )
            row_serie += 1

        ws.merge_range(
            "D"+str(row)+":E"+str(row),
            'DOCUMENTOS GENERADOS',
            self.format_bold_center(wb, 10),
        )
        row += 2
        ws.write(
            'D'+str(row),
            'Total Facturas',
            self.format_bold_border_left(wb, 10),
        )
        ws.write(
            'E'+str(row),
            lista_resumen[0]['total_facturas'],
            self.format_integer_border_right(wb, 10),
        )
        row += 1
        ws.write(
            'D'+str(row),
            'Total Devoluciones',
            self.format_bold_border_left(wb, 10),
        )
        ws.write(
            'E'+str(row),
            lista_resumen[0]['total_devoluciones'],
            self.format_integer_border_right(wb, 10),
        )
        row += 1
        ws.write(
            'D'+str(row),
            'Total Anuladas',
            self.format_bold_border_left(wb, 10),
        )
        ws.write(
            'E'+str(row),
            lista_resumen[0]['total_anuladas'],
            self.format_integer_border_right(wb, 10),
        )
        row += 2
        ws.merge_range(
            "D"+str(row)+":E"+str(row),
            'FORMAS DE VENTAS',
            self.format_bold_center(wb, 10),
        )
        row += 2
        ws.write(
            'D'+str(row),
            'Ventas Contado',
            self.format_border_left(wb, 10),
        )
        ws.write(
            'E'+str(row),
            0,
            self.format_amount_border_right(wb, 10),
        )
        row += 1
        ws.write(
            'D'+str(row),
            'Ventas Crédito'.decode("utf-8"),
            self.format_border_left(wb, 10),
        )
        ws.write(
            'E'+str(row),
            total_general_credito,
            self.format_amount_border_right(wb, 10),
        )
        row += 1
        ws.write(
            'D'+str(row),
            'Total Ventas',
            self.format_bold_left(wb, 10),
        )        
        ws.write(
            'E'+str(row),
            total_general_credito,
            self.format_amount_bold_right(wb, 10),
        )
        row += 2
        ws.merge_range(
            "A"+str(row)+":F"+str(row),
            'D E S G L O C E',
            self.format_bold_center(wb, 10),
        )       
        row += 2
        ws.write(
            'A'+str(row),
            '',
            self.format_border_left(wb, 10),
        )
        ws.write(
            'B'+str(row),
            'VTA_CON_IVA',
            self.format_bold_border_center(wb, 10),
        )
        ws.write(
            'C'+str(row),
            'VTA_SIN_IVA',
            self.format_bold_border_center(wb, 10),
        )
        ws.write(
            'D'+str(row),
            'DESCUENTO',
            self.format_bold_border_center(wb, 10),
        )
        ws.write(
            'E'+str(row),
            'IMPUESTO',
            self.format_bold_border_center(wb, 10),
        )
        ws.write(
            'F'+str(row),
            'TOTAL',
            self.format_bold_border_center(wb, 10),
        )
        row += 1
        ws.write(
            'A'+str(row),
            'Ventas',
            self.format_bold_border_left(wb, 10),
        )
        ws.write(
            'B'+str(row),
            total_general_con_iva,
            self.format_amount_border_right(wb, 10),
        )
        ws.write(
            'C'+str(row),
            total_general_tarifa,
            self.format_amount_border_right(wb, 10),
        )
        ws.write(
            'D'+str(row),
            total_general_descuento,
            self.format_amount_border_right(wb, 10),
        )
        ws.write(
            'E'+str(row),
            total_general_iva,
            self.format_amount_border_right(wb, 10),
        )
        total_fila_ventas = ((total_general_con_iva + total_general_tarifa) - total_general_descuento) + total_general_iva
        ws.write(
            'F'+str(row),
            total_fila_ventas,
            self.format_amount_bold_border_right(wb, 10),
        )
        row += 1
        ws.write(
            'A'+str(row),
            'Devolución'.decode('utf-8'),
            self.format_bold_border_left(wb, 10),
        )
        tot_con_iva_dev = lista_resumen[0]['total_con_iva_devoluciones']
        ws.write(
            'B'+str(row),
            tot_con_iva_dev,
            self.format_amount_border_right(wb, 10),
        )
        tot_tarifa_dev = lista_resumen[0]['total_tarifa_devoluciones']
        ws.write(
            'C'+str(row),
            tot_tarifa_dev,
            self.format_amount_border_right(wb, 10),
        )
        tot_desc_dev = lista_resumen[0]['total_descuento_devoluciones']
        ws.write(
            'D'+str(row),
            tot_desc_dev,
            self.format_amount_border_right(wb, 10),
        )
        tot_iva_dev = lista_resumen[0]['total_iva_devoluciones']
        ws.write(
            'E'+str(row),
            tot_iva_dev,
            self.format_amount_border_right(wb, 10),
        )
        tot_dev = (tot_con_iva_dev + tot_tarifa_dev + tot_iva_dev) - tot_desc_dev
        ws.write(
            'F'+str(row),
            tot_dev,
            self.format_amount_bold_border_right(wb, 10),
        )
        row += 1
        ws.write(
            'A'+str(row),
            'TOTALES',
            self.format_bold_right(wb, 10),
        )
        ws.write(
            'B'+str(row),
            total_general_con_iva,
            self.format_amount_bold_right(wb, 10),
        )
        ws.write(
            'C'+str(row),
            total_general_sin_iva,
            self.format_amount_bold_right(wb, 10),
        )
        ws.write(
            'D'+str(row),
            total_general_descuento,
            self.format_amount_bold_right(wb, 10),
        )
        ws.write(
            'E'+str(row),
            total_general_iva,
            self.format_amount_bold_right(wb, 10),
        )
        ws.write(
            'F'+str(row),
            total_fila_ventas,
            self.format_amount_bold_right(wb, 10),
        )
        row += 2
        ws.write(
            'A'+str(row),
            'Reembolsos',
            self.format_bold_left(wb, 10),
        )
        ws.write(
            'B'+str(row),
            lista_resumen[0]['reembolso_con_iva'],
            self.format_amount_bold_right(wb, 10),
        )
        ws.write(
            'C'+str(row),
            lista_resumen[0]['reembolso_sin_iva'],
            self.format_amount_bold_right(wb, 10),
        )
        ws.write(
            'D'+str(row),
            lista_resumen[0]['reembolso_descuento'],
            self.format_amount_bold_right(wb, 10),
        )
        ws.write(
            'E'+str(row),
            lista_resumen[0]['reembolso_iva'],
            self.format_amount_bold_right(wb, 10),
        )
        total_reembolso = (((lista_resumen[0]['reembolso_con_iva'] + lista_resumen[0]['reembolso_sin_iva'])
            - lista_resumen[0]['reembolso_descuento']) + lista_resumen[0]['reembolso_iva'])
        ws.write(
            'F'+str(row),
            total_reembolso,
            self.format_amount_bold_right(wb, 10),
        )
        row += 2
        ws.merge_range(
            "A"+str(row)+":A"+str(row + 1),
            'Subtotal',
            self.format_bold_center_vcenter_border(wb, 10),
        )
        ws.write(
            'B'+str(row),
            'Subtotal',
            self.format_bold_border_center(wb, 10),
        )
        ws.write(
            'C'+str(row),
            'Descuento',
            self.format_bold_border_center(wb, 10),
        )
        ws.write(
            'D'+str(row),
            'Impuesto',
            self.format_bold_border_center(wb, 10),
        )
        ws.write(
            'E'+str(row),
            'Total',
            self.format_bold_border_center(wb, 10),
        )
        row += 1
        ws.write(
            'B'+str(row),
            total_general_sin_iva,
            self.format_amount_border_right(wb, 10),
        )    
        ws.write(
            'C'+str(row),
            total_general_descuento,
            self.format_amount_border_right(wb, 10),
        )  
        ws.write(
            'D'+str(row),
            total_general_iva,
            self.format_amount_border_right(wb, 10),
        )
        total =  (((total_general_con_iva + total_general_tarifa) - total_general_descuento) + total_general_iva)
        ws.write(
            'E'+str(row),
            total,
            self.format_amount_border_right(wb, 10),
        )
