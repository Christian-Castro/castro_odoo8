# -*- coding: utf-8 -*-


from openerp.osv import osv,fields
from openerp import models, fields, api, _

class Configuracion(models.Model):
    _name="configuracion" 

    id_pais = fields.Many2one('res.country',string="País")
    id_provincia = fields.Many2one('res.country.state',string="Provincia")
    dias_pago = fields.Integer(string="Cantidad de dias para pronto pago")
    ciudad = fields.Char(string='Ciudad')
    cuenta_id_default = fields.Many2one('fiscal.tipodocumento',string="Tipo de Documento Por Defecto")



class Configuracion_General(models.TransientModel):
    _name="configuracion.gen"
    _rec_name='id_pais'

    relacion = fields.Many2one('configuracion',string="Relacion", ondele='cascade',default=lambda self: self.env.ref('ans_escuela.{0}'.format('id_pais')).id,copy=False)
    id_pais = fields.Many2one(related='relacion.id_pais',string="País", help='Pais a mostrar por defecto para los clientes')
    id_provincia = fields.Many2one(related='relacion.id_provincia',string="Provincia", help='Provincia a mostrar por defecto para los clientes')
    dias_pago = fields.Integer(related='relacion.dias_pago',string="Cantidad de dias para pronto pago")
    ciudad = fields.Char(related='relacion.ciudad',string='Ciudad')
    cuenta_id_default = fields.Many2one(related='relacion.cuenta_id_default',string="Tipo de Documento por defecto")

class close_window_purchase(models.Model):
        _name='close.window.purchase'
        _description='Cerrar Ventanas'

        @api.multi
        def cerrar_ventana(self):
            return {
            'type':'ir.actions.act_window_close'
            }
