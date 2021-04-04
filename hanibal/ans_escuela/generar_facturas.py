# -*- coding: utf-8 -*-
import logging
from openerp.osv import osv,fields
from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import ValidationError
#from odoo import profile
_logger = logging.getLogger(__name__)

# class DescuentoAlumonsEscuelaDet(models.TransientModel):
#     _name="cambio.cuenta"

#     id_account = fields.Many2one('account.account',string="Cuenta")

#     @api.multi
#     def cambio_cuenta(self):
#         obj_datos=self.env['res.partner'].search([('tipo','=','P'),('active','=',True)])

#         for l in obj_datos:
#             l.property_account_receivable=self.id_account.id


class account_move_line(models.Model):
    _inherit='account.move.line'

    def _calculo_anios(self):
        ahora = datetime.now()
        lista_anios=[]
        lista_ordenada=[]
        actual=int(ahora.year)+1
        for anio in range(1945, actual):
            lista_anios.append(anio)
            lista_anios=sorted(lista_anios,reverse=True)
        for orden in lista_anios:
            lista_ordenada.append((str(orden),str(orden)))
        return lista_ordenada

    alumno_id=fields.Many2one('res.partner',string="Alumno")
    jornada_id=fields.Many2one(related='alumno_id.jornada_id',string='Jornada',store=True)
    seccion_id=fields.Many2one(related='alumno_id.seccion_id',string='Sección',store=True)
    curso_id=fields.Many2one(related='alumno_id.curso_id',string='Curso',store=True)
    paralelo_id=fields.Many2one(related='alumno_id.paralelo_id',string='Paralelo',store=True)
    codigo_alumno=fields.Char(string='Código',size=20,store=True)
    mes = fields.Selection( (('1','Enero'),
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
                               ('12','Diciembre')) , 'Mes', required=False,store=True)
    anio = fields.Selection( (_calculo_anios) , 'Año', required=False,store=True)
    
class account_journal(models.Model):
    _inherit= "account.journal"

    activa_venta_lote = fields.Boolean(string="Factura Venta Lotes")


class account_invoice_line(models.Model):
    _inherit= "account.invoice.line"

    factura_emitida_id = fields.Many2one("periodo.line", string="Factura Emitida")
    #escuela = fields.Boolean(related="invoice_id.escuela")
    escuela = fields.Boolean(string="Escuela")
    state = fields.Selection(related="invoice_id.state")

    @api.multi
    @api.depends('product_id','quantity','precio_unitario')
    def _valor_producto(self):
        for l in self:
            if l.invoice_id.factura:
                return
            precio_unitario=l.product_id.lst_price
            precio_cantidad = l.product_id.lst_price*l.quantity
            precio_unit = 0.00
            if l.quantity != 0.00 and l.product_id.lst_price != 0.00:
                precio_unit=(l.product_id.lst_price*l.quantity)/l.quantity
            l.update({
                'precio_unitario':precio_unitario ,
                'precio_unitario_nuevo': precio_cantidad ,
                'price_unit': precio_unit ,
                })

    descuentos_ids = fields.Many2many('descuentos',string='Descuentos')
    factura_escuela = fields.Boolean(string="Escuela",default=False)
    precio_unitario_nuevo = fields.Float(string="Precio Unitario",default=0,store=True,compute='_valor_producto')
    precio_unitario = fields.Float(string="Precio Unitario",store=True,compute='_valor_producto')
    descuento = fields.Float(related='precio_descuento',string="Descuento",default=0)
    precio_descuento = fields.Float(string="Descuento")
    price_unit = fields.Float(string='Unit Price', required=True)

    @api.onchange('quantity','descuentos_ids','precio_unitario','product_id')
    def onchange_producto(self):
        #INTEGRACION: SE COMENTA POR QUE DICE QUE EL CAMPO FACTURA NO EXISTE
        if self.invoice_id.factura:
            return
        subtotal=0.0
        subtotal=self.precio_unitario_nuevo
        subtotal_antes_desc=0.0
        subtotal_final=0.0
        if len(self.descuentos_ids)!=0:
            total_descuentos=0.0
            for l in self.descuentos_ids:
                monto_descuentos=0.0
                monto_descuentos=round(subtotal*(l.porcentaje/100),2)
                total_descuentos=total_descuentos+monto_descuentos
                subtotal=subtotal-monto_descuentos
                self.price_unit=subtotal/self.quantity
                self.descuento=total_descuentos
                self.precio_descuento=total_descuentos
                self.invoice_id.subtotal_descuento=total_descuentos
        else:
            self.price_unit=self.precio_unitario
            self.descuento=0.0

    @api.constrains('quantity','descuentos_ids','precio_unitario','product_id')
    def constrains_producto(self):
        #INTEGRACION: SE COMENTA POR QUE DICE QUE EL CAMPO FACTURA NO EXISTE
        if self.invoice_id.factura:
            return
        subtotal=0.0
        subtotal=self.precio_unitario_nuevo
        subtotal_antes_desc=0.0
        subtotal_final=0.0
        if len(self.descuentos_ids)!=0:
            total_descuentos=0.0
            for l in self.descuentos_ids:
                monto_descuentos=0.0
                monto_descuentos=round(subtotal*(l.porcentaje/100),2)
                total_descuentos=total_descuentos+monto_descuentos
                subtotal=subtotal-monto_descuentos
                self.price_unit=subtotal/self.quantity
                self.descuento=total_descuentos
                self.precio_descuento=total_descuentos
                self.invoice_id.subtotal_descuento=total_descuentos
        else:
            self.price_unit=self.precio_unitario
            self.descuento=0.0

    @api.multi
    def action_from(self):
        viewid = self.env.ref('ans_escuela.view_descuentos_factura_cabezera_form').id
        context = self._context.copy()
        obj_descuenta_detalle=self.env['descuentos.factura.cabezera'].search([('factura_id','=',self.id)],limit=1)
        return {   
                'name':'Detalle de Descuentos',
                'res_model': 'descuentos.factura.cabezera',
                'view_type': 'form',
                'views' : [(viewid,'form')],
                'type':'ir.actions.act_window',
                'nodestroy': False,
                'res_id': obj_descuenta_detalle.id,
                'target':'new',
                'context':context,
                }

