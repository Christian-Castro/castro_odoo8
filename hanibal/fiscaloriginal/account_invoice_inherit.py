from openerp import models, fields, api

class account_invoice_inherit(models.Model):
    _inherit = 'account.invoice'

    #CDCM
    #07-04-2021
    #creacion de bandera para crear facturas desde solicitud sin punto de emision    
    requerido_pto_emisison = fields.Boolean(help="para crear facturas desde solicitud sin punto de emision", default=False, string="Boll")
    #CDCM