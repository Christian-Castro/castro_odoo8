{
    "name" : "CRM",
    "version" : "1.0",
    "depends" :[
                "crm",
                "base",
                "sale_crm",
                "sale"                
                ],
    "author" : "Odoo ERP",
    "description" : """
    Gestion por Faces
                    """,
    "website" : "http://none.com",
    "category" : "Ventas",
    "init_xml" : [
    ],
    "demo_xml" : [ 
    ],
    "update_xml" : [
                    
                    "res_partner_view.xml",
                    "menu_view.xml",
                    
                    "crm_lead_view.xml",
                    "ciudades_view.xml",
                    "tipo_opp_view.xml",
                    "calendar_view.xml",
                    "wizard/reporte_log_crm_prospecto_procesos_cantidad_view.xml",
                    "wizard/reporte_log_crm_prospecto_procesos_dias_view.xml",
		    "wizard/reporte_grafico_faces_view.xml",
		    "wizard/reporte_log_crm_prospecto_procesos_resultado_view.xml",
                    "crm_phonecall_view.xml",
		    "wizard/rt_genera_reporte.xml",
		    "wizard/analisis_precios.xml",
		    "wizard/reporte_log_crm_clientes_view.xml",
		    "wizard/tiempos_procesos.xml",
		    "wizard/reporte_log_crm_prospecto_exceso_dias_view.xml", 


                    ],
    "active": False,
    "installable": True,
}



                    












