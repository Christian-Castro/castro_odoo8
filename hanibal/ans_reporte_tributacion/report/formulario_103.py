# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
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

class reporteFormulario103(models.TransientModel):
    _name = "reporte.formulario.103"
    _inherit = "reporte.utileria"
    _rec_name = "name"


    fecha_inicio = fields.Date(string='Fecha Inicio',)
    fecha_fin = fields.Date(string='Fecha Fin',)
    proveedor_id = fields.Many2one(
        string='Proveedor',
        comodel_name='res.partner',
    )
    name = fields.Char(default="Formulario 103")
    tipo_retencion = fields.Many2one(
        string='Tipo De Retención',
        comodel_name='fiscal.tipodocumento',
    )
    

    @api.multi
    def generar_archivo_xlsx(self):
        wb, ws, fp = self.crear_workbook()
        self.setear_ancho_columna(ws)
        self.setear_tamano_hoja(ws, 9)
        self.setear_hoja_orientacion(ws, True)
        # self.mostrar_paginas_derecha_cabecera(ws)
        self.ocultar_lineas_xlsx(ws)
        self.dibujar_cabecera(wb, ws)
        self.dibujar_cabecera_tabla(wb, ws)
        self.dibujar_cuerpo_tabla(wb, ws)
        self.repetir_fila_en_cada_hoja(ws, 1, 6)
        self.ajustar_pagina_a_n_columnas(ws)
        wb.close()
        return self.download_file(fp, "Formulario 103.xlsx")
    
    def setear_ancho_columna(self, ws):
        ws.set_column('A:A', 1)
        ws.set_column('C:C', 7.14)
        ws.set_column('D:D', 7.14)
        ws.set_column('F:F', 9.86)
        ws.set_column('G:G', 15.5)
        ws.set_column('H:H', 12)
        ws.set_column('M:M', 15)

    def dibujar_cabecera(self, wb, ws):
        ws.merge_range(
            "B2:G2",
            "FORMULARIO 103 POR COMPRAS (del %s al %s)" %(self.fecha_inicio, self.fecha_fin),
            self.format_bold_left(wb)
        )
        ws.merge_range(
            "L2:M2",
            "Módulo de Compras".decode("utf-8"),
            self.format_bold_center(wb)
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

    def dibujar_cabecera_tabla(self, wb, ws):
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
        ws.merge_range(
            "K6:M6",
            "RETENCION FUENTE",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "K7",
            "VALOR",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "L7",
            "%",
            self.format_bold_center_border(wb)
        )
        ws.write(
            "M7",
            "No.",
            self.format_bold_center_border(wb)
        )

    def dibujar_cuerpo_tabla(self, wb, ws):
        model_invoice = self.env["account.invoice"]
        model_fiscal_tipodocumento = self.env["fiscal.tipodocumento"]
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

        if self.tipo_retencion:
            retencion_search = "[('id', '=', %s)]" %(self.tipo_retencion.id)
        else:
            retencion_search = "[('tipo', '=', 'fte')]"
        tipodocumento_ids = model_fiscal_tipodocumento.search(safe_eval(retencion_search), order="name asc")
        total_general_base_imponible = 0
        total_general_iva = 0
        total_general_compra = 0
        total_general_retencion = 0
        row = 8
        for tipo in tipodocumento_ids:
            entrar_tipo = True
            total_base_imponible = 0
            total_iva = 0
            total_compra = 0
            total_retencion = 0
            bandera_total = False
            for invoice in invoice_ids:
                if invoice.tipodocumento_id.id == tipo.id:
                    #dibujamos los tipos de retencion
                    bandera_total = True
                    if entrar_tipo:
                        ws.write(
                            "B"+str(row),
                            "Código:".decode("utf-8"),
                            self.format_bold_center(wb)
                        )
                        ws.write(
                            "C"+str(row),
                            invoice.tipodocumento_id.codigointerno,
                            self.format_bold_center(wb)
                        )
                        ws.merge_range(
                            "D"+str(row)+":G"+str(row),
                            str(invoice.tipodocumento_id.name).decode("utf-8"),
                            self.format_bold_center(wb)
                        )
                        row +=1
                        entrar_tipo = False
                    #dibujar ordenes y facturas
                    ws.write(
                        "B"+str(row),
                        invoice.reference or "",
                        self.format_center(wb)
                    )
                    ws.write(
                        "C"+str(row),
                        invoice.date_invoice,
                        self.format_date_center(wb)
                    )
                    ws.write(
                        "D"+str(row),
                        invoice.date_invoice,
                        self.format_date_center(wb)
                    )
                    ws.write(
                        "E"+str(row),
                        "Factura",
                        self.format_center(wb)
                    )
                    ws.write(
                        "F"+str(row),
                        invoice.number,
                        self.format_center(wb)
                    )
                    ws.write(
                        "G"+str(row),
                        str(invoice.partner_id.display_name).decode("utf-8"),
                        self.format_center(wb)
                    )
                    ws.write(
                        "H"+str(row),
                        invoice.amount_untaxed,
                        self.format_amount_right(wb)
                    )
                    total_base_imponible += invoice.amount_untaxed
                    ws.write(
                        "I"+str(row),
                        invoice.amount_tax,
                        self.format_amount_right(wb)
                    )
                    total_iva += invoice.amount_tax
                    ws.write(
                        "J"+str(row),
                        invoice.amount_total,
                        self.format_amount_right(wb)
                    )
                    total_compra += invoice.amount_total
                    ws.write(
                        "K"+str(row),
                        (invoice.totalretencion * -1) if invoice.totalretencion < 0 else invoice.totalretencion,
                        self.format_amount_right(wb)
                    )
                    total_retencion += ((invoice.totalretencion * -1) if invoice.totalretencion < 0 else invoice.totalretencion)
                    #porcentaje retencion
                    porcetnaje_retencion = 0
                    for rec in invoice.retencion_line:
                        porcetnaje_retencion += rec.porcentaje

                    ws.write(
                        "L"+str(row),
                        (porcetnaje_retencion * -1) if porcetnaje_retencion < 0 else porcetnaje_retencion,
                        self.format_percent_center(wb)
                    )
                    ws.write(
                        "M"+str(row),
                        str(invoice.establecimiento)+"-"+str(invoice.puntoemision)+"-"+str(invoice.secuencial),
                        self.format_center(wb)
                    )
                    row += 1
            if bandera_total:
                #total por tipo documento
                ws.write(
                    "H"+str(row),
                    total_base_imponible,
                    self.format_amount_bold__bordertop_right(wb)
                )
                ws.write(
                    "I"+str(row),
                    total_iva,
                    self.format_amount_bold__bordertop_right(wb)
                )
                ws.write(
                    "J"+str(row),
                    total_compra,
                    self.format_amount_bold__bordertop_right(wb)
                )
                ws.write(
                    "K"+str(row),
                    total_retencion,
                    self.format_amount_bold__bordertop_right(wb)
                )
                row += 2
                total_general_base_imponible += total_base_imponible
                total_general_iva += total_iva
                total_general_compra += total_compra
                total_general_retencion += total_retencion
        #Total general
        ws.write(
            "G"+str(row),
            "TOTAL COMPRA",
            self.format_bold_right(wb)
        )
        ws.write(
            "H"+str(row),
            total_general_base_imponible,
            self.format_amount_bold__bordertopbottom_right(wb)
        )
        ws.write(
            "I"+str(row),
            total_general_iva,
            self.format_amount_bold__bordertopbottom_right(wb)
        )
        ws.write(
            "J"+str(row),
            total_general_compra,
            self.format_amount_bold__bordertopbottom_right(wb)
        )
        ws.write(
            "K"+str(row),
            total_general_retencion,
            self.format_amount_bold__bordertopbottom_right(wb)
        )

    def data_formulraio_103_pdf(self):
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

        if self.tipo_retencion:
            retencion_search = "[('id', '=', %s)]" %(self.tipo_retencion.id)
        else:
            retencion_search = "[('tipo', '=', 'fte')]"
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
                    #porcentaje retencion
                    porcetnaje_retencion = 0
                    for rec in invoice.retencion_line:
                        porcetnaje_retencion += rec.porcentaje

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
                        "valor": (invoice.totalretencion * -1) if invoice.totalretencion < 0 else invoice.totalretencion,
                        "porcentaje": (porcetnaje_retencion * -1) * 100 if porcetnaje_retencion < 0 else porcetnaje_retencion * 100,
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
