# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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


from openerp.report import report_sxw



class proforma_crm_report(report_sxw.rml_parse):
    
    ESTADOS = {
            'draft': 'Borrador',
            'manual': 'Confirmado'
            }
    
    
    def __init__(self, cr, uid, name, context):
        super(proforma_crm_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            
            'convert': self.convert,
            'valido': self.date_valida,
            
        })       
        self.context = context 
        
    def convert(self, estado):
        valor = self.ESTADOS[estado]
        return valor
        
    def date_valida(self,fecha,dias):
        print fecha,dias
        if fecha and dias:
            SQL = " select ( SELECT CAST('"+str(fecha)+"' AS DATE) + CAST('"+str(dias)+" days' AS INTERVAL) ):: DATE as date"
	    print SQL
            self.cr.execute(SQL)
            res = self.cr.dictfetchall()
            fecha = res[0]['date'] 
        return fecha
        
report_sxw.report_sxw(
    'report.cotizacion.venta.crm',
    'sale.order',
    'addons/sale/report/proforma_crm_repor.rml',
    parser=proforma_crm_report
)
