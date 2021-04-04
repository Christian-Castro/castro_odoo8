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

class reporteCobranzaAlumno(models.TransientModel):
    _name = "reporte.cobranza"
    _inherit = ["reporte.cobranza", "reporte.utileria"]

    # ver_resumen = fields.Boolean(string="Ver Resumen",default=False)

    @api.multi
    def generar_archivo_xlsx(self):
        fp = self.generar_archivo_mensualidad()
        return self.download_file(fp, "Resumen Cuentas Por Cobrar.xlsx")

    @api.multi
    def generar_archivo_pdf(self):
        fp = self.generar_archivo_mensualidad()
        return self.download_file(fp, "Resumen Cuentas Por Cobrar.xlsx", True)

    def generar_archivo_mensualidad(self):
        wb, ws, fp = self.crear_workbook('Resumen Cuentas Por Cobrar')
        self.setear_ancho_columna(ws)
        self.setear_tamano_hoja(ws, 9)
        self.setear_hoja_orientacion(ws, True)
        # self.mostrar_paginas_derecha_cabecera(ws)
        self.ocultar_lineas_xlsx(ws)
        data_jornada = self.construir_data_mensualidad()
        self.dibujar_cabecera_mensualidad(wb, ws, data_jornada)
        self.dibujar_tabla_mensualidad(wb, ws, data_jornada)
        # self.repetir_fila_en_cada_hoja(ws, 1, 6)
        self.ajustar_pagina_a_n_columnas(ws)
        wb.close()
        return fp

    def setear_ancho_columna(self, ws):
        ws.set_column('A:A', 18)
        ws.set_column('B:B', 15)
        ws.set_column('C:C', 15)
        ws.set_column('D:D', 15)
        ws.set_column('E:E', 15)
        ws.set_column('F:F', 15)
        ws.set_column('G:G', 15)
        ws.set_column('H:H', 15)
        ws.set_column('J:J', 15)
        ws.set_column('K:K', 15)
        ws.set_column('L:L', 15)
        ws.set_column('M:M', 15)

    def construir_data_mensualidad(self):
        model_invoice =self.env['account.invoice']
        model_seccion =self.env['seccion']
        if not self.seccion_id:
            seccion_id = "[]"
        else:
            seccion_id = "[('seccion_id', '=', %s)]" %(self.seccion_id.id)
        invoice_ids = model_invoice.search(
            [
                ('jornada_id', '=', self.jornada_id.id),
                ('date_invoice', '>=', self.fecha_desde),
                ('date_invoice', '<=', self.fecha_hasta),
                ('state', 'in', ['open', 'paid']),
                ('escuela', '=', True),
                ('type', '=', 'out_invoice'),
            ] + safe_eval(seccion_id),
        )

        lista_seccion = []
        for seccion in model_seccion.search([]):
            saldo = []
            lista_curso = []
            lista_paralelo = []
            lista_diario = []
            invoice_seccion_ids = invoice_ids.filtered(lambda invoice: invoice.seccion_id.id == seccion.id)
            curso = sorted(list(set([invoice.curso_id.display_name for invoice in invoice_seccion_ids])))
            paralelo = sorted(list(set([invoice.paralelo_id.display_name for invoice in invoice_seccion_ids])))
            diario = sorted(list(set([invoice.journal_id.display_name for invoice in invoice_seccion_ids])))
            for cur in curso:
                for par in paralelo:
                    for diar in diario:
                        saldo_factura = sum((invoice.amount_total - (sum([line.credit for line in invoice.payment_ids if line.date <= self.fecha_hasta]))
                                        ) for invoice in invoice_seccion_ids.filtered(
                                    lambda invoice: invoice.curso_id.display_name == cur
                                    and invoice.paralelo_id.display_name == par
                                    and invoice.journal_id.display_name == diar
                                ))
                        lista_curso.append(cur)
                        lista_paralelo.append(par)
                        lista_diario.append(diar)
                        saldo.append(saldo_factura)

            curso_dic = {
                'curso': lista_curso,
                'paralelo': lista_paralelo,
                'diario': lista_diario,
                'saldo': saldo,
                'seccion_id': seccion.id,
                'seccion_name': seccion.display_name,
            }
            lista_seccion.append(curso_dic)

        return lista_seccion

        # lista_seccion = []
        # invoice_seccions = sorted(list(set(invoice_ids.mapped('seccion_id.name'))))
        # for seccion in invoice_seccions:
        #     lista_curso = []
        #     lista_paralelo = []
        #     lista_diario = []
        #     saldo = []
        #     filtro_ids = invoice_ids.filtered(lambda filtro: filtro.seccion_id.name == seccion)
        #     self.env.cr.execute("""
        #             select
        #                 c.name as curso,
        #                 p.codigo as paralelo,
        #                 aj.name as diario
        #             from account_invoice ai
        #             inner join jornada j on j.id = ai.jornada_id
        #             inner join curso c on c.id = ai.curso_id
        #             inner join paralelo p on p.id = ai.paralelo_id
        #             inner join account_journal aj on aj.id = ai.journal_id
        #             where ai.id in %s
        #             group by 1,2,3
        #             order by 1,2,3
        #         """ %(str(tuple(filtro_ids.ids)))
        #     )
        #     quiebres = self.env.cr.dictfetchall()
        #     for rec in quiebres:
        #         invoice_filtro_ids = invoice_ids.filtered(lambda invoice_seccion: invoice_seccion.curso_id.name == rec['curso']
        #                                             and invoice_seccion.paralelo_id.codigo == rec['paralelo']
        #                                             and invoice_seccion.journal_id.name == rec['diario'])
                
        #         # saldo_factura = sum((invoice.amount_total - (sum([line.credit for line in invoice.payment_ids if line.date <= self.fecha_hasta]))
        #         #             ) for invoice in invoice_filtro_ids)
        #         saldo_factura = sum(invoice_filtro_ids.filtered(lambda filtro: filtro.payment_ids.date <= self.fecha_hasta).mapped('payment_ids.credit'))
        #         lista_curso.append(rec['curso'])
        #         lista_paralelo.append(rec['paralelo'])
        #         lista_diario.append(rec['diario'])
        #         saldo.append(saldo_factura)

        #     curso_dic = {
        #         'curso': lista_curso,
        #         'paralelo': lista_paralelo,
        #         'diario': lista_diario,
        #         'saldo': saldo,
        #         'seccion_id': list(set(invoice_filtro_ids.mapped('seccion_id.id'))),
        #         'seccion_name': seccion,
        #     }
        #     lista_seccion.append(curso_dic)

        # return lista_seccion
        

    def dibujar_cabecera_mensualidad(self, wb, ws, data_jornada):
        num_columna = self.numero_columnas(data_jornada)
        tamano_letra_cabecera = 10
        ws.merge_range(
            "A1:"+self._rowcol_to_cell(0, num_columna + 2),
            "RESUMEN DE CUENTAS POR COBRAR ALUMNOS MENSUALIDADES %s" %(self.jornada_id.display_name),
            self.format_bold_center(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A2:"+self._rowcol_to_cell(1, num_columna + 2),
            "PERIODO LECTIVO DESDE %s HASTA %s" %(self.fecha_desde, self.fecha_hasta),
            self.format_bold_center(wb, tamano_letra_cabecera),
        )
        ws.merge_range(
            "A3:"+self._rowcol_to_cell(2, num_columna + 2),
            "AL %s" %(str(datetime.now())[0:10]),
            self.format_bold_center(wb, tamano_letra_cabecera),
        )

    def numero_columnas(self, data_jornada):
        div_columnas = []
        for jornada in data_jornada:
            num_curso = len(set(jornada['curso']))
            num_saldo = len(jornada['saldo'])
            div_columnas.append((num_saldo if num_saldo > 0 else 1) / (num_curso if num_curso > 0 else 1))
        
        return max(div_columnas)

    def dibujar_tabla_mensualidad(self, wb, ws, data_jornada):
        num_columnas = self.numero_columnas(data_jornada)
        row = 3
        col = 0
        col_diario = col + 1
        row_saldo = row + 2
        row_curso = row + 2
        nombre_seccion_concatenado = ''
        col_saldo = col + 1
        for seccion in data_jornada:
            cont_columna = 0
            if not seccion['curso']:
                continue
            #cabecera tabla
            ws.merge_range(
                self._rowcol_to_cell(row, col)+":"+self._rowcol_to_cell(row + 1, col),
                "CURSO",
                self.format_bold_center_vcenter_border(wb)
            )
            col_paralelo = col
            ancho_paralelo = len(set(seccion['paralelo']))
            ancho_diario = len(set(seccion['diario']))
            #paralelo
            for paralelo in sorted(set(seccion['paralelo'])):
                col_paralelo += 1
                if ((col_paralelo + ancho_diario) - 1) != col_paralelo:
                    ws.merge_range(
                        self._rowcol_to_cell(row, col_paralelo)+':'+self._rowcol_to_cell(row, (col_paralelo + ancho_diario) - 1),
                        paralelo,
                        self.format_bold_center_border(wb)
                    )
                else:
                    ws.write(
                        self._rowcol_to_cell(row, col_paralelo),
                        paralelo,
                        self.format_bold_center_border(wb)
                    )
                col_paralelo += (ancho_diario - 1)
                cont_columna += 1
            #dibujando columnas vacias
            tamanio_diario = len(set(seccion['diario']))
            self.dibujar_columnas_vacias(row, cont_columna, tamanio_diario, num_columnas, col_paralelo, wb, ws, "")

            #diario
            col_diario = col
            for diario in (sorted(list(set(seccion['diario']))) * ancho_paralelo):
                col_diario += 1
                ws.write(
                    self._rowcol_to_cell(row + 1, col_diario),
                    diario,
                    self.format_bold_center_border(wb)
                )
            self.dibujar_columnas_vacias(row + 1, cont_columna, tamanio_diario, num_columnas, col_paralelo, wb, ws, "TOTALES")
            
            #curso
            row_curso = row + 2
            for curso in sorted(set(seccion['curso'])):
                ws.write(
                    self._rowcol_to_cell(row_curso, col),
                    curso,
                    self.format_bold_left(wb)
                )
                row_curso += 1
            ws.write(
                self._rowcol_to_cell(row_curso, col),
                'TOTAL '+seccion['seccion_name'],
                self.format_bold_center(wb)
            )
            nombre_seccion_concatenado += ', '+seccion['seccion_name']

            #saldo
            row_saldo = row + 2
            col_saldo = col + 1
            salto_saldo = 0
            sum_fila = 0
            for saldo in seccion['saldo']:
                salto_saldo += 1
                sum_fila += saldo
                ws.write(
                    self._rowcol_to_cell(row_saldo, col_saldo),
                    saldo if saldo > 0 else '',
                    self.format_amount_right(wb)
                )
                col_saldo += 1
                if (len(seccion['saldo']) / len(set(seccion['curso']))) == salto_saldo:
                    col_saldo = self.dibujar_columnas_vacias_saldos(row_saldo, cont_columna, tamanio_diario, num_columnas, col_saldo, wb, ws)
                    #total por fila
                    ws.write(
                        self._rowcol_to_cell(row_saldo, col_saldo),
                        sum_fila,
                        self.format_amount_bold_right(wb)
                    )
                    row_saldo += 1
                    col_saldo = col + 1
                    salto_saldo = 0
                    sum_fila = 0

            #totales por columna
            for rec in range(0, num_columnas + 1):
                ws.write_formula(
                    self._rowcol_to_cell(row_saldo, col_saldo),
                    '=SUM('+self._rowcol_to_cell(row_saldo - len(set(seccion['curso'])), col_saldo)+':'+self._rowcol_to_cell(row_saldo - 1, col_saldo)+')',
                    self.format_amount_bold__bordertop_right(wb)
                )
                col_saldo += 1
            #total seccion 
            ws.write(
                self._rowcol_to_cell(row_curso + 2, col_saldo - 1),
                'TOTAL '+seccion['seccion_name'],
                self.format_bold_right_blue(wb)
            )
            ws.write_formula(
                self._rowcol_to_cell(row_curso + 2, num_columnas + 2),
                '=SUM('+self._rowcol_to_cell(row_saldo - len(set(seccion['curso'])), col_saldo - 1)+':'+self._rowcol_to_cell(row_saldo - 1, col_saldo - 1)+')',
                self.format_amount_bold_right_blue(wb)
            )

            row = row_curso + 4
        #total general
        ws.merge_range(
            self._rowcol_to_cell(row, 0)+':'+self._rowcol_to_cell(row, col_saldo - 1),
            'TOTAL '+nombre_seccion_concatenado,
            self.format_bold_right_yellow(wb)
        )
        ws.write_formula(
            self._rowcol_to_cell(row, col_saldo),
            '=SUM('+self._rowcol_to_cell(5, col_saldo)+':'+self._rowcol_to_cell(row - 1, col_saldo)+')',
            self.format_amount_bold_right_yellow(wb)
        )

        ws.write(
            self._rowcol_to_cell(row + 2, 0),
            'ELABORADO POR',
            self.format_bold_left(wb)
        )
        ws.merge_range(
            self._rowcol_to_cell(row + 4, 0)+':'+self._rowcol_to_cell(row + 4, 2),
            self.env.user.display_name,
            self.format_bold_left(wb)
        )

    def dibujar_columnas_vacias(self, row, cont_columna, tamanio_diario, num_columnas, col_paralelo, wb, ws, palabra):
        if (cont_columna * tamanio_diario) != num_columnas + 1:
            col_paralelo += 1
            for rec in range(0, (num_columnas + 1) - (cont_columna * tamanio_diario)):
                ws.write(
                    self._rowcol_to_cell(row, col_paralelo),
                    palabra if rec == ((num_columnas + 1) - (cont_columna * tamanio_diario)) - 1 else "",
                    self.format_bold_center_border(wb)
                )
                col_paralelo += 1

    def dibujar_columnas_vacias_saldos(self, row_saldo, cont_columna, tamanio_diario, num_columnas, col_saldo, wb, ws):
        if (cont_columna * tamanio_diario) != num_columnas:
            for rec in range(0, (num_columnas - (cont_columna * tamanio_diario))):
                ws.write(
                    self._rowcol_to_cell(row_saldo, col_saldo),
                    '',
                    self.format_amount_right(wb)
                )
                col_saldo += 1
        return col_saldo