# -*- coding: utf-8 -*-
from openerp import models, fields, api
import time
import openerp
from datetime import date
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize
from openerp.tools import image_resize_image_big
from openerp.exceptions import ValidationError


class DetallePeriodo(models.Model):
    _name = "periodo.line"
    _order = "anio desc, mes asc"

    mes = fields.Selection( [('Enero','Enero'),
                             ('Febrero','Febrero'),
                             ('Marzo','Marzo'),
                             ('Abril','Abril'),
                             ('Mayo','Mayo'),
                             ('Junio','Junio'),
                             ('Julio','Julio'),
                             ('Agosto','Agosto'),
                             ('Septiembre','Septiembre'),
                             ('Octubre','Octubre'),
                             ('Noviembre','Noviembre'),
                             ('Diciembre','Diciembre')], 'Mes' )
    anio = fields.Char(string='Año', size=4)
    habilitado = fields.Boolean(string='Habilitado', default=True)
    factura_emitida = fields.Boolean(string='Factura Emitida', default=True, help="Sirve para saber si tiene factura hecha")
    periodo_id = fields.Many2one("periodo")
    # partner_id = fields.Many2one("res.partner")

    @api.constrains('mes', 'anio')
    def validar_no_registros_repetidos(self):
        model_periodo_line = self.search([('id', '!=', self.id)])
        model_per_line_filtro = model_periodo_line.filtered(lambda line: line.mes == self.mes and line.anio == self.anio)
        if model_per_line_filtro:
            raise ValidationError("Ya existe el mes %s y año %s" %(str(self.mes), str(self.anio)))

    @api.onchange("anio")
    def solo_enteros_anio(self):
        if self.anio:
            if not self.anio.isnumeric():
                raise ValidationError("Año solo acepta números")

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s/%s" % (rec.mes or 'sin mes', rec.anio or 'sin año')))
        return result

class FacturasEmitidasAlumnos(models.Model):
    _name = "alumno.factura.line"
    _order = "anio desc, mes asc"

    mes = fields.Selection( [('Enero','Enero'),
                             ('Febrero','Febrero'),
                             ('Marzo','Marzo'),
                             ('Abril','Abril'),
                             ('Mayo','Mayo'),
                             ('Junio','Junio'),
                             ('Julio','Julio'),
                             ('Agosto','Agosto'),
                             ('Septiembre','Septiembre'),
                             ('Octubre','Octubre'),
                             ('Noviembre','Noviembre'),
                             ('Diciembre','Diciembre')], 'Mes' )
    anio = fields.Char(string='Año', size=4)
    factura_emitida = fields.Boolean(string='Factura Emitida')
    partner_id = fields.Many2one("res.partner")
    
    @api.onchange("anio")
    def solo_enteros_anio(self):
        if self.anio:
            if not self.anio.isnumeric():
                raise ValidationError("Año solo acepta números")
