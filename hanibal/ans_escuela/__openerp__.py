{
    "name" : "Facturacion",
    "version" : "1.0",
    "depends" :[
                "base",
                "account",
                "sale",
                "account_voucher",
                "fiscaloriginal",
                ],
    "author" : "Odoo ERP",
    "description" : """
    Modulo de ventas
                    """,
    "website" : "http://none.com",
    "category" : "Account",
    "init_xml" : [
    ],
    "demo_xml" : [ 
    ],
    "update_xml" : [
                    
        'report/factura_reporte_view.xml',
        'menus_views.xml',
        'res_partner_view.xml',
        'estructura_escuela_view.xml',
        'descuentos_escuela_view.xml',
        # 'periodo_escuela_view.xml', #RERV comentado xq hay nuevo metodo de periodo
        'localizacion_views.xml',
        'configuracion_views_data.xml',
        'asignacion_descuento_views.xml',
        'cambio_paralelo_views.xml',
        'configuracion_views.xml',
        'tipo_colaborador_views.xml',
        'generar_facturas_view.xml',
        'product_template_views.xml',
        'wizard/account_invoice_lote_view.xml',
        'journal_view.xml',
        'cobro_cliente_view.xml',
        'recordatorio_view.xml',
                    ],
    "data": [
        'views/mes_academico_view.xml',
        'views/anio_academico_view.xml',
        'data_views.xml',
        ],
    "active": False,
    "installable": True,
}
