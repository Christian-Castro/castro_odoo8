# -*- coding: utf-8 -*-
import re

from openerp import models, fields, api
from openerp.exceptions import ValidationError, RedirectWarning
from openerp.osv.orm import except_orm
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime, date
import copy
import logging
_logger = logging.getLogger(__name__)

class NotasCreditoProveedor(models.Model):
    _inherit = 'account.invoice'
    _order = 'date_invoice desc'


    name_nc = fields.Char(string='Nombre Nota De Credito')
    

    #RERV
    @api.onchange('partner_id')
    def onchange_set_fields(self):
        if self.env.context.get('default_type', False) == 'in_refund':
            res = {}
            if self.partner_id:
                if self.partner_id.property_account_payable:
                    self.account_id = self.partner_id.property_account_payable
                if self.partner_id.invoice_ids:
                    res['domain'] = {'factura': [('id', 'in', self.partner_id.invoice_ids.ids)]}
                #posicion fiscal
                if self.partner_id.property_account_position:
                    self.fiscal_position = self.partner_id.property_account_position.id
            else:
                self.account_id = False
                res['domain'] = {'factura': [('id', '=', 0)]}
                #posicion fiscal
                self.fiscal_position = False
            return res

    #RERV
    @api.constrains('establecimiento_h', 'puntoemision_h', 'secuencial_h', 'invice_line')
    def constrains_validaciones(self):
        if ((self.env.context.get('type', False) == 'in_refund'
            or self.env.context.get('type', False) == 'out_refund')
            and self.env.context.get('tipo', False) == 'nota_credito_cliente'
            or self.env.context.get('tipo', False) == 'nota_credito_proveedor'):

            if not self.establecimiento_h.isnumeric():
                raise ValidationError("Establecimiento debe contener solo números enteros")
            elif not len(self.establecimiento_h) == 3:
                raise ValidationError("Establecimiento debe contener 3 enteros")
            if not self.puntoemision_h.isnumeric():
                raise ValidationError("Punto Emisión debe contener solo números enteros")
            elif not len(self.puntoemision_h) == 3:
                raise ValidationError("Punto Emisión debe contener 3 enteros")
            if not self.secuencial_h.isnumeric():
                raise ValidationError("Secuencial debe contener solo números enteros")
            elif not len(self.secuencial_h) == 9:
                raise ValidationError("Secuencial debe contener 9 enteros")
            self.name = 'Nota De Credito %s' %(self.establecimiento_h +'-'+ self.puntoemision_h +'-'+ self.secuencial_h)
            self.name_nc = 'Nota De Credito %s' %(self.establecimiento_h +'-'+ self.puntoemision_h +'-'+ self.secuencial_h)

            if not self.invoice_line:
                raise ValidationError("Debe agregar por lo menos 1 Linea De Factura")

    # Se lo comenta para que no se genere el numerofac al momento de crear la factura
    # def on_change_puntoemision_id(self, cr, uid, ids, puntoemision_id=False, context=None):
    #     res = super(NotasCreditoProveedor, self).on_change_puntoemision_id(cr, uid, ids, puntoemision_id, context)
    #     puntoemision_obj = self.pool.get('fiscal.puntoemision').browse(cr,uid,puntoemision_id,context=context)
    #     if puntoemision_obj:
    #         res['value']['establecimiento_h'] = puntoemision_obj.establecimiento or ''
    #         res['value']['puntoemision_h'] = puntoemision_obj.puntoemision or ''
    #         res['value']['secuencial_h'] = str(int(puntoemision_obj.secuenciaActual)+1).zfill(9) or ''
    #         numerofac =  (puntoemision_obj.establecimiento or '') +'-'+ (puntoemision_obj.puntoemision or '') +'-'+ (str(int(puntoemision_obj.secuenciaActual)+1).zfill(9) or '')
    #         res['value']['numerofac'] = numerofac
    #     return res
