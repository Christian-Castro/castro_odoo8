# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import base64
from io import BytesIO
import os
from openerp.exceptions import ValidationError
from openerp.tools import ustr, DEFAULT_SERVER_DATE_FORMAT
import commands
from datetime import datetime, date

class ReporteFormulario103(models.AbstractModel):
    _name="reporte.utileria"

    def crear_workbook(self, nombre_hoja=False):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet(nombre_hoja if nombre_hoja else '')
        return workbook, worksheet, fp

    def download_file(self, fp, file_name, pdf=False):
        data_base64 = base64.encodestring(fp.getvalue())
        model_attachment = self.env["ir.attachment"]
        model_attachment.search([('name', '=', file_name)]).unlink()
        attachment = model_attachment.create(
            {
                "name": file_name,
                "datas": data_base64,
                "res_field": file_name,
                "datas_fname": file_name,
            }
        )
        if pdf:
            attachment = self.convert_to_pdf(attachment)
        fp.close()
        return {
            "type": "ir.actions.act_url",
            "url": "/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=%s" % (attachment.id),
            "nodestroy": True,
            'target': 'self',
        }

    def convert_to_pdf(self, attachment):
        model_attachment = self.env["ir.attachment"]
        direccion_xls = model_attachment._get_path(attachment.datas)[1]
        direccion = model_attachment._get_path(attachment.datas)[0]
        nombre_bin = attachment.store_fname
        nombre_archivo = attachment.datas_fname
        separa = direccion_xls.rstrip(direccion)#original
        # separa = "/home/rrojas/.local/share/Odoo/filestore/ans_escuela_01-12-2020"
        os.chdir(separa)
        os.rename(nombre_bin,nombre_archivo)
        commands.getoutput("""libreoffice --headless --convert-to pdf *.xlsx""") 
        with open(separa+'/'+nombre_archivo.split('.')[0]+'.pdf', "rb") as f:
            data = f.read()
            file = data.encode("base64")

        nombre_archivo_pdf = nombre_archivo.split('.')[0]+'.pdf'
        model_attachment.search([('name', '=', nombre_archivo_pdf)]).unlink()
        attachment = model_attachment.create(
            {
                "name": nombre_archivo_pdf,
                "datas": file,
                "res_field": nombre_archivo_pdf,
                "datas_fname": nombre_archivo_pdf,
            }
        )
        return attachment

    def format_bold_center(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'bold': 1,
                'border': 0,
                'align': 'center',
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_bold_center_blue(self, workbook, font_size=8):
        bg_blue = "#CCFFFF"
        merge_format = workbook.add_format(
            {
                'bold': 1,
                'border': 0,
                'align': 'center',
                'font_size': font_size,
                'bg_color': bg_blue,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_bold_right_blue(self, workbook, font_size=8):
        bg_blue = "#CCFFFF"
        merge_format = workbook.add_format(
            {
                'bold': 1,
                'border': 0,
                'align': 'right',
                'font_size': font_size,
                'bg_color': bg_blue,
                'text_wrap': True,
            }
        )
        return merge_format
    
    def format_bold_left(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'bold': 1,
                'border': 0,
                'align': 'left',
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format
    
    def format_bold_right(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'bold': 1,
                'border': 0,
                'align': 'right',
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_bold_right_border(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'bold': 1,
                'border': 1,
                'align': 'right',
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_bold_right_yellow(self, workbook, font_size=8):
        bg_yellow = "#FFFFCC"
        merge_format = workbook.add_format(
            {
                'bold': 1,
                'border': 0,
                'align': 'right',
                'font_size': font_size,
                'bg_color': bg_yellow,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_bold_center_vcenter_border(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format
    
    def format_bold_center_border(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'bold': 1,
                'border': 1,
                'align': 'center',
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_center(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'align': 'center',
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_center_borderTopBottom(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'align': 'center',
                'top': 1,
                'bottom': 1,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_right(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_left(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'align': 'left',
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_left_borderTopBottom(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'align': 'left',
                'top': 1,
                'bottom': 1,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_left_bold_borderTopBottom(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'align': 'left',
                'top': 1,
                'bottom': 1,
                'bold': 1,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_date_center(self, workbook, font_size=8):
        date_format = "YYYY-MM-DD"
        merge_format = workbook.add_format(
            {
                'align': 'center',
                'num_format': date_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_date_center_borderTopBottom(self, workbook, font_size=8):
        date_format = "YYYY-MM-DD"
        merge_format = workbook.add_format(
            {
                'align': 'center',
                'top': 1,
                'bottom': 1,
                'num_format': date_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_bold_date_left(self, workbook, font_size=8):
        date_format = "YYYY-MM-DD"
        merge_format = workbook.add_format(
            {
                'align': 'left',
                'bold': 1,
                'num_format': date_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_amount_right(self, workbook, font_size=8):
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'num_format': num_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_amount_border_right(self, workbook, font_size=8):
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'border': 1,
                'num_format': num_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_amount_borderTopBottom_right(self, workbook, font_size=8):
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'top': 1,
                'bottom': 1,
                'num_format': num_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_amount_bold_borderTopBottom_right(self, workbook, font_size=8):
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'top': 1,
                'bottom': 1,
                'bold': 1,
                'num_format': num_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format
    
    def format_amount_bold_right(self, workbook, font_size=8):
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'bold': 1,
                'num_format': num_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_amount_bold_border_right(self, workbook, font_size=8):
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'bold': 1,
                'border': 1,
                'num_format': num_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_amount_bold_right_blue(self, workbook, font_size=8):
        bg_blue = "#CCFFFF"
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'bold': 1,
                'num_format': num_format,
                'font_size': font_size,
                'bg_color': bg_blue,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_amount_bold_right_yellow(self, workbook, font_size=8):
        bg_yellow = "#FFFFCC"
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'bold': 1,
                'num_format': num_format,
                'font_size': font_size,
                'bg_color': bg_yellow,
                'text_wrap': True,
            }
        )
        return merge_format
    
    def format_amount_bold__bordertop_right(self, workbook, font_size=8):
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'top': 1,
                'bold': 1,
                'num_format': num_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_amount_bold__bordertopbottom_right(self, workbook, font_size=8):
        num_format = "#,##0.00"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'top': 1,
                'bottom': 1,
                'bold': 1,
                'num_format': num_format,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_bold_border_left(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'align': 'left',
                'border': 1,
                'bold': 1,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_bold_border_center(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'align': 'center',
                'border': 1,
                'bold': 1,
                'font_size': font_size,
                'text_wrap': True,
                #'valign': 'vjustify',
            }
        )
        return merge_format

    def format_border_left(self, workbook, font_size=8):
        merge_format = workbook.add_format(
            {
                'align': 'left',
                'border': 1,
                'bold': 0,
                'font_size': font_size,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_integer_border_right(self, workbook, font_size=8):
        int_format = "#,##0"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'border': 1,
                'bold': 0,
                'font_size': font_size,
                'num_format': int_format,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_integer_borderTopBottom_right(self, workbook, font_size=8):
        int_format = "#,##0"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'top': 1,
                'bottom': 1,
                'bold': 0,
                'font_size': font_size,
                'num_format': int_format,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_integer_bold_borderTopBottom_right(self, workbook, font_size=8):
        int_format = "#,##0"
        merge_format = workbook.add_format(
            {
                'align': 'right',
                'top': 1,
                'bottom': 1,
                'bold': 1,
                'font_size': font_size,
                'num_format': int_format,
                'text_wrap': True,
            }
        )
        return merge_format

    def format_percent_center(self, workbook, font_size=8):
        pct_format = "#,##0.00%"
        merge_format = workbook.add_format(
            {
                'align': 'center',
                'num_format': pct_format,
                'font_size': font_size,
                'text_wrap': True, #ajuste de texto
            }
        )
        return merge_format

    def strToDatetime(self, strdate):
        return datetime.strptime(strdate, DEFAULT_SERVER_DATE_FORMAT)

    def strToDate(self, dt):
        return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

    @staticmethod
    def _rowcol_to_cell(row, col, row_abs=False, col_abs=False):
        return xl_rowcol_to_cell(row, col, row_abs=row_abs, col_abs=col_abs)

    def setear_hoja_orientacion(self, ws, orientacion):
        if orientacion:
            ws.set_landscape() #horizontal
        else:
            ws.set_portrait() #vertical

    def setear_tamano_hoja(self, ws, indice):
        # Index	Paper format	Paper size
        # 0	    Printer default	Printer default
        # 1	    Letter	        8 1/2 x 11 in
        # 2	    Letter Small	8 1/2 x 11 in
        # 3	    Tabloid	        11 x 17 in
        # 4	    Ledger	        17 x 11 in
        # 5	    Legal	        8 1/2 x 14 in
        # 6	    Statement	    5 1/2 x 8 1/2 in
        # 7	    Executive	    7 1/4 x 10 1/2 in
        # 8	    A3	            297 x 420 mm
        # 9	    A4	            210 x 297 mm
        # 10	A4 Small	    210 x 297 mm
        # 11	A5	            148 x 210 mm
        # 12	B4	            250 x 354 mm
        # 13	B5	            182 x 257 mm
        # 14	Folio	        8 1/2 x 13 in
        # 15	Quarto	        215 x 275 mm
        # 16	—	            10x14 in
        # 17	—	            11x17 in
        # 18	Note	        8 1/2 x 11 in
        # 19	Envelope 9	    3 7/8 x 8 7/8
        # 20	Envelope 10	    4 1/8 x 9 1/2
        # 21	Envelope 11	    4 1/2 x 10 3/8
        # 22	Envelope 12	    4 3/4 x 11
        # 23	Envelope 14	    5 x 11 1/2
        # 24	C size sheet	—
        # 25	D size sheet	—
        # 26	E size sheet	—
        # 27	Envelope DL	    110 x 220 mm
        # 28	Envelope C3	    324 x 458 mm
        # 29	Envelope C4	    229 x 324 mm
        # 30	Envelope C5	    162 x 229 mm
        # 31	Envelope C6	    114 x 162 mm
        # 32	Envelope C65	114 x 229 mm
        # 33	Envelope B4	    250 x 353 mm
        # 34	Envelope B5	    176 x 250 mm
        # 35	Envelope B6	    176 x 125 mm
        # 36	Envelope	    110 x 230 mm
        # 37	Monarch	        3.875 x 7.5 in
        # 38	Envelope	    3 5/8 x 6 1/2 in
        # 39	Fanfold	        14 7/8 x 11 in
        # 40	German Std Fanfold      8 1/2 x 12 in
        # 41	German Legal Fanfold    8 1/2 x 13 in
        for rec in range(0, 41):
            if rec == indice:
                ws.set_paper(indice)
                return True

    def setear_margenes_hoja(self, ws):
        #set_margins(left, right, top, bottom)
        ws.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    
    #set_header
    # Controlar	            Categoría	    Descripción
    # &L	                Justificación	Izquierda
    # &C	 	                            Centrar
    # & R	 	                            Derecho
    # &PAG	                Información	    Número de página
    # &NORTE	 	                        Número total de páginas
    # &RE	 	                            Fecha
    # &T	 	                            Hora
    # &F	 	                            Nombre del archivo
    # &UNA	 	                            Nombre de la hoja de trabajo
    # &Z	 	                            Ruta del libro de trabajo
    # &tamaño de fuente	    Fuente	        Tamaño de fuente
    # &"Estilo de fuente"	                Nombre y estilo de fuente
    # &U	 	                            Subrayado único
    # &MI	 	                            Explicación doble
    # &S	 	                            Tachado
    # &X	 	                            Sobrescrito
    # &Y	 	                            Subíndice
    # &[Imagen]	            Imagenes	    Marcador de posición de imagen
    # &GRAMO	 	                        Igual que & [Imagen]
    # &&                    Misc.	        Y literal "&"
    def mostrar_paginas_derecha_cabecera(self, ws):
        ws.set_header("&RPágina &P de &N".decode("utf-8"))

    def repetir_fila_en_cada_hoja(self, ws, first_row, last_row=False):
        if last_row:
            ws.repeat_rows(first_row, last_row)
        else: 
            ws.repeat_rows(first_row)

    def ocultar_lineas_xlsx(self, ws):
        # 0. No oculte las líneas de la cuadrícula.
        # 1. Ocultar solo las líneas de cuadrícula impresas.
        # 2. Ocultar la pantalla y las líneas de cuadrícula impresas.
        ws.hide_gridlines(2)

    def ajustar_pagina_a_n_columnas(self, ws):
        ws.fit_to_pages(1, 0)
