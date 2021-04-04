# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import io
from datetime import datetime, date
from openerp.tools.safe_eval import safe_eval
from openerp.tools import ustr, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import ValidationError
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
    def generar_reporte_gestion_cobranza_xlsx(self):
        fp = self.generar_archivo()
        return self.download_file(fp, "Reporte Informe Gestión Cobranza.xlsx".decode('utf-8'))

    @api.multi
    def generar_reporte_gestion_cobranza_pdf(self):
        fp = self.generar_archivo()
        return self.download_file(fp, "Reporte Informe Gestión Cobranza.xlsx".decode('utf-8'), True)

    def generar_archivo(self):
        wb, ws, fp = self.crear_workbook('Gestión Cobranza'.decode('utf-8'))
        self.setear_ancho_columna_gestion_cobranza(ws)
        self.setear_tamano_hoja(ws, 9)
        self.setear_hoja_orientacion(ws, True)
        # self.mostrar_paginas_derecha_cabecera(ws)
        self.ocultar_lineas_xlsx(ws)
        data_jornada = self.construir_data_gestion_cobranza()
        self.dibujar_cabecera_gestion_cobranza(wb, ws, data_jornada)
        self.dibujar_tabla_gestion_cobranza(wb, ws, data_jornada)
        # self.repetir_fila_en_cada_hoja(ws, 1, 6)
        self.ajustar_pagina_a_n_columnas(ws)
        wb.close()
        return fp

    def setear_ancho_columna_gestion_cobranza(self, ws):
        ws.set_column('A:A', 10.43)
        ws.set_column('B:B', 35)
        ws.set_column('C:C', 14)
        ws.set_column('D:D', 22)
        ws.set_column('E:E', 18.71)
        ws.set_column('F:F', 35)
        ws.set_column('G:G', 9.57)
        ws.set_column('H:H', 9)
        ws.set_column('I:I', 17.71)

    def construir_data_gestion_cobranza(self):
        model_invoice = self.env['account.invoice']
        model_mail_message = self.env['mail.message']
        cliente_id = "[('partner_id', '=', %s)]" %(self.cliente_id.id) if self.cliente_id else "[]"
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

        if not invoice_ids:
            raise ValidationError("No hay datos para generar el archivo")

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
                    mail_message = model_mail_message.search([('id', 'in', invoice.message_ids.ids)])
                    convenio_pago = [message.body.replace('<p>', '').replace('</p>', '').replace('<br>', ' ')
                        for message in mail_message if message.type == 'comment']
                    fecha = [str(message.date)[0:10] for message in mail_message if message.type == 'comment']

                    lista_quiebre_alumno.append({
                        'codigo_alumno': invoice.alumno_id.codigo_alumno,
                        'cliente': invoice.partner_id.name,
                        'telefono': invoice.partner_id.phone,
                        'email': invoice.partner_id.email,
                        'numero': invoice.numerofac,
                        'alumno': invoice.alumno_id.name,
                        'fecha_emision': invoice.date_invoice,
                        'saldo': invoice.residual,
                        'comentario': '\n'.join(list(set([line.name for line in invoice.invoice_line]))),
                        'fecha': '\n'.join(list(set(fecha))) if fecha else '',
                        'convenio_pago': '\n'.join(list(set(convenio_pago))) if convenio_pago else '',
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
        

    def dibujar_cabecera_gestion_cobranza(self, wb, ws, data_jornada):
        tamano_letra_cabecera = 10
        ws.merge_range(
            "A1:C1",
            "REPORTE FINANCIERO  AREA COBRANZAS (ADMISTRACIÓN Y CONTABILIDAD)".decode('utf-8'),
            self.format_bold_left(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A3:L3",
            "CENTRO EDUCATIVO NUEVA SEMILLA S.A. CENUSA",
            self.format_bold_center(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A4:L4",
            "COBRANZAS %s" %(self.jornada_id.display_name),
            self.format_bold_center(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A5:L5",
            str(datetime.now())[0:10],
            self.format_bold_center(wb, tamano_letra_cabecera),
        )

    def dibujar_tabla_gestion_cobranza(self, wb, ws, data_jornada):
        row = 7
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
                'Cliente',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'C'+str(row),
                'Teléfono'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'D'+str(row),
                'Email',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'E'+str(row),
                'Número Factura'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'F'+str(row),
                'Alumno',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'G'+str(row),
                'Fecha Emisión'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'H'+str(row),
                'Saldo Actual',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'I'+str(row),
                'Comentario',
                self.format_bold_border_center(wb)
            )
            ws.merge_range(
                'J'+str(row - 1)+':L'+str(row - 1),
                'Gestión de Cobranzas'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'J'+str(row),
                'Fecha',
                self.format_bold_border_center(wb)
            )
            ws.merge_range(
                'K'+str(row)+':L'+str(row),
                'Convenio De Pago',
                self.format_bold_border_center(wb)
            )
            row += 1
            for detalle in jornada['detalle']:
                alumno = ''
                saldo = 0
                for det in detalle['detalle_alumno']:
                    ws.write(
                        'A'+str(row),
                        det['codigo_alumno'],
                        self.format_center_borderTopBottom(wb)
                    )
                    ws.write(
                        'B'+str(row),
                        det['cliente'],
                        self.format_left_borderTopBottom(wb)
                    )
                    ws.write(
                        'C'+str(row),
                        det['telefono'] if det['telefono'] else '',
                        self.format_center_borderTopBottom(wb)
                    )
                    ws.write(
                        'D'+str(row),
                        det['email'] if det['email'] else '',
                        self.format_left_borderTopBottom(wb)
                    )
                    ws.write(
                        'E'+str(row),
                        det['numero'] if det['numero'] else '',
                        self.format_center_borderTopBottom(wb)
                    )
                    ws.write(
                        'F'+str(row),
                        det['alumno'],
                        self.format_left_borderTopBottom(wb)
                    )
                    ws.write(
                        'G'+str(row),
                        det['fecha_emision'],
                        self.format_date_center_borderTopBottom(wb)
                    )
                    ws.write(
                        'H'+str(row),
                        det['saldo'] if det['saldo'] else '',
                        self.format_amount_borderTopBottom_right(wb)
                    )
                    saldo += det['saldo']
                    total_general_saldo += det['saldo']
                    ws.write(
                        'I'+str(row),
                        det['comentario'],
                        self.format_left_borderTopBottom(wb)
                    )
                    row += 1
                    alumno = det['alumno']
                    ws.write(
                        'J'+str(row),
                        det['fecha'],
                        self.format_left_borderTopBottom(wb)
                    )
                    ws.merge_range(
                        'K'+str(row)+':L'+str(row),
                        det['convenio_pago'],
                        self.format_left_borderTopBottom(wb)
                    )
                #total por alumno    
                ws.write(
                    'F'+str(row),
                    'Total %s'.decode('utf-8') %(alumno),
                    self.format_left_bold_borderTopBottom(wb)
                )
                ws.write(
                    'H'+str(row),
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
            'G'+str(row),
            'TOTAL',
            self.format_bold_center(wb)
        )
        ws.write(
            'H'+str(row),
            total_general_saldo,
            self.format_amount_bold_right(wb)
        )
