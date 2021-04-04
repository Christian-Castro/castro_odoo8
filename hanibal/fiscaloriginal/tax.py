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
from openerp import api

class account_tax(osv.osv):
    _name = 'account.tax'
    _inherit = 'account.tax'

    def _unit_compute_ret(self, cr, uid, taxes, price_unit,  product=None, partner=None, quantity=0):
        taxes = self._applicable(cr, uid, taxes, price_unit,  product, partner)
        res = []
        cur_price_unit=price_unit
        for tax in taxes:
            # we compute the amount for the current tax object and append it to the result
            data = {'id':tax.id,
                    'name':tax.description and tax.description + " - " + tax.name or tax.name,
                    'account_collected_id':tax.account_collected_id.id,
                    'account_paid_id':tax.account_paid_id.id,
                    'base_code_id': tax.base_code_id.id,
                    'ref_base_code_id': tax.ref_base_code_id.id,
                    'sequence': tax.sequence,
                    'base_sign': tax.base_sign,
                    'tax_sign': tax.tax_sign,
                    'ref_base_sign': tax.ref_base_sign,
                    'ref_tax_sign': tax.ref_tax_sign,
                    'price_unit': cur_price_unit,
                    'tax_code_id': tax.tax_code_id.id,
                    'ref_tax_code_id': tax.ref_tax_code_id.id,

                    'codigo': tax.codigofiscal,
                    'porcentaje': tax.amount,
                    'tipo': tax.tipo,
            }

            res.append(data)
            if tax.type=='percent':
                amount = cur_price_unit * tax.amount
                data['amount'] = amount

            elif tax.type=='fixed':
                data['amount'] = tax.amount
                data['tax_amount']=quantity
               # data['amount'] = quantity
            elif tax.type=='code':
                localdict = {'price_unit':cur_price_unit,  'product':product, 'partner':partner}
                exec tax.python_compute in localdict
                amount = localdict['result']
                data['amount'] = amount
            elif tax.type=='balance':
                data['amount'] = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)
                data['balance'] = cur_price_unit

            amount2 = data.get('amount', 0.0)
            if tax.child_ids:
                if tax.child_depend:
                    latest = res.pop()
                amount = amount2
                child_tax = self._unit_compute(cr, uid, tax.child_ids, amount,  product, partner, quantity)
                res.extend(child_tax)
                if tax.child_depend:
                    for r in res:
                        for name in ('base','ref_base'):
                            if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
                                r[name+'_code_id'] = latest[name+'_code_id']
                                r[name+'_sign'] = latest[name+'_sign']
                                r['price_unit'] = latest['price_unit']
                                latest[name+'_code_id'] = False
                        for name in ('tax','ref_tax'):
                            if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
                                r[name+'_code_id'] = latest[name+'_code_id']
                                r[name+'_sign'] = latest[name+'_sign']
                                r['amount'] = data['amount']
                                latest[name+'_code_id'] = False
            if tax.include_base_amount:
                cur_price_unit+=amount2
        return res

    def _unit_compute_inv_ret(self, cr, uid, taxes, price_unit,  product=None, partner=None):
        
        taxes = self._applicable(cr, uid, taxes, price_unit,  product, partner)
        res = []
        taxes.reverse()
        cur_price_unit = price_unit

        tax_parent_tot = 0.0
        for tax in taxes:
            if (tax.type=='percent') and not tax.include_base_amount:
                tax_parent_tot += tax.amount

        for tax in taxes:
            if (tax.type=='fixed') and not tax.include_base_amount:
                cur_price_unit -= tax.amount

        for tax in taxes:
            if tax.type=='percent':
                if tax.include_base_amount:
                    amount = cur_price_unit - (cur_price_unit / (1 + tax.amount))
                else:
                    amount = (cur_price_unit / (1 + tax_parent_tot)) * tax.amount

            elif tax.type=='fixed':
                amount = tax.amount

            elif tax.type=='code':
                localdict = {'price_unit':cur_price_unit, 'product':product, 'partner':partner}
                exec tax.python_compute_inv in localdict
                amount = localdict['result']
            elif tax.type=='balance':
                amount = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)

            if tax.include_base_amount:
                cur_price_unit -= amount
                todo = 0
            else:
                todo = 1
            res.append({
                'id': tax.id,
                'todo': todo,
                'name': tax.name,
                'amount': amount,
                'account_collected_id': tax.account_collected_id.id,
                'account_paid_id': tax.account_paid_id.id,
                'base_code_id': tax.base_code_id.id,
                'ref_base_code_id': tax.ref_base_code_id.id,
                'sequence': tax.sequence,
                'base_sign': tax.base_sign,
                'tax_sign': tax.tax_sign,
                'ref_base_sign': tax.ref_base_sign,
                'ref_tax_sign': tax.ref_tax_sign,
                'price_unit': cur_price_unit,
                'tax_code_id': tax.tax_code_id.id,
                'ref_tax_code_id': tax.ref_tax_code_id.id,

                'porcentaje': tax.amount,
                'codigo': tax.description,
                'tipo':tax.tipo,                
            })

            if tax.child_ids:
                if tax.child_depend:
                    del res[-1]
                    amount = price_unit

            parent_tax = self._unit_compute_inv(cr, uid, tax.child_ids, amount, product, partner)
            res.extend(parent_tax)

        total = 0.0
        for r in res:
            if r['todo']:
                total += r['amount']
        for r in res:
            r['price_unit'] -= total
            r['todo'] = 0

        return res

    def compute_inv_ret(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None):
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.
        Price Unit is a VAT included price

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        res = self._unit_compute_inv_ret(cr, uid, taxes, price_unit, product, partner=None)
        total = 0.0
        obj_precision = self.pool.get('decimal.precision')
        for r in res:
            prec = obj_precision.precision_get(cr, uid, 'Account')
            if r.get('balance',False):
                r['amount'] = round(r['balance'] * quantity, prec) - total
            else:
                r['amount'] = round(r['amount'] * quantity, prec)
                total += r['amount']
        return res

    def _compute_ret(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None):  
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        res = self._unit_compute_ret(cr, uid, taxes, price_unit,  product, partner, quantity)
        total = 0.0
        precision_pool = self.pool.get('decimal.precision')
        for r in res:
            if r.get('balance',False):
                r['amount'] = round(r.get('balance', 0.0) * quantity, precision_pool.precision_get(cr, uid, 'Account')) - total
            else:
                r['amount'] = round(r.get('amount', 0.0) * quantity, precision_pool.precision_get(cr, uid, 'Account'))
                total += r['amount']

        return res

        #----------------------------------------------------------------------------------
    @api.v7
    def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, force_excluded=False):
        """
        :param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
            tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
            False
        RETURN: {
                'total': 0.0,                # Total without taxes
                'total_included: 0.0,        # Total with taxes
                'taxes': []                  # List of taxes, see compute for the format
            }
        """

        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        
        """precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        totalin = totalex = round(price_unit * quantity, precision)"""
        
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        tax_compute_precision = precision
        
        if taxes and taxes[0].company_id.tax_calculation_rounding_method == 'round_globally':
            tax_compute_precision += 5
        totalin = totalex = round(price_unit * quantity, precision)
        tin = []
        tex = []
        for tax in taxes:
            if not tax.price_include or force_excluded:
                tex.append(tax)
            else:
                tin.append(tax)
        tin = self.compute_inv_ret(cr, uid, tin, price_unit, quantity, product=product, partner=partner)
        for r in tin:
            totalex -= r.get('amount', 0.0)
        totlex_qty = 0.0
        try:
            totlex_qty = totalex/quantity
        except:
            pass
        tex = self._compute_ret(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner)
        for r in tex:
            totalin += r.get('amount', 0.0)

        return {
            'total': totalex,
            'total_included': totalin,
            'taxes': tin + tex
        }
        
        
    @api.v8
    def compute_all(self, price_unit, quantity, product=None, partner=None, force_excluded=False):
        return self._model.compute_all(
            self._cr, self._uid, self, price_unit, quantity,
            product=product, partner=partner, force_excluded=force_excluded)
    
    #----------------------------------------------------------------------------------
        
    _columns = {
        'codigofiscal': fields.char('Concepto de Retencion',10),    
        'descripcion': fields.char('Descripcion',100),
        'tipo': fields.selection([('iva','IVA'),('fte','FUENTE')],'Tipo'),
        'base': fields.selection([('iva','IVA'),('subtotal','Subtotal'),('basecero','Base 0'),('baseiva','Base 12'),('basenograva','Base no grava IVA')],'Base imponible'),
        'reglaretencion_id':fields.one2many('fiscal.reglaretencion', 'tax_id', 'Reglas para impuestos'),
        'esretencion' : fields.boolean('Es Retencion', requiered=True),
    }

    _defaults = {    
        'esretencion' : False,
    }

    def check_reglasretencion(self, cr, uid, ids, context=None):
        for tax in self.browse(cr, uid, ids, context=context):
            if not tax.esretencion:
                continue
            if not tax.reglaretencion_id:
                return False
            
        return True  

    _constraints = [
                    (check_reglasretencion,'Ingrese por lo menos una regla para retencion.', ['reglaretencion_id']),
                ]

