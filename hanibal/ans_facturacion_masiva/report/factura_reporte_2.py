# -*- coding: utf-8 -*-

import time
import string
from openerp.report import report_sxw
from amount_to_text_ec import amount_to_text_ec

class factura_reporte(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(factura_reporte, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert':self.convert,
            'item':self.item(),
            'formatearfecha':self.formatearfecha,
            'get_detalle_lines':self._get_detalle_lines,
            'get_direccion' : self._get_direccion,
            'get_cliente' : self._get_cliente,
            'get_fono' : self._get_fono,
            'get_rep': self._get_rep,
            'get_autorizado' : self._get_autorizado,
            'efec': self._efec,
            'elec': self._elec,
            'tar':self._tar,
            'otro':self._otro,
        })
    
    def _efec(self,cla , val ):
        if cla == 'fp_efectivo':
            return val
    
    def _elec(self,cla , val ):
        if cla == 'fp_din_electronico':
            return val
    
    def _tar(self,cla , val ):
        if cla == 'fp_tr_cre_deb':
            return val
    
    def _otro(self,cla , val ):
        if cla == 'fp_otros':
            return val
        
    def _valor(self,clave):
        if clave == True:
            return 'Si'
        else:
            return 'No'
    
    it=0
    def item(self):
        self.it += 1
        return self.it
    
    def convert(self, amount):
        amt_en = amount_to_text_ec().amount_to_text_cheque(amount,'','Dólares')
        if amt_en:
            amt_en = amt_en[0].upper()+amt_en[1:]
        
        if len(amt_en)> self.MAX_MONTO:
            amt_en = amt_en[:self.MAX_MONTO]
        return amt_en
        
    
    def formatearfecha(self,fecha):
        f = time.strptime(fecha,"%Y-%m-%d")
        fecha = time.strftime("%d/%m/%Y",f)
        dia = fecha[:2]
        mes = fecha[3:5]
        anio = fecha[6:]
        
        mes = int(mes)
        if(mes==1):
            mes_es = 'enero'
        elif mes==2:
            mes_es = 'febrero'
        elif mes==3:
            mes_es = 'marzo'
        elif mes==4:
            mes_es = 'abril'
        elif mes==5:
            mes_es = 'mayo'
        elif mes==6:
            mes_es = 'junio'
        elif mes==7:
            mes_es = 'julio'
        elif mes==8:
            mes_es = 'agosto'
        elif mes==9:
            mes_es = 'septiembre'
        elif mes==10:
            mes_es = 'octubre'
        elif mes==11:
            mes_es = 'noviembre'
        else:
            mes_es = 'diciembre'
       
        fecha = dia+'/'+mes_es+'/'+anio
        return fecha       
    #35 #55
    MAX_DETALLE_WIDTH = 45
    MAX_DETALLE_LINES = 25 ##24
    MAX_CLIENTE = 85
    MAX_DIRECCION = 85
    MAX_MONTO = 62
    MAX_FONO = 12
    MAX_REP = 18
    MAX_AUTORIZADO = 30
    
    def _buscar_inicio_palabra(self,texto,pos):
        x = pos
        while x>=0:
            if texto[x] == ' ':
                if x==pos:
                    return x
                return x+1
            x-=1
        return 0
    
    def _buscar_final_palabra(self,texto,pos):
        tam = len(texto)
        x = pos
        while x<tam:
            if texto[x] == ' ':
                if x==pos:
                    return x
                return x-1
            x+=1
        return tam-1
    
    def _get_posicion_corte(self,texto,desde,hasta):
        inicio = self._buscar_inicio_palabra(texto, hasta)
        fin = self._buscar_final_palabra(texto, hasta)
        
        if inicio == fin:
            return inicio
        
        if fin+1 <= self.MAX_DETALLE_WIDTH:
            return fin+1
        
        return inicio-1 
    
    def _buscar_breakline(self,linea):
        lineas = string.split(linea,'\n')
        return lineas
    
    def _procesa_notas(self,linea):   
        lns = self._buscar_breakline(linea)     
        detalles = []
        #ESTO TAMBIEN ACTUALICE
        for linea in lns[1:]:
            desde = 0
            tam_total = len(linea)
            while desde < tam_total:
                restante = linea[desde:tam_total]
                tam_restante  = len(restante)
                if tam_restante <= self.MAX_DETALLE_WIDTH:
                    cantidad = False
                    vunitario = False
                    vtotal = False
                    codigo = False
                    descuento = False
                                        
                    l = {
                     'cantidad':cantidad,
                     'descripcion':restante,
                     'vunitario':vunitario,
                     'vtotal':vtotal,
                     'codigo':codigo,
                     'descuento':descuento,
                     'isnote': True,
                    }
                    detalles.append(l)
                    break
                    #return detalles
                
                pos = self._get_posicion_corte(linea, desde, desde+self.MAX_DETALLE_WIDTH-1)
                descripcion = linea[desde:pos]
                tam  = len(descripcion)
                
                cantidad = False
                vunitario = False
                vtotal = False
                codigo = False
                descuento = False
                            
                l = {
                     'cantidad': cantidad,
                     'descripcion': descripcion,
                     'vunitario': vunitario,
                     'vtotal' : vtotal,
                     'codigo':codigo,
                     'descuento':descuento,
                     'isnote': True,
                     }
                
                detalles.append(l)
                desde = pos+1
                
        return detalles
        
    def _procesa_linea(self,linea):
        detalles = []
        #ersta part es por la falta de un campo
        lns = self._buscar_breakline(linea.name or ' ')
        if lns :
            tam_total = len(lns[0])
        #tam_total = len(linea.name)
        desde = 0
        while desde < tam_total:
            restante = linea.name or ' '[desde:tam_total]
            tam_restante  = len(restante)
            if tam_restante <= self.MAX_DETALLE_WIDTH:
                cantidad = False
                vunitario = False
                vtotal = False
                codigo = False
                descuento = False
                if desde == 0:
                    cantidad  = linea.product_uom_qty
                    vunitario = linea.price_unit
                    vtotal  = linea.price_subtotal
                    codigo = linea.product_id.default_code
                    descuento = linea.discount
                    nombre_producto =  linea.product_id.name_template
                    ######_get_nombre_producto
                l = {
                 'cantidad':cantidad,
                 'descripcion':restante,
                 'vunitario':vunitario,
                 'vtotal':vtotal,
                 'codigo':codigo,
                 'descuento':descuento,
                 'isnote': False,
                 'nombre_producto':nombre_producto
                }
                detalles.append(l)
                return detalles
            
            pos = self._get_posicion_corte(linea.name or ' ', desde, desde+self.MAX_DETALLE_WIDTH-1)
            descripcion = linea.name or ' '[desde:pos]
            tam  = len(descripcion)
           
            if desde == 0:
                cantidad  = linea.product_uom_qty
                vunitario = linea.price_unit
                vtotal  = linea.price_subtotal
                codigo = linea.product_id.default_code
                descuento = linea.discount
            else:
                cantidad = False
                vunitario = False
                vtotal = False
                codigo = False
                descuento = False
                        
            l = {
                 'cantidad': cantidad,
                 'descripcion': descripcion,
                 'vunitario': vunitario,
                 'vtotal' : vtotal,
                 'codigo':codigo,
                 'descuento':descuento,
                 'isnote': False,
                 }
            
            detalles.append(l)
            desde = pos+1        
    x=0    
    def _get_detalle_lines(self,factura):
        
        detalles = []
        
        for l in factura.order_line:
            lineas = self._procesa_linea(l)
            for tmp in lineas:
                detalles.append(tmp)
            if l.name:
                notas = self._procesa_notas(l.name)
                for n in notas:
                    detalles.append(n)
        print  'detalles**********************'
        print len(detalles)
        if len(detalles) > self.MAX_DETALLE_LINES:
            self.MAX_DETALLE_LINES += 55 
        faltante = self.MAX_DETALLE_LINES - len(detalles)
        print ' self.MAX_DETALLE_LINES**********************'
        print  self.MAX_DETALLE_LINES
        i=0
        while i < faltante:
            l = {
             'cantidad': False,
             'descripcion': False ,
             'vunitario': False,
             'vtotal' : False,
             'codigo':False,
             'descuento':False,
             'isnote': False,
             }
            detalles.append(l)
            i+=1

        return detalles
    
    def _get_direccion(self,dir1 , dir2 , cit ):
        if not dir1 and not dir2 and not cit :
            return False
        
        texto = ''
        if dir1 and dir2:
            texto = dir1+' y '+dir2
        elif dir1:
            texto = dir1
        elif dir2:
            texto = dir2
        
        if cit:
            texto = texto + ' ('+cit+')'
        
        if len(texto) > self.MAX_DIRECCION:
            texto = texto[:self.MAX_DIRECCION]
        return texto
    
    def _get_cliente(self,cliente):
        if not cliente:
            return False
        title = cliente.title and (' '+cliente.title.shortcut+' ') or ''
        txt = cliente.name + title
        if len(txt) > self.MAX_CLIENTE:
            txt = txt[:self.MAX_CLIENTE]
        return txt
        txt = cliente.name +'\n'+ cliente.street +'\n'+'RUC: '+cliente.vat+'\n'+'Telefono: '+cliente.phone
        return txt
    def _get_fono(self,fono):
        if not fono:
            return False
        if len(fono) > self.MAX_FONO:
            fono = fono[:self.MAX_FONO]
        return fono
    
    def _get_rep(self,vendedor,origen):
        if not (vendedor or origen):
            return False
        
        texto = '' 
        if vendedor and origen:
            texto = vendedor.login.upper()+' ('+origen+')'
        elif vendedor:
            texto  = vendedor.login.upper()
        elif origen:
            texto = origen
            
        if len(texto) > self.MAX_REP:
            texto = texto[:self.MAX_REP]
        return texto
    
    def _get_autorizado(self,vendedor):
        if not vendedor:
            return False
        
        sql = "select rp.name as name from res_users ru, res_partner rp where ru.partner_id = rp.id and ru.id = %s "
        self.cr.execute(sql,(vendedor.id,))
        res = self.cr.dictfetchall()
        texto = str(res[0]['name']).upper()
        
        if len(texto) > self.MAX_AUTORIZADO:
            texto = texto[:self.MAX_AUTORIZADO]
        
        return texto

    def _get_nombre_producto(self,producto):
        if not producto:
            return False

        sql = " select name_template as name from product_product  where id= %s"
       ## sql = "select rp.name as name from res_users ru, res_partner rp where ru.partner_id = rp.id and ru.id = %s "
        self.cr.execute(sql,(producto.id,))
        res = self.cr.dictfetchall()
        texto = str(res[0]['name']).upper()
        
        if len(texto) > self.MAX_AUTORIZADO:
            texto = texto[:self.MAX_AUTORIZADO]
        
        return texto 
report_sxw.report_sxw(
    'report.factura.reporte',
    'sale.order',
    'addonsan/account_invoice/report/factura_reporte.rml',
    parser=factura_reporte,header=False )
