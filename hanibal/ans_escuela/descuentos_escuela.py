# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import models, fields, api, _


class descuentos_escuela(models.Model):
    _name = 'descuentos'
    
    name = fields.Char('Descripción')
    porcentaje = fields.Float('Porcentaje')
    sequence = fields.Integer('Sequence')
    cuenta_id = fields.Many2one('account.account',string="Cuenta")
    is_pronto_pago = fields.Boolean(string="Es pronto pago",default=False)
    dias = fields.Integer(string="Dias de Descuento")


class descuentos_tomar_escuela(models.Model):
    _name="descuentos.tomar"
    
    sequence = fields.Integer('Sequence')
    descuento_id = fields.Many2one('descuentos','Descuento')
    porcentaje = fields.Float(related='descuento_id.porcentaje',string='Porcentaje')
    partner_ids = fields.Many2one('res.partner','Alumno',ondelete="cascade")

class descuentos_factura_escuela(models.Model):
    _name="descuentos.factura"
    
    descuento_id = fields.Many2one('descuentos','Descuento')
    monto = fields.Float(string='Total')
    factura_id = fields.Many2one('account.invoice','Facturas',ondelete="cascade")


class Detalle_Descuento_line(models.Model):
    _name = "descuentos.factura.producto"

    factura_det_id = fields.Many2one('descuentos.factura.cabezera','Facturas',ondelete="cascade")
    descuento_id = fields.Many2one('descuentos','Descuento')
    porcentaje = fields.Float(related='descuento_id.porcentaje',string='Porcentaje')
    base = fields.Float(string="Base")
    monto = fields.Float(string="Monto")


class Detalle_Descuento_line(models.Model):
    _name = "descuentos.factura.cabezera"

    factura_id = fields.Many2one('account.invoice.line','Facturas',ondelete="cascade")
    detalle_descuento = fields.One2many('descuentos.factura.producto','factura_det_id',string="Detalle")