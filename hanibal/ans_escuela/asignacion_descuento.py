# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class DescuentoAlumonsEscuelaDetalle(models.TransientModel):
    _name="descuento.alumno.detalle"
    _order = "jornada_id,seccion_id,curso_id,paralelo_id"

    descuento_id =fields.Many2one('descuento.alumno',string="Relacion")
    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    alumno_id=fields.Many2one('res.partner',string="Alumno")
    alumno_nombre = fields.Char(related='alumno_id.name',string="Alumno")
    representante_id=fields.Many2one('res.partner',string="Representante")
    colaborador = fields.Many2one('tipo.colaborador',string="Colaborador")
    cant_representados = fields.Integer(string="# de Representados")
    descuentos_ids = fields.Many2many('descuentos',string='Descuentos')
    aplicar =fields.Boolean(string="Aplicar")
   
    
    

class DescuentoAlumonsEscuela(models.TransientModel):
    _name="descuento.alumno"
    _rec_name = 'descuento_id'

    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    colaborador = fields.Many2one('tipo.colaborador',string="Colaborador")
    descuento_id = fields.Many2one('descuentos',string="Descuento")
    porcentaje = fields.Float(related='descuento_id.porcentaje',string="Porcentaje")
    alumno_id=fields.Many2one('res.partner',string="Alumno",domain="[('tipo','=','H'),('parent_id','=',representante_id)]")
    representante_id=fields.Many2one('res.partner',string="Representante")
    num_representados = fields.Integer(string="# de Representados")
    descuento_line=fields.One2many('descuento.alumno.detalle','descuento_id',string="Relacion")
    consulto=fields.Boolean(string="Consulta")
    alumno_ids = fields.Many2one(related='alumno_id',string="Alumno",domain="[('tipo','=','H')]")

    @api.multi
    def consultar_alumnos(self):
    	self.env.cr.execute("""delete from descuento_alumno_detalle""")
        if self.jornada_id:
            if self.seccion_id:
                if self.curso_id:
                    if self.paralelo_id:
                        if self.colaborador.id:
                            if self.representante_id:
                                if self.alumno_id:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('paralelo_id','=',self.paralelo_id.id),
                                                                    ('parent_id.colaborador','=',self.colaborador.id),
                                                                    ('parent_id','=',self.representante_id.id),
                                                                    ('id','=',self.alumno_id.id),
                                                                    ('tipo','!=','C')])
                                else:
                                    obj_datos=self.env['res.partner'].search([
                                                                        ('jornada_id','=',self.jornada_id.id),
                                                                        ('seccion_id','=',self.seccion_id.id),
                                                                        ('curso_id','=',self.curso_id.id),
                                                                        ('paralelo_id','=',self.paralelo_id.id),
                                                                        ('parent_id.colaborador','=',self.colaborador.id),
                                                                        ('parent_id','=',self.representante_id.id),
                                                                        ('tipo','!=','C')])
                            else:
                                if self.alumno_id:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('paralelo_id','=',self.paralelo_id.id),
                                                                    ('parent_id.colaborador','=',self.colaborador.id),
                                                                    ('id','=',self.alumno_id.id),
                                                                    ('tipo','!=','C')])
                                else:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('paralelo_id','=',self.paralelo_id.id),
                                                                    ('parent_id.colaborador','=',self.colaborador.id),
                                                                    ('tipo','!=','C')])
                        else:
                            if self.representante_id:
                                if self.alumno_id:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('paralelo_id','=',self.paralelo_id.id),
                                                                    ('parent_id','=',self.representante_id.id),
                                                                    ('id','=',self.alumno_id.id),
                                                                    ('tipo','!=','C')])
                                else:
                                    obj_datos=self.env['res.partner'].search([
                                                                        ('jornada_id','=',self.jornada_id.id),
                                                                        ('seccion_id','=',self.seccion_id.id),
                                                                        ('curso_id','=',self.curso_id.id),
                                                                        ('paralelo_id','=',self.paralelo_id.id),
                                                                        ('parent_id','=',self.representante_id.id),
                                                                        ('tipo','!=','C')])
                            else:
                                if self.alumno_id:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('paralelo_id','=',self.paralelo_id.id),
                                                                    ('id','=',self.alumno_id.id),
                                                                    ('tipo','!=','C')])
                                else:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('paralelo_id','=',self.paralelo_id.id),
                                                                    ('tipo','!=','C')])

                    else:
                        if self.colaborador.id:
                            if self.representante_id:
                                if self.alumno_id:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('parent_id.colaborador','=',self.colaborador.id),
                                                                    ('parent_id','=',self.representante_id.id),
                                                                    ('id','=',self.alumno_id.id),
                                                                    ('tipo','!=','C')])
                                else:
                                    obj_datos=self.env['res.partner'].search([
                                                                        ('jornada_id','=',self.jornada_id.id),
                                                                        ('seccion_id','=',self.seccion_id.id),
                                                                        ('curso_id','=',self.curso_id.id),
                                                                        ('parent_id.colaborador','=',self.colaborador.id),
                                                                        ('parent_id','=',self.representante_id.id),
                                                                        ('tipo','!=','C')])
                            else:
                                if self.alumno_id:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('parent_id.colaborador','=',self.colaborador.id),
                                                                    ('id','=',self.alumno_id.id),
                                                                    ('tipo','!=','C')])
                                else:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('parent_id.colaborador','=',self.colaborador.id),
                                                                    ('tipo','!=','C')])
                        else:
                            if self.representante_id:
                                if self.alumno_id:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('parent_id','=',self.representante_id.id),
                                                                    ('id','=',self.alumno_id.id),
                                                                    ('tipo','!=','C')])
                                else:
                                    obj_datos=self.env['res.partner'].search([
                                                                        ('jornada_id','=',self.jornada_id.id),
                                                                        ('seccion_id','=',self.seccion_id.id),
                                                                        ('curso_id','=',self.curso_id.id),
                                                                        ('parent_id','=',self.representante_id.id),
                                                                        ('tipo','!=','C')])
                            else:
                                if self.alumno_id:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('id','=',self.alumno_id.id),
                                                                    ('tipo','!=','C')])
                                else:
                                    obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('curso_id','=',self.curso_id.id),
                                                                    ('tipo','!=','C')])

                else:
                    if self.colaborador.id:
                        if self.representante_id:
                            if self.alumno_id:
                                obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_id.id),
                                                                ('seccion_id','=',self.seccion_id.id),
                                                                ('parent_id.colaborador','=',self.colaborador.id),
                                                                ('parent_id','=',self.representante_id.id),
                                                                ('id','=',self.alumno_id.id),
                                                                ('tipo','!=','C')])
                            else:
                                obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('parent_id.colaborador','=',self.colaborador.id),
                                                                    ('parent_id','=',self.representante_id.id),
                                                                    ('tipo','!=','C')])
                        else:
                            if self.alumno_id:
                                obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_id.id),
                                                                ('seccion_id','=',self.seccion_id.id),
                                                                ('parent_id.colaborador','=',self.colaborador.id),
                                                                ('id','=',self.alumno_id.id),
                                                                ('tipo','!=','C')])
                            else:
                                obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_id.id),
                                                                ('seccion_id','=',self.seccion_id.id),
                                                                ('parent_id.colaborador','=',self.colaborador.id),
                                                                ('tipo','!=','C')])
                    else:
                        if self.representante_id:
                            if self.alumno_id:
                                obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_id.id),
                                                                ('seccion_id','=',self.seccion_id.id),
                                                                ('parent_id','=',self.representante_id.id),
                                                                ('id','=',self.alumno_id.id),
                                                                ('tipo','!=','C')])
                            else:
                                obj_datos=self.env['res.partner'].search([
                                                                    ('jornada_id','=',self.jornada_id.id),
                                                                    ('seccion_id','=',self.seccion_id.id),
                                                                    ('parent_id','=',self.representante_id.id),
                                                                    ('tipo','!=','C')])
                        else:
                            if self.alumno_id:
                                obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_id.id),
                                                                ('seccion_id','=',self.seccion_id.id),
                                                                ('id','=',self.alumno_id.id),
                                                                ('tipo','!=','C')])
                            else:
                                obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_id.id),
                                                                ('seccion_id','=',self.seccion_id.id),
                                                                ('tipo','!=','C')])
            else:
                if self.colaborador.id:
                    if self.representante_id:
                        if self.alumno_id:
                            obj_datos=self.env['res.partner'].search([
                                                            ('jornada_id','=',self.jornada_id.id),
                                                            ('parent_id.colaborador','=',self.colaborador.id),
                                                            ('parent_id','=',self.representante_id.id),
                                                            ('id','=',self.alumno_id.id),
                                                            ('tipo','!=','C')])
                        else:
                            obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_id.id),
                                                                ('parent_id.colaborador','=',self.colaborador.id),
                                                                ('parent_id','=',self.representante_id.id),
                                                                ('tipo','!=','C')])
                    else:
                        if self.alumno_id:
                            obj_datos=self.env['res.partner'].search([
                                                            ('jornada_id','=',self.jornada_id.id),
                                                            ('parent_id.colaborador','=',self.colaborador.id),
                                                            ('id','=',self.alumno_id.id),
                                                            ('tipo','!=','C')])
                        else:
                            obj_datos=self.env['res.partner'].search([
                                                            ('jornada_id','=',self.jornada_id.id),
                                                            ('parent_id.colaborador','=',self.colaborador.id),
                                                            ('tipo','!=','C')])
                else:
                    if self.representante_id:
                        if self.alumno_id:
                            obj_datos=self.env['res.partner'].search([
                                                            ('jornada_id','=',self.jornada_id.id),
                                                            ('parent_id','=',self.representante_id.id),
                                                            ('id','=',self.alumno_id.id),
                                                            ('tipo','!=','C')])
                        else:
                            obj_datos=self.env['res.partner'].search([
                                                                ('jornada_id','=',self.jornada_id.id),
                                                                ('parent_id','=',self.representante_id.id),
                                                                ('tipo','!=','C')])
                    else:
                        if self.alumno_id:
                            obj_datos=self.env['res.partner'].search([
                                                            ('jornada_id','=',self.jornada_id.id),
                                                            ('id','=',self.alumno_id.id),
                                                            ('tipo','!=','C')])
                        else:
                            obj_datos=self.env['res.partner'].search([
                                                            ('jornada_id','=',self.jornada_id.id),
                                                            ('tipo','!=','C')])
        else:
            if self.colaborador.id:
                if self.representante_id:
                    if self.alumno_id:
                        obj_datos=self.env['res.partner'].search([
                                                        ('parent_id.colaborador','=',self.colaborador.id),
                                                        ('parent_id','=',self.representante_id.id),
                                                        ('id','=',self.alumno_id.id),
                                                        ('tipo','!=','C')])
                    else:
                        obj_datos=self.env['res.partner'].search([
                                                            ('parent_id.colaborador','=',self.colaborador.id),
                                                            ('parent_id','=',self.representante_id.id),
                                                            ('tipo','!=','C')])
                else:
                    if self.alumno_id:
                        obj_datos=self.env['res.partner'].search([
                                                        ('parent_id.colaborador','=',self.colaborador.id),
                                                        ('id','=',self.alumno_id.id),
                                                        ('tipo','!=','C')])
                    else:
                        obj_datos=self.env['res.partner'].search([
                                                        ('colaborador','=',self.colaborador.id),
                                                        ('tipo','!=','C')])
            else:
                if self.representante_id:
                    if self.alumno_id:
                        obj_datos=self.env['res.partner'].search([
                                                        ('parent_id','=',self.representante_id.id),
                                                        ('id','=',self.alumno_id.id),
                                                        ('tipo','!=','C')])
                    else:
                        obj_datos=self.env['res.partner'].search([
                                                            ('parent_id','=',self.representante_id.id),
                                                            ('tipo','!=','C')])
                else:
                    if self.alumno_id:
                        obj_datos=self.env['res.partner'].search([
                                                        ('id','=',self.alumno_id.id),
                                                        ('tipo','!=','C')])
                    else:
                        obj_datos=self.env['res.partner'].search([
                                                        ('parent_id','!=',False),
                                                        ('tipo','!=','C')])

        


        obj_detalle=self.env['descuento.alumno.detalle']
        for datos in obj_datos:
            cat_rep = self.env['res.partner'].search([('parent_id','=',datos.parent_id.id)])
            dicct={}
            lista=[]
            if datos.parent_id:
                if self.num_representados:
                    if len(cat_rep)==self.num_representados:
                        for descuentos in datos.descuentos_line:
                            lista.append(descuentos.descuento_id.id)
                        dicct={
                            'descuento_id':self.id,
                            'jornada_id':datos.jornada_id.id,
                            'seccion_id':datos.seccion_id.id,
                            'curso_id':datos.curso_id.id,
                            'paralelo_id':datos.paralelo_id.id,
                            'alumno_id':datos.id,
                            'representante_id':datos.parent_id.id,
                            'colaborador':datos.parent_id.colaborador.id,
                            'cant_representados':len(cat_rep),
                            'aplicar':True,
                            
                        }
                        obj_registro=obj_detalle.create(dicct)
                        obj_registro.descuentos_ids=lista
                else:
                    for descuentos in datos.descuentos_line:
                            lista.append(descuentos.descuento_id.id)
                    dicct={
                        'descuento_id':self.id,
                        'jornada_id':datos.jornada_id.id,
                        'seccion_id':datos.seccion_id.id,
                        'curso_id':datos.curso_id.id,
                        'paralelo_id':datos.paralelo_id.id,
                        'alumno_id':datos.id,
                        'representante_id':datos.parent_id.id,
                        'colaborador':datos.parent_id.colaborador.id,
                        'cant_representados':len(cat_rep),
                        'aplicar':True,
                        
                    }
                    obj_registro=obj_detalle.create(dicct)
                    obj_registro.descuentos_ids=lista
            else:
                padres = self.env['res.partner'].search([('parent_id','=',datos.id)])
                if self.num_representados:
                    if len(padres)==self.num_representados:
                        for dato in padres:
                            lista=[]
                            for descuentos in dato.descuentos_line:
                                lista.append(descuentos.descuento_id.id)
                            dicc={
                            'descuento_id':self.id,
                            'jornada_id':dato.jornada_id.id,
                            'seccion_id':dato.seccion_id.id,
                            'curso_id':dato.curso_id.id,
                            'paralelo_id':dato.paralelo_id.id,
                            'alumno_id':dato.id,
                            'representante_id':dato.parent_id.id,
                            'colaborador':dato.parent_id.colaborador.id,
                            'cant_representados':len(padres),
                            'aplicar':True,
                            
                            }
                            obj_registro=obj_detalle.create(dicc)
                            obj_registro.descuentos_ids=lista
                else:
                    for dato in padres:
                        lista=[]
                        for descuentos in dato.descuentos_line:
                            lista.append(descuentos.descuento_id.id)
                        dicc={
                        'descuento_id':self.id,
                        'jornada_id':dato.jornada_id.id,
                        'seccion_id':dato.seccion_id.id,
                        'curso_id':dato.curso_id.id,
                        'paralelo_id':dato.paralelo_id.id,
                        'alumno_id':dato.id,
                        'representante_id':dato.parent_id.id,
                        'colaborador':dato.parent_id.colaborador.id,
                        'cant_representados':len(padres),
                        'aplicar':True,
                        
                        }
                        obj_registro=obj_detalle.create(dicc)
                        obj_registro.descuentos_ids=lista

        self.consulto=True


    @api.multi
    def aplicar_descuento(self):

        for lineas in self.descuento_line:
            if lineas.aplicar:
                obj_descuento = self.env['descuentos.tomar'].search([('partner_ids','=',lineas.alumno_id.id),('descuento_id','=',self.descuento_id.id)],limit=1)
                if len(obj_descuento)==0:
                    obj_descuento = self.env['descuentos.tomar'].create({
                    'descuento_id':self.descuento_id.id,
                    'porcentaje':self.descuento_id.porcentaje,
                    'partner_ids':lineas.alumno_id.id
                    })
        self.consultar_alumnos()

    @api.multi
    def des_aplicar_descuento(self):

        for lineas in self.descuento_line:
            if lineas.aplicar:
                obj_descuento = self.env['descuentos.tomar'].search([('partner_ids','=',lineas.alumno_id.id),('descuento_id','=',self.descuento_id.id)],limit=1)
                obj_descuento.unlink()

        self.consultar_alumnos()