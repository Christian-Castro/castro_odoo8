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

import time
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import re
from openerp.tools.translate import _
from openerp.exceptions import except_orm,Warning
from openerp import api,tools

#===============================================================================
# class ir_model_data(osv.osv):
#     _name = 'ir.model.data'
#     _inherit = 'ir.model.data'
#     
#     @tools.ormcache(skiparg=3)
#     def xmlid_lookup(self, cr, uid, xmlid):
#         """Low level xmlid lookup
#         Return (id, res_model, res_id) or raise ValueError if not found
#         """
#         module, name = xmlid.split('.', 1)    
#         if str(module) == str('fiscal'):
#             cr.execute("select * from ir_model_data where name = 'retencion_preimpreso' and module = 'fiscal'")
#             res = cr.dictfetchall()
#             if len(res) > 0 :
#                 pass
#             else:
#                 if str(name) == str('retencion_preimpreso'):
#                     cr.execute("""INSERT INTO ir_model_data(            id,  name, module, model, res_id)
#                                VALUES ((select (max(id)::int + 10000000) from ir_model_data)  ,'retencion_preimpreso'
#                                ,'fiscal', 'ir.module.module', (select (max(res_id)::int + 1) from ir_model_data) );""")
#                             
#         ids = self.search(cr, uid, [('module','=',module), ('name','=', name)])
#         if not ids:
#             raise ValueError('External ID not found in the system: %s' % (xmlid))
#         # the sql constraints ensure us we have only one result
#         res = self.read(cr, uid, ids[0], ['model', 'res_id'])
#         if not res['res_id']:
#             raise ValueError('External ID not found in the system: %s' % (xmlid))
#         return ids[0], res['model'], res['res_id']
#     
# ir_model_data()
#===============================================================================

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        #self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        for line in self.tax_line:
            #print 'si hay self.tax_line',self.tax_line
            if line.amount >= 0:
                #print 'si tiene line.amount',line.amount
                self.amount_tax += line.amount
            else: 
                print 'NOOOOO  tiene line.amount'
        for line in self.tax_line:
            # anibal if line.amount > 0:
            if line.amount >= 0:
                self.amount_untaxed += line.base
                #print 'entre a self.amount_untaxed += line.base  ', self.tax_line
       # print '************************* antes de cambiar las catnidades en fiscal*************', self.amount_tax
       # print '************************* antes de cambiar las catnidades en fiscal*************',self.amount_total
       # print '************************* antes de cambiar las catnidades en fiscal*************',line.amount
      #  print '************************* antes de cambiar las catnidades en fiscal*************',self.amount_untaxed
      #  print '************************* antes de cambiar las catnidades en fiscal*************'
      #  print '************************* antes de cambiar las catnidades en fiscal*************'
        self.amount_total = self.amount_untaxed + self.amount_tax
      #  print '************************* desp de cambiar las catnidades en fiscal*************',self.amount_total
      #  print '************************* 2 de cambiar las catnidades en fiscal*************',line.amount
      #  print '************************* 2 de cambiar las catnidades en fiscal*************',self.amount_untaxed
      #  print '************************* 2 de cambiar las catnidades en fiscal*************'
      #  print '************************* 2 de cambiar las catnidades en fiscal*************'
      #  print '************************* 2 de cambiar las catnidades en fiscal*************'
    
    # antes que byron cambie lo de los subtotales 
    # def calculando(self, cr, uid, ids, name, args, context={}):

      #  res = {}
      #  for invoice in self.browse(cr, uid, ids, context=context):
      #      res[invoice.id] = {
      #          'amount_untaxed': 0.0,
      #          'amount_tax': 0.0,
      #          'amount_total': 0.0,
      #          'baseivacero' : 0.0,
      #          'baseivanocero' : 0.0,
      #          'baseninguniva': 0.0,
      #          'totalretencion': 0.0,
      #          'total': 0.0,
      #          'descuento': 0.0,
      #          'iva':0.0,
      #      }
      #      for line in invoice.invoice_line:
      #          #===============================================================
      #          # for tax in line.invoice_line_tax_id:
      #          #     if tax.type == 'none':
      #          #         res[invoice.id]['baseninguniva'] += line.price_subtotal
      #          #     if str(tax.amount) == '0.12':
      #          #         res[invoice.id]['baseivanocero'] += line.price_subtotal
      #          #     if str(tax.amount) == '0.0':
      #          #         res[invoice.id]['baseivacero'] += line.price_subtotal 
      #          #===============================================================
            
      #          res[invoice.id]['total'] += line.total
      #          #res[invoice.id]['descuento'] += line.descuento
      #          #res[invoice.id]['amount_untaxed'] += line.price_subtotal
      #          #res[invoice.id]['iva'] += line.valor_iva
      #      for line in invoice.tax_line:
      #          if line.amount > 0:
      #              res[invoice.id]['amount_tax'] += line.amount
      #      for line in invoice.tax_line:
      #          if line.amount > 0:
      #              res[invoice.id]['baseivanocero'] += line.base
      #          if line.amount == 0:
      #              res[invoice.id]['baseivacero'] += line.base
      #          if line.amount < 0:
      #              res[invoice.id]['descuento'] += line.amount
      #          

      #      for line in invoice.retencion_line:
      #          res[invoice.id]['totalretencion'] += line.amount
            
      #      res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']

      #  return res


    def calculando(self, cr, uid, ids, name, args, context={}):

        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'baseivacero' : 0.0,
                'baseivanocero' : 0.0,
                'baseninguniva': 0.0,
                'totalretencion': 0.0,
                'total': 0.0,
                'descuento': 0.0,
                'iva':0.0,
            }
            # CAMBIO U1 18-02-2020
            for line in invoice.invoice_line:
                for tax in line.invoice_line_tax_id:
                    if tax.type == 'none':
                        res[invoice.id]['baseninguniva'] += line.price_subtotal
                    if str(tax.amount) == '0.12':
                        res[invoice.id]['baseivanocero'] += line.price_subtotal
                    if str(tax.amount) == '0.0':
                        res[invoice.id]['baseivacero'] += line.price_subtotal 
            
                res[invoice.id]['total'] += line.total
                #res[invoice.id]['descuento'] += line.descuento
                #res[invoice.id]['amount_untaxed'] += line.price_subtotal
                #res[invoice.id]['iva'] += line.valor_iva
            for line in invoice.tax_line:
                if line.amount > 0:
                    res[invoice.id]['amount_tax'] += line.amount
            for line in invoice.tax_line:
                #------------------------------------------- if line.amount > 0:
                    #------------- res[invoice.id]['baseivanocero'] += line.base
                #------------------------------------------ if line.amount == 0:
                    #--------------- res[invoice.id]['baseivacero'] += line.base
                if line.amount < 0:
                    res[invoice.id]['descuento'] += line.amount
            # CAMBIO U1 18-02-2020    

            for line in invoice.retencion_line:
                res[invoice.id]['totalretencion'] += line.amount
            
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']

        return res



    
    def _get_invoice_line(self, cr, uid, ids, context={}):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context={}):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()
    
    def calcularnumerofac(self,cr,uid,ids,field_name,arg,context={}):
        facturas = self.browse(cr,uid,ids,context=context)
        
        res={}
        for invoice_obj in facturas:
            estab = ptoemi = sec = False 
            if invoice_obj.type == 'in_invoice':
                estab = invoice_obj.establecimientoprov 
                ptoemi = invoice_obj.puntoemisionprov 
                sec = invoice_obj.secuencialprov
            elif invoice_obj.type == 'out_invoice':
                estab = invoice_obj.establecimiento
                ptoemi = invoice_obj.puntoemision
                ## anibal sec = invoice_obj.secuencial
               ## anibal para que no de secuencial sec = str(int(invoice_obj.secuencial) + 1).zfill(9)


                
            num = ''    
            if estab and ptoemi and sec:
                num = estab +'-'+ ptoemi +'-'+ sec
                            
            res[invoice_obj.id] = num
            
        return res;   
    

    def calcularnumerofac_2(self,cr,uid,ids,field_name,arg,context={}):## creado por anibal
        facturas = self.browse(cr,uid,ids,context=context)
        
        res={}
        for invoice_obj in facturas:
            estab = ptoemi = sec = False 
            if invoice_obj.type == 'out_invoice':
                estab = invoice_obj.establecimiento
                ptoemi = invoice_obj.puntoemision
                ## anibal sec = invoice_obj.secuencial
               ## anibal para que no de secuencial sec = str(int(invoice_obj.secuencial) + 1).zfill(9)


                
            num = ''    
            if estab and ptoemi and sec:
                num = estab +'-'+ ptoemi +'-'+ sec
                            
            res[invoice_obj.id] = num
            
        return res;  





    
    def calcularSecuencial(self,factura):
        #print 'calcular secuencialxxs'
        #print str(factura.type)
        res = {}
        if factura.state in ('open','paid','cancel','proforma','proforma2'):
            return res
        res={
          'numeAutImp': '0',
          'Numautorizacion': '0',
          'puntoemision': '0', 
          'establecimiento': '0', 
          'secuencial': '0',
          'numeroret' : '000-000-0',
         }
              
        if factura.journal_id and factura.journal_id.tipodocumento_id:
            if factura.puntoemision_id:
                if str(factura.type) == 'in_invoice':
                    if factura.retencion_line and len(factura.retencion_line)>0:
                        if self._sumar_retenciones(factura.retencion_line)>0:
                                ptoemi = factura.puntoemision_id
                                res['numeAutImp'] = str(ptoemi.numeAutImp)
                                res['Numautorizacion'] = str(ptoemi.Numautorizacion)
                                res['puntoemision'] = str(ptoemi.puntoemision)
                                res['establecimiento'] = str(ptoemi.establecimiento)
                                res['secuencial'] = str(int(ptoemi.secuenciaActual) + 1).zfill(9)
                                res['numeroret'] = str(ptoemi.establecimiento)+'-'+str(ptoemi.puntoemision)+'-'+str(int(ptoemi.secuenciaActual) + 1).zfill(9)
                        else:
                            res={
                              'numeAutImp': '00000',
                              'Numautorizacion': '00000',
                              'puntoemision': '000', 
                              'establecimiento': '000', 
                              'secuencial': '0',
                              'numeroret' : '000-000-0',
                             }
                    else:
                        res={
                          'numeAutImp': '00000',
                          'Numautorizacion': '00000',
                          'puntoemision': '000', 
                          'establecimiento': '000', 
                          'secuencial': '0',
                          'numeroret' : '000-000-0',
                         }
                if str(factura.type) == 'out_invoice' or str(factura.type) == 'out_refund':
                    ptoemi = factura.puntoemision_id
                    res['numeAutImp'] = str(ptoemi.numeAutImp)
                    res['Numautorizacion'] = str(ptoemi.Numautorizacion)
                    res['puntoemision'] = str(ptoemi.puntoemision)
                    res['establecimiento'] = str(ptoemi.establecimiento)
                    ## anibal
                    #print 'voy a presentar el secuencial es ceri???  '
                    #print res['secuencial']
                    #print 'ya presente el secuencial inicial'

                    ## anibal
                    res['secuencial'] = str(int(ptoemi.secuenciaActual) + 1).zfill(9)
                    #print 'voy a presentar el secuencial NUEVO OOOOOO   '
                    #print res['secuencial']
                    #print 'ya presente el secuencial NUEVOOOO'
                    ## anibal

		    if str(ptoemi.establecimiento) and str(ptoemi.puntoemision) and res['secuencial']: #coja el secuancial  anibal
		        num = str(ptoemi.establecimiento) +'-'+ str(ptoemi.puntoemision) +'-'+ res['secuencial']
                        #print 'mira num ', num 
                            

	            num = str(ptoemi.establecimiento) +'-'+ str(ptoemi.puntoemision) +'-'+ res['secuencial']
                    #print 'mira num2 ', num 
                            
                    res['numerofac'] = num
                    res['numeroret'] = None
                     
            else:
                res={
                  'numeAutImp': None,
                  'Numautorizacion': None,
                  'puntoemision': None, 
                  'establecimiento': None, 
                  'secuencial': None,
                  'numeroret' : None,
                 }
        else:
            res={
              'numeAutImp': None,
              'Numautorizacion': None,
              'puntoemision': None,
              'establecimiento': None,
              'secuencial': None,
              'numeroret' : None,
             }
     
        return res;
    
    
   
    
    def _periodo(self, cr, uid, ids, context={}):
        
        fecha = time.strftime('%Y-%m-%d')   
        period_pool = self.pool.get('account.period')
        pids = period_pool.find(cr, uid, fecha, context=None)
        return pids[0]
    
    _columns = {        
        'tipodocumento_id': fields.related( 'puntoemision_id','tipodocumento_id',type="many2one",relation="fiscal.tipodocumento",string="Tipo de Documento",store=True),
        'puntoemision_id':fields.many2one('fiscal.puntoemision','Punto de Emision', required=True,states={'open':[('readonly',True)],'paid':[('readonly',True)]},),
        
        
        'numeAutImp': fields.char('Num Aut Imprenta'),
        'Numautorizacion': fields.char('Autorizacion'),
        'puntoemision': fields.char('Punto de emision'),
        'establecimiento': fields.char('Establecimiento'),
        'secuencial': fields.char('Secuencial'),
        'numeroret': fields.char('Retención'),
         
                
        'sustentotributario_id': fields.many2one('fiscal.sustentotributario','Sustento Tributario'),
        
    
        'num_autfac': fields.char('Numero de Autorizacion de Factura',size=10),	
        'venc_autfac': fields.date('Fecha de validez'),
        'num_autimpfac': fields.char('Numero de autorizacion de imprenta',5),
        
        'baseivacero': fields.function(calculando,digits_compute=dp.get_precision('Account'),store=True ,string='Base Iva Cero', multi='all'),
        'baseivanocero': fields.function(calculando,digits_compute=dp.get_precision('Account'),store=True, string='Base Iva No Cero', multi='all'),
        'baseninguniva': fields.function(calculando,digits_compute=dp.get_precision('Account'),store=True, string='Base Ningun 12',multi='all'),
        'total': fields.function(calculando,digits_compute=dp.get_precision('Account'),store=True, string='Total', multi='all'),
        'descuento': fields.function(calculando,digits_compute=dp.get_precision('Account'),store=True, string='Descuento',    multi='all'),
        'iva': fields.function(calculando,digits_compute=dp.get_precision('Account'),store=True, string='IVA', multi='all'),
        'totalretencion': fields.function(calculando,digits_compute=dp.get_precision('Account'), string='Retencion',store=True, multi='all'),


        'retencion_line': fields.one2many('fiscal.retencion.ln', 'invoice_id', 'Detalle de Retenciones', readonly=True, states={'draft':[('readonly',False)]}),

        'fiscal_position': fields.related('partner_id', 'property_account_position', type='many2one', relation='account.fiscal.position', string='Posicion Fiscal', readonly=True, store=True, states={'draft':[('readonly',True)]}),
        
        'puntoemisionprov': fields.char('Punto de Emision', size=3),
        'establecimientoprov': fields.char('Establecimiento', size=3),
        'secuencialprov': fields.char('Secuencial', size=9),
        'numerofac': fields.char('Comprobante', size=17),   # anibal fields.function(calcularnumerofac, string='Comprobante', type='char',size=50, store=True),
        'numeroret': fields.char('Retención'),
        'write_uid' : fields.many2one('res.users','Autorizado',readonly=True),
        #        segunda parte Fiscal-PAGOS
        'fiscal_invoice_pagos_line':fields.one2many('fiscal.invoice.fpagos','invoice_ids','Pagos'),
        'fiscaltipopago_id':fields.many2one('fiscal.tipopago','Tipo de Pago'),
        'pais_id':fields.many2one('res.country','Pais'),
        'dobletributacion': fields.selection([('SI','SI'),('NO','NO'),('NA','NA'),],select=True,string="Doble Tributacion"),
        'retenciondobletributacion': fields.selection([('SI','SI'),('NO','NO'),('NA','NA'),],select=True,string="Retencion Tributaria"),
        'fiscal_option':fields.boolean('Bandera'),
        
        'parte_relacionada':fields.selection([('SI','SI'),('NO','NO')],select=True,string="Parte relacionada"),
        'reembolsos_id': fields.one2many('facturas.reembolsos','invoice_id','Comprobante de Reembolso'),
        
        #=======================================================================
        # 'partner_r_id':fields.many2one('res.partner','Alumno'),
        # 'seccion_id':fields.many2one('seccion','Sección'),
        # 'curso_id':fields.many2one('curso','Curso'),
        # 'paralelo_id':fields.many2one('paralelo','Paralelo'),
        #=======================================================================
        
        #===================================================================
        # ACTUALIZADO 19-ENE-2020
        # BF
        #===================================================================
        "invoice_id":fields.many2one("factura.electronica","Factura Electrónica"),
	}
    
    _defaults={
       'dobletributacion':None,
       'retenciondobletributacion':None,
       'parte_relacionada':'NO',
       'date_invoice': lambda *a: time.strftime('%Y-%m-%d'),
       'period_id':_periodo,
    }
    
