# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import models, fields, api, _
import unicodedata

class jornada(models.Model):
    _name = 'jornada'
    _rec_name = 'name'
    
    
    codigo=fields.Char('Código')
    name=fields.Char('Descripción')

    @api.constrains('codigo')
    def _check_name_insensitive(self):
        model_ids = self.search([('id', '!=', self.id)])
        list_names = [x.codigo.upper() for x in model_ids if x.codigo]
        if self.codigo.upper() in list_names:
            raise Warning(
                "Ya existe un registro con el codigo: %s " % (self.codigo.upper())
            )

    def create(self, cr, uid, vals, context=None):
         if vals.get('codigo', False):
             lower = vals.get('codigo', False)
             value=lower.upper()
             vals.update({'codigo':value})
         return super(jornada,self).create(cr,uid,vals,context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('codigo', False) :
            lower = vals.get('codigo', False)
            value=lower.upper()
            vals.update({'codigo':value})
        return super(jornada, self).write(cr, uid, ids, vals, context=context)

    @api.multi
    def unlink(self):
        for l in self:
            self.env.cr.execute("""select name from curso where jornada_id={0}""".format(l.id))
            jornada=self.env.cr.dictfetchall()
            for jor in jornada:
                if jor['name'] != None:
                    raise osv.except_osv(('Alerta'),("La jornada tiene relacion con un curso."))
        return super(jornada, self).unlink()


class seccion(models.Model):
    _name = 'seccion'
    _rec_name = 'name'

    
    codigo=fields.Char('Código')
    name=fields.Char('Descripción')

    @api.constrains('codigo')
    def _check_name_insensitive(self):
        model_ids = self.search([('id', '!=', self.id)])
        list_names = [x.codigo.upper() for x in model_ids if x.codigo]
        if self.codigo.upper() in list_names:
            raise Warning(
                "Ya existe un registro con el codigo: %s " % (self.codigo.upper())
            )

    def create(self, cr, uid, vals, context=None):
         if vals.get('codigo', False):
             lower = vals.get('codigo', False)
             value=lower.upper()
             vals.update({'codigo':value})
         return super(seccion,self).create(cr,uid,vals,context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('codigo', False) :
            lower = vals.get('codigo', False)
            value=lower.upper()
            vals.update({'codigo':value})
        return super(seccion, self).write(cr, uid, ids, vals, context=context)

    @api.multi
    def unlink(self):
        for l in self:
            self.env.cr.execute("""select name from curso where seccion_id={0}""".format(l.id))
            seccion=self.env.cr.dictfetchall()
            for secc in seccion:
                if secc['name'] != None:
                    raise osv.except_osv(('Alerta'),("La seccion tiene relacion con un curso."))
        return super(seccion, self).unlink()
    

class curso(models.Model):
    _name = 'curso'
    _rec_name = 'display_name'
    
    codigo=fields.Char('Código')
    name=fields.Char('Descripción') 
    seccion_id=fields.Many2one('seccion','Sección')
    jornada_id=fields.Many2one('jornada','Jornada')
    producto_id=fields.Many2one("product.product",string="Producto")
    display_name =fields.Char(string="Nombre a mostrar")

    @api.constrains('name','seccion_id','jornada_id')
    def guardar_display_name(self):
        display_name=' '
        jornada=''
        seccion=''
        curso=''
        if self.seccion_id==False and self.jornada_id==False and self.name==False:
            self.display_name=str(str(self.codigo).encode('utf-8'))
        else:
            jornada=(self.jornada_id.name.encode('utf-8'))
            seccion=(self.seccion_id.name.encode('utf-8'))
            curso=(self.name.encode('utf-8'))
            display_name=str(jornada+'/'+seccion+'/'+curso)
            print(display_name,'display_name')
            self.env.cr.execute("update curso set display_name='{0}' where id={1}".format(str(display_name),self.id))

    @api.constrains('codigo')
    def _check_name_insensitive(self):
        model_ids = self.search([('id', '!=', self.id)])
        list_names = [x.codigo.upper() for x in model_ids if x.codigo]
        if self.codigo.upper() in list_names:
            raise Warning(
                "Ya existe un registro con el codigo: %s " % (self.codigo.upper())
            )

    def create(self, cr, uid, vals, context=None):
         if vals.get('codigo', False):
             lower = vals.get('codigo', False)
             value=lower.upper() 
             vals.update({'codigo':value})
         return super(curso,self).create(cr,uid,vals,context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('codigo', False) :
            lower = vals.get('codigo', False)
            value=lower.upper()
            vals.update({'codigo':value})
        return super(curso, self).write(cr, uid, ids, vals, context=context)

    @api.multi
    def unlink(self):
        for l in self:
            self.env.cr.execute("""select codigo from paralelo where curso_id={0}""".format(l.id))
            paralelo=self.env.cr.dictfetchall()
            for par in paralelo:
                if par['name'] != None:
                    raise osv.except_osv(('Alerta'),("El curso tiene relacion con un paralelo."))
        return super(curso, self).unlink()

class paralelo(models.Model):
    _name = 'paralelo'
    _rec_name = 'codigo'
    
    codigo=fields.Char('Código')
    curso_id=fields.Many2one('curso','Curso')
    jornada_id=fields.Many2one(related='curso_id.jornada_id',string="Jornada")
    seccion_id=fields.Many2one(related='curso_id.seccion_id',string="Sección")

    # @api.constrains('codigo','curso_id') 
    # def _check_name_insensitive(self):
    #     model_ids = self.search([('id', '!=', self.id)])
    #     list_names = [x.codigo for x in model_ids if x.codigo]
    #     list_cursos = [x.curso_id.id for x in model_ids if x.curso_id.id]
    #     if self.codigo in list_names and self.curso_id.id in list_cursos:
    #         raise Warning(
    #             "Ya existe un registro con el codigo: %s " % (self.codigo)
    #         )


    def create(self, cr, uid, vals, context=None):
         if vals.get('codigo', False):
             lower = vals.get('codigo', False)
             value=lower.upper()
             vals.update({'codigo':value})
         return super(paralelo,self).create(cr,uid,vals,context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('codigo', False) :
            lower = vals.get('codigo', False)
            value=lower.upper()
            vals.update({'codigo':value})
        return super(paralelo, self).write(cr, uid, ids, vals, context=context)

    @api.multi
    def unlink(self):
        for l in self:
            self.env.cr.execute("""select name from res_partner where paralelo_id={0}""".format(l.id))
            representado=self.env.cr.dictfetchall()
            for repre in representado:
                if repre['name'] != None:
                    raise osv.except_osv(('Alerta'),("El paralelo tiene relacion con un representado."))
        return super(paralelo, self).unlink()

