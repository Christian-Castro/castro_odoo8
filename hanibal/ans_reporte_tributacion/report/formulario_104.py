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

class ReporteFormulario104(models.TransientModel):
    _name = "reporte.formulario.104"
    _inherit = "reporte.utileria"


    fecha_inicio = fields.Date(string='Fecha Inicio',)
    fecha_fin = fields.Date(string='Fecha Fin',)
    proveedor_id = fields.Many2one(
        string='Proveedor',
        comodel_name='res.partner',
    )
    name = fields.Char(default="Fommulario 104")
    tipo_retencion = fields.Many2one(
        string='Tipo De Retención',
        comodel_name='fiscal.tipodocumento',
    )

    @api.multi
    def generar_archivo_xlsx(self):
        fp = self.generar_archivo()
        return self.download_file(fp, "Formulario 104.xlsx")

    @api.multi
    def generar_archivo_pdf(self):
        fp = self.generar_archivo()
        return self.download_file(fp, "Formulario 104.xlsx", True)

    def generar_archivo(self):
        wb, ws, fp = self.crear_workbook()
        self.setear_ancho_columna(ws)
        self.setear_tamano_hoja(ws, 9)
        self.setear_hoja_orientacion(ws, True)
        # self.mostrar_paginas_derecha_cabecera(ws)
        self.ocultar_lineas_xlsx(ws)
        data_formulario_104 = self.construir_data()
        self.dibujar_cabecera(wb, ws, data_formulario_104)
        self.dibujar_cabecera_tabla(wb, ws, data_formulario_104)
        self.dibujar_cuerpo_tabla(wb, ws, data_formulario_104)
        # self.repetir_fila_en_cada_hoja(ws, 1, 6)
        self.ajustar_pagina_a_n_columnas(ws)
        wb.close()
        return fp

    def setear_ancho_columna(self, ws):
        ws.set_column('A:A', 0.2)
        ws.set_column(1, 23, 15) #desde la B hasta Z ancho 15

    def construir_data(self):
        model_invoice = self.env["account.invoice"]
        model_fiscal_tipodocumento = self.env["fiscal.tipodocumento"]
        data = []
        detalle_list = []
        tipo_list = []

        if self.proveedor_id:
            proveedor = "[('partner_id', '=', %s)]" %(self.proveedor_id.id)
        else:
            proveedor = "[]"

        invoice_ids = model_invoice.search(
            [
                ("state", "in", ["open", "paid"]),
                ("date_invoice", ">=", self.fecha_inicio),
                ("date_invoice", "<=", self.fecha_fin),
                ("type", "=", "in_invoice"),
            ] + safe_eval(proveedor)
        )

        retencion_search = "[('tipo', '=', 'iva')]"
        if self.tipo_retencion:
            retencion_search = "[('id', '=', %s)]" %(self.tipo_retencion.id)
        tipodocumento_ids = model_fiscal_tipodocumento.search(safe_eval(retencion_search), order="name asc")

        for tipo in tipodocumento_ids:
            entrar_tipo = True
            for invoice in invoice_ids:
                if invoice.tipodocumento_id.id == tipo.id:
                    if entrar_tipo:
                        tipo_dict = {
                            "codigo": invoice.tipodocumento_id.codigointerno,
                            "tipo_retencion": invoice.tipodocumento_id.name,
                        }
                        entrar_tipo = False
                        tipo_list.append(tipo_dict)
                    lista_iva_retenido = []
                    for line in invoice.retencion_line:
                        iva_retenido = {
                            'porcentaje': (line.porcentaje * -1) * 100 if line.porcentaje < 0 else line.porcentaje * 100,
                            'valor': line.amount * - 1 if line.amount < 0 else line.amount,
                        }
                        lista_iva_retenido.append(iva_retenido)

                    detalle_dict = {
                        "comprobante": invoice.reference or "",
                        "registro": invoice.date_invoice,
                        "emision": invoice.date_invoice,
                        "tipo": "Factura",
                        "numero_documento": invoice.number,
                        "proveedor": invoice.partner_id.display_name,
                        "base_imponible": invoice.amount_untaxed,
                        "iva": invoice.amount_tax,
                        "total_compra": invoice.amount_total,
                        "iva_retenido": lista_iva_retenido,
                        "numero_retencion": str(invoice.establecimiento)+"-"+str(invoice.puntoemision)+"-"+str(invoice.secuencial),
                    }
                    detalle_list.append(detalle_dict)
            retencion_dic = {
                "retencion": tipo_list,
                "detalle": detalle_list,
            }
            data.append(retencion_dic)
            tipo_list = []
            detalle_list = []
        return data

    def dibujar_cabecera(self, wb, ws, data_formulario_104):
        columnas_iva = self.obtener_columna_iva_retenido(data_formulario_104)
        ws.merge_range(
            "B2:G2",
            "FORMULARIO 104 POR COMPRAS (del %s al %s)" %(self.fecha_inicio, self.fecha_fin),
            self.format_bold_left(wb)
        )
        letra = "J"
        for rec in columnas_iva:
            letra = self.aumentar_letra(letra)
        if not columnas_iva:
            letra = self.aumentar_letra(letra)
        letra = self.aumentar_letra(letra)
        ws.merge_range(
            "J2:"+letra+"2",
            "Módulo de Compras".decode("utf-8"),
            self.format_bold_right(wb)
        )
        ws.merge_range(
            "B3:G3",
            str(self.proveedor_id.display_name or "TODOS LOS PROVEEDORES").decode("utf-8"),
            self.format_bold_left(wb)
        )
        ws.merge_range(
            "B4:G4",
            datetime.now(),
            self.format_bold_date_left(wb)
        )

    def dibujar_cabecera_tabla(self, wb, ws, data_formulario_104):
        columnas_iva = self.obtener_columna_iva_retenido(data_formulario_104)
        ws.merge_range(
            "B6:B7",
            "No. COMPRO",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "C6:D6",
            "FECHA",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "C7",
            "REGISTRO",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "D7",
            "EMISION",
            self.format_bold_center_border(wb)
        )
        ws.merge_range(
            "E6:F6",
            "DOCUMENTO",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "E7",
            "TIPO",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "F7",
            "No.",
            self.format_bold_center_border(wb)
        )
        ws.merge_range(
            "G6:G7",
            "PROVEEDOR",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "H6:H7",
            "BASE IMPONIBLE",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "I6:I7",
            "I.V.A",
            self.format_bold_center_vcenter_border(wb)
        )
        ws.merge_range(
            "J6:J7",
            "TOTAL COMPRA",
            self.format_bold_center_vcenter_border(wb)
        )
        letra = 'K'
        for col in columnas_iva:
            ws.write(
                letra+"7",
                str(col)+'%',
                self.format_bold_center_border(wb)
            )
            letra = self.aumentar_letra(letra)
        if columnas_iva:
            letra = self.disminuir_letra(letra)
        if len(columnas_iva) > 1:
            ws.merge_range(
                "K6:"+letra+"6",
                "IVA RETENIDO",
                self.format_bold_center_border(wb)
            )
        else:
            if len(columnas_iva) < 1:
                ws.write(
                    "K7",
                    "",
                    self.format_bold_center_border(wb)
                )
            ws.write(
                "K6",
                "IVA RETENIDO",
                self.format_bold_center_border(wb)
            )
        letra = self.aumentar_letra(letra)
        ws.merge_range(
            letra+"6:"+letra+"7",
            "NUM. RETEN",
            self.format_bold_center_vcenter_border(wb)
        )

    def obtener_columna_iva_retenido(self, data_formulario_104):
        columna_iva = []
        for data in data_formulario_104:
            for detalle in data['detalle']:
                for iva in detalle['iva_retenido']:
                    columna_iva.append(iva['porcentaje'])
        columna_iva = sorted(list(set(columna_iva)), reverse=True)
        return columna_iva

    def aumentar_letra(self, letra):
        letra = ord(letra) + 1 #obtengo el numero ascii
        letra = chr(letra) #obtengo el caracter ascii
        return letra
    
    def disminuir_letra(self, letra):
        letra = ord(letra) - 1 #obtengo el numero ascii
        letra = chr(letra) #obtengo el caracter ascii
        return letra

    def dibujar_cuerpo_tabla(self, wb, ws, data_formulario_104):
        columnas_iva = self.obtener_columna_iva_retenido(data_formulario_104)
        row = 8
        row_retencion = row
        total_general_base_imponible = 0
        total_general_iva = 0
        total_general_compra = 0
        row_list = []
        dic_row = {}
        for data in data_formulario_104:
            toal_base_imponible = 0
            total_iva = 0
            total_compra = 0
            for retencion in data['retencion']:
                ws.write(
                    "B"+str(row),
                    "Código:".decode("utf-8"),
                    self.format_bold_center(wb),
                )
                ws.write(
                    "C"+str(row),
                    retencion['codigo'],
                    self.format_bold_center(wb),
                )
                ws.merge_range(
                    "D"+str(row)+":G"+str(row),
                    retencion['tipo_retencion'],
                    self.format_bold_left(wb),
                )
                row += 1
                row_retencion = row
                dic_row = {'row_inicial': row}
            for line in data['detalle']:
                ws.write(
                    "B"+str(row),
                    line['comprobante'],
                    self.format_center(wb),
                )
                ws.write(
                    "C"+str(row),
                    line['registro'],
                    self.format_date_center(wb),
                )
                ws.write(
                    "D"+str(row),
                    line['emision'],
                    self.format_date_center(wb),
                )
                ws.write(
                    "E"+str(row),
                    "Factura",
                    self.format_center(wb),
                )
                ws.write(
                    "F"+str(row),
                    line['numero_documento'],
                    self.format_center(wb),
                )
                ws.write(
                    "G"+str(row),
                    line['proveedor'],
                    self.format_left(wb),
                )
                ws.write(
                    "H"+str(row),
                    line['base_imponible'],
                    self.format_amount_right(wb),
                )
                toal_base_imponible += line['base_imponible']
                total_general_base_imponible += line['base_imponible']
                ws.write(
                    "I"+str(row),
                    line['iva'],
                    self.format_amount_right(wb),
                )
                total_iva += line['iva']
                total_general_iva += line['iva']
                ws.write(
                    "J"+str(row),
                    line['total_compra'],
                    self.format_amount_right(wb),
                )
                total_compra += line['total_compra']
                total_general_compra += line['total_compra']
                #####iva retenido
                letra = "K"
                for col in columnas_iva:
                    for iva_ret in line['iva_retenido']:
                        if col == iva_ret['porcentaje']:
                            ws.write(
                                letra+str(row),
                                iva_ret['valor'],
                                self.format_amount_right(wb),
                            )
                    letra = self.aumentar_letra(letra)
                ######
                if not columnas_iva:
                    letra = self.aumentar_letra(letra)
                ws.write(
                    letra+str(row),
                    line['numero_retencion'],
                    self.format_amount_right(wb),
                )
                row += 1
            dic_row['row_final'] = row - 1
            row_list.append(dic_row)
            # total por retencion
            ws.write(
                "H"+str(row),
                toal_base_imponible,
                self.format_amount_bold__bordertopbottom_right(wb),
            )
            ws.write(
                "I"+str(row),
                total_iva,
                self.format_amount_bold__bordertopbottom_right(wb),
            )
            ws.write(
                "J"+str(row),
                total_compra,
                self.format_amount_bold__bordertopbottom_right(wb),
            )
            letra = "K"
            for col in columnas_iva:
                ws.write_formula(
                    letra+str(row),
                    "=SUM("+letra+str(row_retencion)+":"+letra+str(row - 1)+")",
                    self.format_amount_bold__bordertopbottom_right(wb),
                )
                letra = self.aumentar_letra(letra)
            row += 1
        #total general
        row += 2
        ws.merge_range(
            "B"+str(row)+":G"+str(row),
            "TOTAL GENERAL",
            self.format_bold_right(wb),
        )
        ws.write(
            "H"+str(row),
            total_general_base_imponible,
            self.format_amount_bold__bordertopbottom_right(wb),
        )
        ws.write(
            "I"+str(row),
            total_general_iva,
            self.format_amount_bold__bordertopbottom_right(wb),
        )
        ws.write(
            "J"+str(row),
            total_general_compra,
            self.format_amount_bold__bordertopbottom_right(wb),
        )
        letra = "K"
        for col in columnas_iva:
            #armar rango de suma
            rango_fil_col = ""
            for rango in row_list:
                rango_fil_col += letra+str(rango["row_inicial"])+":"+letra+str(rango["row_final"])+","
            ws.write_formula(
                letra+str(row),
                "=SUM("+rango_fil_col+")",
                self.format_amount_bold__bordertopbottom_right(wb),
            )
            letra = self.aumentar_letra(letra)
        if not columnas_iva:
            ws.write(
                "K"+str(row),
                0,
                self.format_amount_bold__bordertopbottom_right(wb),
            )