class account_invoice(models.Model):
    _inherit= "account.invoice"
    _rec_name = "numerofac"

    mes_inicio_id = fields.Many2one(comodel_name='academic.month', string='Mes Inicio', help="Mes incial del que desea pagar el año lectivo")
    mes_final_id = fields.Many2one(comodel_name='academic.month', string='Mes Final', help="Mes final hasta donde desea pagar el año lectivo")
    anio_lectivo = fields.Char(related="mes_inicio_id.anio_lectivo", string='Año Lectivo')

    @api.multi
    def name_get(self):
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Supplier Invoice'),
            'out_refund': _('Refund'),
            'in_refund': _('Supplier Refund'),
        }
        result = []
        for inv in self:
            #RERV IF AGREGADO PARA PROVEEDOR
            if self.env.context.get('proveedor', False):
                result.append((inv.id, "%s %s" % (inv.supplier_invoice_number or TYPES[inv.type], inv.name or '')))
            else:
                result.append((inv.id, "%s %s" % (inv.numerofac or TYPES[inv.type], inv.name or '')))
        return result

    #----------------------------------- WM --------------------------------------------------------
    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                'default_reference': inv.name,
                'close_after_process': True,
                'invoice_type': inv.type,
                'invoice_id': inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'default_alumno_id':inv.alumno_id.id,
                'default_partner_id':inv.partner_id.id,
                'default_jornada_id':inv.jornada_id.id,
                'default_seccion_id':inv.seccion_id.id,
                'default_curso_id':inv.curso_id.id,
                'default_paralelo_id':inv.paralelo_id.id,
                'default_mes':inv.mes,
                'default_anio':inv.anio,
            }
        }

    #----------------------------------- WM --------------------------------------------------------

    def _calculo_anios(self):
      ahora = datetime.now()
      lista_anios=[]
      lista_ordenada=[]
      actual=int(ahora.year)+1
      for anio in range(1945, actual):
        lista_anios.append(anio)
      lista_anios=sorted(lista_anios,reverse=True)
      for orden in lista_anios:
        lista_ordenada.append((str(orden),str(orden)))
      return lista_ordenada

    escuela = fields.Boolean(string="Estructura escolar",default='True')
    validar = fields.Boolean(string="Validar",default=False)
    jornada_id=fields.Many2one(related='alumno_id.jornada_id',string='Jornada',copy=False, index=True,store=True)
    seccion_id=fields.Many2one(related='alumno_id.seccion_id',string='Sección',copy=False, index=True,store=True)
    curso_id=fields.Many2one(related='alumno_id.curso_id',string='Curso',copy=False, index=True,store=True)
    paralelo_id=fields.Many2one(related='alumno_id.paralelo_id',string='Paralelo',copy=False, index=True,store=True)
    #codigo_alumno=fields.Char(related='alumno_id.codigo_alumno','Código',size=20)
    #representante_id=fields.Many2one(related='partner_id.parent_id',string="Representante")
    alumno_id=fields.Many2one('res.partner',string="Alumno")
    mes = fields.Selection( (('1','Enero'),
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
                               ('12','Diciembre')) , 'Mes', required=False)
    anio = fields.Selection( (_calculo_anios) , 'Año', required=False)
    descuentos_facturar = fields.One2many("descuentos.factura","factura_id",string="Detalle Descuento",ondelete='cascade')

    @api.onchange('alumno_id','partner_id')
    def onchange_cliente(self):
        if self.alumno_id:
            if self.partner_id.id!=self.alumno_id.parent_id.id:
                self.partner_id=self.alumno_id.parent_id.id

    @api.constrains('alumno_id','partner_id')
    def constrains_cliente(self):
        if self.alumno_id:
            if self.partner_id.id!=self.alumno_id.parent_id.id:
                self.partner_id=self.alumno_id.parent_id.id
                raise osv.except_osv(('Alerta'),("El representante no corresponde al Alumno seleccionado."))


    @api.multi
    def _onchange_descuento(self):
        acumulador=0.0
        for l in self.invoice_line:
            acumulador=acumulador+l.descuento
        self.subtotal_descuento=acumulador

    subtotal_descuento = fields.Float(string="Descuento",store=True,compute='_onchange_descuento')
    total_pago = fields.Float(string="Subtotal Antes descuento")

    @api.onchange('partner_id','invoice_line.descuentos_ids','invoice_line')
    def onchange_descuentos(self):
        subtotal_antes=0.0
        descuento=0.0
        if len(self.invoice_line)!=0:
            for l in self.invoice_line:
                subtotal_antes=subtotal_antes+l.precio_unitario_nuevo
                descuento=descuento+l.descuento
            self.total_pago=subtotal_antes
            self.subtotal_descuento=descuento
        else:
            self.total_pago=0
            self.subtotal_descuento=0
            self.amount_tax=0
            self.amount_total=0

    @api.constrains('partner_id','invoice_line.descuentos_ids','invoice_line')
    def contrains_descuentos(self):
        #RERV esto esta haciendo deschequear escuela ya que se pone lectura y no acepta en modo lectura setear un valor
        # if self.validar==False:
        #     self.validar=True
        subtotal_antes=0.0
        descuento=0.0
        if len(self.invoice_line)!=0:
            for l in self.invoice_line:
                subtotal_antes=subtotal_antes+l.precio_unitario_nuevo
                descuento=descuento+l.descuento
            self.total_pago=subtotal_antes
            self.subtotal_descuento=descuento
        else:
            self.total_pago=0
            self.subtotal_descuento=0
            self.amount_tax=0
            self.amount_total=0
        for d in self.invoice_line:
            d.price_subtotal=d.price_unit*d.quantity

    #@profile
    @api.multi
    def validar_nuevo(self):
        self.action_date_assign()
        self.action_move_create()
        self.action_number()
		#RERV if agregado par que solo pase a estado abierto cuando no sea factura refund
        if self.type == 'out_invoice' or self.type == 'in_invoice':
            self.invoice_validate()
        obj_move= self.env['account.move.line']
        ahora = datetime.now()
        for m in self.invoice_line:
            monto_descuentos=0.0
            subtotal=m.precio_unitario_nuevo
            obj_move_line= self.env['account.move.line'].search([('name','=',str(m.name)),('move_id','=',self.move_id.id),('credit','=',m.price_subtotal)],limit=1)
            #RERV if agregado para cuado sea factura proveedor sea el saldo en debito
            monto_credito = 0
            monto_debito = 0
            if self.type == 'in_refund' and self.tipo == 'nota_credito_proveedor':
                monto_debito = m.precio_unitario_nuevo
            else:
                monto_credito = m.precio_unitario_nuevo
            print(obj_move_line.invoice.id,'obj_move_line.invoice.id')
            print(obj_move_line.name,'obj_move_line.name')
            print(self.partner_id.id,'self.partner_id.id')
            print(obj_move_line.account_id.id,'obj_move_line.account_id.id')
            print(obj_move_line.journal_id.id,'obj_move_line.journal_id.id')
            print(monto_credito,'monto_credito')
            print(monto_debito,'monto_debito')
            print(obj_move_line.period_id.id,'obj_move_line.period_id.id')
            print(obj_move_line.move_id.id,'obj_move_line.move_id.id')
            print(obj_move_line.date,'obj_move_line.date')
            print(m.precio_unitario_nuevo,'m.precio_unitario_nuevo')
            print(self.alumno_id.id,'self.alumno_id.id')
            print(self.alumno_id.jornada_id.id,'self.alumno_id.jornada_id.id')
            print(self.alumno_id.seccion_id.id,'self.alumno_id.seccion_id.id')
            print(self.alumno_id.curso_id.id,'self.alumno_id.curso_id.id')
            print(self.alumno_id.paralelo_id.id,'self.alumno_id.paralelo_id.id')
            print(self.alumno_id.codigo_alumno,'self.alumno_id.codigo_alumno')
            dic={
                    'invoice':obj_move_line.invoice.id,
                    'name':obj_move_line.name,
                    'partner_id':self.partner_id.id,
                    'account_id':obj_move_line.account_id.id,
                    'journal_id':obj_move_line.journal_id.id,
                    'credit':monto_credito,
                    'debit': monto_debito,
                    'period_id':obj_move_line.period_id.id,
                    'move_id':obj_move_line.move_id.id,
                    'date':obj_move_line.date,
                    'tax_amount':m.precio_unitario_nuevo,
                    'alumno_id':self.alumno_id.id,
                    'jornada_id':self.alumno_id.jornada_id.id,
                    'seccion_id':self.alumno_id.seccion_id.id,
                    'curso_id':self.alumno_id.curso_id.id,
                    'paralelo_id':self.alumno_id.paralelo_id.id,
                    'codigo_alumno':self.alumno_id.codigo_alumno,
                    # 'mes':self.mes,
                    # 'anio':self.anio,
                    }
			#RERV if agregado para que se ejecute si el objeto existe
            if obj_move_line:
                self.env.cr.execute("""DELETE from account_move_line WHERE id={1} AND move_id={0}""".format(self.move_id.id,obj_move_line.id))
            for l in m.descuentos_ids:
                obj_desc = self.env['descuentos'].search([('id','=',l.id)])
                monto_descuentos=0.0
                monto_descuentos=round(subtotal*(obj_desc.porcentaje/100),3)
                subtotal=subtotal-monto_descuentos
                obj_p = self.env['account.period'].search([('id','!=',None)],limit=1)
                print('*****************************************')
                print(self.move_id.id,'self.move_id.id')
                print(obj_desc.name,'obj_desc.name')
                print(self.partner_id.id,'self.partner_id.id')
                print(obj_desc.cuenta_id.id,'obj_desc.cuenta_id.id')
                print(self.journal_id.id,'self.journal_id.id')
                print(monto_descuentos,'monto_descuentos')
                print(obj_move_line.period_id.id,'obj_move_line.period_id.id')
                print(self.move_id.id,'self.move_id.id')
                print(ahora,'ahora')
                desc_1=obj_move.create({
                    'invoice':self.move_id.id,
                    'name':obj_desc.name,
                    'partner_id':self.partner_id.id,
                    'account_id':obj_desc.cuenta_id.id,
                    'journal_id':self.journal_id.id,
                    'debit':monto_descuentos,
                    'period_id':obj_move_line.period_id.id,
                    'move_id':self.move_id.id,
                    'date':ahora,
                    'tax_amount':0.0,
                    'credit':0.0,
                    'alumno_id':self.alumno_id.id,
                    'jornada_id':self.alumno_id.jornada_id.id,
                    'seccion_id':self.alumno_id.seccion_id.id,
                    'curso_id':self.alumno_id.curso_id.id,
                    'paralelo_id':self.alumno_id.paralelo_id.id,
                    'codigo_alumno':self.alumno_id.codigo_alumno,
                    # 'mes':self.mes,
                    # 'anio':self.anio,
                    })
			#RERV if agregado para que ejecute si el objeto existe
            if obj_move_line:
                print('-----------------------------------------------')
                print('Entra para crear factura')
                credito=obj_move.create(dic)
			#RERV if agregado para que ejecute si la factura es nota de credito cliente
            if self.type == 'out_invoice' or (self.type == 'out_refund' and self.tipo == 'nota_credito_cliente'):
                for z in self.env['account.move.line'].search([('move_id','=',self.move_id.id)]):
                    dato="update account_move_line set jornada_id={0}, seccion_id={1}, curso_id={2}, paralelo_id={3},mes='{4}',anio='{5}' where id={6}".format(self.alumno_id.jornada_id.id,self.alumno_id.seccion_id.id,self.alumno_id.curso_id.id,self.alumno_id.paralelo_id.id,str(self.mes),str(self.anio),z.id)
                    print(dato)
                    self.env.cr.execute(dato)
            ## popup de los descuentos
            obj_datos=self.env['res.partner'].search([('id','=',self.partner_id.id)],limit=1)
            lista_desc=[]
            obj_descuenta_line=self.env['descuentos.factura']
            obj_descuenta_producto=self.env['descuentos.factura.producto']
            obj_descuenta_detalle=self.env['descuentos.factura.cabezera'].create({
                'factura_id':m.id,
                })
            monto_descuentos=0.0
            total_descuentos=[]
            subtotal=m.precio_unitario_nuevo
            for desc in m.descuentos_ids:
                obj_desc = self.env['descuentos'].search([('id','=',desc.id)])
                #monto_descuentos=float("{0:.2f}".format(subtotal*(obj_desc.porcentaje/100)))
                monto_descuentos=round(subtotal*(obj_desc.porcentaje/100),3)
                obj_descuenta_producto.create({
                    'factura_det_id':obj_descuenta_detalle.id,
                    'descuento_id':obj_desc.id,
                    'base': subtotal,
                    'monto':monto_descuentos,
                    })
                subtotal=subtotal-monto_descuentos

                obj_descuenta_line_vali=self.env['descuentos.factura'].search([('factura_id','=',self.id),('descuento_id','=',desc.id)])
                if len(obj_descuenta_line_vali)!=0:
                    obj_descuenta_line_vali.monto=obj_descuenta_line_vali.monto+monto_descuentos
                else:
                    obj_descuenta_line.create({
                    'factura_id':self.id,
                    'descuento_id':desc.id,
                    'monto':monto_descuentos
                    })

        obj_move_n= self.env['account.move.line'].search([('move_id','=',self.move_id.id)])
        for line in obj_move_n:
            if line.alumno_id.id == self.alumno_id.id:
                _logger.info("False")
            else:
                line.alumno_id=self.alumno_id.id
        self.residual = self.amount_total

        return self.number

    @api.constrains('date_invoice')
    def calculo_fechas(self):
        DATE_FORMAT = '%Y-%m-%d'
        if self.date_invoice:
            datetime_object = datetime.strptime(self.date_invoice, DATE_FORMAT)
            fecha_dato= datetime_object.date()
            if int(str(fecha_dato.strftime('%m')))<9:
                mes=str(fecha_dato.strftime('%m'))
                self.mes= mes[1:]
            else:
                mes=str(fecha_dato.strftime('%m'))
                self.mes= mes[1:]
            self.anio= str(fecha_dato.strftime('%Y'))

    #RERV
    @api.multi
    def write(self, vals):
        res = super(account_invoice, self).write(vals)
        if self.escuela and self.type == 'out_invoice':
            #Borro facturas emitidas dentro del alumno
            if self.state in ['cancel']:
                model_month = self.env['academic.month']
                model_partner = self.env['res.partner'].search([('id', '=', self.alumno_id.id )])
                month_ids = model_month.search([
                        ('year_id', '=', self.mes_inicio_id.year_id.id),
                        ('date_start', '>=', self.mes_inicio_id.date_start),
                        ('date_stop', '<=', self.mes_final_id.date_stop),
                    ])

                lista_emitida_ids = []
                for line in model_partner.factura_emitida_ids:
                    if line.id in month_ids.ids:
                        lista_emitida_ids.append(line.id)
                if lista_emitida_ids:
                    for line in lista_emitida_ids:
                        model_partner.factura_emitida_ids = [(3, line)]

            if self.escuela and self.type == 'out_invoice' and self.state in ['open', 'paid']:
                model_month = self.env['academic.month']
                #Crear las facturas en el alumno
                month_ids = model_month.search([
                        ('year_id', '=', self.mes_inicio_id.year_id.id),
                        ('date_start', '>=', self.mes_inicio_id.date_start),
                        ('date_stop', '<=', self.mes_final_id.date_stop),
                    ])
                # factura_emitida_ids = self.mapped('alumno_id.factura_emitida_ids')
                # for rec in factura_emitida_ids:
                #     if rec.id in month_ids.ids:
                #         raise ValidationError("Ya existe otra factura con el alumno %s dentro del mes incio %s y mes final %s" %(
                #             self.alumno_id.name, self.mes_inicio_id.display_name, self.mes_final_id.display_name))

                self.alumno_id.factura_emitida_ids = [(6, 0, month_ids.ids)]
        return res

    #RERV
    @api.constrains('state')
    def constrains_facturas_no_repetidas_dentro_del_periodo(self):
        if self.state == 'open':
            model_month = self.env['academic.month']
            month_ids = model_month.search([
                    ('year_id', '=', self.mes_inicio_id.year_id.id),
                    ('date_start', '>=', self.mes_inicio_id.date_start),
                    ('date_stop', '<=', self.mes_final_id.date_stop),
                ])
            factura_emitida_ids = self.mapped('alumno_id.factura_emitida_ids')
            for rec in factura_emitida_ids:
                if rec.id in month_ids.ids:
                    raise ValidationError("Ya existe otra factura con el alumno %s dentro del mes incio %s y mes final %s" %(
                        self.alumno_id.name, self.mes_inicio_id.display_name, self.mes_final_id.display_name))

    #RERV
    @api.constrains('mes_inicio_id', 'mes_final_id')
    def constrains_validar_mes_final_mayor_mes_incial(self):
        if self.mes_inicio_id and self.mes_final_id:
            if self.mes_final_id.date_stop < self.mes_inicio_id.date_start:
                raise ValidationError("Mes final no debe ser menor a mes incial")

    #RERV
    @api.constrains('curso_id', 'invoice_line', 'mes_inicio_id', 'mes_final_id', 'alumno_id')
    def constrains_producto_curso_no_repetido_en_otra_factura(self):
        if self.escuela and self.env.context.get('type') == 'out_invoice':
            model_invoice = self.env['account.invoice']
            invoice_ids = model_invoice.search([
                            ('id', '!=', self.id),
                            ('type', '=', 'out_invoice'),
                            ('escuela', '=', True),
                            ('state', 'in', ['draft', 'open', 'paid']),
                            ('alumno_id', '=', self.alumno_id.id),
                        ])
            #mes
            model_month = self.env['academic.month']
            month_ids = model_month.search([
                    ('year_id', '=', self.mes_inicio_id.year_id.id),
                    ('date_start', '>=', self.mes_inicio_id.date_start),
                    ('date_stop', '<=', self.mes_final_id.date_stop),
                ])
            # meses_existentes = [rec.id for rec in invoice_ids if rec.mes_inicio_id.id in month_ids.ids or rec.mes_final_id.id in month_ids.ids]
            invoice_ids = invoice_ids.filtered(lambda filtro: filtro.mes_inicio_id.id in month_ids.ids or filtro.mes_final_id.id in month_ids.ids)
            invoice_line_ids = invoice_ids.mapped('invoice_line')
            product_ids = self.mapped('invoice_line.product_id')
            if self.curso_id.producto_id.id in product_ids.ids:
                invoice_line_ids = invoice_line_ids.filtered(lambda line: line.product_id.id == self.curso_id.producto_id.id)
                if invoice_line_ids:
                    raise ValidationError("El Producto %s del alumno %s del curso %s ya existe en otra factura %s dentro del rango de fechas %s %s" %(
                            self.curso_id.producto_id.display_name,
                            self.alumno_id.name,
                            self.curso_id.display_name, 
                            '/'.join([rec.invoice_id.display_name for rec in invoice_line_ids]),
                            self.mes_inicio_id.display_name,
                            self.mes_final_id.display_name,
                        ))

