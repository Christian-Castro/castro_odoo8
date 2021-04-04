# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

#===============================================================================
# PEGAR ESTA LINEA DESPUES DE ESTO ** f.codigo_barra(f.clave_acceso) **
# ABRIR DIRECTO EL ARCHIVO RML
# DEBE QUEDAR ASI DENTRO DEL ARCHIVO RML DE RIDE DE FACTURA PARA QUE APAREZA EL CODIGO DE BARRA DIBUJADO:
#
# <blockTable colWidths="130.0,130.0" style="Table55">
#   <tr>
#     <td>
#       <para style="P10">[[ f.codigo_barra(f.clave_acceso) ]]</para>
#       <image file="/opt/odoo/server/addonsfa/code128.png" width="7cm" height="2cm"/>
#     </td>
#     <td>
#       <para style="P5">
#         <font color="white"> </font>
#       </para>
#     </td>
#   </tr>
# </blockTable>
#===============================================================================
#===============================================================================
#<image file="/opt/odoo/server/addonsfa/code128.png" width="7cm" height="2cm"/>
#<image width="5cm" height="3cm" >[[ f.comp_id.logo ]]</image>

from openerp.report import report_sxw


class ride_factura_fiscal(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(ride_factura_fiscal, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            
        })
    
    
report_sxw.report_sxw(
    'report.ride.factura.electronica.fiscal',
    'account.invoice',
    'addonsan_personales/fiscal/report/ride_facturas_electronica.rml',
    parser=ride_factura_fiscal,header=False)

#===============================================================================
# 
# AL PEGAR ESTE PY EN LA CARPETA REPORT DE FISCAL TIENES QUE VERIFICAR LA RUTA DEL ARCHIVO
# 'addonsan_personales/fiscal/report/ride_facturas_electronica.rml'
# TIENES QUE PONER LA RUTA DE ADDONS DE DONDE ESTA EL MODULO FISCAL
#===============================================================================

#===============================================================================
# EN EL XML TAMBIEN ESTA DEFINIDA LA RUTA DEL ARCHIVO RML
# rml="fiscal/report/ride_facturas_electronica.rml"
# ESTA RUTA TIENES QUE VALIDAR , CREO QUE TU MODULO SE LLAMA FISCAL MISMO
#===============================================================================

#===============================================================================
# EN EL ARCHIVO RML DEL REPORTE VALIDA LA RUTA DE DONDE ESTAS GENERANDO LOS PNG QUE SON LA IMAGEN
# DEL CODIGO DE BARRAS
# /opt/odoo/server/addons/fac_elec_ans/code128.png
# LA LINEA EN DONDE DEFINO LA RUTA A TOMAR EL CODIGO DE BARRAS ES LA  -->552
#===============================================================================

#===============================================================================
# 
# AL COPIAR EL ARCHIVO PY Y XML NO TE OLVIDES DE DECLARARLOS PARA QUE PUEDAN SER VISTOS
# EN EL SISTEMA Y PODER GENERAR EL RML
#===============================================================================

#===============================================================================
# EN LA LINEA 27 DEL XML DE LA FACTURA ESTA EL CAMPO A COPIAR Y PEGAR EN TU FUENTE
#===============================================================================

#===============================================================================
# EN LA LIENA 312 DEL PY ESTA LA LINEA DEL CAMPO A CREAR QUE SE RELACIONA A LA FACTURA ELECTRONICA
#===============================================================================

