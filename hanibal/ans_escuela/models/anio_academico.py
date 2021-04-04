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
from dateutil.relativedelta import relativedelta


class AcademicYear(models.Model):
    ''' Definiendo un año académico '''

    _name = "periodo"
    _description = "Academic Year"
    _order = "date_stop desc"

    # sequence = fields.Integer('Secuencia', required=True,
    #                           help="En que orden de secuencia desea ver este año.")
    name = fields.Char('Nombre', required=True, select=1,
                       help='Nombre del año academico')
    code = fields.Char('Código', required=True, select=1,
                       help='Código del año academico')
    date_start = fields.Date('Fecha Inicio', required=True,
                             help='Iniciando la fecha del año academico')
    date_stop = fields.Date('Fecha Final', required=True,
                            help='Fin del año academico')
    month_ids = fields.One2many('academic.month', 'year_id', string='Mes',
                                help="Relación del mes academico")
    anio_lectivo = fields.Char('Año Lectivo')
    active = fields.Boolean('Activo', default=False)
    description = fields.Text('Descripción')
    
    @api.multi
    def write(self, vals):
        if self.date_start:
            vals['anio_lectivo'] = self.date_start[0:4]
        else:
            vals['anio_lectivo'] = ''
        res = super(AcademicYear, self).write(vals)
        return res

    @api.model
    def next_year(self, sequence):
        year_ids = self.search([('sequence', '>', sequence)], order='id ASC',
                               limit=1)
        if year_ids:
            return year_ids.id
        return False

    @api.multi
    def name_get(self):
        res = []
        for acd_year_rec in self:
            name = "[" + (acd_year_rec['code'] or '') + "]" + (acd_year_rec['name'] or '')
            res.append((acd_year_rec['id'], name))
        return res

    @api.constrains('date_start', 'date_stop')
    def _check_academic_year(self):
        obj_academic_ids = self.search([])
        academic_list = []
        for rec_academic in obj_academic_ids:
            academic_list.append(rec_academic.id)
        for current_academic_yr in self:
            if current_academic_yr.id in academic_list:
                academic_list.remove(current_academic_yr.id)
            data_academic_yr = self.browse(academic_list)
            for old_ac in data_academic_yr:
                if old_ac.date_start <= self.date_start <= old_ac.date_stop \
                   or old_ac.date_start <= self.date_stop <= old_ac.date_stop:
                    raise UserError(_('Error! No puedes definir \
                                     años académicos superpuestos.'))

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        if self.date_stop and self.date_start:
            if self.date_stop < self.date_start:
                raise UserError(_('Error! La duración del año académico \
                                es invalido.'))

    @api.multi
    def generate_academicmonth(self):
        # interval = 1
        month_obj = self.env['academic.month']
        model_meses = self.mapped('month_ids')
        if model_meses:    
            model_meses.unlink()
        for data in self:
            ds = datetime.strptime(data.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < data.date_stop:
                de = ds + relativedelta(day=1, months=+1, days=-1)
                if de.strftime('%Y-%m-%d') > data.date_stop:
                    de = datetime.strptime(data.date_stop, '%Y-%m-%d')
                month_obj.create({
                    'name': self.meses_ingles_a_espaniol(ds.strftime('%B')),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'year_id': data.id,
                    'anio_lectivo': data.date_start[0:4],
                })
                ds = ds + relativedelta(day=1, months=+1)
        return True


    def meses_ingles_a_espaniol(self, mes):
        if mes:
            meses = {
                'January': 'Enero',
                'February': 'Febrero',
                'March': 'Marzo',
                'April': 'Abril',
                'May': 'Mayo',
                'June': 'Junio',
                'July': 'Julio',
                'August': 'Agosto',
                'September': 'Septiembre',
                'October': 'Octubre',
                'November': 'Noviembre',
                'December': 'Diciembre',
            }
            if mes in meses:
                mes = meses[mes]
                return mes
            else:
                return mes
        else:
            raise UserError(_("No existe Fecha Inicio"))


    @api.constrains('active')
    def contrains_validar_solo_un_activo(self):
        if len(self.search([('active', '=', True)])) > 1:
            raise UserError("Error! No puede tener activo más de un año lectivo")
