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

from openerp.osv import osv,fields
import time

class account_invoice_lote(osv.osv_memory):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "account.invoice.lote"
    _description = "Generar facturas"
    
    _columns = {
            'anio_id':fields.many2one('periodo','Periodo'),
                    }
    
    def invoice_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []

        proxy = self.pool['res.partner']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.customer != True and record.tipo != 'P':
                raise osv.except_osv(('Alerta!'), 
        ("Solo puede generar la factura automática de Representantes!"))
            else:
                self.crear_factura(cr, uid, ids, record, context)

        return {'type': 'ir.actions.act_window_close'}
    
    def crear_factura(self,cr,uid,ids,record,context=None):
        producto_id = 1
        self.crear_cabecera(cr, uid, ids, record , context)
        self.crear_detalle(cr, uid, ids, producto_id , context)
    
    def crear_cabecera(self,cr,uid,ids, P ,context=None):
        
        
        obj_inv=self.pool.get('account.invoice')
        journal_id = 1 
        user_id = uid
        
        dct={
            'partner_id':P.parent_id.id,
            'partner_r_id':P.id,
            'account_id':P.parent_id.property_account_receivable.id,
            'journal_id':journal_id,
            'user_id':user_id,
            'date_invoice':time.strftime('%Y-%m-%d'),
            'reference_type':'none',
        }
        id_fact=obj_inv.create(cr,uid,dct)
        #record.signal_workflow('invoice_open')
        self.crear_detalle(cr, uid, ids, id_fact, context)
    
    def crear_detalle(self,cr,uid,ids,cab_id,context=None):
        produc_id = 1 
        cantidad = 1
        obj_prod = self.pool.get('product.product').browse(cr,uid,produc_id)
        obj_inv_line = self.pool.get('account.invoice.line')
        dct={
            'product_id':produc_id,
            'name':obj_prod.name_template,
            'account_id':obj_prod.property_account_income.id or obj_prod.categ_id.property_account_income_categ.id,
            'quantity':cantidad,
            'price_unit':obj_prod.product_tmpl_id.list_price,
            'invoice_id':cab_id,
             }
        
        obj_inv_line.create(cr,uid,dct)
        
        