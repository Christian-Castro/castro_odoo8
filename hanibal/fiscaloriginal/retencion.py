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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class fiscal_retencion_ln(osv.osv):
    _name = "fiscal.retencion.ln"
    _description = "Detalle de Retencion"  

    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Factura', ondelete='cascade', select=True),
        'name': fields.char('Descripcion', size=64, required=True),
        'account_id': fields.many2one('account.account', 'Tax Account', required=True, domain=[('type','<>','view'),('type','<>','income'), ('type', '<>', 'closed')]),
        'base': fields.float('Base', digits_compute=dp.get_precision('Account')),
        'amount': fields.float('Monto', digits_compute=dp.get_precision('Account')),
        'manual': fields.boolean('Manual'),
        'sequence': fields.integer('Secuencia', help="Gives the sequence order when displaying a list of invoice tax."),
        'base_amount': fields.float('Base Code Amount', digits_compute=dp.get_precision('Account')),        
        'tax_amount': fields.float('Tax Code Amount', digits_compute=dp.get_precision('Account')),
        'company_id': fields.related('account_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'base_code_id': fields.many2one('account.tax.code', 'Base Code', help="The account basis of the tax declaration."),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', help="The tax basis of the tax declaration."),

        'ejerciciofiscal': fields.char('Ejercicio Fiscal', size=4),
        'tipo': fields.char('Impuesto',size=64),
        'codigo': fields.char('Codigo',size=10),
        'porcentaje': fields.float('Porcentaje', digits_compute=dp.get_precision('Account')),
    }

    _order = 'sequence'
    _defaults = {
        'manual': 1,
        'base_amount': 0.0,
        'tax_amount': 0.0,
    }

    def computetax(self, taxes_obj , base, quantity , line , invoice , tax_grouped):
        currency = invoice.currency_id.with_context(date=invoice.date_invoice )
        company_currency = invoice.company_id.currency_id
        for tax in taxes_obj:
            if tax != []:
                taxes = tax[0].compute_all( base ,quantity,line.product_id,invoice.partner_id)['taxes']
                for tax in taxes:
                    val = {
                        'invoice_id': invoice.id,
                        'name': tax['name'],
                        'amount': tax['amount'],
                        'manual': False,
                        'sequence': tax['sequence'],
                        'base': currency.round(tax['price_unit']),
                        'porcentaje': tax['porcentaje'],
                        'codigo': tax['codigo'],
                        'tipo': tax['tipo'],
                    }
                    
                    if invoice.type in ('out_invoice','in_invoice'):
                        val['base_code_id'] = tax['base_code_id']
                        val['tax_code_id'] = tax['tax_code_id']
                        val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                        val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                        val['account_id'] = tax['account_collected_id'] or line.account_id.id
                        
                    else:
                        val['base_code_id'] = tax['ref_base_code_id']
                        val['tax_code_id'] = tax['ref_tax_code_id']
                        val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                        val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                        val['account_id'] = tax['account_paid_id'] or line.account_id.id
    
                    # If the taxes generate moves on the same financial account as the invoice line
                    # and no default analytic account is defined at the tax level, propagate the
                    # analytic account from the invoice line to the tax line. This is necessary
                    # in situations were (part of) the taxes cannot be reclaimed,
                    # to ensure the tax move is allocated to the proper analytic account.
                    if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                        val['account_analytic_id'] = line.account_analytic_id.id
    
                    key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                    if not key in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['base'] += val['base']
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base_amount'] += val['base_amount']
                        tax_grouped[key]['tax_amount'] += val['tax_amount']
    
    
    def actualizarretenciones(self,tipoproducto,fiscal_position):
        
        taxes = []
        reglas = tipoproducto.reglaretencion_id
        if(reglas):
            for r in reglas:
                if(r.posicionfiscal_id == fiscal_position):
                    if(r.tax_id.esretencion):
                        taxes.append(r.tax_id)
        return taxes

    
    
    def compute(self, invoice):
        
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice)
        inv = self.env['account.invoice'].browse(invoice.id)
        
        for line in inv.invoice_line:
            taxsubtotal =[]
            taxiva = []
            taxbaseiva = []
            taxbasecero=[]
            taxbasenograva=[]
           
            retenciones = self.actualizarretenciones(line.product_id.product_tmpl_id.tipoproducto_id,inv.fiscal_position)
            
            for tax in retenciones:
                if tax.base == 'subtotal':
                    taxsubtotal.append(tax)
                elif tax.base == 'iva':
                    taxiva.append(tax)
                elif tax.base == 'baseiva':
                    taxbaseiva.append(tax)
                elif tax.base == 'basecero':
                    taxbasecero.append(tax)
                elif tax.base == 'basenograva':
                    taxbasenograva.append(tax)   
                else:
                    raise osv.except_osv('Advertencia','Existen impuestos para retenciones con bases imponibles no definidas.')    
            
            subtotal = line.price_subtotal
            iva = line.valor_iva
            baseiva = line.baseiva
            basecero = line.basecero
            basenograva = line.basenograva
            
            self.computetax( taxsubtotal    ,subtotal    ,1            ,line, inv ,tax_grouped)
            self.computetax( taxiva         ,iva         ,1            ,line, inv ,tax_grouped )
            self.computetax( taxbaseiva     ,baseiva     ,line.quantity,line, inv ,tax_grouped )
            self.computetax( taxbasecero    ,basecero    ,line.quantity,line, inv ,tax_grouped )
            self.computetax( taxbasenograva ,basenograva ,line.quantity,line, inv ,tax_grouped )
            
        
        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])
        return tax_grouped
    
    
