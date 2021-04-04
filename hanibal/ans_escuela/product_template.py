# -*- coding: utf-8 -*-


from openerp.osv import osv,fields
from openerp import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit="product.template" 

    cuenta_descuento_id = fields.Many2one('account.account',string="Cuenta de Descuento")
