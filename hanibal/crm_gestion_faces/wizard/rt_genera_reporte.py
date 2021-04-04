# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
import time

class rt_genera_reporte(osv.osv_memory):

    _name = 'rt.genera.reporte'
    _inherit = "account.common.report"
    _columns = {
        'partner_id':fields.many2one('res.partner','Cliente'),
        'user_id':fields.many2one('res.users','Comercial'),
        'product_id':fields.many2one('product.product','Producto'),
        'desde' : fields.date('Desde'),
        'hasta' : fields.date('Hasta'),
       
         }
    
    _defaults = {
       
        
    } 
  

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        var = self.read(cr, uid, ids, ['partner_id','user_id','product_id','desde','hasta'], context=context)[0]
        data['form'].update(var)        
        return data
    
    
    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'reporte.cotizacion',
                'datas': data, }

rt_genera_reporte()
