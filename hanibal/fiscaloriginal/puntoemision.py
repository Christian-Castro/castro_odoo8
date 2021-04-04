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

class fiscal_puntoemision(osv.osv):

	_name = 'fiscal.puntoemision'
	_columns = {
			# 'id' : fields.char('Codigo Interno',size=128, required=True),
			'name' : fields.char('Nombre',size=100, required=True),

			'fechacreacion' : fields.date('Fecha de Creacion', required=True),
			'fechainicio' : fields.date('Fecha Inicio', required=True),
			'fechafinal' : fields.date('Fecha Final', required=True),

			'Numautorizacion' : fields.char('Autorizacion Numero',size=50, required=True),

			'puntoemision' : fields.char('Punto Emision',size=3, required=True),
			'establecimiento' : fields.char('Establecimiento',size=3, required=True),
			'secuenciaInicial' : fields.char('Sec. Inicial',size=50, required=True),
			'secuenciaFinal' : fields.char('Sec. Final',size=50, required=True),
			'secuenciaActual' : fields.char('Sec. Actual',size=50, required=True),
			'habilitado' : fields.boolean('habilitado', required=True),
			'numeAutImp' : fields.char('Num. Aut. Imprenta',size=50, required=True),
			'tipodocumento_id':fields.many2one('fiscal.tipodocumento', 'Tipo Documento',required=True),
			#AA
			'tipopuntoemision': fields.selection([('felectronico','Electronico'),('preimpreso','PreImpreso'),('autoimpresor','Autoimpresor')],'Tratamiento',required=True,readonly=False),
		}

	_defaults = {	
			'habilitado' : True,
			#'fechacreacion': lambda *a: time.strftime('%Y-%m-%d'),
		}
	
fiscal_puntoemision()

class fiscal_tipodocumento(osv.osv):
	
	_name = 'fiscal.tipodocumento'
	_description = 'Tipos de Documentos Fi_scal'

	_columns = {
		'codigointerno':fields.char('Codigo Interno', 3, required=True),
		'name':fields.char('Nombre', 100, required=True),
		'fechacreacion': fields.date('Fecha Creacion', required=True),
		'codigofiscal': fields.char('Codigo Fiscal', 10, required=True),
		'habilitado' : fields.boolean('habilitado', required=True),
		'puntoemision_ids':fields.one2many('fiscal.puntoemision', 'tipodocumento_id', 'Punto Emision', required=False),
		'esretencion' : fields.boolean('Es o no Retencion', reqired=True),
		'porcentajeretencion': fields.float('porcentajeretencion'),
		'diasgraciarecepcion': fields.float('Dias de gracia de Recepcion'),
		'tipo': fields.selection([('iva','IVA'),('fte','FUENTE')],'Tipo'),
		#Folios
		'folios_id':fields.many2one('folios.configuracion','Tipo Documento',ondelete='cascade')
	}
	
	_defaults={
               'habilitado':True,
               }
	
fiscal_tipodocumento()

class fiscal_sustentotributario(osv.osv):

	_name = 'fiscal.sustentotributario'
	_description = 'Sustento Tributario'

	_columns = {
        'codigofiscal':fields.char('Codigo SRI', 3, required=True),
        'name':fields.char('Nombre', 100, required=True),
	    'habilitado' : fields.boolean('habilitado', required=True),
	    #Folios
	    'folios_id':fields.many2one('folios.configuracion','Sustento tributario',ondelete='cascade')
    }

	_defaults={
               'habilitado':True,
               }
	
fiscal_sustentotributario()
