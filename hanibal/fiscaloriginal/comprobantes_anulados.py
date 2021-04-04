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
from xml.dom import minidom
import re

class fiscal_comprobantesanulados(osv.osv):
    _name = 'fiscal.comprobantesanulados'

    _columns = {
            'tipocomprobante': fields.char('Tipo de Comprobante',size=5, required=True),
            'establecimiento' : fields.char('Establecimiento',size=3, required=True),
            'puntoemision' : fields.char('Punto emision',size=3, required=True),
            'secuencialinicio' : fields.char('Sec. Desde',size=50, required=True),
            'secuencialfin' : fields.char('Sec. Hasta',size=50, required=True),
            'autorizacion' : fields.char('Autorizacion Numero',size=50, required=True),
            
            'tipodocumento_id':fields.many2one('fiscal.tipodocumento', 'Tipo Documento', required=True),
			'atsproceso_id':fields.many2one('fiscal.ats_proceso','ATS Proceso',required=True,ondelete='cascade'),
			'manual':fields.boolean('Manual', required=True),
            'puntoemision_id': fields.many2one('fiscal.puntoemision','Punto Emision',)
		}
    
    _defaults={'manual':True}
    
    def onchange_puntoemision_id(self, cr, uid, ids, puntoemision_id):
        result = {}
        if puntoemision_id:
            p = self.pool.get('fiscal.puntoemision').browse(cr, uid, puntoemision_id)
            
            result['value']= {
                        'tipodocumento_id' : p.tipodocumento_id.id,
                        'tipocomprobante' : p.tipodocumento_id.codigofiscal,
                        'autorizacion' : p.Numautorizacion,
                        'puntoemision' : p.puntoemision,
                        'establecimiento' : p.establecimiento,
                     }
                
        return result
    
    def onchange_tipodocumento_id(self, cr, uid, ids, tipodocumento_id):
        result = {}
        if tipodocumento_id:
            p = self.pool.get('fiscal.tipodocumento').browse(cr, uid, tipodocumento_id)
            
            result['value']= {
                        'tipocomprobante' : p.codigofiscal,
                     }
                
        return result
    
    def onchange_secuencial(self, cr, uid, ids, puntoemision_id, secuencialinicio,secuencialfin):
        result = {}
        if not puntoemision_id:
            return result
        
        p = self.pool.get('fiscal.puntoemision').browse(cr, uid, puntoemision_id)
        desde = int(p.secuenciaInicial)
        hasta = int(p.secuenciaFinal)
        
        if secuencialinicio:
            mensaje=''
            if not re.match('\d{9}',secuencialinicio):
                mensaje = 'Secuencial Desde, debe contener solo números y en total 9 dígitos.'
            elif(int(secuencialinicio)<desde or int(secuencialinicio)>hasta):
                mensaje = 'Secuencial Desde debe estar dentro del rango: ['+str(desde)+','+str(hasta)+']'
                
            if mensaje:
                result.update({
                               'value' : {
                                          'secuencialinicio':''
                                          },
                               'warning': {
                                           'title': 'Error',
                                           'message': mensaje,
                                           }
                               })
                return result
        if secuencialfin:
            mensaje=''
            if not re.match('\d{9}',secuencialfin):
                mensaje = 'Secuencial Hasta, debe contener solo números y en total 9 dígitos.'
            elif int(secuencialfin)<desde or int(secuencialfin)>hasta:
                mensaje = 'Secuencial Hasta debe estar dentro del rango: ['+str(desde)+','+str(hasta)+']'
                
            if mensaje:
                result.update({
                           'value' : {
                                      'secuencialfin':''
                                      },
                           'warning': {
                                       'title': 'Error',
                                       'message': mensaje
                                       }
                           })
                return result
        if secuencialinicio and secuencialfin:
            secuencialinicio = int(secuencialinicio)
            secuencialfin = int(secuencialfin)
            if(secuencialinicio>secuencialfin):
                    result.update({
                               'value' : {
                                          'secuencialinicio':'',
                                          'secuencialfin':''
                                          },
                               'warning': {
                                           'title': 'Error',
                                           'message': 'Secuencial Desde debe ser mayor que Secuencial Hasta',
                                           }
                               })
                
        return result
    
    def toxml(self,listaanulados):        
        doc = minidom.Document()
        anulados = doc.createElement('anulados')
        doc.appendChild(anulados)
        for anulado in listaanulados:
            detalle = doc.createElement('detalleAnulados')
            anulados.appendChild(detalle)
            
            node = doc.createElement('tipoComprobante')
            detalle.appendChild(node)
            txt = doc.createTextNode(anulado.tipocomprobante)
            node.appendChild(txt)
            
            node = doc.createElement('establecimiento')
            detalle.appendChild(node)
            txt = doc.createTextNode(anulado.establecimiento)
            node.appendChild(txt)
            
            node = doc.createElement('puntoEmision')
            detalle.appendChild(node)
            txt = doc.createTextNode(anulado.puntoemision)
            node.appendChild(txt)
            
            node = doc.createElement('secuencialInicio')
            detalle.appendChild(node)
            txt = doc.createTextNode(anulado.secuencialinicio)
            node.appendChild(txt)
            
            node = doc.createElement('secuencialFin')
            detalle.appendChild(node)
            txt = doc.createTextNode(anulado.secuencialfin)
            node.appendChild(txt)
            
            node = doc.createElement('autorizacion')
            detalle.appendChild(node)
            txt = doc.createTextNode(anulado.autorizacion)
            node.appendChild(txt)
            
        return anulados

       
fiscal_comprobantesanulados()