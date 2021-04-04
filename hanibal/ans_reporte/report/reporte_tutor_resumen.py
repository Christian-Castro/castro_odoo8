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

class reporteTutorResumido(models.TransientModel):
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
    def generar_reporte_tutor_resumen_xlsx(self):
        fp = self.generar_archivo_tutor_resumido()
        return self.download_file(fp, "Informe Tutor Resumido.xlsx")

    @api.multi
    def generar_reporte_tutor_resumen_pdf(self):
        fp = self.generar_archivo_tutor_resumido()
        return self.download_file(fp, "Informe Tutor Resumido.xlsx", True)

    def generar_archivo_tutor_resumido(self):
        wb, ws, fp = self.crear_workbook('Informe Tutor Resumido')
        self.setear_ancho_columna_tutor_resumido(ws)
        self.setear_tamano_hoja(ws, 9)
        self.setear_hoja_orientacion(ws, True)
        # self.mostrar_paginas_derecha_cabecera(ws)
        self.ocultar_lineas_xlsx(ws)
        data_tutor_resumido = self.construir_data_tutor_resumido()
        self.dibujar_cabecera_tutor_resumido(wb, ws, data_tutor_resumido)
        self.dibujar_tabla_tutor_resumido(wb, ws, data_tutor_resumido)
        self.setear_columna_por_entrada(ws, data_tutor_resumido)
        # self.repetir_fila_en_cada_hoja(ws, 1, 6)
        self.ajustar_pagina_a_n_columnas(ws)
        wb.close()
        return fp

    def setear_ancho_columna_tutor_resumido(self, ws):
        ws.set_column('A:A', 30.14)
        ws.set_column('B:B', 35)
        ws.set_column('C:C', 9.29)
        ws.set_column('E:E', 35)
        ws.set_column('F:F', 11)
        ws.set_column('G:G', 17.71)


    def setear_columna_por_entrada(self, ws, data_tutor_resumido):
        # columna_b = []
        columna_d = []
        # columna_e = []
        columna_f = []
        columna_g = []
        for jornada in data_tutor_resumido:
            for det in jornada['detalle']:
                # columna_b.append(len(str(det['cliente'].replace("\xd1", 'n'))))
                columna_d.append(len(str(det['email'])))
                # columna_e.append(len(str(det['alumno'])))
                columna_f.append(len(str(det['saldo'])))
                columna_g.append(len(str(det['comentario'])))
        # ws.set_column('B:B', max(columna_b))
        ws.set_column('D:D', max(columna_d if columna_d else [10]))

    def construir_data_tutor_resumido(self):
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
                invoice_filtro = invoice_alumno_ids.filtered(lambda invoice_alumno: invoice_alumno.alumno_id.name == alumno)
                codigo_alumno = list(set(invoice_filtro.mapped('alumno_id.codigo_alumno')))
                cliente = list(set(invoice_filtro.mapped('partner_id.name')))
                telefono = list(set(invoice_filtro.mapped('partner_id.phone')))
                email = list(set(invoice_filtro.mapped('partner_id.email')))
                saldo = sum(invoice_filtro.mapped('residual'))
                comentario = list(set(invoice_filtro.mapped('invoice_line.name')))
                fecha = []
                convenio_pago = []
                for invoice in invoice_filtro:
                    mail_message = model_mail_message.search([('id', 'in', invoice.message_ids.ids)])
                    convenio_pago += [message.body.replace('<p>', '').replace('</p>', '').replace('<br>', ' ')
                        for message in mail_message if message.type == 'comment']
                    fecha += [str(message.date)[0:10] for message in mail_message if message.type == 'comment']

                if invoice_filtro:
                    lista_detalle.append({
                        'codigo_alumno': codigo_alumno[0],
                        'cliente': cliente[0],
                        'telefono': telefono[0],
                        'email': email[0],
                        'alumno': alumno,
                        'saldo': saldo,
                        'comentario': '\n'.join(comentario),
                        'fecha': '\n'.join(list(set(fecha))) if fecha else '',
                        'convenio_pago': '\n'.join(list(set(convenio_pago))) if convenio_pago else '',
                    })
            if lista_detalle:
                lista_jornada.append({
                    'detalle': lista_detalle,
                    'seccion': rec['seccion'],
                    'curso': rec['curso'],
                    'paralelo': rec['paralelo'],
                })
        return lista_jornada
        

    def dibujar_cabecera_tutor_resumido(self, wb, ws, data_tutor_resumido):
        tamano_letra_cabecera = 10
        ws.merge_range(
            "A1:C1",
            "REPORTE TUTOR RESUMIDO",
            self.format_bold_left(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A3:J3",
            "CENTRO EDUCATIVO NUEVA SEMILLA S.A. CENUSA",
            self.format_bold_center(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A4:J4",
            "COBRANZAS %s" %(self.jornada_id.display_name),
            self.format_bold_center(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A5:J5",
            str(datetime.now())[0:10],
            self.format_bold_center(wb, tamano_letra_cabecera),
        )

    def dibujar_tabla_tutor_resumido(self, wb, ws, data_tutor_resumido):
        row = 6
        for jornada in data_tutor_resumido:
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
                'Código Alumno Del Banco Recaudaciones Sat'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'B'+str(row),
                'Nombre Del Cliente \n (Representante)',
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
                'Alumno',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'F'+str(row),
                'Saldo Actual',
                self.format_bold_border_center(wb)
            )
            ws.write(
                'G'+str(row),
                'Comentario',
                self.format_bold_border_center(wb)
            )
            ws.merge_range(
                'H'+str(row - 1)+':J'+str(row - 1),
                'Gestión de Cobranzas'.decode('utf-8'),
                self.format_bold_border_center(wb)
            )
            ws.write(
                'H'+str(row),
                'Fecha',
                self.format_bold_border_center(wb)
            )
            ws.merge_range(
                'I'+str(row)+':J'+str(row),
                'Convenio De Pago',
                self.format_bold_border_center(wb)
            )
            row += 1
            for det in jornada['detalle']:
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
                    det['alumno'],
                    self.format_left_borderTopBottom(wb)
                )
                ws.write(
                    'F'+str(row),
                    det['saldo'] if det['saldo'] > 0 else '',
                    self.format_amount_borderTopBottom_right(wb)
                )
                ws.write(
                    'G'+str(row),
                    det['comentario'],
                    self.format_left_borderTopBottom(wb)
                )
                ws.write(
                    'H'+str(row),
                    det['fecha'],
                    self.format_left_borderTopBottom(wb)
                )
                ws.merge_range(
                    'I'+str(row)+':J'+str(row),
                    det['convenio_pago'],
                    self.format_left_borderTopBottom(wb)
                )
                row += 1
            row += 2
