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
import re

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    _columns = {
        'num_autfac': fields.char('Numero de Autorizacion de Factura',10),	
        'venc_autfac': fields.date('Fecha de Vencimiento de Factura'),
        'num_autimpfac': fields.char('Numero de autorizacion de imprenta',10),
        'num_autncre': fields.char('Numero de Autorizacion de Notas de Credito',10),
        'venc_autncre':fields.date('Fecha de Vencimiento de Notas de Credito'),	
        'tipoid': fields.many2one('fiscal.tipoidentificacion','Tipo',required=False),
   }

    coef_natural = (2,1,2,1,2,1,2,1,2)
    coef_juridica = (4,3,2,7,6,5,4,3,2) 
    coef_publica = (3,2,7,6,5,4,3,2)
    
    PERSONA_NATURAL = 1
    PERSONA_JURIDICA = 2
    PERSONA_PUBLICA = 3
    
    DIG_VER_PUBLICO = 8
    DIG_VER_JURIDICO = 9
    DIG_VER_NATURAL = 9

    MODULO10 = 10
    MODULO11 = 11

    #tamanios de los tipos de identificacion
    TAMANIORUC = 13
    TAMANIOCEDULA = 10
    TAMANIOPASAPORTE = 13
    
    #tipos de identificacion
    RUC = 'RUC'
    CEDULA = 'CI'
    PASAPORTE = 'PAS'

    def multiplicarTuplas(self,t1,t2):
        mult=[]
        for x1,x2 in zip(t1,t2):
            mult.append(int(x1)*int(x2))
        return mult
        

    def pasaVerificador(self,ruc,tipoPersona):
        #si es persona natural tipoPersona < 6 o
        #si es persona juridca = 9 el digito verificador
        #es el digito numero 10 (indice 9)
        #si es institucion publica el digito verificador
        #es el 9 (indice 8)
        if(tipoPersona < 6 ):
            num = ruc[:9]
            indiceVerificador = self.DIG_VER_NATURAL
            coeficientes = self.coef_natural
            modulo = self.MODULO10
        elif(tipoPersona == '6'):
            num = ruc[:8]
            indiceVerificador = self.DIG_VER_PUBLICO
            coeficientes = self.coef_publica
            modulo = self.MODULO11
        elif(tipoPersona == '9'):
            num = ruc[:9]
            indiceVerificador = self.DIG_VER_JURIDICO
            coeficientes = self.coef_juridica
            modulo = self.MODULO11
        else:
            msg = 'Tipo de persona es incorrecto'
            return False
        
        mult = self.multiplicarTuplas(num,coeficientes)
    
        total = 0
        for valor in mult:
            if modulo == self.MODULO10 and valor > 10:
                valor = valor - 9
            total = total + valor
        
        residuo = total % modulo
        if residuo == 0:
            verificador = 0
        else:
            verificador = modulo - residuo
    
        if(int(ruc[indiceVerificador]) == verificador):
            return True
        return False
   
    
    def verificarTipoDePersona(self, digitoTipoPersona, tipoPersona):
        if(tipoPersona == self.PERSONA_JURIDICA):
            return digitoTipoPersona == 9
        if(tipoPersona == self.PERSONA_PUBLICA):
            return digitoTipoPersona == 6
        if(tipoPersona == self.PERSONA_NATURAL):
            return digitoTipoPersona < 6
        
        msg = 'Tipo de persona tiene un valor no aceptado'
        return

    # Metodo que verifica si una identificacion tipo cedula, ruc o pasaporte
    # es valida segun el criterio impuesto por el SRI del Ecuador.
    # si modoEstricto=True la funcion realiza la validacion del digito verificador
    # sin tomar en cuenta el parametro tipoPersona.
    # si modoEstricto=False entonces el parametro tipoPersona es obligatorio
    # y con este compara si el tipo de persona contenido en el ruc es igual al 
    # tipo de persona ingresado como parametro.
    def isRucValido(self,vat,tipoid,modoEstricto=True):        
        if(tipoid == self.RUC):
            tamanioid = self.TAMANIORUC
        elif(tipoid == self.CEDULA):
            tamanioid = self.TAMANIOCEDULA
        elif(tipoid == self.PASAPORTE):
            tamanioid = self.TAMANIOPASAPORTE
        else:
            msg = 'Error. Tipo de identificacion no valida'
            return False
        
        #validando el tamanio del ruc, ci o pasaporte
        tamanio = len(vat);
        if(tamanio != tamanioid):
            msg = 'Identificacion debe contener '+str(tamanioid)+' digitos.'
            return False
        
        #para ruc y ci solo deben contener digitos
        if (tipoid == self.RUC and not re.match('\d{13}',vat)):
            msg = 'RUC debe contener solo numeros'
            
            return False
        elif(tipoid == self.CEDULA and not re.match('\d{10}',vat)):
            msg = 'CI debe contener solo numeros'
            return False
        
        #para pasaporte puede ser cualquier caracter, solo comprobamos que este entre
        #el minimo y maximo permitido en tamanio de digitos
        if(tipoid == self.PASAPORTE):
            if(tamanio<self.TAMANIOCEDULA or tamanio>self.TAMANIOPASAPORTE):
                msg = 'Pasaporte debe tener minimo 10 digitos y maximo 13'
                return False
            else:
                return True
        
        #si es RUC o CI validamos que sea consistente
        #es decir que tenga la estructura indicada por el SRI
        codProvincia = int(vat[:2])
        if(codProvincia > 24):
            msg = 'Provincia incorrecta'
            return False
        
        #solo el tipo es RUC se valida el numero de establecimientos
        if(tipoid == self.RUC):
            establecimiento = int(vat[10:])
            if not (establecimiento >= 1):
                msg = 'Establecimiento debe ser por lo menos 001'
                return False    
        
        #si modoEstricto=True se hace la validacion del digito verificador
        #de lo contrario termina la validacion
        tipoPersonaCalculado = int(vat[2:3])
        if modoEstricto:
            #ejecutando validacion del digito verificador
            if not self.pasaVerificador(vat,tipoPersonaCalculado):
                msg = 'Numero de Identificacion no cumple validacion del digito verificador.'
                return False  
            
            return True
        
        return True
        
        
    def check_vat_ec(self, cr, uid, ids, context=None):
        for partners in self.browse(cr, uid, ids, context=context):
            if not partners.vat and not partners.parent_id:
                continue
            if not self.isRucValido(partners.vat,partners.tipoid.sigla,False) and not partners.parent_id:
                return False
        return True


    def check_ident(self, cr, uid, ids, context=None):
        
        for partners in self.browse(cr, uid, ids, context=context):
            if partners.customer or partners.supplier: 
                if not partners.parent_id:
                    cr.execute("select count(*) from res_partner where vat = %s ",(partners.vat,))
                    res = cr.dictfetchall()
                    if res[0]['count'] > int(len(partners.child_ids) + 1)  :
                        return False
        return True         


    def check_num_autfac(self,cr,uid,ids,context=None):
        for partner in self.browse(cr, uid, ids, context=context):
            if not partner.num_autfac:
                continue
            tam = len(partner.num_autfac) 
            if tam>0:
                if tam!=10 or not re.match('\d{10}',partner.num_autfac):
                    return False
        return True  

    def check_vat(self, cr, uid, ids, context=None):
        return True      

    _constraints = [
                         (check_vat,'', ['vat']),
                        # (check_vat_ec,'Numero de identificacion incorrecto.', ['vat']),
                        # (check_ident,'El numero de identificacion ya ha sido registrado.', ['vat']),
                         #(check_num_autfac,'Numero de autorizacion de factura incorrecto', ['num_autfac'])
                     ]

   

res_partner()
