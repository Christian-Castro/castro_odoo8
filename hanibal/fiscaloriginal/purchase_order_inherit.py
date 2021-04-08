from openerp import models, fields, api
from openerp.exceptions import ValidationError

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    @api.constrains('order_line')
    def comprobar_impuestos(self):
        for rec in self.order_line:
            if not rec.taxes_id:
                raise ValidationError('El campo impuestos del producto %s esta vacio....'%rec.product_id.name)

    def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
        
        record = super(PurchaseOrderInherit, self)._prepare_invoice(cr, uid, order, line_ids, context=None)
        record.update({'requerido_pto_emisison':False})
        # record.update({'puntoemision_id':order.puntoemision_id.id})
        return record