# -*- coding: utf-8 -*-
# -*- coding: 850 -*-
from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import ValidationError
DATE_FORMAT = '%Y-%m-%d'

class RecordatorioDetalleExtra(models.Model):
    _inherit = 'mail.mail'

    id_recordatorio = fields.Many2one('recordatorio.extra',string="Recordatorio")



class RecordatorioDetalleExtra(models.Model):
    _name = 'recordatorio.detalle.extra'

    recordatorio_extra_cabecera = fields.Many2one('recordatorio.extra',string="Cabecera",ondele='cascade')
    concepto = fields.Char(string="Concepto")
    monto = fields.Float(string="Monto")
    fecha_factura = fields.Date(string='Fecha')


class RecordatorioExtra(models.Model):
    _name = 'recordatorio.extra'

    recordatorio_cabecera_extra = fields.Many2one('recordatorio',string="Cabecera",ondele='cascade')
    recordatorio_detalle_ext = fields.One2many('recordatorio.detalle.extra','recordatorio_extra_cabecera',string="Detalle",ondele='cascade')
    alumno_id = fields.Many2one('res.partner',string="Alumno")
    representante_id = fields.Many2one('res.partner',string="Representante",domain="[('tipo','=','P'),('parner_id','=',alumno_id)]")
    correo_repres = fields.Char(string="Correo")
    descripcion = fields.Char(string="Descripcion")
    fecha_emision = fields.Date(string="Fecha Emision")

    _defaults = {
        'fecha_emision': fields.datetime.now(),
    }

class RecordatorioDetalle(models.Model):
    _name = 'recordatorio.detalle'

    recordatorio_cabecera = fields.Many2one('recordatorio',string="Cabecera")
    jornada_id = fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id = fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id = fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id = fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    descripcion = fields.Char(string="Estructura Escolar")
    alumno_id = fields.Many2one('res.partner',string="Alumno")
    representante_id = fields.Many2one('res.partner',string="Representante",domain="[('tipo','=','P'),('parner_id','=',alumno_id)]")
    correo_repres = fields.Char(string="Correo")
    factura_id = fields.Many2one('account.invoice',string="Factura")
    numerofac = fields.Char(related='factura_id.numerofac',string='Factura')
    fecha_factura = fields.Date(string='Fecha')
    concepto = fields.Char(string="Concepto")
    monto = fields.Float(string="Monto")
    saldo = fields.Float(string="Saldo")
    cant_notificacion = fields.Integer(string="# Notificaciones")
    fecha_envio_correo = fields.Date(string='Fecha envio correo')
    fecha_emision = fields.Date(string="Fecha Emision")
    mail_id = fields.Many2one('mail.mail',string="Mail")

    _defaults = {
        'fecha_emision': fields.datetime.now(),
    }

    @api.multi
    def action_from(self):
        if self.mail_id.id:
            viewid = self.env.ref('ans_escuela.view_mails_form').id
            context = self._context.copy()
            return {   
                    'name':'Detalle de Email',
                    'res_model': 'mail.mail',
                    'view_type': 'form',
                    'views' : [(viewid,'form')],
                    'type':'ir.actions.act_window',
                    'nodestroy': True,
                    'res_id': self.mail_id.id,
                    'target':'new',
                    'context':context,
                    }
        else:
            raise ValidationError('No ha enviado correo.')