# ojo solo se comenta para poder trabajar    
    def _formas_pago(self,cr,uid,ids,context=None):
        #print 'enteeeeeeeeeeeeeeeeeeeeeee a formas de pago'
        identi_brw = self.browse(cr,uid,ids,context)
       ## print identi_brw
        for t in identi_brw:
            if t.amount_total:
               #print  '**************CANTIDAD TOTAL ***********************'
               #print t.amount_total
               #print  '**************CANTIDAD FINAL ***********************'
               if t.fiscal_invoice_pagos_line and t.amount_total < 1000 and (t.type == 'in_invoice' or t.type == 'out_invoice' ):
                    #raise osv.except_osv('Error!','No Puede Defirnir Formas de pago a Facturas Menores a 1000 Dolares')
                    return True
                     
               if t.amount_total >= 1000 and not t.fiscal_invoice_pagos_line and (t.type == 'in_invoice' or t.type == 'out_invoice'):
                   # raise osv.except_osv('Error!','Defina Formas de Pago a su Factura')
                   return True;

            return True
        
    _constraints=[
                 (_formas_pago,('Error en Formas de Pago'),['amount_total'] )
                 ]


    #===========================================================================
    # def onchange_alumno(self, cr, uid,ids, alumno_id, context=None):
    #     #TODO : compute new values from the db/system
    #     if alumno_id:
    #         p = self.pool.get('res.partner').browse(cr,uid,alumno_id)
    #         result = {'value': {
    #         'seccion_id': p.seccion_id.id,
    #         'curso_id': p.curso_id.id,
    #         'paralelo_id': p.paralelo_id.id,
    #         }}
    #         return result
    #===========================================================================
        
    def onchange_tipopago_id(self,cr,uid,ids,tipopago=False,context=None):
        result2={}
        if tipopago:
            cliente = self.pool.get('fiscal.tipopago').browse(cr,uid,tipopago)
            if cliente.identificador == '01':
                    result2['value']={
                                   'fiscal_option': False ,
                                   'pais_id':False,
                                   'dobletributacion':'NA',
                                   'retenciondobletributacion':'NA', }  
            if cliente.identificador == '02':
                    result2['value']={
                                   'fiscal_option': True  ,
                                   'dobletributacion':'NO',
                                   'retenciondobletributacion':'NO',  }  
        return result2

    
    def onchange_trubutacion_id(self,cr,uid,ids,dobletributacion=False,context=None):
        result2={}
        if dobletributacion == 'SI':
            result2['value']={
                           'retenciondobletributacion': 'NA' , }
        else:
            result2['value']={
                           'retenciondobletributacion': 'NO' , }  
        return result2
    
    def onchange_cuenta_curso_id(self,cr,uid,ids,curso=False,context=None):
        result2={}
        
        if curso:
            curso_cuenta = self.pool.get('curso').browse(cr,uid,curso)
            if curso_cuenta:
                result2['value']={
                           'account_id': curso_cuenta.account_id.id }
        return result2

    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,date_invoice=False,
                             payment_term=False, partner_bank_id=False, company_id=False,currency_id=False):
        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids,type,partner_id,date_invoice,payment_term,partner_bank_id,company_id,currency_id)
        result2={}
        if partner_id:
            p = self.pool.get('res.partner').browse(cr,uid,partner_id)
            result2= {
                        'num_autfac'    :p.num_autfac,
                        'venc_autfac'   :p.venc_autfac,
                        'num_autimpfac' :p.num_autimpfac,
                     }
        result['value'].update(result2)
        return result
    
    def _validar_preimpreso_factura(self,puntoemision,establecimiento,secuencial):
        if not puntoemision:
            return False
        elif not re.match('\d{3}',puntoemision):
            return False
        elif int(puntoemision) <= 0:
            return False
        elif not establecimiento:
            return False
        elif not re.match('\d{3}',establecimiento):
            return False
        elif int(establecimiento) <= 0:
            return False
        elif not secuencial:
            return False
        elif not re.match('\d{9}',secuencial):
            return False
        elif int(secuencial) <= 0:
            return False
        
        return True
    
    def _sumar_retenciones(self, retenciones):
        suma=0
        for retencion in retenciones:
            suma += retencion.amount<0 and retencion.amount*-1 or retencion.amount
            
        return suma
    
    def _solodigitos(self,texto):
        for t in texto:
            if t not in ('0','1','2','3','4','5','6','7','8','9'):
                return False
        return True   
    
    @api.multi
    def validar_adicionales(self ):
        factura = self

        if not (factura.journal_id and factura.journal_id.tipodocumento_id):
            return True       
        
        if factura.type == 'in_invoice':
            if not factura.num_autfac:
                raise osv.except_osv('Error','El campo Número de Autorización de Factura es requerido.')
            elif not (len(factura.num_autfac)==10 and self._solodigitos(factura.num_autfac)):
                raise osv.except_osv('Error','Campo Número de Autorización de factura debe contener solo números y contener 10 digitos ')
            elif not factura.num_autimpfac:
                raise osv.except_osv('Error','El campo Número de Autorización de Imprenta es requerido.')
            elif not (len(factura.num_autimpfac)>=4 and len(factura.num_autimpfac)<=5 and self._solodigitos(factura.num_autimpfac)):
                raise osv.except_osv('Error','El campo Autorización de Imprenta debe contener solo números entre 4 y 5 dígitos.')
            elif not factura.venc_autfac:
                raise osv.except_osv('Error','El campo Fecha de Validez es obligatorio.')
