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
    
class fiscal_formapago(osv.osv):
    _name='fiscal.formapago'
    _columns = {
        'name' : fields.char('Nombre',size=100,required=True),
        'codigofiscal' : fields.char('CodigoFiscal',size=100,required=True),
        'habilitado':fields.boolean('Habilitado',required=True),
        #Folios

        'folios_id':fields.many2one('folios.configuracion','Tipos de Productos',ondelete='cascade')
    }
    
    _defaults={
               'habilitado':True,
               }

    def _identificador(self,cr,uid,ids,context=None):
        identi_brw = self.browse(cr,uid,ids,context)
        for t in identi_brw:
            if t.codigofiscal:
                val_id = str(t.codigofiscal)
                query = " select count(*) from fiscal_formapago where codigofiscal = '"+str(val_id)+"' "
                cr.execute(query)
                rr = cr.dictfetchall()
                if rr[0]['count'] > 1:
                    raise osv.except_osv('Error!','El codigofiscal no se puede repetir')
                else:
                    return True
    _constraints=[
                 
                 (_identificador,('El identificador no se puede repetir'),['codigofiscal'] )
                 
                 ]
    
fiscal_formapago()
