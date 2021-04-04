import time

from report import report_sxw
from tools import amount_to_text_en

class compra_reporte(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(compra_reporte, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'convert': self.convert,
        })        
        
    def convert(self, estado):
        if estado=='draft':
            return 'Solicitud de presupuesto'
        elif estado=='wait':
            return 'En espera'
        elif estado == 'confirmed':
            return 'Esperando Aprobacion'
        elif estado == 'approved':
            return 'Aprobado'
        elif estado == 'except_picking':
            return 'Excepcion de Envio'
        elif estado == 'except_invoice':
            return 'Excepcion de Factura'
        elif estado == 'done':
            return 'Finalizado'
        elif estado == 'cancel':
            return 'Cancelado'
        
        return 'Estado no valido'
            
        
report_sxw.report_sxw(
    'report.solicitud.compra',
    'purchase.order',
    'addons/sri/report/solicitudcompra_reporte.rml',
    parser=compra_reporte
)

report_sxw.report_sxw(
    'report.orden.compra',
    'purchase.order',
    'addons/sri/report/ordencompra_reporte.rml',
    parser=compra_reporte
)

report_sxw.report_sxw(
    'report.ordeninterna.compra',
    'purchase.order',
    'addons/sri/report/ordencomprainterna_reporte.rml',
    parser=compra_reporte
)