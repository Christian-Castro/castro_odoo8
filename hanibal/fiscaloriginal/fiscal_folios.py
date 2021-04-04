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


class fiscal_folios(osv.osv):

	_name = 'fiscal.folios'
	_columns = {	'name' : fields.char('Nombre',size=100, required=True),

			'fechavalidezinicio' : fields.date('Inicio', required=True),
			'fechavalidezfinal' : fields.date('Fin', required=True),

			'numautorizacion' : fields.char('Autorizacion',size=50, required=True),

			'puntoemision' : fields.char('P Emision',size=3, required=True),
			'establecimiento' : fields.char('Establecimiento',size=3, required=True),
			'secuenciaInicial' : fields.char('Sec. Inicial',size=50, required=True),
			'secuenciaFinal' : fields.char('Sec. Final',size=50, required=True),
			'secuenciaActual' : fields.char('Sec. Actual',size=50, required=True),
			'habilitado' : fields.boolean('Habilitado', required=True),
			'numeAutImp' : fields.char('Num. Aut. Imprenta',size=50, required=True),
			#'tipodocumento_id':fields.many2one('fiscal.tipodocumento', 'Tipo Documento',required=True),
			'tipopuntoemision': fields.selection([('felectronico','Electronico'),('preimpreso','PreImpreso'),('autoimpresor','Autoimpresor')],'Tratamiento',required=True,readonly=False),


		}

	_defaults = {	
			'habilitado' : True,
			
		}
	
fiscal_folios()