account_tax()

# class account_tax(osv.osv):
#     _name = 'account.tax'
#     _inherit = 'account.tax'
# 
#     def _unit_compute_ret(self, cr, uid, taxes, price_unit, address_id=None, product=None, partner=None, quantity=0):
#         taxes = self._applicable(cr, uid, taxes, price_unit, address_id, product, partner)
#         res = []
#         cur_price_unit=price_unit
#         obj_partener_address = self.pool.get('res.partner.address')
#         for tax in taxes:
#             # we compute the amount for the current tax object and append it to the result
#             data = {'id':tax.id,
#                     'name':tax.description and tax.description + " - " + tax.name or tax.name,
#                     'account_collected_id':tax.account_collected_id.id,
#                     'account_paid_id':tax.account_paid_id.id,
#                     'base_code_id': tax.base_code_id.id,
#                     'ref_base_code_id': tax.ref_base_code_id.id,
#                     'sequence': tax.sequence,
#                     'base_sign': tax.base_sign,
#                     'tax_sign': tax.tax_sign,
#                     'ref_base_sign': tax.ref_base_sign,
#                     'ref_tax_sign': tax.ref_tax_sign,
#                     'price_unit': cur_price_unit,
#                     'tax_code_id': tax.tax_code_id.id,
#                     'ref_tax_code_id': tax.ref_tax_code_id.id,
# 
#                     'codigo': tax.codigofiscal,
#                     'porcentaje': tax.amount,
#                     'tipo': tax.tipo,
#             }
# 
#             res.append(data)
#             if tax.type=='percent':
#                 amount = cur_price_unit * tax.amount
#                 data['amount'] = amount
# 
#             elif tax.type=='fixed':
#                 data['amount'] = tax.amount
#                 data['tax_amount']=quantity
#                # data['amount'] = quantity
#             elif tax.type=='code':
#                 address = address_id and obj_partener_address.browse(cr, uid, address_id) or None
#                 localdict = {'price_unit':cur_price_unit, 'address':address, 'product':product, 'partner':partner}
#                 exec tax.python_compute in localdict
#                 amount = localdict['result']
#                 data['amount'] = amount
#             elif tax.type=='balance':
#                 data['amount'] = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)
#                 data['balance'] = cur_price_unit
# 
#             amount2 = data.get('amount', 0.0)
#             if tax.child_ids:
#                 if tax.child_depend:
#                     latest = res.pop()
#                 amount = amount2
#                 child_tax = self._unit_compute(cr, uid, tax.child_ids, amount, address_id, product, partner, quantity)
#                 res.extend(child_tax)
#                 if tax.child_depend:
#                     for r in res:
#                         for name in ('base','ref_base'):
#                             if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
#                                 r[name+'_code_id'] = latest[name+'_code_id']
#                                 r[name+'_sign'] = latest[name+'_sign']
#                                 r['price_unit'] = latest['price_unit']
#                                 latest[name+'_code_id'] = False
#                         for name in ('tax','ref_tax'):
#                             if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
#                                 r[name+'_code_id'] = latest[name+'_code_id']
#                                 r[name+'_sign'] = latest[name+'_sign']
#                                 r['amount'] = data['amount']
#                                 latest[name+'_code_id'] = False
#             if tax.include_base_amount:
#                 cur_price_unit+=amount2
#         return res
# 
#     def _unit_compute_inv_ret(self, cr, uid, taxes, price_unit, address_id=None, product=None, partner=None):
#         taxes = self._applicable(cr, uid, taxes, price_unit, address_id, product, partner)
#         obj_partener_address = self.pool.get('res.partner.address')
#         res = []
#         taxes.reverse()
#         cur_price_unit = price_unit
# 
#         tax_parent_tot = 0.0
#         for tax in taxes:
#             if (tax.type=='percent') and not tax.include_base_amount:
#                 tax_parent_tot += tax.amount
# 
#         for tax in taxes:
#             if (tax.type=='fixed') and not tax.include_base_amount:
#                 cur_price_unit -= tax.amount
# 
#         for tax in taxes:
#             if tax.type=='percent':
#                 if tax.include_base_amount:
#                     amount = cur_price_unit - (cur_price_unit / (1 + tax.amount))
#                 else:
#                     amount = (cur_price_unit / (1 + tax_parent_tot)) * tax.amount
# 
#             elif tax.type=='fixed':
#                 amount = tax.amount
# 
#             elif tax.type=='code':
#                 address = address_id and obj_partener_address.browse(cr, uid, address_id) or None
#                 localdict = {'price_unit':cur_price_unit, 'address':address, 'product':product, 'partner':partner}
#                 exec tax.python_compute_inv in localdict
#                 amount = localdict['result']
#             elif tax.type=='balance':
#                 amount = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)
# 
#             if tax.include_base_amount:
#                 cur_price_unit -= amount
#                 todo = 0
#             else:
#                 todo = 1
#             res.append({
#                 'id': tax.id,
#                 'todo': todo,
#                 'name': tax.name,
#                 'amount': amount,
#                 'account_collected_id': tax.account_collected_id.id,
#                 'account_paid_id': tax.account_paid_id.id,
#                 'base_code_id': tax.base_code_id.id,
#                 'ref_base_code_id': tax.ref_base_code_id.id,
#                 'sequence': tax.sequence,
#                 'base_sign': tax.base_sign,
#                 'tax_sign': tax.tax_sign,
#                 'ref_base_sign': tax.ref_base_sign,
#                 'ref_tax_sign': tax.ref_tax_sign,
#                 'price_unit': cur_price_unit,
#                 'tax_code_id': tax.tax_code_id.id,
#                 'ref_tax_code_id': tax.ref_tax_code_id.id,
# 
#                 'porcentaje': tax.amount,
#                 'codigo': tax.description,
#                 'tipo':tax.tipo,                
#             })
# 
#             if tax.child_ids:
#                 if tax.child_depend:
#                     del res[-1]
#                     amount = price_unit
# 
#             parent_tax = self._unit_compute_inv(cr, uid, tax.child_ids, amount, address_id, product, partner)
#             res.extend(parent_tax)
# 
#         total = 0.0
#         for r in res:
#             if r['todo']:
#                 total += r['amount']
#         for r in res:
#             r['price_unit'] -= total
#             r['todo'] = 0
# 
#         return res
# 
#     def compute_inv_ret(self, cr, uid, taxes, price_unit, quantity, address_id=None, product=None, partner=None):
#         """
#         Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.
#         Price Unit is a VAT included price
# 
#         RETURN:
#             [ tax ]
#             tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
#             one tax for each tax id in IDS and their children
#         """
#         res = self._unit_compute_inv_ret(cr, uid, taxes, price_unit, address_id, product, partner=None)
#         total = 0.0
#         obj_precision = self.pool.get('decimal.precision')
#         for r in res:
#             prec = obj_precision.precision_get(cr, uid, 'Account')
#             if r.get('balance',False):
#                 r['amount'] = round(r['balance'] * quantity, prec) - total
#             else:
#                 r['amount'] = round(r['amount'] * quantity, prec)
#                 total += r['amount']
#         return res
# 
#     def _compute_ret(self, cr, uid, taxes, price_unit, quantity, address_id=None, product=None, partner=None):  
#         """
#         Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.
# 
#         RETURN:
#             [ tax ]
#             tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
#             one tax for each tax id in IDS and their children
#         """
#         res = self._unit_compute_ret(cr, uid, taxes, price_unit, address_id, product, partner, quantity)
#         total = 0.0
#         precision_pool = self.pool.get('decimal.precision')
#         for r in res:
#             if r.get('balance',False):
#                 r['amount'] = round(r.get('balance', 0.0) * quantity, precision_pool.precision_get(cr, uid, 'Account')) - total
#             else:
#                 r['amount'] = round(r.get('amount', 0.0) * quantity, precision_pool.precision_get(cr, uid, 'Account'))
#                 total += r['amount']
# 
#         return res
# 
#     def compute_all(self, cr, uid, taxes, price_unit, quantity, address_id=None, product=None, partner=None, force_excluded=False):
#   
#         """
#         :param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
#             tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
#             False
#         RETURN: {
#                 'total': 0.0,                # Total without taxes
#                 'total_included: 0.0,        # Total with taxes
#                 'taxes': []                  # List of taxes, see compute for the format
#             }
#         """
#         precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
#         totalin = totalex = round(price_unit * quantity, precision)
#         tin = []
#         tex = []
#         for tax in taxes:
#             if not tax.price_include or force_excluded:
#                 tex.append(tax)
#             else:
#                 tin.append(tax)
#         tin = self.compute_inv_ret(cr, uid, tin, price_unit, quantity, address_id=address_id, product=product, partner=partner)
#         for r in tin:
#             totalex -= r.get('amount', 0.0)
#         totlex_qty = 0.0
#         try:
#             totlex_qty = totalex/quantity
#         except:
#             pass
#         tex = self._compute_ret(cr, uid, tex, totlex_qty, quantity, address_id=address_id, product=product, partner=partner)
#         for r in tex:
#             totalin += r.get('amount', 0.0)
# 
#         return {
#             'total': totalex,
#             'total_included': totalin,
#             'taxes': tin + tex
#         }
#         
#     _columns = {
#         'codigofiscal': fields.char('Concepto de Retencion',10),    
#         'descripcion': fields.char('Descripcion',100),
#         'tipo': fields.selection([('iva','IVA'),('fte','FUENTE')],'Tipo'),
#         'base': fields.selection([('iva','IVA'),('subtotal','Subtotal'),('basecero','Base 0'),('baseiva','Base 12'),('basenograva','Base no grava IVA')],'Base imponible'),
#         'reglaretencion_id':fields.one2many('fiscal.reglaretencion', 'tax_id', 'Reglas para impuestos'),
#         'esretencion' : fields.boolean('Es Retencion', requiered=True),
#     }
# 
#     _defaults = {    
#         'esretencion' : False,
#     }
# 
#     def check_reglasretencion(self, cr, uid, ids, context=None):
#         for tax in self.browse(cr, uid, ids, context=context):
#             if not tax.esretencion:
#                 continue
#             if not tax.reglaretencion_id:
#                 return False
#             
#         return True  
# 
#     _constraints = [
#                     (check_reglasretencion,'Ingrese por lo menos una regla para retencion.', ['reglaretencion_id']),
#                 ]
# 
# account_tax()