class GenerarFacturasDetalle(models.Model):
    _name="generar.facturas.detalle"

    def _calculo_anios(self):
      ahora = datetime.now()
      lista_anios=[]
      lista_ordenada=[]
      actual=int(ahora.year)+1
      for anio in range(1945, actual):
        lista_anios.append(anio)
      lista_anios=sorted(lista_anios,reverse=True)
      for orden in lista_anios:
        lista_ordenada.append((str(orden),str(orden)))
      return lista_ordenada

    factura_id =fields.Many2one('generar.facturas', string="",ondelete='cascade')
    factura_emitida_id = fields.Many2one('generar.facturas', string="", ondelete='cascade') #RERV
    codigo_interno = fields.Many2one("account.invoice",string="Codigo Interno")
    numerofac = fields.Char(related='codigo_interno.numerofac',string='Factura')
    number = fields.Char(string="Número de factura")
    alumno_id=fields.Many2one('res.partner',string="Alumno")
    representante_id = fields.Many2one(related='alumno_id.parent_id',string="Representante",store=True)
    representante_nombre = fields.Char(related='alumno_id.parent_id.name',string="Representante")
    jornada_id=fields.Many2one(related='alumno_id.jornada_id',string='Jornada',copy=False, index=True,store=True)
    seccion_id=fields.Many2one(related='alumno_id.seccion_id',string='Sección',copy=False, index=True,store=True)
    curso_id=fields.Many2one(related='alumno_id.curso_id',string='Curso',copy=False, index=True,store=True)
    paralelo_id=fields.Many2one(related='alumno_id.paralelo_id',string='Paralelo',copy=False, index=True,store=True)
    codigo_alumno = fields.Char(related='alumno_id.codigo_alumno',string="Código",store=True)
    alumno_nombre = fields.Char(related='alumno_id.name',string="Alumno")
    antes_descuento = fields.Float(string="Antes Descuento",default=0)
    descuento = fields.Float(string="Descuento",default=0)
    subtotal = fields.Float(string="Subtotal",default=0)
    iva = fields.Float(string="Iva",default=0)
    total = fields.Float(string="Total",default=0)
    mes = fields.Selection( (('1','Enero'),
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
                               ('12','Diciembre')) , 'Mes', required=False)
    anio = fields.Selection( (_calculo_anios) , 'Año', required=False)
    numero = fields.Integer(string="Numero")
    invoice_ids = fields.Many2many(comodel_name='account.invoice', string='Factura')