class Recordatorio(models.Model):
    _name = 'recordatorio'
    _rec_name = 'sequence'
    _order="sequence asc"

    recordatorio_detalle_extra = fields.One2many('recordatorio.extra','recordatorio_cabecera_extra',string="Detalle",ondele='cascade')
    recordatorio_detalle = fields.One2many('recordatorio.detalle','recordatorio_cabecera',string="Detalle")
    sequence = fields.Char('Codigo', readonly=True, copy=False)
    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)
    fecha_desde = fields.Date(string="Fecha Inicial")
    fecha_hasta = fields.Date(string="Fecha Final")
    numero_facturas = fields.Integer(string="Cant. Facturas Impagas")
    plantilla_correo_id = fields.Many2one('email.template',string="Plantilla de Correo")
    jornada_id = fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id = fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id = fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id = fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    alumno_id = fields.Many2one('res.partner',string="Alumno",domain="[('tipo','=','H'),('parent_id','=',representante_id)]")
    representante_id = fields.Many2one('res.partner',string="Representante",domain="[('tipo','=','P')]")
    estado = fields.Selection( (('0','Borrador'),
                               ('1','Ejecutado'),
                               ('2','Finalizado')) , 'Estados', required=False)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('recordatorio') or '/'
        vals['sequence'] = seq
        a = super(Recordatorio, self).create(vals)
        return a

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

    
    @api.multi
    def traer_informacion(self):
        ## EXTRAER DATOS
        self.estado='0'
        self.env.cr.execute("delete from recordatorio_detalle where recordatorio_cabecera={0}".format(self.id))
        valido=0
        obj_datos={}
        if self.jornada_id:
            if self.seccion_id:
                if self.curso_id:
                    if self.paralelo_id:
                        valido=1
                        if self.representante_id:
                            if self.alumno_id:
                                obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('paralelo_id','=',self.paralelo_id.id),('parent_id','=',self.representante_id.id),('id','=',self.alumno_id.id),('tipo','=','H'),('active','in',(True,False))])
                            else:
                                obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('paralelo_id','=',self.paralelo_id.id),('parent_id','=',self.representante_id.id),('tipo','=','H'),('active','in',(True,False))])
                        else:
                            obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('paralelo_id','=',self.paralelo_id.id),('tipo','=','H'),('active','in',(True,False))])
                    else:
                        valido=2
                        if self.representante_id:
                            if self.alumno_id:
                                obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('parent_id','=',self.representante_id.id),('id','=',self.alumno_id.id),('tipo','=','H'),('active','in',(True,False))])
                            else:
                                obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('parent_id','=',self.representante_id.id),('tipo','=','H'),('active','in',(True,False))])
                        else:
                            obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('tipo','=','H'),('active','in',(True,False))])
                else:
                    valido=3
                    if self.representante_id:
                        if self.alumno_id:
                            obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('parent_id','=',self.representante_id.id),('id','=',self.alumno_id.id),('tipo','=','H'),('active','in',(True,False))])
                        else:
                            obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('parent_id','=',self.representante_id.id),('tipo','=','H'),('active','in',(True,False))])
                    else:
                        obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('tipo','=','H'),('active','in',(True,False))])
            else:
                valido=4
                if self.representante_id:
                    if self.alumno_id:
                        obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('parent_id','=',self.representante_id.id),('id','=',self.alumno_id.id),('tipo','=','H'),('active','in',(True,False))])
                    else:
                        obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('parent_id','=',self.representante_id.id),('tipo','=','H'),('active','in',(True,False))])
                else:
                    obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('tipo','=','H'),('active','in',(True,False))])
        if len(obj_datos)==0:
            if self.representante_id:
                if self.alumno_id:
                    obj_datos=self.env['res.partner'].search([('parent_id','=',self.representante_id.id),('id','=',self.alumno_id.id),('tipo','=','H'),('active','in',(True,False))])
                else:
                    obj_datos=self.env['res.partner'].search([('parent_id','=',self.representante_id.id),('tipo','=','H'),('active','in',(True,False))])
                    print(len(obj_datos),'len(obj_datos) 2')

        contador=0
        if len(obj_datos)!=0:
            for datos in obj_datos:
                #print('else',datos.id)
                if self.representante_id:
                    if valido==1:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('partner_id','=',self.representante_id.id),('alumno_id','=',datos.id),('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('paralelo_id','=',self.paralelo_id.id),('state','=','open'),('residual','!=',0.0)])
                    elif valido==2:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('partner_id','=',self.representante_id.id),('alumno_id','=',datos.id),('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('state','=','open'),('residual','!=',0.0)])
                    elif valido==3:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('partner_id','=',self.representante_id.id),('alumno_id','=',datos.id),('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('state','=','open'),('residual','!=',0.0)])
                    elif valido==4:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('partner_id','=',self.representante_id.id),('alumno_id','=',datos.id),('jornada_id','=',self.jornada_id.id),('state','=','open'),('residual','!=',0.0)])
                    else:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('partner_id','=',self.representante_id.id),('alumno_id','=',datos.id),('state','=','open'),('residual','!=',0.0)])
                else:
                    if valido==1:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('alumno_id','=',datos.id),('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('paralelo_id','=',self.paralelo_id.id),('state','=','open'),('residual','!=',0.0)])
                    elif valido==2:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('alumno_id','=',datos.id),('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('state','=','open'),('residual','!=',0.0)])
                    elif valido==3:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('alumno_id','=',datos.id),('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('state','=','open'),('residual','!=',0.0)])
                    elif valido==4:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('alumno_id','=',datos.id),('jornada_id','=',self.jornada_id.id),('state','=','open'),('residual','!=',0.0)])
                    else:
                        obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('alumno_id','=',datos.id),('state','=','open'),('residual','!=',0.0)])

                #print(len(obj_factura),'cantidad facturas')
                if len(obj_factura) >= self.numero_facturas:
                    detalle_rec = self.env['recordatorio.detalle']
                    for fac in obj_factura:
                        descrip = ''
                        for line in fac.invoice_line:
                            descrip=descrip +str(line.name)+ '-'
                        
                        descripcion = '%s/%s/%s/%s' % (fac.jornada_id.codigo,fac.seccion_id.name,fac.curso_id.name,fac.paralelo_id.codigo)

                        obj_detalle = detalle_rec.create({
                            'recordatorio_cabecera':self.id,
                            'jornada_id':fac.jornada_id.id,
                            'seccion_id':fac.seccion_id.id,
                            'curso_id':fac.curso_id.id,
                            'paralelo_id':fac.paralelo_id.id,
                            'descripcion':descripcion,
                            'alumno_id':fac.alumno_id.id,
                            'representante_id':fac.partner_id.id,
                            'correo_repres':fac.partner_id.email,
                            'factura_id':fac.id,
                            'concepto':descrip,
                            'fecha_factura':fac.date_invoice,
                            'monto':fac.amount_total,
                            'saldo':fac.residual,
                        })
                        #print(obj_detalle.id,'detalle recordatorio 1 ')
        else:
            obj_factura = self.env['account.invoice'].search([('date_invoice','>=',self.fecha_desde),('date_invoice','<=',self.fecha_hasta),('state','=','open'),('residual','!=',0.0)])
            if len(obj_factura) >= self.numero_facturas:
                detalle_rec = self.env['recordatorio.detalle']
                for fac in obj_factura:
                    descrip = ''
                    for line in fac.invoice_line:
                        descrip=descrip +str(line.name)+ '-'

                    descripcion = '%s/%s/%s/%s' % (fac.jornada_id.codigo,fac.seccion_id.name,fac.curso_id.name,fac.paralelo_id.codigo)

                    obj_detalle = detalle_rec.create({
                        'recordatorio_cabecera':self.id,
                        'jornada_id':fac.jornada_id.id,
                        'seccion_id':fac.seccion_id.id,
                        'curso_id':fac.curso_id.id,
                        'paralelo_id':fac.paralelo_id.id,
                        'descripcion':descripcion,
                        'alumno_id':fac.alumno_id.id,
                        'representante_id':fac.partner_id.id,
                        'correo_repres':fac.partner_id.email,
                        'factura_id':fac.id,
                        'concepto':descrip,
                        'fecha_factura':fac.date_invoice,
                        'monto':fac.amount_total,
                        'saldo':fac.residual,
                    })
                    #print(obj_detalle.id,'detalle recordatorio 2 ')

        ## CONTEO DE CORREO

        obj_mails=self.env['mail.mail'].search([('id_recordatorio','!=',None)])
        print(len(obj_mails),'cantidad mails')
        lista_id= [value.id_recordatorio.id for value in obj_mails]
        print(lista_id,'cantidad lista_id')
        obj_detalle_extra=self.env['recordatorio.extra'].search([('id','in',lista_id)])
        lista=[]
        for l in obj_detalle_extra:
            dicr={
            'alumno_id':None,
            'representante':None,
            'descripcion':None,
            'contador':None
            }
            contador=0
            for e in obj_detalle_extra:
                print(l.alumno_id.id,l.representante_id.id,l.descripcion,'valor 1')
                print(e.alumno_id.id,e.representante_id.id,e.descripcion,'valor 2')
                if e.alumno_id.id == l.alumno_id.id and e.representante_id.id == l.representante_id.id and e.descripcion == l.descripcion:
                    contador=contador+1
                print(contador,'contador')

            dicr={
                    'alumno_id':l.alumno_id.id,
                    'representante_id':l.representante_id.id,
                    'descripcion':l.descripcion,
                    'contador':contador
                }
            lista.append(dicr)
            print(dicr,'dicr')
        for d in lista:
            obj_rec=self.env['recordatorio.detalle'].search([('recordatorio_cabecera','=',self.id),('alumno_id','=',d['alumno_id']),('representante_id','=',d['representante_id']),('descripcion','=',d['descripcion'])])
            for o in obj_rec:
                o.cant_notificacion=d['contador']



    @api.multi
    def generar_correos(self):
        # ENVIO DE RECORDATORIO
        self.env.cr.execute("""delete from recordatorio_extra where recordatorio_cabecera_extra={0}""".format(self.id))
        obj_detalle = self.env['recordatorio.detalle'].search([('recordatorio_cabecera','=',self.id)])

        dic={
            'alumno_id':None,
            'representante':None,
            'descripcion':None,
            'correo_repres':None
        }
        obj_detalle = self.env['recordatorio.detalle'].search([('recordatorio_cabecera','=',self.id)])
        for l in obj_detalle:
            print(l.id)
            val=0
            for d in dic:
                if l.alumno_id.id == dic['alumno_id'] and l.representante_id.id == dic['representante_id']:
                    val=1
            if val==0:
                dic={
                    'alumno_id':l.alumno_id.id,
                    'representante_id':l.representante_id.id,
                    'descripcion':l.descripcion,
                    'correo_repres':l.correo_repres,
                    'recordatorio_cabecera_extra':self.id
                }
                obj_cab = self.env['recordatorio.extra'].create(dic)
                obj_det = self.env['recordatorio.detalle.extra'].create({
                    'recordatorio_extra_cabecera':obj_cab.id,
                    'concepto':l.concepto,
                    'monto':l.monto,
                    'fecha_factura':l.fecha_factura
                    })
            else:
                obj_datos= self.env['recordatorio.extra'].search([('alumno_id','=',l.alumno_id.id),('representante_id','=',l.representante_id.id),('recordatorio_cabecera_extra','=',self.id)])
                if len(obj_datos)!=0:
                    obj_det = self.env['recordatorio.detalle.extra'].create({
                        'recordatorio_extra_cabecera':obj_cab.id,
                        'concepto':l.concepto,
                        'monto':l.monto,
                        'fecha_factura':l.fecha_factura
                        })


        print(self.plantilla_correo_id.id,'self.plantilla_correo_id.id')
        obj_envio = self.env['email.template'].browse(self.plantilla_correo_id.id)
        print(obj_envio.id)
        for s in self.recordatorio_detalle_extra:
            email_id=obj_envio.send_mail(s.id)
            print(email_id,'email_id')
            obj_mail=self.env['mail.mail'].browse(email_id)
            print(obj_mail,'obj_mail')

            tabla="""<table style="padding:0px;width:600px;margin:auto;background: #FFFFFF repeat top /100%;color:#777777" border="1">
                     <tbody>
                     <tr>
                        <th style=" 0 0px 0;">MES</th>
                        <th style=" 0 0px 0;">VALOR</th>
                      </tr>
                      detalle_tabla
                      </tbody></table>"""
            detalle=""

        
            for linea in s.recordatorio_detalle_ext:
                detalle=detalle+"""<tr>"""
                detalle=detalle+"""<td style=" 0 0px 0;">{0}</td> """.format(linea.concepto)
                linea_valor_valor_redondeado="$%.2f" % (linea.monto or 0)
                detalle=detalle+"""<td style=" 0 0px 0;">{0}</td> """.format(linea_valor_valor_redondeado)

                detalle=detalle+"""</tr>"""

            print(len(s.recordatorio_detalle_ext),'len(s.recordatorio_detalle_ext)')
            if len(s.recordatorio_detalle_ext)>0:
                body_html_modifi=obj_mail.body_html.replace("detalle_tabla",tabla.replace("detalle_tabla",detalle))
            else:
                body_html_modifi=obj_mail.body_html.replace("detalle_tabla","")
            obj_mail.body_html=body_html_modifi
            obj_mail.mail_message_id.body=body_html_modifi
            obj_mail.id_recordatorio=s.id

        ## RELACIONAR CORREO

        obj_detalle_extra=self.env['recordatorio.extra'].search([('recordatorio_cabecera_extra','=',self.id)])
        for l in obj_detalle_extra:
            obj_rec=self.env['recordatorio.detalle'].search([('recordatorio_cabecera','=',self.id),('alumno_id','=',l.alumno_id.id),('representante_id','=',l.representante_id.id),('descripcion','=',l.descripcion)])
            obj_mails=self.env['mail.mail'].search([('id_recordatorio','=',l.id)])
            for value in obj_rec:
                value.mail_id=obj_mails.id
                value.fecha_envio_correo=obj_mails.create_date
                #self.env.cr.execute("update recordatorio_detalle set id_mail={0} where id={1} ".format(obj_mails.id,value.id))

        if len(self.recordatorio_detalle)!=0:
            self.estado='1'
            viewid = self.env.ref("ans_escuela.cerrar_ventana_purchase_falla").id
            return {
            'name':'Recordatorio generados con Éxito!',
            'view_type':'form',
            'views' : [(viewid,'form')],
            'res_model':'close.window.purchase',
            'type':'ir.actions.act_window',
            'target':'new',
            }
        else:
            viewid = self.env.ref("ans_escuela.cerrar_ventana_purchase_falla").id
            return {
            'name':'No hay estudiantes para generar recordatorios.',
            'view_type':'form',
            'views' : [(viewid,'form')],
            'res_model':'close.window.purchase',
            'type':'ir.actions.act_window',
            'target':'new',
            }

