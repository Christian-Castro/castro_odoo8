# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import models, fields, api, _

class Tipo_Colaborador(models.Model):
    _name = 'tipo.colaborador'
    _rec_name = 'name'
    
    
    name=fields.Char(string='Nombre')
    active=fields.Boolean(string='Activo',default=True)