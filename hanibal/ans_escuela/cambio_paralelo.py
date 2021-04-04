# -*- coding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import models, fields, api, _

class CambioParaleloDetalle(models.Model):
    _name="cambio.paralelo.detalle"
    _order = "contador asc"

    paralelod_id =fields.Many2one('cambio.paralelo',string="Relacion")
    contador = fields.Integer(string="Número")
    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    alumno_id=fields.Many2one('res.partner',string="Alumno")
    alumno_nombre = fields.Char(related='alumno_id.name',string="Alumno")
    codigo_alumno = fields.Char(related='alumno_id.codigo_alumno',string="Código")
    facturar = fields.Boolean('Facturar')
    #cobrar = fields.Boolean('Cobrar')
   
    
class CambioParaleloDetalleDespues(models.Model):
    _name="cambio.paralelo.detalle_nuevo"
    _order = "contador asc"

    paralelod_nuevo_id =fields.Many2one('cambio.paralelo',string="Relacion")
    contador = fields.Integer(string="Número")
    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    alumno_id=fields.Many2one('res.partner',string="Alumno")
    alumno_nombre = fields.Char(related='alumno_id.name',string="Alumno")
    codigo_alumno = fields.Char(related='alumno_id.codigo_alumno',string="Código")
    facturar = fields.Boolean('Facturar')
    #cobrar = fields.Boolean('Cobrar')

