{
    "name" : "ANS Reporte Tributación",
    "version" : "1.0",
    "depends" :[
        "ans_escuela",
        #"ans_reporte",
        "account",
        "purchase",
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
    "data": [
        "views/menu_view.xml",
        "data/paperformat.xml",
        "report/template_formulario_103_pdf.xml",
        "report/formulario_103_view.xml",
        "report/formulario_104_view.xml",
        "report/ventas_view.xml",
        "views/account_jornal_view.xml",
    ],
    "active": False,
    "installable": True,
}