#             elif factura.date_invoice >= factura.venc_autfac:
#                 raise osv.except_osv('Error','Factura se encuentra con fecha caducada.')  
            elif not factura.sustentotributario_id:
                raise osv.except_osv('Error','El campo Sustento Tributario es requerido.')
        
        return True    
    @api.multi
    def validar_distribucion_analitica(self):
        factura = self

        if not factura.journal_id.dist_analitica:
            return True
        
        for linea in factura.invoice_line:    
            if not linea.analytics_id:
                raise osv.except_osv('Distribución analítica no registrada.','Existen Detalles de Factura que no tienen registrada una distribución analítica.')
        
        return True    
    
    @api.multi
    def is_puntoemision_valido(self):

        invoice_obj = self
        puntoemision_obj = invoice_obj.puntoemision_id
        tipodocumento_obj = invoice_obj.journal_id.tipodocumento_id
        puntoemision = invoice_obj.puntoemisionprov
        establecimiento = invoice_obj.establecimientoprov
        secuencial = invoice_obj.secuencialprov
        
        mensaje = None      
        if tipodocumento_obj:
            if(invoice_obj.type=='in_invoice'):
                #se ha establecido la fecha del comprobante de retencion con la misma fecha de la factura
                fecharetencion = invoice_obj.date_invoice
                retenciones = invoice_obj.retencion_line
                #validando preimpreso de la factura
                if not self._validar_preimpreso_factura(puntoemision,establecimiento,secuencial):
                    mensaje = 'Número de pre-impreso de factura incorrecto.'       
                elif self._existepreimpreso(invoice_obj.partner_id.id,puntoemision,establecimiento,secuencial):
                    mensaje = 'Número de pre-impreso de factura ya se encuentra registrado.'  
                elif not puntoemision_obj:
                    mensaje = 'Punto de emision para Retención es un campo obligatorio.'     
                #validando punto de emision de comprobante de retencion
                #solo mientras existan retenciones aplicadas a la factura
                #y solo si la suma de las retenciones es > 0
                elif len(retenciones)>0:
                    if self._sumar_retenciones(retenciones) > 0:
                        if not puntoemision_obj:
                            mensaje = 'Existen retenciones aplicadas a esta factura, '\
                            'pero no se ha definido un punto de emisión para el comprobante de retención.'
                        elif (fecharetencion < puntoemision_obj.fechainicio) or \
                            (fecharetencion > puntoemision_obj.fechafinal):
                            mensaje = 'Comprobante de retención se encuentra con fecha caducada.'
                        elif (((int(puntoemision_obj.secuenciaActual)+1) > int(puntoemision_obj.secuenciaFinal)) or \
                              ((int(puntoemision_obj.secuenciaActual)+1) < int(puntoemision_obj.secuenciaInicial))):   
                            mensaje = 'Secuencial del Comprobante de retención se encuentra fuera del rango establecido.'
                        elif self._existepuntoemision(invoice_obj.type,puntoemision_obj.puntoemision,puntoemision_obj.establecimiento,int(puntoemision_obj.secuenciaActual)+1):
                            mensaje = 'Comprobante de Retencion '+puntoemision_obj.establecimiento+'-'+puntoemision_obj.puntoemision+'-'+str(int(puntoemision_obj.secuenciaActual)+1).zfill(9)+' ya ha sido registrado para otra Factura.'
            elif(invoice_obj.type=='out_invoice'):                
                if not puntoemision_obj:
                    mensaje = 'Debe seleccionar un punto de emision para la factura.'
                elif (invoice_obj.date_invoice < puntoemision_obj.fechainicio) or (invoice_obj.date_invoice > puntoemision_obj.fechafinal):
                    mensaje = 'Factura se encuentra con fecha caducada.'
                elif (((int(puntoemision_obj.secuenciaActual)+1) > int(puntoemision_obj.secuenciaFinal)) or ((int(puntoemision_obj.secuenciaActual)+1) < int(puntoemision_obj.secuenciaInicial))):
                    mensaje = 'Secuencial de factura esta fuera del rango permitido.'
                elif self._existepuntoemision(invoice_obj.type,puntoemision_obj.puntoemision,puntoemision_obj.establecimiento,int(puntoemision_obj.secuenciaActual)+1):
                    mensaje = 'Factura número '+puntoemision_obj.establecimiento+'-'+puntoemision_obj.puntoemision+'-'+str(int(puntoemision_obj.secuenciaActual)+1)+' ya ha sido registrada para otro cliente.'

            if mensaje:
                raise osv.except_osv('Error',mensaje)
            
        return True
    
    @api.multi
    def _existepuntoemision(self,invoice_type,puntoemision,establecimiento,secuencial):
        query = ''
        if invoice_type in  ('in_invoice','out_invoice'):
            query = """ select i.id
                        from account_invoice as i
                        where i.type = %s
                        and i.state in ('open','paid')
                        and i.establecimiento = %s
                        and i.puntoemision = %s
                        and i.secuencial = %s """
        else:
            raise osv.except_osv("Error", "Tipo de comprobante no soportado.")
            
        self._cr.execute(query,(invoice_type,puntoemision,establecimiento,str(secuencial,).zfill(9)))
        rows = self._cr.fetchall()
        return len(rows)>0
    
    @api.multi
    def _existepreimpreso(self,partner_id,puntoemision,establecimiento,secuencial):
        query = "SELECT i.id " + \
                "FROM account_invoice as i " + \
                "where i.type='in_invoice' " + \
                    "and i.state in ('open','paid') " + \
                    "and i.partner_id = %s " + \
                    "and i.puntoemisionprov = %s " + \
                    "and i.establecimientoprov = %s " + \
                    "and i.secuencialprov = %s "
        self._cr.execute(query,(str(partner_id),puntoemision,establecimiento,secuencial,))
        rows = self._cr.fetchall()
        return len(rows)>0
        
    def on_change_journal_id(self,cr,uid,ids,journal_id=False,context=None):
        result={}
        if journal_id:
            journal_obj = self.pool.get('account.journal').browse(cr,uid,journal_id,context=context)
            tipodocumento_id = journal_obj.tipodocumento_id.id

            if not tipodocumento_id:
                tipodocumento_id=''
            result= {'value':{
                                'tipodocumento_id' : tipodocumento_id                                         
                            }            
                    }
        return result

    def on_change_puntoemision_id(self,cr,uid,ids,puntoemision_id=False,context=None):
        
        result={}
        if puntoemision_id:
            puntoemision_obj = self.pool.get('fiscal.puntoemision').browse(cr,uid,puntoemision_id,context=context)
            
            result= {'value':{
                                'tipodocumento_id': puntoemision_obj.tipodocumento_id.id,
                                'Numautorizacion' : puntoemision_obj.Numautorizacion,
                                'puntoemision'    : puntoemision_obj.puntoemision,
                                'establecimiento' : puntoemision_obj.establecimiento,
                                'secuencial'      : str(int(puntoemision_obj.secuenciaActual)+1).zfill(9),
                                'numeAutImp'      : puntoemision_obj.numeAutImp
                            }            
                    }
        return result
    
    def button_compute2(self, cr, uid, ids, context=None, set_total=False):
        self.button_reset_taxes2(cr, uid, ids, context)
        for inv in self.browse(cr, uid, ids, context=context):
            if set_total:
                self.pool.get('account.invoice').write(cr, uid, [inv.id], {'check_total': inv.amount_total})
        return True
    
    def button_reset_taxes2(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ait_obj = self.pool.get('account.invoice.tax')
        ret_obj = self.pool.get('fiscal.retencion.ln')
        for id in ids:
            inv = self.browse(cr, uid, id, context=ctx)
            
            partner = inv.partner_id
            tipo = inv.type

            cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (id,))
            if tipo == 'in_invoice':
                cr.execute("DELETE FROM fiscal_retencion_ln WHERE invoice_id=%s AND manual is False", (id,))

            if partner.lang:
                ctx.update({'lang': partner.lang})
            for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
                ait_obj.create(cr, uid, taxe)
            
            if tipo == 'in_invoice':
                for ret in ret_obj.compute(cr, uid, id, context=ctx).values():
                    ret_obj.create(cr, uid, ret)
        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=ctx)
        return True
    
    
    @api.multi
    def button_reset_taxes(self):
        
        account_invoice_tax = self.env['account.invoice.tax']
        ret_obj = self.env['fiscal.retencion.ln']
        ctx = dict(self._context)
        for invoice in self:
            if invoice.type=='in_invoice':
                if invoice.journal_id and invoice.journal_id.tipodocumento_id:
                    flag1 = self.validar_adicionales()
                    flag2 = self.validar_distribucion_analitica()
                    flag3 = self.is_puntoemision_valido()
                    if not (flag1 and flag2 and flag3):
                        return False
           ##anibal if invoice.type=='out_invoice':
                ##anibalif invoice.journal_id and invoice.journal_id.tipodocumento_id:
                    ##anibalflag1 = self.validar_punto_emision(invoice.id)
                
                    
            partner = invoice.partner_id
            self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (invoice.id,))
            if str(invoice.type) == str('in_invoice'):
                self._cr.execute("DELETE FROM fiscal_retencion_ln WHERE invoice_id=%s AND manual is False", (invoice.id,))
            self.invalidate_cache()
            partner = invoice.partner_id
            if partner.lang:
                ctx['lang'] = partner.lang
            for taxe in account_invoice_tax.compute(invoice).values():
                account_invoice_tax.create(taxe)

            if str(invoice.type) == str('in_invoice'):
                for ret in ret_obj.compute(invoice).values():
                    #print ret
