# -*- coding: utf-8 -*-
from openerp import models, fields, api
import time
import openerp
from datetime import date
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, image_colorize
from openerp.tools import image_resize_image_big
from openerp.exceptions import except_orm, Warning as UserError


class AcademicMonth(models.Model):
    ''' Definiendo un mes de un año academico '''
    _name = "academic.month"
    _description = "Mes Academico"
    _order = "date_start"

    name = fields.Char('Nombre', required=True, help='Nombre del mes academico')
    code = fields.Char('Código', required=True, help='codigo del mes academico')
    date_start = fields.Date('Inicio Del Periodo', required=True,
                             help='Inicio del mes academico')
    date_stop = fields.Date('Fin Del Periodo', required=True,
                            help='Fin del mes academico')
    year_id = fields.Many2one('periodo', 'Año Academico', required=True,
                              help="Relacionado con el año academico")
    description = fields.Text('Descripción')
    anio_lectivo = fields.Char(related="year_id.anio_lectivo", string="Año Lectivo")
    habilitado = fields.Boolean(string='Habilitado', help="Si esta habilitado permite generar facturas para ese mes del periodo")
    

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        if self.date_stop and self.date_start and \
                self.date_stop < self.date_start:
            raise UserError(_('Error ! La duración del \
                             mes(es) es/son invalido(s).'))

    @api.constrains('year_id', 'date_start', 'date_stop')
    def _check_year_limit(self):
        if self.year_id and self.date_start and self.date_stop:
            if self.year_id.date_stop < self.date_stop or \
                self.year_id.date_stop < self.date_start or \
                self.year_id.date_start > self.date_start or \
                    self.year_id.date_start > self.date_stop:
                raise UserError(_('Mes invalido ! algunos meses se superponen o\
                                el periodo de fecha no esta al alcance de \
                                el año academico.'))

    @api.multi
    def name_get(self):
        result = []
        for inv in self:
            result.append((inv.id, "%s - %s" % (inv.name or '', inv.date_start[0:4] or '')))
        return result