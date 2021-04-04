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
    
class fiscal_tpago(osv.osv):
    _name='fiscal.tipopago'
    _columns = {
        'name' : fields.char('Nombre',size=100,required=True),
        'codigofiscal' : fields.char('CodigoFiscal',size=100,required=True),
        'identificador': fields.selection([('01','Local'),('02','Exterior'),],select=True,string="Identificador",required=True),
        'habilitado':fields.boolean('Habilitado',required=True),
    }
    
    _defaults={
               'habilitado':True,
               }

    def _identificarepetido(self,cr,uid,ids,context=None):
        brw = self.browse(cr,uid,ids,context)
        for t in brw:
            if t.codigofiscal:
                v_codigofiscal = str(t.codigofiscal)
                query = " select count(*) from fiscal_tpago where codigofiscal = '"+str(v_codigofiscal)+"' "
                cr.execute(query)
                rr = cr.dictfetchall()
                if rr[0]['count'] > 1:
                    raise osv.except_osv('Error!','El codigoFISCAL no se puede repetir')
                else:
                    return True
    _constraints=[
                 
                 (_identificarepetido,('El codigoFISCAL no se puede repetir'),['codigofiscal'] )
                 
                 ]
    
fiscal_tpago()
