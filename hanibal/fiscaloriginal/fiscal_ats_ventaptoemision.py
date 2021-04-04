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
############################################################################### -*- encoding: utf-8 -*-

from openerp.osv import osv,fields
from xml.dom import minidom

class fiscal_ats_ventaptoemision(osv.osv):
    _name = 'fiscal.ats_ventaptoemision'

    def toxml(self, listaventaspto):        
        doc = minidom.Document()
        ventaspto = doc.createElement('ventasEstablecimiento')
        doc.appendChild(ventaspto)
                
        for v in listaventaspto:
                
                detalle = doc.createElement('ventaEst')
                ventaspto.appendChild(detalle)
                
                node = doc.createElement('codEstab')
                detalle.appendChild(node)
                txt = doc.createTextNode( v.establecimiento )
                node.appendChild(txt)
                
                node = doc.createElement('ventasEstab')
                detalle.appendChild(node)
                txt = doc.createTextNode("%.2f" % v.total)
                node.appendChild(txt)
            
        return ventaspto
    
    
    _columns = {
   
            'atsproceso_id':fields.many2one('fiscal.ats_proceso','ATS Proceso', required=True,ondelete='cascade'),
            'establecimiento':fields.char('Establecimiento',size=3,required=True),
            'total': fields.float('Total', digits=(8,2),required=True),
            'manual': fields.boolean('Manual', required=True),

        }
    
    _defaults = {
                 'manual':True
                 }
        
fiscal_ats_ventaptoemision()