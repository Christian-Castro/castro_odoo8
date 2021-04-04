{
    "name" : "Reportes Escuela",
    "version" : "1.0",
    "depends" :[
                "ans_escuela",
				"fiscaloriginal",
                "account",
                "ans_reporte_tributacion",          
                ],
    "author" : "Anonimo",
    "description" : """
    Modulo de ventas
                    """,
    "website" : "",
    "category" : "Escuela",
    "init_xml" : [
    ],
    "demo_xml" : [ 
    ],
    "update_xml" : [
        'data_views.xml',
        'reporte_general_views.xml',
        'reporte_cobranza_views.xml',
        'reporte_estadocuenta_views.xml',
        'reporte_caja_views.xml',
        'reporte_orden_pago_views.xml',
        'reporte_cobros_automaticos_views.xml',
        'reporte_recordatorio_views.xml',
                    ],
    "data": [
        "views/account_jornal_view.xml",
    ],
    "active": False,
    "installable": True,
}