#                     if ret['tax_amount'] == 0.0 and ret['amount'] == 0.0 and str(invoice.journal_id.tipodocumentosri_id.codigosri).strip() == str('41').strip():
#                         pass
#                     else:
                    ret_obj.create(ret)
        # dummy write on self to trigger recomputations
        return self.with_context(ctx).write({'invoice_line': []})
    
#     def button_reset_taxes(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         ctx = context.copy()
#         ait_obj = self.pool.get('account.invoice.tax')
#         ret_obj = self.pool.get('fiscal.retencion.ln')
#         for id in ids:
#             inv = self.browse(cr, uid, id, context=ctx)
#             
#             if inv.type=='in_invoice':
#                 if inv.journal_id and inv.journal_id.tipodocumento_id:
#                     flag1 = self.validar_adicionales(cr, uid, ids, context)
#                     flag2 = self.validar_distribucion_analitica(cr, uid, ids, context)
#                     flag3 = self.is_puntoemision_valido(cr, uid, ids, context)
#                     
#                     if not (flag1 and flag2 and flag3):
#                         return False
#             
#             partner = inv.partner_id
#             tipo = inv.type
# 
#             cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (id,))
#             if tipo == 'in_invoice':
#                 cr.execute("DELETE FROM fiscal_retencion_ln WHERE invoice_id=%s AND manual is False", (id,))
# 
#             if partner.lang:
#                 ctx.update({'lang': partner.lang})
#             for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
#                 ait_obj.create(cr, uid, taxe)
#             
#             if tipo == 'in_invoice':
#                 for ret in ret_obj.compute(cr, uid, id, context=ctx).values():
#                     ret_obj.create(cr, uid, ret)
#         # Update the stored value (fields.function), so we write to trigger recompute
#         self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=ctx)
#         return True

    def check_retencion_lines(self, cr, uid, inv, compute_taxes, ret_obj):
        if not inv.retencion_line:
            for tax in compute_taxes.values():
                ret_obj.create(cr, uid, tax)
        else:
            tax_key = []
            for tax in inv.retencion_line:
                if tax.manual:
                    continue
                key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id)
                tax_key.append(key)
                if not key in compute_taxes:
                    raise osv.except_osv(_('Warning !'), _('Global taxes defined, but they are not in invoice lines !'))
                base = compute_taxes[key]['base']
                if abs(base - tax.base) > inv.company_id.currency_id.rounding:
                    raise osv.except_osv(_('Warning !'), _('Tax base different!\nClick on compute to update the tax base.'))
            for key in compute_taxes:
                if not key in tax_key:
                    raise osv.except_osv(_('Warning !'), _('Taxes are missing!\nClick on compute button.'))
    
    
    @api.multi
    def period(self,invoice_id):
        
        vh = self.env['account.invoice'].browse(invoice_id)
        if vh.period_id:
            if vh.date_invoice >= vh.period_id.date_start and vh.date_invoice <= vh.period_id.date_stop :   
                return 0
            else:
                return 1
        return 0

    @api.multi
    def action_move_create(self):
        self.button_reset_taxes()
        #print 'dentro de action_move_create*************'
        if self.period(self.id) == 1 :
            raise Warning('¡Error!','Fecha de comprobante no pertenece al periodo declarado')

        """ Creates invoice related analytics and financial move lines """

        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']
        retencion_line = self.env['fiscal.retencion.ln']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                from openerp import fields
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv)
            inv.check_tax_lines(compute_taxes)

            if inv.type == 'in_invoice':
                if not self.numeroret:
                    res = self.calcularSecuencial(inv)
                    ## anibal
                    #print 'tranquilos ya regrese con secuencial = ' ,res
                    inv.write(res)
                    #self.actualiza_secuencial(inv)

            if inv.type == 'out_invoice' or inv.type == 'out_refund':
                    ## anibal
                #print 'voy a calcular secuencial de factura ',self.numerofac
                    ## anibal
                #print 'res = self.calcularSecuencial(inv) '
                if not self.numerofac:
                    res = self.calcularSecuencial(inv)
                    #print 'mira reeeeeeeeeeeeessss ', res
                    inv.write(res)
                    ## pongo esta linea a ver que pasa
                    self.actualiza_secuencial_factura(inv)
                    ## fin de   pongo esta linea a ver que pasa

                #print 'mira dossssssssssssssss ', res
            #if inv.type == 'out_refund':
            #    res = self.calcularsecuencial(inv)
            #    inv.write(res)
            #    self.actualiza_secuencial(inv)

            # I disabled the check_total feature
            if self.env['res.users'].has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type == 'in_invoice':
                iml += retencion_line.move_line_get( inv.id)
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.name or inv.supplier_invoice_number or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False
                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            move = account_move.with_context(ctx).create(move_vals)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()

        self._log_event()
        return True
    
    @api.multi
    def actualiza_secuencial(self,invoice):
        
        if invoice.puntoemision_liq_id: 
            puntoemision_liq = invoice.puntoemision_liq_id
        
            num_b = str(int(invoice.puntoemision_liq_id.secuenciaactual) + 1).zfill(9)
        
            res_b = {
                 'secuenciaactual':num_b
                } 
        
            puntoemision_liq.write(res_b)
        else:
            return True

    @api.multi
    def actualiza_secuencial_factura(self,invoice):
        #print 'entre a actualiza_secuencial_factura'
        if invoice.puntoemision_id: 
            #print  'sientre a actualiza_secuencial_factura'
            puntoemision_id = invoice.puntoemision_id
            #print  'sientre a actualiza_secuencial_factura puntoemision_id',puntoemision_id       
            num_b = str(int(invoice.puntoemision_id.secuenciaActual) + 1)## para que quede el numero .zfill(9)

            #print  'sientre a actualiza_secuencial_factura num_b',num_b        
            res_b = {
                 'secuenciaActual':num_b
                } 
        
            puntoemision_id.write(res_b)
            #print 'termine actualiza_sencuelal factura'
        else:
            return True



    
    def action_puntoemision(self, cr, uid, ids, context=None):
        invoice_obj = self.browse(cr,uid,ids,context=context)[0]
        tipodocumento_obj = invoice_obj.tipodocumento_id 
        #print ' voy a action_puntoemision 1111111111111111 '
        mensaje = None      
        if tipodocumento_obj:
            if(invoice_obj.type=='in_invoice'):
                retenciones = invoice_obj.retencion_line
                if len(retenciones)>0:
                    if self._sumar_retenciones(retenciones) > 0:
                        if invoice_obj.puntoemision_id:
                            num = str(int(invoice_obj.puntoemision_id.secuenciaActual)+1).zfill(9)
                            pto_obj = self.pool.get('fiscal.puntoemision')
                            pto_obj.write(cr, uid, invoice_obj.puntoemision_id.id, {'secuenciaActual':num}, context)
                        else:
                            raise osv.except_osv('Error','Punto de emisión para comprobante de retención debería estar definido.')
            elif(invoice_obj.type=='out_invoice'):   
                    #print ' voy a action_puntoemision 22222222222222 '            
                    if invoice_obj.puntoemision_id:
                        num = str(int(invoice_obj.puntoemision_id.secuenciaActual)+1).zfill(9)
                        pto_obj = self.pool.get('fiscal.puntoemision')
                        pto_obj.write(cr, uid, invoice_obj.puntoemision_id.id, {'secuenciaActual':num}, context)
                    else:
                        raise osv.except_osv('Error','Punto de emisión para factura debería estar definido.')

            if mensaje:
                raise osv.except_osv('Error',mensaje)
            
        return True

