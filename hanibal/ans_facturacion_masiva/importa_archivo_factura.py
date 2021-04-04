# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import models, fields

class importar_archivo_factura(models.Model):
    
    _name="importar.archivo.factura"
    
    numerofactura = fields.Char("Numero de factura")
    fechafactura  = fields.Date("Fecha de factura")
    nombrealumno  = fields.Char("Nombre del alumno")
    concepto  = fields.Char("Concepto")
    curso     = fields.Char("Curso")
    subtotal   = fields.Float("Subtotal")
    descuento  = fields.Float("Descuento")
    valorneto  = fields.Float("Subtotal")
    impuesto   = fields.Float("Impuesto")
    total      = fields.Float("Total")
    pasar = fields.Boolean("F.E.",default=True)
    detalle_id = fields.Many2one('importar.archivo','Importar Archivo',required=False,ondelete='cascade')
           