class CambioParalelo(models.Model):
    _name="cambio.paralelo"
    _rec_name = 'jornada_actual_id'

    #actual
    jornada_actual_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_actual_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_actual_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_actual_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    alumno_id=fields.Many2one('res.partner',string="Alumno")
    
    #nuevo
    jornada_nuevo_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_nuevo_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_nuevo_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_nuevo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)

    paralelo_line=fields.One2many('cambio.paralelo.detalle','paralelod_id',string="Relacion")
    paralelos_line_nuevo=fields.One2many('cambio.paralelo.detalle_nuevo','paralelod_nuevo_id',string="Relacion")
    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)
    estado = fields.Selection( (('0','Borrador'),
                               ('1','Ejecutado'),
                               ('2','Anulado')) , 'Estados', required=False)
    accion = fields.Selection( (('0','Ninguno'),
                               ('1','Facturar'),
                               ('2','Cobrar'),
                               ('3','Deshabilitar Facturación')) , 'Acción', required=False, default='0')



    @api.onchange('jornada_nuevo_id')
    def onchange_jornada(self):
        for l in self:
            if l.jornada_nuevo_id:
                l.seccion_nuevo_id=False
                l.curso_nuevo_id= False
                l.paralelo_nuevo_id = False

    @api.onchange('seccion_nuevo_id')
    def onchange_seccion(self):
        for l in self:
            if l.seccion_nuevo_id:
                l.curso_nuevo_id= False
                l.paralelo_nuevo_id = False

    @api.onchange('curso_nuevo_id')
    def onchange_curso(self):
        for l in self:
            if l.curso_nuevo_id:
                l.paralelo_nuevo_id = False

    @api.onchange('jornada_actual_id')
    def onchange_jornada_actual(self):
        for l in self:
            if l.jornada_actual_id:
                l.seccion_actual_id=False
                l.curso_actual_id= False
                l.paralelo_actual_id = False

    @api.onchange('seccion_actual_id')
    def onchange_seccion_actual(self):
        for l in self:
            if l.seccion_actual_id:
                l.curso_actual_id= False
                l.paralelo_actual_id = False

    @api.onchange('curso_actual_id')
    def onchange_curso_actual(self):
        for l in self:
            if l.curso_actual_id:
                l.paralelo_actual_id = False

    @api.multi
    def consultar(self):
        self.estado='0'
        self.env.cr.execute("""delete from cambio_paralelo_detalle""")
        if self.jornada_actual_id:
            if self.seccion_actual_id:
                if self.curso_actual_id:
                    if self.paralelo_actual_id:
                        obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_actual_id.id),
                                                                ('seccion_id','=',self.seccion_actual_id.id),
                                                                ('curso_id','=',self.curso_actual_id.id),
                                                                ('paralelo_id','=',self.paralelo_actual_id.id),
                                                                ('tipo','=','H')])
                    else:
                        obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_actual_id.id),
                                                                ('seccion_id','=',self.seccion_actual_id.id),
                                                                ('curso_id','=',self.curso_actual_id.id),
                                                                ('tipo','=','H')])
                else:
                    obj_datos=self.env['res.partner'].search([
                                                            ('jornada_id','=',self.jornada_actual_id.id),
                                                            ('seccion_id','=',self.seccion_actual_id.id),
                                                                ('tipo','=','H')])
            else:
                obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_actual_id.id),
                                                                ('tipo','=','H')])
        orden=1
        obj_detalle=self.env['cambio.paralelo.detalle']
        for datos in obj_datos:
            dicc={}
            dicct={}
            obj_detalle.create({
                'contador':orden,
                'jornada_id':datos.jornada_id.id,
                'seccion_id':datos.seccion_id.id,
                'curso_id':datos.curso_id.id,
                'paralelo_id':datos.paralelo_id.id,
                'alumno_id':datos.id,                
                'codigo':datos.codigo_alumno,
                'facturar':True,
                'cobrar':True,
                'paralelod_id':self.id,

            })
            orden=orden+1



    @api.multi
    def ejecutar(self):
        self.estado='1'

        if self.accion=='0': 
            if self.jornada_nuevo_id and self.seccion_nuevo_id and self.curso_nuevo_id and self.paralelo_nuevo_id:

                for datos in self.paralelo_line:
                    obj_alumno = self.env['res.partner'].search([('id','=',datos.alumno_id.id),('tipo','=','H')])
                    obj_alumno.jornada_anterior_id=obj_alumno.jornada_id.id
                    obj_alumno.seccion_anterior_id=obj_alumno.seccion_id.id
                    obj_alumno.curso_anterior_id=obj_alumno.curso_id.id
                    obj_alumno.paralelo_anterior_id=obj_alumno.paralelo_id.id

                    obj_alumno.update({'jornada_id':False})
                    obj_alumno.update({'seccion_id':False})
                    obj_alumno.update({'curso_id':False})
                    obj_alumno.update({'paralelo_id':False})

                for datos in self.paralelo_line:
                    obj_alumno = self.env['res.partner'].search([('id','=',datos.alumno_id.id),('tipo','=','H')])
                    obj_alumno.write({'jornada_id':self.jornada_nuevo_id.id})
                    obj_alumno.jornada_id=self.jornada_nuevo_id.id
                    obj_alumno.write({'seccion_id':self.seccion_nuevo_id.id})
                    obj_alumno.seccion_id=self.seccion_nuevo_id.id
                    obj_alumno.write({'curso_id':self.curso_nuevo_id.id})
                    obj_alumno.curso_id=self.curso_nuevo_id.id
                    obj_alumno.write({'paralelo_id':self.paralelo_nuevo_id.id})
                    obj_alumno.paralelo_id=self.paralelo_nuevo_id.id


                for nuevo in self.paralelo_line:
                    orden=1
                    obj_alumno_nuevo = self.env['res.partner'].search([('id','=',nuevo.alumno_id.id),('tipo','=','H')])
                    obj_detalle=self.env['cambio.paralelo.detalle_nuevo']
                    for datos in obj_alumno_nuevo:
                        dicc={}
                        dicct={}
                        obj_detalle.create({
                            'contador':orden,
                            'jornada_id':datos.jornada_id.id,
                            'seccion_id':datos.seccion_id.id,
                            'curso_id':datos.curso_id.id,
                            'paralelo_id':datos.paralelo_id.id,
                            'alumno_id':datos.id,                
                            'codigo':datos.codigo_alumno,
                            'facturar':True,
                            'cobrar':True,
                            'paralelod_nuevo_id':self.id,

                        })
                        orden=orden+1
            else:
                raise osv.except_osv(('Alerta'),("Debe llenar la jornada, seccion, curso y paralelo al que desea realizar el cambio de paralelo."))
        elif self.accion=='1':
            for datos in self.paralelo_line:
                obj_alumno = self.env['res.partner'].search([('id','=',datos.alumno_id.id),('tipo','=','H')])
                obj_alumno_detalle = self.env['res.partner.historico'].create({
                    'usuario_id':self.usuario_id.id,
                    'enero':obj_alumno.enero,
                    'febrero':obj_alumno.febrero,
                    'marzo':obj_alumno.marzo,
                    'abril':obj_alumno.abril,
                    'mayo':obj_alumno.mayo,
                    'junio':obj_alumno.junio,
                    'julio':obj_alumno.julio,
                    'agosto':obj_alumno.agosto,
                    'septiembre':obj_alumno.septiembre,
                    'octubre':obj_alumno.octubre,
                    'noviembre':obj_alumno.noviembre,
                    'diciembre':obj_alumno.diciembre,
                    'alumno_id':obj_alumno.id,
                    'accion':'1',
                    })

                obj_alumno.enero=True
                obj_alumno.febrero=True
                obj_alumno.marzo=True
                obj_alumno.abril=True
                obj_alumno.mayo=True
                obj_alumno.junio=True
                obj_alumno.julio=True
                obj_alumno.agosto=True
                obj_alumno.septiembre=True
                obj_alumno.octubre=True
                obj_alumno.noviembre=True
                obj_alumno.diciembre=True
        elif self.accion=='2':
            for datos in self.paralelo_line:
                datos.facturar=False
                obj_alumno = self.env['res.partner'].search([('id','=',datos.alumno_id.id),('tipo','=','H')])
                obj_alumno_detalle = self.env['res.partner.historico'].create({
                    'usuario_id':self.usuario_id.id,
                    'enero':obj_alumno.enero,
                    'febrero':obj_alumno.febrero,
                    'marzo':obj_alumno.marzo,
                    'abril':obj_alumno.abril,
                    'mayo':obj_alumno.mayo,
                    'junio':obj_alumno.junio,
                    'julio':obj_alumno.julio,
                    'agosto':obj_alumno.agosto,
                    'septiembre':obj_alumno.septiembre,
                    'octubre':obj_alumno.octubre,
                    'noviembre':obj_alumno.noviembre,
                    'diciembre':obj_alumno.diciembre,
                    'alumno_id':obj_alumno.id,
                    'accion':'2',
                    })

                obj_alumno.enero=False
                obj_alumno.febrero=False
                obj_alumno.marzo=False
                obj_alumno.abril=False
                obj_alumno.mayo=False
                obj_alumno.junio=False
                obj_alumno.julio=False
                obj_alumno.agosto=False
                obj_alumno.septiembre=False
                obj_alumno.octubre=False
                obj_alumno.noviembre=False
                obj_alumno.diciembre=False
        elif self.accion=='3':
            for datos in self.paralelo_line:
                datos.facturar=False
                obj_alumno = self.env['res.partner'].search([('id','=',datos.alumno_id.id),('tipo','=','H')])
                obj_alumno.facturar=False



    @api.multi
    def anular(self):
        self.estado='2'
        if self.accion=='0':
            for datos in self.paralelos_line_nuevo:
                obj_alumno = self.env['res.partner'].search([('id','=',datos.alumno_id.id),('tipo','=','H')])
                obj_alumno.jornada_id=obj_alumno.jornada_anterior_id.id
                obj_alumno.seccion_id=obj_alumno.seccion_anterior_id.id
                obj_alumno.curso_id=obj_alumno.curso_anterior_id.id
                obj_alumno.paralelo_id=obj_alumno.paralelo_anterior_id.id

                obj_alumno.update({'jornada_anterior_id':False})
                obj_alumno.update({'seccion_anterior_id':False})
                obj_alumno.update({'curso_anterior_id':False})
                obj_alumno.update({'paralelo_anterior_id':False})



        elif self.accion=='1':
            for datos in self.paralelo_line:
                obj_alumno = self.env['res.partner'].search([('id','=',datos.alumno_id.id),('tipo','=','H')])
                for hist in obj_alumno.historico_id:
                    obj_alumno.enero=hist.enero
                    obj_alumno.febrero=hist.febrero
                    obj_alumno.marzo=hist.marzo
                    obj_alumno.abril=hist.abril
                    obj_alumno.mayo=hist.mayo
                    obj_alumno.junio=hist.junio
                    obj_alumno.julio=hist.julio
                    obj_alumno.agosto=hist.agosto
                    obj_alumno.septiembre=hist.septiembre
                    obj_alumno.octubre=hist.octubre
                    obj_alumno.noviembre=hist.noviembre
                    obj_alumno.diciembre=hist.diciembre

                self.env.cr.execute("delete from res_partner_historico where alumno_id={0} and accion='1'".format(obj_alumno.id))

        elif self.accion=='2':
            for datos in self.paralelo_line:
                datos.cobrar=True
                obj_alumno = self.env['res.partner'].search([('id','=',datos.alumno_id.id),('tipo','=','H')])
                for hist in obj_alumno.historico_id:
                    obj_alumno.enero=hist.enero
                    obj_alumno.febrero=hist.febrero
                    obj_alumno.marzo=hist.marzo
                    obj_alumno.abril=hist.abril
                    obj_alumno.mayo=hist.mayo
                    obj_alumno.junio=hist.junio
                    obj_alumno.julio=hist.julio
                    obj_alumno.agosto=hist.agosto
                    obj_alumno.septiembre=hist.septiembre
                    obj_alumno.octubre=hist.octubre
                    obj_alumno.noviembre=hist.noviembre
                    obj_alumno.diciembre=hist.diciembre

                self.env.cr.execute("delete from res_partner_historico where alumno_id={0} and accion='2'".format(obj_alumno.id))

        elif self.accion=='3':
            for datos in self.paralelo_line:
                datos.facturar=True
                obj_alumno = self.env['res.partner'].search([('id','=',datos.alumno_id.id),('tipo','=','H')])
                obj_alumno.facturar=True

