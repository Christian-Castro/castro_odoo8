import time

from openerp.report import report_sxw
from openerp.tools import amount_to_text_en

class retencion_reporte(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(retencion_reporte, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'anio':self.anio,
            'formatearfecha':self.formatearfecha,
            'get_detalle_lines':self._get_detalle_lines,
            'get_cliente': self._get_cliente,
            'get_direccion': self._get_direccion,
            'get_numeroret': self._get_numeroret,
            'get_total' : self._get_total,
            'get_porcentaje' : self._get_porcentaje,
        })
    
    def anio(self, fecha):
        f = time.strptime(fecha,"%Y-%m-%d")
        return f.tm_year
    
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
    
    MAX_DETALLE_WIDTH = 56
    MAX_DETALLE_LINES = 8
    MAX_CLIENTE = 40
    MAX_DIRECCION = 38
        
    def _get_cliente(self,cliente):
        if not cliente:
            return False
        
        if len(cliente) > self.MAX_CLIENTE:
            cliente = cliente[:self.MAX_CLIENTE]
        return cliente
    
    def _get_direccion(self,dir):
        if not dir:
            return False
        
        texto = ''
        if dir.street and dir.street2:
            texto = dir.street+' y '+dir.street2
        elif dir.street:
            texto = dir.street
        elif dir.street2:
            texto = dir.street2
        
        if dir.city:
            texto = texto + ' ('+dir.city+')'
        
        if len(texto) > self.MAX_DIRECCION:
            texto = texto[:self.MAX_DIRECCION]
        return texto
    
    def _get_numeroret(self,establecimiento,puntoemision,secuencial):
        texto = False
        if establecimiento and puntoemision and secuencial:
            texto = establecimiento+'-'+puntoemision+'-'+secuencial
        return texto
    
    def _get_porcentaje(self,porcentaje):
        
        if not porcentaje:
            return False
        if porcentaje<0:
            return porcentaje*(-1)
        return porcentaje
    
    def _get_total(self,total):
        
        if not total:
            return False
        if total<0:
            return total*(-1)
        return total
    
    def _get_detalle_lines(self,factura):
        x=1
        detalles = []        
        
        for l in factura.retencion_line:
            if x > self.MAX_DETALLE_LINES:
                break
            
            l = {
                 'ejerciciofiscal':self.anio(factura.date_invoice),
                 'baseimponible':l.base,
                 'impuesto':l.tipo=='fte' and 'Fuente' or 'IVA',
                 'codigo':l.codigo,
                 'porcentaje' : l.porcentaje*-100,
                 'valor':l.amount<0 and l.amount*-1 or l.amount,
             }
            detalles.append(l)
            x+=1
            
        faltante = self.MAX_DETALLE_LINES - len(detalles)
        
        i=0
        while i < faltante:
            l = {
                 'ejerciciofiscal':False,
                 'baseimponible':False,
                 'impuesto':False,
                 'codigo':False,
                 'porcentaje' : False,
                 'valor':False,
             }
            detalles.append(l)
            i+=1

        return detalles
    
        
report_sxw.report_sxw(
    'report.retencion.reporte',
    'account.invoice',
    'addons/sri/report/retencion_reporte.rml',
    parser=retencion_reporte
)