# -*- coding: utf-8 -*-


from openerp.osv import osv,fields
from openerp import models, fields, api, _

class rescountry(models.Model):
    _inherit="res.country" 

    codigo=fields.Char(string='Código', size=4)