#     #Esta funcion realiza el calculo de los taxes para cada invoice line inclusive el redondeo. 
#     #retorna un diccionario con todos los taxes calculados
#     def compute(self, cr, uid, invoice_id, context=None):
#         tax_grouped = {}
#         cur_obj = self.pool.get('res.currency')
#         inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
#         cur = inv.currency_id
# 
#         for line in inv.invoice_line:
#             taxsubtotal =[]
#             taxiva = []
#             taxbaseiva = []
#             taxbasecero=[]
#             taxbasenograva=[]        
#             
#             retenciones = self.actualizarretenciones(line.product_id.tipoproducto_id,inv.fiscal_position)
#             
#             #for tax in line.retenciones_id:
#             for tax in retenciones:
#                 if tax.base == 'subtotal':
#                     taxsubtotal.append(tax)
#                 elif tax.base == 'iva':
#                     taxiva.append(tax)
#                 elif tax.base == 'baseiva':
#                     taxbaseiva.append(tax)
#                 elif tax.base == 'basecero':
#                     taxbasecero.append(tax)
#                 elif tax.base == 'basenograva':
#                     taxbasenograva.append(tax)   
#                 else:
#                      raise osv.except_osv('Advertencia','Existen impuestos para retenciones con bases imponibles no definidas.')	
# 
#             subtotal = line.price_subtotal
#             iva = line.valor_iva
#             baseiva = line.baseiva
#             basecero = line.basecero
#             basenograva = line.basenograva
#             
#             self.computetax(cr, uid, context, taxsubtotal,   subtotal,  1,     line, cur_obj, inv, cur, tax_grouped)
#             self.computetax(cr, uid, context, taxiva,    iva,         1,        line, cur_obj, inv, cur, tax_grouped)
#             self.computetax(cr, uid, context, taxbaseiva, baseiva, line.quantity, line, cur_obj, inv, cur, tax_grouped)
#             self.computetax(cr, uid, context, taxbasecero, basecero, line.quantity, line, cur_obj, inv, cur, tax_grouped)
#             self.computetax(cr, uid, context, taxbasenograva, basenograva, line.quantity, line, cur_obj, inv, cur, tax_grouped)
# 
#         for t in tax_grouped.values():
#             t['base'] = cur_obj.round(cr, uid, cur, t['base'])
#             t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
#             t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
#             t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
#         return tax_grouped

    def move_line_get(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM fiscal_retencion_ln WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            if not t['amount'] \
                    and not t['tax_code_id'] \
                    and not t['tax_amount']:
                continue
            res.append({
                'type':'tax',
                'name':t['name'],
                'price_unit': t['amount'],
                'quantity': 1,
                'price': t['amount'] or 0.0,
                'account_id': t['account_id'],
                'tax_code_id': t['tax_code_id'],
                'tax_amount': t['tax_amount']
            })
        return res

fiscal_retencion_ln()