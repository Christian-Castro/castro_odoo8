# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
    
class purchase_order(osv.osv):
    name='purchase.order'
    _inherit = "purchase.order"
    _columns = {
        'solicitadopor' : fields.many2one('res.users','Solicitado por'),
        'revisadopor' : fields.many2one('res.users','Revisado por'),
        'fechadepago': fields.date('Fecha de pago')
    }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """Collects require data from purchase order line that is used to create invoice line 
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        return {
            'name': order_line.name,
            'account_id': account_id,
            'price_unit': order_line.price_unit or 0.0,
            'quantity': order_line.product_qty,
            'product_id': order_line.product_id.id or False,
            'uos_id': order_line.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
            'account_analytic_id': order_line.account_analytic_id.id or False,
            'retenciones_id': [(6, 0, [x.id for x in order_line.retenciones_id])],
        }

    

    def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        res = False

        journal_obj = self.pool.get('account.journal')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        fiscal_obj = self.pool.get('account.fiscal.position')
        property_obj = self.pool.get('ir.property')

        for order in self.browse(cr, uid, ids, context=context):
            pay_acc_id = order.partner_id.property_account_payable.id
            journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase'),('company_id', '=', order.company_id.id)], limit=1)
            if not journal_ids:
                raise osv.except_osv(_('Error !'),
                    _('There is no purchase journal defined for this company: "%s" (id:%d)') % (order.company_id.name, order.company_id.id))

            # generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
            inv_lines = []
            for po_line in order.order_line:
                if po_line.product_id:
                    acc_id = po_line.product_id.product_tmpl_id.property_account_expense.id
                    if not acc_id:
                        acc_id = po_line.product_id.categ_id.property_account_expense_categ.id
                    if not acc_id:
                        raise osv.except_osv(_('Error !'), _('There is no expense account defined for this product: "%s" (id:%d)') % (po_line.product_id.name, po_line.product_id.id,))
                else:
                    acc_id = property_obj.get(cr, uid, 'property_account_expense_categ', 'product.category').id
                fpos = order.fiscal_position or False
                acc_id = fiscal_obj.map_account(cr, uid, fpos, acc_id)

                inv_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
                inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                inv_lines.append(inv_line_id)

                po_line.write({'invoiced':True, 'invoice_lines': [(4, inv_line_id)]}, context=context)

            # get invoice data and create invoice
            inv_data = {
                'name': order.partner_ref or order.name,
                'reference': order.partner_ref or order.name,
                'account_id': pay_acc_id,
                'type': 'in_invoice',
                'partner_id': order.partner_id.id,
                'currency_id': order.pricelist_id.currency_id.id,
                'address_invoice_id': order.partner_address_id.id,
                'address_contact_id': order.partner_address_id.id,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'invoice_line': [(6, 0, inv_lines)], 
                'origin': order.name,
                'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
                'payment_term': order.partner_id.property_payment_term and order.partner_id.property_payment_term.id or False,
                'company_id': order.company_id.id,
            }
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # compute the invoice
            inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)]}, context=context)
            res = inv_id
        return res    
   
purchase_order()

class purchase_order_line(osv.osv):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'
    
    def create(self, cr, uid, values, context=None):
        producto = self.pool.get('product.product').browse(cr, uid, values['product_id'], context)
        tipo = producto.tipoproducto_id
        reglas = tipo.reglaretencion_id
        
        obj = self.pool.get('purchase.order').browse(cr, uid, values['order_id'], context)
            
        partner = obj.partner_id
        fp = partner.property_account_position
        taxes = []
        if(reglas):
            for r in reglas:
                if(r.posicionfiscal_id == fp):
                    if(r.tax_id.esretencion):
                        taxes.append(r.tax_id.id)

        tmp = {'retenciones_id':[(6, 0, taxes)]}
        values.update(tmp)

        return super(purchase_order_line,self).create(cr,uid,values,context)
    
    _columns = {
        'retenciones_id': fields.many2many('account.tax', 'sri_purchase_retencion_line_tax_relation', 'retencion_line_id', 'tax_id', 'Retenciones Taxes', domain=[('parent_id','=',False)]),
    }
    
purchase_order_line()

class purchase_requisition(osv.osv):
    _name = 'purchase.requisition'
    _inherit = 'purchase.requisition'
    
    _columns = {
        'revisadopor': fields.many2one('res.users', 'Revisado por'),
        'aprobadopor': fields.many2one('res.users', 'Aprobado por'),
        
        'create_uid': fields.many2one('res.users', 'Autoriza'),   
        
    }
    
    
    