#DESDE AKI ES ALGO NUEVO
#     def imprime_factura(self, cr, uid, ids, context=None):
#         """
#     		CON ESTA FUNCION IMPRIMO LA FACTURA DE CLIENTE
#     	"""
#         assert len(ids) == 1, 'This option should only be used for a single id at a time.'
#         self.write(cr, uid, ids, {'sent': True}, context=context)
#         datas = {
#     	     'ids': ids,
#     	     'model': 'account.invoice',
#     	     'form': self.read(cr, uid, ids[0], context=context)
#     	}
#         return {
#     	    'type': 'ir.actions.report.xml',
#     	    'report_name': 'factura.reporte',
#     	    'datas': datas
#       
#     	}

    """def imprime_factura2(self, cr, uid, ids, context=None):
        '''
    		CON ESTA FUNCION IMPRIMO LA FACTURA DE CLIENTE
    	'''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
    	     'ids': ids,
    	     'model': 'account.invoice',
    	     'form': self.read(cr, uid, ids[0], context=context)
    	}
        return {
    	    'type': 'ir.actions.report.xml',
    	    'report_name': 'factura.reporte',
    	    'datas': datas
    
    	}"""


account_invoice()

class account_invoice_tax(osv.osv):
    _name = "account.invoice.tax"
    _inherit = 'account.invoice.tax'
    
    _columns = {
        'esretencion': fields.boolean('Es Retencion'),
    }


    @api.v8
    def compute(self, invoice):
        
        tax_grouped = {}
        """currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))"""
        currency = invoice.currency_id.with_context(date=invoice.date_invoice )
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    #val['account_analytic_id'] = tax['account_analytic_collected_id']
                    val['account_analytic_id'] = False
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    #val['account_analytic_id'] = tax['account_analytic_paid_id']
                    val['account_analytic_id'] = False

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped

