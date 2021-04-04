# -*- coding: utf-8 -*-

import time
from report import report_sxw
from osv import osv
import pooler

class requisicioncompra_reporte(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(requisicioncompra_reporte, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'reqstate_to_string' : self.reqstate_to_string,
            'comprastate_to_string': self.comprastate_to_string,
        })
    
    def reqstate_to_string(self, estado):
        if estado=='draft':
            return 'Nuevo'
        elif estado=='in_progress':
            return 'En Progreso'
        elif estado == 'cancel':
            return 'Cancelado'
        elif estado == 'done':
            return 'Realizado'
        
        return 'Estado no valido'

    def comprastate_to_string(self, estado):
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
        'report.requisicion.compra',
        'purchase.requisition',
        'addons/sri/report/requisicioncompra_reporte.rml',
        parser=requisicioncompra_reporte
        )


