# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import datetime,timedelta,date
import calendar
import base64
DATE_FORMAT = '%Y-%m-%d'

class AccountJournal(models.Model):
    _inherit="account.journal" 

    tipofac_id = fields.Selection([('0','Mensualidad'),('1','Matricula'),('2','Varios'),],select=True,string="Tipo de Factura")

class CargaMasivaLineas(models.Model):
    
    _name="carga.archivo.line" 

    x_codigo_alumno = fields.Char(string="Codigo Alumno")
    x_fecha_emision = fields.Date(string="Emision")
    x_id_nombre_alumno = fields.Many2one('res.partner',string="Nombre Alumno")
    x_vencimiento = fields.Date(string="Vencimiento")
    x_curso = fields.Many2one('curso',string="Curso")
    x_valor = fields.Float(string="Valor")
    x_id_carga = fields.Many2one('carga.archivo',string="Carga Masiva")
    x_id_account_invoice = fields.Many2one('account.invoice',string="Factura")

class CargaMasiva(models.Model):
    
    _name="carga.archivo"
    _rec_name="x_banco"
    
    x_fecha_subida = fields.Date(string='Fecha Subida',default=fields.Datetime.now,index=True, copy=False,readonly=True)
    x_anio = fields.Selection('anios',string="Año")
    x_mes = fields.Selection([('1','Enero'),
                                ('2','Febrero'),
                                ('3','Marzo'),
                                ('4','Abril'),
                                ('5','Mayo'),
                                ('6','Junio'),
                                ('7','Julio'),
                                ('8','Agosto'),
                                ('9','Septiembre'),
                                ('10','Octubre'),
                                ('11','Noviembre'),
                                ('12','Diciembre')],string="Mes")
    x_banco = fields.Many2one('account.journal',string="Banco")
    x_tipo_factura = fields.Selection([('0','Mensualidad'),
                                        ('1','Matricula'),
                                        ('2','Varios')],string="Tipo Factura")
    x_codigo_banco = fields.Char(related='x_banco.code',string="Codigo en Banco")
    x_enviado_banco = fields.Selection([('1','Si'),
                                    ('2','No')],default='2',string="Enviado al banco")
    x_id_transaccion = fields.Char(string="# Transaccion")
    x_id_line = fields.One2many('carga.archivo.line','x_id_carga',string="Carga lineas")
    #datos archivo
    x_archivo_txt = fields.Char(string='Nombre archivo')
    x_binario_txt = fields.Binary(string='Archivo .txt')
    x_bandera = fields.Boolean(string='Genero documento',default=False)

    def anios(self):
        res=[]
        year=datetime.now()
        for num in range(21):
            res.append((str(year.year-num),str(year.year-num)))
        return res

    @api.multi
    def mostrar_datos(self):
        for l in self:
            formatter_string="%Y-%m-%d"
            datetime_object = datetime.strptime(str(str(l.x_anio)+'-'+str(l.x_mes)+'-'+'01'),formatter_string)
            fecha_inicio=datetime_object.date()
            dateMonthEnd="%s-%s-%s" % (fecha_inicio.year,fecha_inicio.month, calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1])
            datetime_objec = datetime.strptime(dateMonthEnd,"%Y-%m-%d")
            fecha_final=datetime_objec.date()
            self.env.cr.execute("""select id from account_invoice where escuela=True and state='open' and date_invoice between '{0}' and '{1}'""".format(str(str(l.x_anio)+'-'+str(l.x_mes)+'-'+'01'),str(dateMonthEnd)))
            factura=self.env.cr.dictfetchall()
            lista=[]
            for jor in factura:
                lista.append(jor['id'])

            obj_datos = self.env['account.invoice'].search([('id','in',lista)])
            print(len(obj_datos),'objeto')
            obj_datos_line=self.env['carga.archivo.line'].search([('x_id_carga','=',l.id)])
            # BORRAR LOS DATOS ANTERIORES CUANDO SE PRESIONA EL BOTON
            for b in obj_datos_line:
                b.unlink()
            # CREO EL DETALLE DEL FILTRO REALIZADO
            for obj in obj_datos:
                obj_datos_line=self.env['carga.archivo.line'].create({
                    'x_id_account_invoice':obj.id,
                    'x_codigo_alumno':obj.alumno_id.codigo_alumno,
                    'x_fecha_emision':obj.date_invoice,
                    'x_id_nombre_alumno':obj.alumno_id.id,
                    'x_vencimiento':obj.date_due,
                    'x_curso':obj.curso_id.id,
                    'x_valor':obj.residual,
                    'x_id_carga':l.id
                    })

    def cambiar_formato(self,valor):
        valor=valor.split('.')
        cantidad=len(valor[0])
        print(cantidad)
        formato=''
        if cantidad==1:
            formato='0000000'+valor[0]+'.'+valor[1]
        if cantidad==2:
            formato='000000'+valor[0]+'.'+valor[1]
        if cantidad==3:
            formato='00000'+valor[0]+'.'+valor[1]
        if cantidad==4:
            formato='0000'+valor[0]+'.'+valor[1]
        if cantidad==5:
            formato='000'+valor[0]+'.'+valor[1]
        if cantidad==6:
            formato='00'+valor[0]+'.'+valor[1]
        if cantidad==7:
            formato='0'+valor[0]+'.'+valor[1]
        return formato


    @api.multi
    def descarga_txt(self):
        formatter_string="%Y-%m-%d"
        for d in self:
            datetime_ = datetime.strptime(str(d.x_fecha_subida),formatter_string)
            fecha_subida=datetime_.date()
            if d.x_tipo_factura=='0':
                tipo='0'
            elif d.x_tipo_factura=='1':
                tipo='1'
            else:
                tipo='2'
            contenido='codigo_escuela'+'\t'+str(fecha_subida.month)+'/'+str(fecha_subida.day)+'/'+str(fecha_subida.year)+'\n'
            for line in d.x_id_line:
                fecha=line.x_fecha_emision.split(' ')
                datetime_object = datetime.strptime(str(fecha[0]),formatter_string)
                emision=datetime_object.date()
                datetime_objectv = datetime.strptime(line.x_vencimiento,formatter_string)
                vencimiento=datetime_objectv.date()
                contenido=contenido+line.x_codigo_alumno+'\t'+str(emision.month)+'/'+str(emision.day)+'/'+str(emision.year)+tipo+' '+str(self.cambiar_formato(str(round(line.x_valor,2))))+'\t'+str(vencimiento.month)+'/'+str(vencimiento.day)+'/'+str(vencimiento.year)+'1/1/1900N'+line.x_id_nombre_alumno.name+' '+line.x_curso.name+' '+line.x_curso.seccion_id.name+'\t'+str(self.cambiar_formato(str(round(line.x_valor,2))))+'\t'+str('1'+self.cambiar_formato(str(round(line.x_valor,2))))+'\t'+str(self.cambiar_formato(str(round(line.x_valor,2))))+'\n'
            nombre=d.x_banco.name+'.txt'
            d.x_archivo_txt=nombre
            d.x_enviado_banco='1'
            d.x_bandera=True
            contenido_total=contenido.encode('utf-8')
        return  self.write({'x_archivo_txt':nombre,'x_binario_txt': bytes(base64.b64encode(contenido_total))})