account_invoice_tax()

# class account_invoice_tax(osv.osv):
#     _name = "account.invoice.tax"
#     _inherit = 'account.invoice.tax'
# 
#     _columns = {
#         'esretencion': fields.boolean('Es Retencion'),
#     }
# 
#     def compute(self, cr, uid, invoice_id, context=None):
#         tax_grouped = super(account_invoice_tax,self).compute(cr,uid,invoice_id,context)
#         for tax in tax_grouped.values():
#             tmp = {'esretencion':False}
#             tax.update(tmp)        
#         
#         return tax_grouped
#     
# account_invoice_tax()

class account_invoice_line(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
    

    def _amount_iva(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')

        for line in self.browse(cr, uid, ids):
            taxes = line.invoice_line_tax_id
            tmp = []
            for tax in taxes:
                if(tax.amount == 0.12):
                    tmp.append(tax)
            taxes = tmp
            
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, taxes, price, line.quantity, product=line.product_id,  partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total_included'] - taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res
    
    def _amount_bases(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')

        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = line.invoice_line_tax_id
            res[line.id] = {
                'baseiva': 0.0,
                'basecero': 0.0,
                'basenograva': 0.0,                
            }
            for tax in taxes:
                if tax.type == 'none':
                    res[line.id]['baseiva'] = 0  
                    res[line.id]['basecero'] = 0
                    res[line.id]['basenograva'] =  price
                elif tax.amount == 0.12:
                    res[line.id]['baseiva'] =  price
                    res[line.id]['basecero'] = 0
                    res[line.id]['basenograva'] = 0
                elif tax.amount == 0.0:
                    res[line.id]['baseiva'] = 0
                    res[line.id]['basecero'] =  price
                    res[line.id]['basenograva'] = 0 
                else:
                    res[line.id]['baseiva'] = -1 
                    res[line.id]['basecero'] =  -1
                    res[line.id]['basenograva'] = -1
        return res
    
    def _amount_total(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        cur_obj = self.pool.get('res.currency')
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in self.browse(cr, uid, ids):
            price = round(line.price_unit * line.quantity, precision)
            res[line.id] = price
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res
    
    def _amount_descuento(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        cur_obj = self.pool.get('res.currency')
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in self.browse(cr, uid, ids):
            descuento = line.price_unit - line.price_unit * (1-(line.discount or 0.0)/100.0)
            descuento = round(descuento * line.quantity, precision)
            res[line.id] = descuento
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _columns = {
        'retenciones_id': fields.many2many('account.tax', 'fiscal_retencion_ln_tax_relation', 'retencion_line_id', 'tax_id', 'Retenciones Taxes', domain=[('parent_id','=',False)]),
        'valor_iva':fields.function(_amount_iva, string='IVA', type="float",digits_compute=dp.get_precision('Account'), store=True),
        'baseiva':fields.function(_amount_bases, string='Base IVA', type="float", digits_compute= dp.get_precision('Account'), store=True, multi='all'),
        'basecero':fields.function(_amount_bases, string='Base Cero', type="float", digits_compute= dp.get_precision('Account'), store=True, multi='all'),
        'basenograva':fields.function(_amount_bases, string='Base no grava IVA', type="float", digits_compute= dp.get_precision('Account'), store=True, multi='all'),
        'total': fields.function(_amount_total, string='Total', type="float", digits_compute= dp.get_precision('Account'), store=True),
        'descuento': fields.function(_amount_descuento, string='Descuento', type="float", digits_compute= dp.get_precision('Account'), store=True),
    }

    

    def create(self, cr, uid, values, context=None):

        if(values.has_key('invoice_id')):
            values['product_id']        
            producto = self.pool.get('product.product').browse(cr, uid, values['product_id'], context)
            tipo = producto.tipoproducto_id
            reglas = tipo.reglaretencion_id
            
            factura = self.pool.get('account.invoice').browse(cr, uid, values['invoice_id'], context)
            partner = factura.partner_id
            fp = partner.property_account_position
    
            taxes = []
            if(reglas):
                for r in reglas:
                    if(r.posicionfiscal_id == fp):
                        if(r.tax_id.esretencion):
                            taxes.append(r.tax_id.id)
    
            tmp = {'retenciones_id':[(6, 0, taxes)]}
            values.update(tmp)

        return super(account_invoice_line,self).create(cr,uid,values,context)
    
#===============================================================================
#     @api.multi
#     def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
#             partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
#             company_id=None,partner_r_id=False):
#         
#         context = self._context
#         company_id = company_id if company_id is not None else context.get('company_id', False)
#         self = self.with_context(company_id=company_id, force_company=company_id)
#         print '..............................................'
#         print context
#         print partner_id
#         print partner_r_id
#         print fposition_id
#         print '..............................................'
#         if not partner_id:
#             raise except_orm(_('No Partner Defined!'), _("You must first select a partner!"))
#         if not product:
#             if type in ('in_invoice', 'in_refund'):
#                 return {'value': {}, 'domain': {'uos_id': []}}
#             else:
#                 return {'value': {'price_unit': 0.0}, 'domain': {'uos_id': []}}
#         
#         values = {}
# 
#         part = self.env['res.partner'].browse(partner_id)
#         
#         part_r = self.env['res.partner'].browse(context['prt'])
#         
#         fpos = self.env['account.fiscal.position'].browse(fposition_id)
# 
#         if part.lang:
#             self = self.with_context(lang=part.lang)
#         product = self.env['product.product'].browse(product)
# 
#         values['name'] = product.partner_ref
#         if type in ('out_invoice', 'out_refund'):
#             account = product.property_account_income or product.categ_id.property_account_income_categ
#         else:
#             account = product.property_account_expense or product.categ_id.property_account_expense_categ
#         account = fpos.map_account(account)
#         if account:
#             values['account_id'] = account.id
# 
#         if type in ('out_invoice', 'out_refund'):
#             taxes = product.taxes_id or account.tax_ids
#             if product.description_sale:
#                 values['name'] += '\n' + product.description_sale
#         else:
#             taxes = product.supplier_taxes_id or account.tax_ids
#             if product.description_purchase:
#                 values['name'] += '\n' + product.description_purchase
# 
#         fp_taxes = fpos.map_tax(taxes)
#         lst=[]
#         if fp_taxes.ids:
#             lst.append(fp_taxes.ids[0])
#         for l in part_r.descuentos_line:
#             lst.append(l.descuento_id.id)
#     
#         #values['invoice_line_tax_id'] = fp_taxes.ids
#         values['invoice_line_tax_id'] = lst
# 
#         if type in ('in_invoice', 'in_refund'):
#             if price_unit and price_unit != product.standard_price:
#                 values['price_unit'] = price_unit
#             else:
#                 values['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.standard_price, taxes, fp_taxes.ids)
#         else:
#             values['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.lst_price, taxes, fp_taxes.ids)
# 
#         values['uos_id'] = product.uom_id.id
#         if uom_id:
#             uom = self.env['product.uom'].browse(uom_id)
#             if product.uom_id.category_id.id == uom.category_id.id:
#                 values['uos_id'] = uom_id
# 
#         domain = {'uos_id': [('category_id', '=', product.uom_id.category_id.id)]}
# 
#         company = self.env['res.company'].browse(company_id)
#         currency = self.env['res.currency'].browse(currency_id)
# 
#         if company and currency:
#             if company.currency_id != currency:
#                 values['price_unit'] = values['price_unit'] * currency.rate
# 
#             if values['uos_id'] and values['uos_id'] != product.uom_id.id:
#                 values['price_unit'] = self.env['product.uom']._compute_price(
#                     product.uom_id.id, values['price_unit'], values['uos_id'])
# 
#         return {'value': values, 'domain': domain}
#===============================================================================


account_invoice_line()

# se guardaran los pagos
class fiscal_invoice_pagos(osv.osv):
    _name='fiscal.invoice.fpagos'
    _columns={
              
      'invoice_ids':fields.many2one('account.invoice',required=False,ondelete='cascade'),
      'formapago_id':fields.many2one('fiscal.formapago','Formas de pago'),
      'dias':fields.float('Días'),
              
              }

    _defaults={
       'dias':0,
    }
    
fiscal_invoice_pagos()


class facturas_reembolsos(osv.osv):
    
    _name = 'facturas.reembolsos'
    
    _columns={
        
        'invoice_id': fields.many2one('account.invoice','Comprobante de Reembolso',required=False,ondelete='cascade'),
        'tipoid': fields.many2one('fiscal.tipoidentificacion','Tipo Identificación'),
        'partner_id':fields.many2one('res.partner','Proveedor',domain="[('supplier','=',True)]"),
        'identificacion_pro':fields.char('Identificación Proveedor',size=20),
        'tipodocumento_id': fields.many2one( 'fiscal.tipodocumento','Tipo de Comprobante'),
        'establecimiento':fields.char('Establecimiento',size=3),
        'puntoemision':fields.char('Punto de Emisión',size=3),
        'secuencial':fields.char('Secuencial',size=9),
        'autorizacion':fields.char('No Autorización'),
        'fecha_emision':fields.date('Fecha de Autorización'),
        'ivacero':fields.float('Tarifa IVA 0%'),
        'iva_dif_cero':fields.float('Tarifa IVA diferente 0%'),
        'tarifa_no_iva':fields.float('Tarifa No Objeto de IVA'),
        'monto_exe_reembolso':fields.float('Monto excede reembolso'),
        'monto_ice':fields.float('Monto de ICE'),
        'monto_iva':fields.float('Monto IVA'),   
    }
    
    
    def change_vat(self,cr,uid,ids,partner=False,context=None):
        vals = {}
        if partner:
            prt = self.pool.get('res.partner').browse(cr,uid,[partner])
            vals['value']={
                    'identificacion_pro':prt.vat,
                           }
        return vals

facturas_reembolsos()

class account_move(osv.osv):
    
    _name='account.move'
    _inherit = 'account.move' 
    #Do not touch _name it must be same as _inherit
    #_name = 'account.move.line'
    _columns={
        'seccion_id':fields.many2one('seccion','Sección'),
        'curso_id':fields.many2one('curso','Curso'),
        'paralelo_id':fields.many2one('paralelo','Paralelo'),
        }


class account_move_line(osv.osv):
    
    _name='account.move.line'
    _inherit = 'account.move.line' 
    #Do not touch _name it must be same as _inherit
    #_name = 'account.move.line'
    _columns={
        'seccion_id':fields.many2one('seccion','Sección'),
        'curso_id':fields.many2one('curso','Curso'),
        'paralelo_id':fields.many2one('paralelo','Paralelo'),
        }
    
    def create(self, cr, uid, vals, context=None, check=True):
        account_obj = self.pool.get('account.account')
        tax_obj = self.pool.get('account.tax')
        move_obj = self.pool.get('account.move')
        cur_obj = self.pool.get('res.currency')
        journal_obj = self.pool.get('account.journal')
        context = dict(context or {})
        if vals.get('move_id', False):
            move = self.pool.get('account.move').browse(cr, uid, vals['move_id'], context=context)
            if move.company_id:
                vals['company_id'] = move.company_id.id
            if move.date and not vals.get('date'):
                vals['date'] = move.date
        if ('account_id' in vals) and not account_obj.read(cr, uid, [vals['account_id']], ['active'])[0]['active']:
            raise osv.except_osv(_('Bad Account!'), _('You cannot use an inactive account.'))
        if 'journal_id' in vals and vals['journal_id']:
            context['journal_id'] = vals['journal_id']
        if 'period_id' in vals and vals['period_id']:
            context['period_id'] = vals['period_id']
        if ('journal_id' not in context) and ('move_id' in vals) and vals['move_id']:
            m = move_obj.browse(cr, uid, vals['move_id'])
            context['journal_id'] = m.journal_id.id
            context['period_id'] = m.period_id.id
        #we need to treat the case where a value is given in the context for period_id as a string
        if 'period_id' in context and not isinstance(context.get('period_id', ''), (int, long)):
            period_candidate_ids = self.pool.get('account.period').name_search(cr, uid, name=context.get('period_id',''))
            if len(period_candidate_ids) != 1:
                raise osv.except_osv(_('Error!'), _('No period found or more than one period found for the given date.'))
            context['period_id'] = period_candidate_ids[0][0]
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            context['journal_id'] = context.get('search_default_journal_id')
        self._update_journal_check(cr, uid, context['journal_id'], context['period_id'], context)
        move_id = vals.get('move_id', False)
        journal = journal_obj.browse(cr, uid, context['journal_id'], context=context)
        vals['journal_id'] = vals.get('journal_id') or context.get('journal_id')
        vals['period_id'] = vals.get('period_id') or context.get('period_id')
        vals['date'] = vals.get('date') or context.get('date')
        if not move_id:
            if journal.centralisation:
                #Check for centralisation
                res = self._check_moves(cr, uid, context)
                if res:
                    vals['move_id'] = res[0]
            if not vals.get('move_id', False):
                if journal.sequence_id:
                    #name = self.pool.get('ir.sequence').next_by_id(cr, uid, journal.sequence_id.id)
                    v = {
                        'date': vals.get('date', time.strftime('%Y-%m-%d')),
                        'period_id': context['period_id'],
                        'journal_id': context['journal_id']
                    }
                    if vals.get('ref', ''):
                        v.update({'ref': vals['ref']})
                    move_id = move_obj.create(cr, uid, v, context)
                    vals['move_id'] = move_id
                else:
                    raise osv.except_osv(_('No Piece Number!'), _('Cannot create an automatic sequence for this piece.\nPut a sequence in the journal definition for automatic numbering or create a sequence manually for this piece.'))
        ok = not (journal.type_control_ids or journal.account_control_ids)
        if ('account_id' in vals):
            account = account_obj.browse(cr, uid, vals['account_id'], context=context)
            if journal.type_control_ids:
                type = account.user_type
                for t in journal.type_control_ids:
                    if type.code == t.code:
                        ok = True
                        break
            if journal.account_control_ids and not ok:
                for a in journal.account_control_ids:
                    if a.id == vals['account_id']:
                        ok = True
                        break
            # Automatically convert in the account's secondary currency if there is one and
            # the provided values were not already multi-currency
            if account.currency_id and 'amount_currency' not in vals and account.currency_id.id != account.company_id.currency_id.id:
                vals['currency_id'] = account.currency_id.id
                ctx = {}
                if 'date' in vals:
                    ctx['date'] = vals['date']
                vals['amount_currency'] = cur_obj.compute(cr, uid, account.company_id.currency_id.id,
                    account.currency_id.id, vals.get('debit', 0.0)-vals.get('credit', 0.0), context=ctx)
        if not ok:
            raise osv.except_osv(_('Bad Account!'), _('You cannot use this general account in this journal, check the tab \'Entry Controls\' on the related journal.'))

        result = super(account_move_line, self).create(cr, uid, vals, context=context)
        # CREATE Taxes
        if vals.get('account_tax_id', False):
            tax_id = tax_obj.browse(cr, uid, vals['account_tax_id'])
            total = vals['debit'] - vals['credit']
            base_code = 'base_code_id'
            tax_code = 'tax_code_id'
            account_id = 'account_collected_id'
            base_sign = 'base_sign'
            tax_sign = 'tax_sign'
            is_refund = ((total > 0 and tax_id.type_tax_use == 'sale') or (total < 0 and tax_id.type_tax_use != 'sale'))
            if journal.type in ('purchase_refund', 'sale_refund') or (journal.type in ('cash', 'bank') and is_refund):
                base_code = 'ref_base_code_id'
                tax_code = 'ref_tax_code_id'
                account_id = 'account_paid_id'
                base_sign = 'ref_base_sign'
                tax_sign = 'ref_tax_sign'
            base_adjusted = False
            for tax in tax_obj.compute_all(cr, uid, [tax_id], total, 1.00, force_excluded=False).get('taxes'):
                #create the base movement
                if base_adjusted == False:
                    base_adjusted = True
                    if tax_id.price_include:
                        total = tax['price_unit']
                    newvals = {
                        'tax_code_id': tax[base_code],
                        'tax_amount': tax[base_sign] * abs(total),
                    }
                    if tax_id.price_include:
                        if tax['price_unit'] < 0:
                            newvals['credit'] = abs(tax['price_unit'])
                        else:
                            newvals['debit'] = tax['price_unit']
                    self.write(cr, uid, [result], newvals, context=context)
                else:
                    data = {
                        'move_id': vals['move_id'],
                        'name': tools.ustr(vals['name'] or '') + ' ' + tools.ustr(tax['name'] or ''),
                        'date': vals['date'],
                        'partner_id': vals.get('partner_id', False),
                        'ref': vals.get('ref', False),
                        'statement_id': vals.get('statement_id', False),
                        'account_tax_id': False,
                        'tax_code_id': tax[base_code],
                        'tax_amount': tax[base_sign] * abs(total),
                        'account_id': vals['account_id'],
                        'credit': 0.0,
                        'debit': 0.0,
                    }
                    self.create(cr, uid, data, context)
                #create the Tax movement
                if not tax['amount'] and not tax[tax_code]:
                    continue
                #FORWARD-PORT UPTO SAAS-6
                tax_analytic = (tax_code == 'tax_code_id' and tax.get('account_analytic_collected_id')) or (tax_code == 'ref_tax_code_id' and tax.get('account_analytic_paid_id'))

                data = {
                    'move_id': vals['move_id'],
                    'name': tools.ustr(vals['name'] or '') + ' ' + tools.ustr(tax['name'] or ''),
                    'date': vals['date'],
                    'partner_id': vals.get('partner_id',False),
                    'ref': vals.get('ref',False),
                    'statement_id': vals.get('statement_id', False),
                    'account_tax_id': False,
                    'tax_code_id': tax[tax_code],
                    'tax_amount': tax[tax_sign] * abs(tax['amount']),
                    'account_id': tax[account_id] or vals['account_id'],
                    'credit': tax['amount']<0 and -tax['amount'] or 0.0,
                    'debit': tax['amount']>0 and tax['amount'] or 0.0,
                    'analytic_account_id': tax_analytic,
                }
                self.create(cr, uid, data, context)
            del vals['account_tax_id']

        recompute = journal.env.recompute and context.get('recompute', True)
        if check and not context.get('novalidate') and (recompute or journal.entry_posted):
            tmp = move_obj.validate(cr, uid, [vals['move_id']], context)
            if journal.entry_posted and tmp:
                move_obj.button_validate(cr,uid, [vals['move_id']], context)
        return result