class GenerarFacturas(models.Model):
    _name="generar.facturas"
    _rec_name = "display_name"

    mes_inicio_id = fields.Many2one("academic.month", string="Periodo Lectivo")
    mes_final_id = fields.Many2one("academic.month", string="Fecha final")

    def _calculo_anios(self):
      ahora = datetime.now()
      lista_anios=[]
      lista_ordenada=[]
      actual=int(ahora.year)+1
      for anio in range(1945, actual):
        lista_anios.append(anio)
      lista_anios=sorted(lista_anios,reverse=True)
      for orden in lista_anios:
        lista_ordenada.append((str(orden),str(orden)))
      return lista_ordenada
    #Nelio
    #Funcionalidad De obtencion de punto de emision
    @api.multi
    def _obtener_punto(self):
        for ges in self:
            doc = self.env['configuracion'].search([])
            for l in doc:
                if l.cuenta_id_default:
                    ges.punto_emision = l.cuenta_id_default.id

    # Nelio
    #Se aplica en un onchange la funcionalidad anteriori
    @api.onchange("diario")
    def llenar_datos(self):
        self._obtener_punto()



    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)
    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    diario = fields.Many2one('account.journal',string="Diario",domain="[('activa_venta_lote','=',True)]")
    punto_emision = fields.Many2one('fiscal.puntoemision',string="Punto de Emision")
    mes = fields.Selection( (('1','Enero'),
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
                               ('12','Diciembre')) , 'Mes', required=False)
    anio = fields.Selection( (_calculo_anios) , 'Año', required=False)
    fecha_factura= fields.Date('Fecha factura', copy=False,select=True)
    detalle_facturar = fields.One2many("generar.facturas.detalle", "factura_id",string="Detalle",ondelete='cascade')
    factura_emitida_id = fields.One2many("generar.facturas.detalle", "factura_emitida_id", string="Facturas Emitidas", ondelete='cascade')
    estado = fields.Selection( (('0','Borrador'),
                               ('1','Ejecutado'),
                               ('2','Finalizado')) , 'Estados', required=False)
    display_name =fields.Char(string="Nombre a mostrar")

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

    @api.constrains('diario','mes','anio')
    def guardar_display_name(self):
        self.display_name=str(str(self.diario.name)+'/'+str(self.mes_inicio_id.name)+'/'+str(self.mes_inicio_id.anio_lectivo))

    @api.multi
    def calculos(self, descuentos_line, id_alumno, lista_impuesto_id, lst_price, contador):
        lista_alumnos=[]
        lista_detalle=[]
        dicc={}
        dicct={}
        monto_descuentos=0.0
        total_descuentos=0.0
        subtotal=0.0
        lista_porcentajes = []
        total=0.0
        subtotal=lst_price
        datos_impuestos=self.env['account.tax'].search([('id','in',lista_impuesto_id)])
        lista_impuesto_montos=datos_impuestos.mapped('amount')
        obj_detalle=self.env['generar.facturas.detalle']
        pronto = True
        for desc in descuentos_line:
            if desc.descuento_id.is_pronto_pago:
                pronto = False
                factura_anterior = self.env['account.invoice'].search([('alumno_id', '=', id_alumno)],
                                                                      order='date_invoice desc', limit=1)
                dia = 0
                for factura in factura_anterior:
                    if factura.state != "paid":
                        _logger.info("no paid")
                    else:
                        if factura.payments_ids != False:
                            for payment in factura.payments_ids:
                                dia = factura.date_invoice - payment.date
                            if dia > desc.descuento_id.dias:
                                _logger.info("es false")
                            else:
                                pronto = True
                                lista_porcentajes.append(desc.porcentaje)
                        else:
                            _logger.info("es false")
            else:
                lista_porcentajes.append(desc.porcentaje)

        for descuentos in lista_porcentajes:
            monto_descuentos=0.0
            monto_descuentos=round(subtotal*(descuentos/100),3)
            total_descuentos=total_descuentos+monto_descuentos
            subtotal=subtotal-monto_descuentos

        #INTEGRACION: SE DECLARA LA VARIABLE
        iva_total=0.0
        for iva_interes in lista_impuesto_montos:
            iva=0.0
            iva=subtotal*iva_interes
            iva_total=iva
        total=subtotal+iva_total

        obj_detalle.create({
                'factura_id':self.id,
                #'representante_id':datos.parent_id,
                'alumno_id':id_alumno,
                'antes_descuento':lst_price,
                'descuento':total_descuentos,
                'subtotal':subtotal,
                'iva':iva_total,
                'total':total,
                'numero':contador,
            })

    @api.multi
    def traer_informacion(self):
        self.estado='0'
		#RERV comentaod xq los campos ya no existen
        # obj_detalle_fact=self.env['generar.facturas.detalle'].search([('anio','=',self.anio),('mes','=',self.mes),('factura_id','!=',self.id)])
        # lista_registrados = [value.alumno_id.id for value in obj_detalle_fact]

        if self.jornada_id:
            if self.seccion_id:
                if self.curso_id:
                    if self.paralelo_id:
                        obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('paralelo_id','=',self.paralelo_id.id),('active','in',(True,False))])
                    else:
                        obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('curso_id','=',self.curso_id.id),('active','in',(True,False))])
                else:
                    obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('seccion_id','=',self.seccion_id.id),('active','in',(True,False))])
            else:
                obj_datos=self.env['res.partner'].search([('jornada_id','=',self.jornada_id.id),('active','in',(True,False))])
        
        self.env.cr.execute("""delete from generar_facturas_detalle where factura_id={0}""".format(self.id))
        #RERV borrar informacion de las lineas de facturas masivas en facturas ya emitidos
        if self.mapped("factura_emitida_id"):
            self.mapped("factura_emitida_id").unlink()
        contador=0
        for datos in obj_datos:
            #RERV if para traer solo alumnos que no tenga creado esa factura
            month_ids = self.env['academic.month'].search([
                    ('year_id', '=', self.mes_inicio_id.year_id.id),
                    ('date_start', '>=', self.mes_inicio_id.date_start),
                    ('date_stop', '<=', self.mes_inicio_id.date_stop),
                ])
            model_invoice = self.env['account.invoice']
            invoice_ids = model_invoice.search([
                    ('id', '!=', self.id),
                    ('type', '=', 'out_invoice'),
                    ('escuela', '=', True),
                    ('state', 'in', ['draft', 'open', 'paid']),
                    ('alumno_id', '=', datos.id),
                ])
            
            # entra = [rec for rec in month_ids.ids if rec in datos.factura_emitida_ids.ids]
            invoice_ids = [rec for rec in invoice_ids if rec.mes_inicio_id.id in month_ids.ids or rec.mes_final_id.id in month_ids.ids]
            if not invoice_ids:
                # if datos.id in lista_registrados:
                #     _logger.info("no esta en las facturas generadas"+str(datos.id))
                # else:
                contador = contador + 1
                #Obtener la lista de las id de los impuestos del producto del curso
                lista_impuesto_id = datos.curso_id.producto_id.taxes_id.mapped('id')
                # if datos.enero== True and self.mes=='1':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.febrero== True and self.mes=='2':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.marzo== True and self.mes=='3':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.abril== True and self.mes=='4':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.mayo== True and self.mes=='5':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.junio== True and self.mes=='6':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.julio== True and self.mes=='7':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.agosto== True and self.mes=='8':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.septiembre== True and self.mes=='9':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.octubre== True and self.mes=='10':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.noviembre== True and self.mes=='11':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                # elif datos.diciembre== True and self.mes=='12':
                #     self.calculos(datos.descuentos_line,datos.id,lista_impuesto_id,datos.curso_id.producto_id.lst_price,contador)
                self.calculos(datos.descuentos_line, datos.id, lista_impuesto_id, datos.curso_id.producto_id.lst_price, contador)
            else:
                self.env['generar.facturas.detalle'].create({
                    'factura_emitida_id':self.id,
                    # 'numero':contador,
                    'representante_id':datos.parent_id.id,
                    'alumno_id':datos.id,
                    'codigo_alumno': datos.codigo_alumno,
                    'invoice_ids': [(6, 0, invoice_ids[0].ids)],
                })

    @api.multi
    def calcular_restante_emision(self,facturas,cont):
        emision_obj = self.env['fiscal.puntoemision'].search([('id','=',facturas)],limit=1)
        for l in emision_obj:
            secuencia = int(l.secuenciaFinal)-int(l.secuenciaActual)
            if secuencia < cont:
                raise osv.except_osv("Error!","No se pudo completar el proceso, Revisar la secuencia del punto de emision")
        return emision_obj.id or False


    @api.multi
    def obtener_punto_emision_data(self,puntoemision_id):
        if puntoemision_id:
            puntoemision_obj = self.env['fiscal.puntoemision'].search([('id','=',puntoemision_id)])
            result = {
                'tipodocumento_id': puntoemision_obj.tipodocumento_id.id,
                'Numautorizacion': puntoemision_obj.Numautorizacion,
                'puntoemision': puntoemision_obj.puntoemision,
                'establecimiento': puntoemision_obj.establecimiento,
                'secuencial': str(int(puntoemision_obj.secuenciaActual) + 1).zfill(9),
                'numeAutImp': puntoemision_obj.numeAutImp
            }
        #INTEGRACION: SE PONE UN ELSE PARA HACER LA VALIDACION
            return result
        else:
            return False



    @api.multi
    def generar_factura_borrador(self):
        obj_detalle=self.env['account.invoice']
        descuentos_fact = self.env['descuentos.factura']
        facturas = len([x.id for x in self.detalle_facturar])
        puntoemision_id = self.calcular_restante_emision(self.punto_emision.id,facturas)
        for line in self.detalle_facturar:
            if line.alumno_id.property_account_receivable.type == "view":
                raise osv.except_osv(_("Error"),_("No se puede continuar porque debe configurar una cuenta que no sea vista de "+str(line.alumno_id.name)))
            #RERV puntoemision_id agregado porque es requerido al crear la factura
            obj_factura=obj_detalle.create({
                    'partner_id':line.representante_id.id,
                    'journal_id':self.diario.id,
                    'account_id':line.alumno_id.property_account_receivable.id,
                    'escuela':True,
                    'alumno_id':line.alumno_id.id,
                    'mes_inicio_id': self.mes_inicio_id.id,
                    'mes_final_id': self.mes_inicio_id.id,
                    'date_invoice':self.fecha_factura,
                    'subtotal_descuento':float(line.descuento),
                    'type': 'out_invoice',
                    'puntoemision_id': self.punto_emision.id,
                    #'total_pago':float(line.antes_descuento),
                })
            line.alumno_id.factura_emitida_id = [(6, 0, self.factura_emitida_id.ids)]
            # Nelio
            # AGREGAR CAMPOS DE FISCALES
            result = self.obtener_punto_emision_data(self.punto_emision.id)
            obj_factura.tipodocumento_id = result['tipodocumento_id']
            obj_factura.puntoemision_id = self.punto_emision
            obj_factura.numeAutImp = result['numeAutImp']
            obj_factura.Numautorizacion = result['Numautorizacion']
            obj_factura.establecimiento = result['establecimiento']
            obj_factura.secuencial = result['secuencial']
            obj_factura.puntoemision = result['puntoemision']


            obj_factura.total_pago=line.antes_descuento
            obj_detalle_line=self.env['account.invoice.line']
            obj_factura_line=obj_detalle_line.create({
                    'product_id':line.alumno_id.curso_id.producto_id.id,
                    'uos_id':line.alumno_id.curso_id.producto_id.uom_id.id,
                    'name':str(line.alumno_id.curso_id.producto_id.name+' - '+str(self.mes_inicio_id.name)+' - '+str(self.mes_inicio_id.anio_lectivo)),
                    'invoice_id':obj_factura.id,
                    'account_id':line.alumno_id.curso_id.producto_id.property_account_income.id,
                    'price_unit':line.subtotal,
                    'factura_escuela':True,
                    'descuento':line.descuento,
                    'precio_unitario':line.alumno_id.curso_id.producto_id.lst_price,
                })
            obj_factura_line.invoice_line_tax_id=self.curso_id.producto_id.taxes_id

            obj_datos=self.env['res.partner'].search([('id','=',line.alumno_id.id)],limit=1)
            lista_desc=[]
            obj_descuenta_line=self.env['descuentos.factura']
            obj_descuenta_producto=self.env['descuentos.factura.producto']
            obj_descuenta_detalle=self.env['descuentos.factura.cabezera'].create({
                'factura_id':obj_factura_line.id,
                })
            subtotal = line.alumno_id.curso_id.producto_id.lst_price
            monto_descuentos = 0.0
            total_descuentos = []
            for desc in obj_datos.descuentos_line:
                pronto = True
                if desc.descuento_id.is_pronto_pago:
                   pronto = False
                   factura_anterior = self.env['account.invoice'].search([('alumno_id','=',line.alumno_id.id)],order='date_invoice desc',limit=1)
                   dia = 0
                   for factura in factura_anterior:
                       if factura.state != "paid":
                           _logger.info("no paid")
                       else:
                           if factura.payments_ids != False:
                               for payment in factura.payments_ids:
                                   dia = factura.date_invoice - payment.date
                               if dia > desc.dias:
                                   _logger.info("descuento"+str(line.alumno_id.name))
                               else:
                                   pronto = True

                if pronto == False:
                    continue

                monto_descuentos=round(subtotal*(desc.porcentaje/100),3)
                obj_descuenta_producto.create({
                    'factura_det_id':obj_descuenta_detalle.id,
                    'descuento_id':desc.descuento_id.id,
                    'base': subtotal,
                    'monto':monto_descuentos,
                    })
                subtotal=subtotal-monto_descuentos


                obj_descuenta_line.create({
                    'factura_id':obj_factura.id,
                    'descuento_id':desc.descuento_id.id
                    })
                lista_desc.append(desc.descuento_id.id)

            obj_factura_line.update({'descuentos_ids':lista_desc})
            line.codigo_interno=obj_factura.id

            for m in line.codigo_interno.invoice_line:
                obj_descuenta_detalle=self.env['descuentos.factura.cabezera'].search([('factura_id','=',m.id)])
                for d in obj_descuenta_detalle.detalle_descuento:
                    obj_descuenta_detalle=self.env['descuentos.factura'].search([('descuento_id','=',d.descuento_id.id),('factura_id','=',line.codigo_interno.id)])
                    obj_descuenta_detalle.monto=obj_descuenta_detalle.monto+d.monto


        if len(self.detalle_facturar)!=0:
            self.estado='1'
            viewid = self.env.ref("ans_escuela.cerrar_ventana_purchase_falla").id
            return {
            'name':'Facturas Generadas con Éxito!',
            'view_type':'form',
            'views' : [(viewid,'form')],
            'res_model':'close.window.purchase',
            'type':'ir.actions.act_window',
            'target':'new',
            }
        else:
            viewid = self.env.ref("ans_escuela.cerrar_ventana_purchase_falla").id
            return {
            'name':'No hay estudiantes para generar las facturas.',
            'view_type':'form',
            'views' : [(viewid,'form')],
            'res_model':'close.window.purchase',
            'type':'ir.actions.act_window',
            'target':'new',
            }

    @api.multi
    def validar_facturas(self):
        self.estado='2'
        for line in self.detalle_facturar:
            _logger.info("codigo interno factura ---------->"+str(line.codigo_interno))
            number = line.codigo_interno.validar_nuevo()
            line.number = number
        viewid = self.env.ref("ans_escuela.cerrar_ventana_purchase_falla").id
        return {
        'name':'¡Validación con Éxito!',
        'view_type':'form',
        'views' : [(viewid,'form')],
        'res_model':'close.window.purchase',
        'type':'ir.actions.act_window',
        'target':'new',
        }

    #INTEGRACION: SE DESCOMENTA PARA QUE VALIDE Y NO PUEDA ELIMINAR LOS REGISTROS
    @api.multi
    def unlink(self):
        for dat in self:
            for l in dat.detalle_facturar:
                if l.codigo_interno.id != False:
                    raise osv.except_osv(('Alerta'),("No se puede eliminar el registro por que existen Facturas Borrador creadas."))
        return super(GenerarFacturas, self).unlink()