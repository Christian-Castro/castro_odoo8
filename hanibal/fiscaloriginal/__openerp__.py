{
    "name" : "Fiscal Module",
    "version" : "8.0",
    "depends" :["base",
                "base_vat",
                "hr_expense",
                "account",
                "account_voucher",
                "purchase",
                "purchase_requisition",
                "account_analytic_plans",
                # "pg1__notas_credito_cliente",
                ],
    "author" : "OpenERP",
    "description" : """
    What it does!
                    """,
    "website" : "http://none.com",
    "category" : "Generic Modules",
    "init_xml" : [
    ],
    "demo_xml" : [ 
    ],
    "update_xml" : [
                    "puntoemision_view.xml",
                    "comprobantes_anulados_view.xml",
                    "facturacliente_view.xml",
                    "journal_view.xml",
                    "partner_view.xml",
                    "ats_proceso_view.xml",
                    "producto_view.xml",
                    "reglaretencion_view.xml",
                    "tax_view.xml",
                    "tipoidentificacion_view.xml",                    
                    "tipoproducto_view.xml",
                    "retencion_view.xml",
                    #NUEVO"pagocliente_view.xml",
        	        "report/factura_reporte.xml",
                    #"report/compra_reporte.xml",
                    #"report/requisicioncompra_reporte.xml",
                    #"wizard/atsproceso_wizard.xml",
                    "factura_workflow.xml",
                    #"compra_view.xml",
                    #"ats_workflow.xml",
                    "fiscal_tipopago_view.xml",
                    "fiscal_formapago_view.xml",
                    #"fiscal_ats_ventaptoemision_view.xml",
                    "folios_config_view.xml", 
                    #"fiscal_folios_view.xml", 
                    
                    
                    "report/ride_factura_electronica.xml",
                    
                    ],
    "active": False,
    "installable": True,
}




