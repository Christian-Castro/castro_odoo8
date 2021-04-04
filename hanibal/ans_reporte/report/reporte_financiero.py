# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import io
from datetime import datetime, date
from openerp.tools.safe_eval import safe_eval
from openerp.tools import ustr, DEFAULT_SERVER_DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)
try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')

class reporteFinanniero(models.TransientModel):
    _name = "reporte.cobranza"
    _inherit = ["reporte.cobranza", "reporte.utileria"]

    cliente_id = fields.Many2one(
        string='Cliente',
        comodel_name='res.partner',
    )
    alumno_id = fields.Many2one(
        string='Alumno',
        comodel_name='res.partner',
    )

    @api.multi
    def generar_reporte_financiero_xlsx(self):
        fp = self.generar_archivo_financiero()
        return self.download_file(fp, "Reporte Financiero.xlsx")

    @api.multi
    def generar_reporte_financiero_pdf(self):
        fp = self.generar_archivo_financiero()
        return self.download_file(fp, "Reporte Financiero.xlsx", True)

    def generar_archivo_financiero(self):
        wb, ws, fp = self.crear_workbook('Financiero')
        self.setear_ancho_columna_financiero(ws)
        self.setear_tamano_hoja(ws, 9)
        self.setear_hoja_orientacion(ws, True)
        # self.mostrar_paginas_derecha_cabecera(ws)
        self.ocultar_lineas_xlsx(ws)
        data_jornada = self.construir_data_financiero()
        self.dibujar_cabecera_financiero(wb, ws, data_jornada)
        self.dibujar_tabla_financiero(wb, ws, data_jornada)
        # self.repetir_fila_en_cada_hoja(ws, 1, 6)
        self.ajustar_pagina_a_n_columnas(ws)
        wb.close()
        return fp

    def setear_ancho_columna_financiero(self, ws):
        ws.set_column('A:A', 10.43)
        ws.set_column('B:B', 35)
        ws.set_column('C:C', 14)
        ws.set_column('D:D', 9.71)
        ws.set_column('E:E', 18.71)
        ws.set_column('F:F', 11)
        ws.set_column('G:G', 11)
        ws.set_column('H:H', 11)
        ws.set_column('I:I', 15)
        ws.set_column('J:J', 11)
        ws.set_column('K:K', 17.71)

    def construir_data_financiero(self):
        model_invoice = self.env['account.invoice']
        cliente_id = "[('partner_id', '=', %s)]" %(self.cliente_id) if self.cliente_id else "[]"
        alumno_id = "[('alumno_id', '=', %s)]" %(self.alumno_id.id) if self.alumno_id else "[]"
        journal_ids = "[('journal_id', 'in', %s)]" %(self.journal_ids.ids) if self.journal_ids else "[]"

        invoice_ids = model_invoice.search(
            [
                ('jornada_id', '=', self.jornada_id.id),
                ('date_invoice', '>=', self.fecha_desde),
                ('date_invoice', '<=', self.fecha_hasta),
                ('state', 'in', ['open', 'paid']),
                ('escuela', '=', True),
                ('type', '=', 'out_invoice'),
            ] + safe_eval(cliente_id)+safe_eval(alumno_id)+safe_eval(journal_ids),
        )

        self.env.cr.execute("""
                select 
                    s.name as seccion,
                    c.name as curso,
                    p.codigo as paralelo
                from account_invoice ai 
                inner join seccion s on s.id = ai.seccion_id
                inner join jornada j on j.id = ai.jornada_id
                inner join curso c on c.id = ai.curso_id
                inner join paralelo p on p.id = ai.paralelo_id
                where ai.id in %s
                group by 1,2,3
                order by 1,2,3
            """ %(str(tuple(invoice_ids.ids)))
        )
        quiebres = self.env.cr.dictfetchall()

        lista_jornada = []
        for rec in quiebres:
            lista_detalle = []
            invoice_alumno_ids = invoice_ids.filtered(lambda invoice_seccion: invoice_seccion.seccion_id.name == rec['seccion']
                                                and invoice_seccion.curso_id.name == rec['curso']
                                                and invoice_seccion.paralelo_id.codigo == rec['paralelo'])
            alumno_names = sorted(list(set(invoice_alumno_ids.mapped('alumno_id.name'))))
            for alumno in alumno_names:
                lista_quiebre_alumno = []
                for invoice in invoice_alumno_ids.filtered(lambda invoice_alumno: invoice_alumno.alumno_id.name == alumno):
                    lista_quiebre_alumno.append({
                        'codigo_alumno': invoice.alumno_id.codigo_alumno,
                        'alumno': invoice.alumno_id.name,
                        'numero': invoice.numerofac,
                        'fecha_emision': invoice.date_invoice,
                        'fecha_vencimiento': invoice.date_due,
                        'dias_mora': (datetime.now() - self.strToDatetime(invoice.date_due)).days,
                        'valor': invoice.amount_total,
                        'pagos': sum(line.credit for line in (invoice.filtered(
                                lambda diario: diario.journal_id.cheques_postfechados == False)).payment_ids),
                        "cheques_postfechados": sum(line.credit for line in (invoice.filtered(
                                lambda diario: diario.journal_id.cheques_postfechados == True)).payment_ids),
                        'saldo': invoice.residual,
                        'comentario': '\n'.join([line.name for line in invoice.invoice_line]),
                    })
                if lista_quiebre_alumno:
                    lista_detalle.append({
                        'detalle_alumno': lista_quiebre_alumno,
                    })
            if lista_detalle:
                lista_jornada.append({
                    'detalle': lista_detalle,
                    'seccion': rec['seccion'],
                    'curso': rec['curso'],
                    'paralelo': rec['paralelo'],
                })
        return lista_jornada
        

    def dibujar_cabecera_financiero(self, wb, ws, data_jornada):
        tamano_letra_cabecera = 10
        ws.merge_range(
            "A1:C1",
            "REPORTE FINANCIERO DE COBRANZAS PARA CONTABILIDAD",
            self.format_bold_left(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A3:K3",
            "COBRANZAS %s" %(self.jornada_id.display_name),
            self.format_bold_center(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A4:K4",
            str(datetime.now())[0:10],
            self.format_bold_center(wb, tamano_letra_cabecera),
        )

    def dibujar_tabla_financiero(self, wb, ws, data_jornada):
        row = 6
        total_general_dias_mora = 0
        total_general_valor = 0
        total_general_pagos = 0
        total_general_cheques_postfechados = 0
        total_general_saldo = 0
        for jornada in data_jornada:
            ws.write(
                'A'+str(row),
                'Fecha De Corte',
                self.format_bold_left(wb)
            )
            ws.write(
                'B'+str(row),
                datetime.now(),
                self.format_date_center(wb)
            )
            row += 1
            ws.write(
                'A'+str(row),
                'Curso',
                self.format_bold_left(wb)
            )
            ws.write(
                'B'+str(row),
                jornada['curso'],
                self.format_left(wb)
            )
            ws.write(
                'D'+str(row),
                'Paralelo: %s' %(jornada['paralelo']),
                self.format_left(wb)
            )
            ws.write(
                'E'+str(row),
                'Sección: %s'.decode('utf-8') %(jornada['seccion']),
                self.format_left(wb)
            )
            row += 3
            ws.write(
                'A'+str(row),
                'Código Alumno'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'B'+str(row),
                'Alumno',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'C'+str(row),
                'Número'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'D'+str(row),
                'Emisión'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'E'+str(row),
                'Vencimiento',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'F'+str(row),
                'Días Mora'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'G'+str(row),
                'Valor',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'H'+str(row),
                'Pagos(Abonos)',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'I'+str(row),
                'Cheques Postfechados',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'J'+str(row),
                'Saldo Actual',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'K'+str(row),
                'Comentario',
                self.format_bold_border_center(wb)
            )
            row += 1
            for detalle in jornada['detalle']:
                alumno = ''
                dias_mora = 0
                valor = 0
                pagos = 0
                cheques_postfechados = 0
                saldo = 0
                for det in detalle['detalle_alumno']:
                    ws.write(
                        'A'+str(row),
                        det['codigo_alumno'],
                        self.format_center_borderTopBottom(wb)
                    )
                    ws.write(
                        'B'+str(row),
                        det['alumno'],
                        self.format_left_borderTopBottom(wb)
                    )
                    ws.write(
                        'C'+str(row),
                        det['numero'] if det['numero'] else '',
                        self.format_center_borderTopBottom(wb)
                    )
                    ws.write(
                        'D'+str(row),
                        det['fecha_emision'],
                        self.format_date_center_borderTopBottom(wb)
                    )
                    ws.write(
                        'E'+str(row),
                        det['fecha_vencimiento'],
                        self.format_date_center_borderTopBottom(wb)
                    )
                    ws.write(
                        'F'+str(row),
                        det['dias_mora'] if det['dias_mora'] > 0 else '',
                        self.format_integer_borderTopBottom_right(wb)
                    )
                    dias_mora += det['dias_mora']
                    total_general_dias_mora += det['dias_mora']
                    ws.write(
                        'G'+str(row),
                        det['valor'] if det['valor'] > 0 else '',
                        self.format_amount_borderTopBottom_right(wb)
                    )
                    valor += det['valor']
                    total_general_valor += det['valor'] 
                    ws.write(
                        'H'+str(row),
                        det['pagos'] if det['pagos'] > 0 else '',
                        self.format_amount_borderTopBottom_right(wb)
                    )
                    pagos += det['pagos']
                    total_general_pagos += det['pagos']
                    ws.write(
                        'I'+str(row),
                        det['cheques_postfechados'] if det['cheques_postfechados'] > 0 else '',
                        self.format_amount_borderTopBottom_right(wb)
                    )
                    cheques_postfechados += det['cheques_postfechados']
                    total_general_cheques_postfechados += det['cheques_postfechados']
                    ws.write(
                        'J'+str(row),
                        det['saldo'] if det['saldo'] > 0 else '',
                        self.format_amount_borderTopBottom_right(wb)
                    )
                    saldo += det['saldo']
                    total_general_saldo += det['saldo']
                    ws.write(
                        'K'+str(row),
                        det['comentario'],
                        self.format_left_borderTopBottom(wb)
                    )
                    row += 1
                    alumno = det['alumno']
                #total por alumno    
                ws.write(
                    'B'+str(row),
                    'Total %s' %(alumno),
                    self.format_left_bold_borderTopBottom(wb)
                )
                ws.write(
                    'F'+str(row),
                    dias_mora,
                    self.format_integer_bold_borderTopBottom_right(wb)
                )
                ws.write(
                    'G'+str(row),
                    valor,
                    self.format_amount_bold_borderTopBottom_right(wb)
                )
                ws.write(
                    'H'+str(row),
                    pagos,
                    self.format_amount_bold_borderTopBottom_right(wb)
                )
                ws.write(
                    'I'+str(row),
                    cheques_postfechados,
                    self.format_amount_bold_borderTopBottom_right(wb)
                )
                ws.write(
                    'J'+str(row),
                    saldo,
                    self.format_amount_bold_borderTopBottom_right(wb)
                )
                row += 1
            row += 3
        #total general
        row -= 1
        ws.merge_range(
            'A'+str(row)+':B'+str(row),
            'Elaborado Por:',
            self.format_bold_left(wb)
        )
        ws.merge_range(
            'C'+str(row)+':D'+str(row),
            self.env.user.display_name,
            self.format_left(wb)
        )
        ws.write(
            'E'+str(row),
            'TOTAL',
            self.format_bold_center(wb)
        )
        ws.write(
            'F'+str(row),
            total_general_dias_mora,
            self.format_amount_bold_right(wb)
        )
        ws.write(
            'G'+str(row),
            total_general_valor,
            self.format_amount_bold_right(wb)
        )
        ws.write(
            'H'+str(row),
            total_general_pagos,
            self.format_amount_bold_right(wb)
        )
        ws.write(
            'I'+str(row),
            total_general_cheques_postfechados,
            self.format_amount_bold_right(wb)
        )
        ws.write(
            'J'+str(row),
            total_general_saldo,
            self.format_amount_bold_right(wb)
        )

    def strToDatetime(self, strdate):
        return datetime.strptime(strdate, DEFAULT_SERVER_DATE_FORMAT)
