# -*- coding: utf-8 -*-


from openerp.exceptions import ValidationError
from openerp.osv import  fields,osv
from openerp import models, fields, api, _
from datetime import datetime

class account_voucher(models.Model):

    _name = 'account.voucher'
    _inherit = 'account.voucher'

    ############################             WM              #######################################
    account_journal_caja_id = fields.Many2one('account.journal',string="Caja",default=lambda self: self._default_route_ids())
    exigir_doc_banco = fields.Boolean(related='journal_id.exigir_doc_banco',string="Exigir datos bancarios en pago")
    banco_id=fields.Many2one('res.bank','Banco')
    documento = fields.Char(string="Documento")
    fecha_ch = fields.Date(string='Fecha de Cheque')
    usuario_id = fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)



    @api.constrains('partner_id')
    def contrains_amount(self):
        if self.amount<=0 and not self.journal_id.is_cruce:
            raise ValidationError('El monto cobrado no debe ser cero.')

       
    @api.model
    def _default_route_ids(self):
        obj_datos=self.env['account.journal'].search([('usuarios_ids','in',self._uid),('caja','=',True)])
        if len(obj_datos)==1:
            return obj_datos.id
        else:
            return False

    @api.multi
    def onchange_type(self, alumno_id=False):
        lista=[]
        alumno = self.env['res.partner'].search([('id','=',alumno_id)])
        lista.append(alumno.parent_id.id)
        facturas = self.env['account.invoice'].search([('alumno_id','=',alumno_id),('residual','!=',0)])
        for l in facturas:
            if l.partner_id.id not in lista:
                lista.append(l.partner_id.id)
        return {'domain':{'partner_id':[('id','in',lista)]}}

    escolar = fields.Boolean('Estructura Escolar',default=True)

    @api.multi
    def onchange_alumno_id(self):
        if self.alumno_id:
            return {
                'value': {
                    'partner_id': False,
                    }
                }
        else:
            return {
                'value': {
                    'partner_id': False,
                }
            }

    alumno_id_related=fields.Many2one(related='alumno_id',string='Jornada',copy=False, index=True)

    ############################             WM              #######################################
    alumno_id = fields.Many2one('res.partner','Alumno')
    
    def _calculo_anios(self):
        ahora = datetime.now()
        lista_anios=[]
        lista_ordenada=[]
        actual=int(ahora.year)+1
        for anio in range(1945, actual):
            lista_anios.append(anio)
            lista_anios=sorted(lista_anios,reverse=True)
        for orden in lista_anios:
            lista_ordenada.append((str(orden),str(orden)))
        return lista_ordenada
    
    # jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    # seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    # curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    # paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    jornada_id=fields.Many2one(related='alumno_id.jornada_id',string='Jornada',copy=False, index=True,store=True)
    seccion_id=fields.Many2one(related='alumno_id.seccion_id',string='Sección',copy=False, index=True,store=True)
    curso_id=fields.Many2one(related='alumno_id.curso_id',string='Curso',copy=False, index=True,store=True)
    paralelo_id=fields.Many2one(related='alumno_id.paralelo_id',string='Paralelo',copy=False, index=True,store=True)

    mes = fields.Selection( (('1','Enero'),
                               ('2','Febrero'),
                               ('3','Marzo'),
                               ('4','Abril'),
                               ('5','Mayo'),
                               ('6','Junio'),
                               ('7','Julio'),
                               ('8','Agosto'),
                               ('9','Septiembre'),
                               ('10','Octubre'),
                               ('11','Noviembre'),
                               ('12','Diciembre')) , 'Mes', required=False)
    anio = fields.Selection( (_calculo_anios) , 'Año', required=False)
    
    #===========================================================================
    # CAMBIOS PARA TRAER DE ALUMNOS EL RESTO DE DATOS
    #===========================================================================
    # @api.multi
    # def onchange_alumno_id(self, alumno_id=False):
    #     if alumno_id:
    #         alumno = self.env['res.partner'].browse(alumno_id)
    #         return {
    #             'value': {
    #                 'jornada_id': alumno.jornada_id.id ,
    #                 'seccion_id': alumno.seccion_id.id,
    #                 'curso_id': alumno.curso_id.id,
    #                 'paralelo_id': alumno.paralelo_id.id,
    #                 'partner_id': alumno.parent_id.id,
    #             }
    #         }
    #     else:
    #         return {
    #             'value': {
    #                 'jornada_id': False ,
    #                 'seccion_id': False,
    #                 'curso_id': False,
    #                 'paralelo_id': False,
    #                 'partner_id': False,
    #             }
    #         }
    #     return {}


  
    
    # def proforma_voucher(self, cr, uid, ids, context=None):
    #     for voucher in self.browse(cr, uid, ids, context=context):
    #         if voucher.alumno_id:
    #             if voucher.alumno_id.parent_id.id != voucher.partner_id.id:
    #                 raise ValidationError('No coinciden Padre e Hijo seleccionado.')
    #             if len(voucher.line_ids) == 0 :
    #                 if voucher.alumno_id.parent_id.id != voucher.partner_id.id:
    #                     raise ValidationError('No puede confirmar este pago')
    #     self.action_move_line_create(cr, uid, ids, context=context)
    #     return True
    
    
    def account_move_get(self, cr, uid, voucher_id, context=None):
        '''
        This method prepare the creation of the account move related to the given voucher.

        :param voucher_id: Id of voucher for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.pool.get('ir.sequence')
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher.number:
            name = voucher.number
        elif voucher.journal_id.sequence_id:
            if not voucher.journal_id.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            c = dict(context)
            c.update({'fiscalyear_id': voucher.period_id.fiscalyear_id.id})
            name = seq_obj.next_by_id(cr, uid, voucher.journal_id.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                        _('Please define a sequence on the journal.'))
        if not voucher.reference:
            ref = name.replace('/','')
        else:
            ref = voucher.reference

        move = {
            'name': name,
            'journal_id': voucher.journal_id.id,
            'narration': voucher.narration,
            'date': voucher.date,
            'ref': ref,
            'period_id': voucher.period_id.id,
            
            'alumno_id': voucher.alumno_id.id or False,
            'jornada_id': voucher.jornada_id.id or False,
            'curso_id': voucher.curso_id.id or False,
            'seccion_id': voucher.seccion_id.id or False,
            'paralelo_id': voucher.paralelo_id.id or False,
            'mes': voucher.mes  or False,
            'anio': voucher.anio or False,
            
        }
        return move
                             
class account_move(osv.osv):
    
    _name='account.move'
    _inherit = 'account.move' 
    
    alumno_id = fields.Many2one('res.partner','Alumno')
    def _calculo_anios(self):
        ahora = datetime.now()
        lista_anios=[]
        lista_ordenada=[]
        actual=int(ahora.year)+1
        for anio in range(1945, actual):
            lista_anios.append(anio)
            lista_anios=sorted(lista_anios,reverse=True)
        for orden in lista_anios:
            lista_ordenada.append((str(orden),str(orden)))
        return lista_ordenada
    
    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    mes = fields.Selection( (('1','Enero'),
                               ('2','Febrero'),
                               ('3','Marzo'),
                               ('4','Abril'),
                               ('5','Mayo'),
                               ('6','Junio'),
                               ('7','Julio'),
                               ('8','Agosto'),
                               ('9','Septiembre'),
                               ('10','Octubre'),
                               ('11','Noviembre'),
                               ('12','Diciembre')) , 'Mes', required=False)
    anio = fields.Selection( (_calculo_anios) , 'Año', required=False,store=True)


from openerp.osv import fields, osv
    
    

from openerp import models, fields, api, _


################################################################################################
############################             WM              #######################################
################################################################################################
   
class account_journal_cobro(models.Model):
    _name= "account.journal.user"

    user_id = fields.Many2one('res.users',string="Usuario")
    journal_cabecera_id = fields.Many2one('account.journal',string="Relacion Journal")


class account_journal_cobro(models.Model):
    _inherit= "account.journal"

    @api.constrains('detalle_journal')
    def _accesos_usuarios_1(self):
        for l in self:
            lista_usuario=[]
            if len(l.detalle_journal)!=0:
                for m in l.detalle_journal:
                    lista_usuario.append(m.user_id.id)

                l.usuarios_ids=lista_usuario
            else:
                l.usuarios_ids=None

            # l.write({
            #     'usuarios_ids':lista_usuario
            #     })
            # l.update({
            #     'usuarios_ids':lista_usuario
            #     })


    caja = fields.Boolean(string="Caja")
    exigir_doc_banco = fields.Boolean(string="Exigir datos bancarios en pago")
    detalle_journal= fields.One2many('account.journal.user','journal_cabecera_id',string="Relacion Detalle")
    usuarios_ids = fields.Many2many('res.users',string="Accesos de Usuarios")
