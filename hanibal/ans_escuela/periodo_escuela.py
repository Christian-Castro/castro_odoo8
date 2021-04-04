# -*- coding: utf-8 -*-
from openerp import models, fields, api

class periodo_escuela(models.Model):
    
    _name = 'periodo'
    
    
    name = fields.Char('Descripción')
    active = fields.Boolean('Activo')
    mes = fields.Selection( [('01','Enero'),
                             ('02','Febrero'),
                             ('03','Marzo'),
                             ('04','Abril'),
                             ('05','Mayo'),
                             ('06','Junio'),
                             ('07','Julio'),
                             ('08','Agosto'),
                             ('09','Septiembre'),
                             ('10','Octubre'),
                             ('11','Noviembre'),
                             ('12','Diciembre')],'Mes' )
    periodo_id = fields.One2many(comodel_name='periodo.line', inverse_name="periodo_id", string='Periodo')
    
    _defaults = {  
        'active': True,  
        }
    
    _sql_constraints = [
        ('periodos_activos_uniq', 'unique(active,mes)',
            'No puede tener mas de un abierto, inhabilite el mes actual para crear uno nuevo!'),
    ]
    
periodo_escuela()