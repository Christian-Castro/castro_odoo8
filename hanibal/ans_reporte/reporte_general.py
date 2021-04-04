# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import datetime,timedelta,date
import calendar
import base64

class ReporteEscuelaDetalle(models.TransientModel):
    _name="reporte.escuela.detalle"
    _order = "jornada_id,seccion_id,curso_id,paralelo_id"

    reporte_id =fields.Many2one('reporte.escuela',string="Relacion")
    orden=fields.Char(string="Orden",readonly='1')
    codigo=fields.Char(string="Código",readonly='1')
    alumno=fields.Char(string="Alumno",readonly='1')
    representante=fields.Char(string="Representante",readonly='1')
    correo=fields.Char(string="Correo",readonly='1')
    direccion=fields.Char(string="Direccion",readonly='1')
    telefono=fields.Char(string="Telefono",readonly='1')
    cedula=fields.Char(string="Cédula",readonly='1')
    state=fields.Char(string="Status",readonly='1')
    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    cant_estudiante = fields.Integer(string="Cant. Representados:")

class ReporteEscuela(models.TransientModel):
    _name="reporte.escuela"
    _rec_name = 'jornada_id'

    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)
    filename=fields.Char(string="Nombre de archivo")
    archivo_xls=fields.Binary(string='Archivo Excel')
    filename_pdf=fields.Char(string="Nombre de archivo")
    archivo_pdf=fields.Binary(string='Archivo PDF')
    reporte_line=fields.One2many('reporte.escuela.detalle','reporte_id',string="Relacion")
    fecha_emision= fields.Datetime('Fecha Emisión', readonly=True, copy=False,select=True,)

    _defaults = {
        'fecha_emision': fields.datetime.now(),
    }

    @api.onchange('jornada_id')
    def onchange_jornada(self):
        for l in self:
            if l.jornada_id:
                l.seccion_id=False
                l.curso_id= False
                l.paralelo_id = False

    @api.onchange('seccion_id')
    def onchange_seccion(self):
        for l in self:
            if l.seccion_id:
                l.curso_id= False
                l.paralelo_id = False

    @api.onchange('curso_id')
    def onchange_curso(self):
        for l in self:
            if l.curso_id:
                l.paralelo_id = False


