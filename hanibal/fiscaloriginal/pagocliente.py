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
import openerp.addons.decimal_precision as dp
from report.amount_to_text_ec import amount_to_text_ec
from openerp.tools.amount_to_text_en import amount_to_text

class account_voucher(osv.osv):
    _name = 'account.voucher'
    _inherit = 'account.voucher'
       
    _columns = {
        'puntoemision_id':fields.many2one('fiscal.puntoemision','Punto de Emision'),
		'tipodocumento_id': fields.related( 'journal_id','tipodocumento_id',type="many2one",relation="fiscal.tipodocumento",string="Tipo de Documento",store=False),
		'Numautorizacion' : fields.char('Autorizacion Numero',size=50, requiered=True),
		'puntoemision' : fields.char('Punto Emision',size=3, requiered=True),
		'establecimiento' : fields.char('Establecimiento',size=3, requiered=True),
		'secuencial' : fields.char('Secuencial',size=50, requiered=True),
		'numeAutImp' : fields.char('Aut. Imprenta',size=50, requiered=True),

		'vencautorizacion': fields.date('Fecha de Vencimiento de Retencion'),
		'esretencion' : fields.related('tipodocumento_id','esretencion',type='boolean',string='Es retencion', required=False),
        'porcentajeretencion': fields.float('porcentajeretencion'),
		'codigofiscal': fields.char('Codigo Fiscal', 10),
        
        'tiporet' : fields.selection([('iva','IVA'),('fte','Fuente')],'Tipo Retención'),
        'account_id2':fields.many2one('account.account', 'Account', ),
        'account_id3':fields.integer('Account', ),
	}

    _defaults = {	
			'esretencion' : False,
		}

    def check_validaretencion(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
	       if voucher.journal_id.tipodocumento_id != '':
	    		if voucher.journal_id.tipodocumento_id.esretencion :
    				if not voucher.puntoemision or not voucher.establecimiento or not voucher.secuencial or not voucher.Numautorizacion or not voucher.vencautorizacion or not voucher.numeAutImp:
    					return False
        return True   

    def check_validalongitudNumautorizacion(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
    	    if voucher.journal_id.tipodocumento_id != '':
    	    	if voucher.journal_id.tipodocumento_id.esretencion :
    				if voucher.Numautorizacion and len(voucher.Numautorizacion) != 10 :
    					return False
        return True 

    def check_validalongitudnumeAutImp(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
    	    if voucher.journal_id.tipodocumento_id != '':
    	    	if voucher.journal_id.tipodocumento_id.esretencion :
    				if voucher.numeAutImp and len(voucher.numeAutImp) != 4 :
    					return False
        return True   

    def check_validalongitudestablecimiento(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
	       if voucher.journal_id.tipodocumento_id != '':
	           if voucher.journal_id.tipodocumento_id.esretencion :
			     if voucher.establecimiento and len(voucher.establecimiento) != 3 :
					return False
        return True   

    def check_validalongitudpuntoemision(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.journal_id.tipodocumento_id != '':
               if voucher.journal_id.tipodocumento_id.esretencion :
                   if voucher.puntoemision and len(voucher.puntoemision) != 3 :
					return False
        return True   

    def check_validalongitudsecuencial(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.journal_id.tipodocumento_id != '':
                if voucher.journal_id.tipodocumento_id.esretencion :
                    if voucher.secuencial and len(voucher.secuencial) != 9 :   
                        return False
        return True   


    def check_validavencautorizacion(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.journal_id.tipodocumento_id != '':
                if voucher.journal_id.tipodocumento_id.esretencion :
                    if voucher.date <= voucher.vencautorizacion:
    					# self.pool.get('account.voucher').write(cr, uid, voucher.id, {'esretencion':True}, context)
    					return True
        return True 

    def check_actualizainformacion (self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.journal_id.tipodocumento_id != '':
                if voucher.journal_id.tipodocumento_id.esretencion :
                #	self.pool.get('account.voucher').write(cr, uid, voucher.id, {'esretencion':True}, context)
                    return True
			#else:
			#	self.pool.get('account.voucher').write(cr, uid, voucher.id, {'esretencion':False}, context)

        return True 

    def on_change_puntoemision_id(self,cr,uid,ids,puntoemision_id=False,context=None):
        result={}
        if puntoemision_id:
            puntoemision_obj = self.pool.get('fiscal.puntoemision').browse(cr,uid,puntoemision_id,context=context)
            tipodocumento_id = puntoemision_obj.tipodocumento_id

            result= {'value':{
                                'porcentajeretencion' : tipodocumento_id.porcentajeretencion,
                                'codigofiscal'           : tipodocumento_id.codigofiscal,
                                'tipodocumento_id'    : tipodocumento_id.id,


                            }            
                    }
        return result
    
    def onchange_journal2(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        result = super(account_voucher,self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)
        j=False
        if journal_id:
            j = self.pool.get('account.journal').browse(cr,uid,journal_id)

        result2 = {
                     'esretencion': j and j.tipodocumento_id and j.tipodocumento_id.esretencion or False,
                   }
        if result:
            result['value'].update(result2)
        
        return result
            
  
    _constraints = [
                (check_validaretencion,'Informacion incompleta para el registro de retencion.', ['Pago Retencion']),
                (check_validalongitudNumautorizacion,'El numero de autorizacion debe ser de 10 caracteres.', ['Numautorizacion']),
                (check_validalongitudnumeAutImp,'El Num Aut Imprenta debe ser de 4 caracteres.', ['Aut. Imprenta']),
                (check_validalongitudestablecimiento,'El establecimiento debe ser 3 caracteres.', ['Establecimiento']),
                (check_validalongitudpuntoemision,'El punto de emision debe ser 3 caracteres.', ['Punto Emision']),
                (check_validalongitudsecuencial,'El secuencial debe ser 9 caracteres.', ['Secuencial']),
                (check_validavencautorizacion,'Retencion con Fecha Caducada.', ['vencautorizacion']),
                (check_actualizainformacion,'', ['None']),
            ]
    
    
    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        
        """ Inherited - add amount_in_word and allow_check_writting in returned value dictionary """
         
        if not context:
            context = {}
        default = super(account_voucher, self).onchange_amount(cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=context)
        if 'value' in default:
            amount = 'amount' in default['value'] and default['value']['amount'] or amount
             
            lang = context.get('lang')
            amount_in_word = ''
            if(lang and len(lang)>=2 and lang[:2]=='es'):
                amount_in_word = amount_to_text_ec().amount_to_text_cheque(amount,'','')
            else:
                amount_in_word = amount_to_text(amount)
                 
            default['value'].update({'amount_in_word':amount_in_word})
            if journal_id:
                allow_check_writing = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context).allow_check_writing
                default['value'].update({'allow_check':allow_check_writing})
                 
        return default
    
    def setaprobadopor(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'aprobadopor':uid})
        return True
account_voucher()