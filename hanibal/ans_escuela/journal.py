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

class account_journal(osv.osv):
    _name = 'account.journal'
    _inherit = 'account.journal'
    
    _columns = {
        ##'tipodocumento_id':fields.many2one('fiscal.tipodocumento','Tipo de Documento'),
        ##'tipodocumentosri_id':fields.many2one('fiscal.tipodocumento','Tipo de Documento'),
        'dist_analitica' : fields. boolean('Distribución Analítica'),
        'categoria_reporte' : fields.selection([('efe','Efectivo'),
                                                ('ch','Cheque'),
                                                ('tc','Tarjeta de Crédito'),
                                                ('dep','Depósito Bancario'),
                                                ('trans','Transferencia Bancaria'),
                                                ('nc','Nota de Crédito'),
                                                ('rti','Retencion iva'),
                                                ('rtf','Retencion fuente'),
                                                 ('liq','Liquidación')
                                                ],'Categoria Reporte de Caja')
	}
    
    _defaults = {
        'dist_analitica': False
                 }

account_journal()