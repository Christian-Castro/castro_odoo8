# -*- coding: utf-8 -*-

import logging
from openerp.osv import osv,fields
from openerp import models, fields, api, _
_logger = logging.getLogger(__name__)

class respartnerHistorico(models.Model):
    _name="res.partner.historico" 

    alumno_id = fields.Many2one('res.partner',string="Alumno")
    usuario_id=fields.Many2one('res.users',string="Usuario", default=lambda self:self.env.user ,readonly=True)
    enero = fields.Boolean(string="Enero")
    febrero = fields.Boolean(string="Febrero")
    marzo = fields.Boolean(string="Marzo")
    abril = fields.Boolean(string="Abril")
    mayo = fields.Boolean(string="Mayo")
    junio = fields.Boolean(string="Junio")
    julio = fields.Boolean(string="Julio")
    agosto = fields.Boolean(string="Agosto")
    septiembre = fields.Boolean(string="Septiembre")
    octubre = fields.Boolean(string="Octubre")
    noviembre = fields.Boolean(string="Noviembre")
    diciembre = fields.Boolean(string="Diciembre")
    accion = fields.Selection( (('0','Ninguno'),
                               ('1','Facturar'),
                               ('2','Cobrar')) , 'Acción', required=False, default='0')

class respartner(models.Model):
    _inherit="res.partner" 
    _order= "name"
    _rec_name = "name"

    property_account_receivable_related = fields.Many2one(related='property_account_receivable',string="Cuenta a cobrar",store=True)
    banco_id=fields.Many2one('res.bank','Banco')
    cuenta_banco=fields.Char('Cuenta Bancaria',size=20)
    codigo_alumno=fields.Char('Código',size=20)
    tipo= fields.Selection( [('P','Representante'),
                               ('C','Clientes'),
                               ('PA','Padre'),
                               ('M','Madre'),
                               ('H','Representado')] , 'Tipo', required=False)

    jornada_id=fields.Many2one('jornada','Jornada',copy=False, index=True)
    seccion_id=fields.Many2one('seccion','Sección',copy=False, index=True)
    curso_id=fields.Many2one('curso','Curso',copy=False, index=True)
    paralelo_id=fields.Many2one('paralelo','Paralelo',copy=False, index=True)
    cedula=fields.Char(strint='Ced/RUC')
    codigo_auto = fields.Boolean('Cod. Automatico',default=True)
    descuentos_line=fields.One2many('descuentos.tomar', 'partner_ids', string='Descuentos detalle',
         copy=True)
    colaborador = fields.Many2one('tipo.colaborador',string="Colaborador")
    enero = fields.Boolean(string="Enero",default=True)
    febrero = fields.Boolean(string="Febrero",default=True)
    marzo = fields.Boolean(string="Marzo",default=True)
    abril = fields.Boolean(string="Abril",default=True)
    mayo = fields.Boolean(string="Mayo",default=True)
    junio = fields.Boolean(string="Junio",default=True)
    julio = fields.Boolean(string="Julio",default=True)
    agosto = fields.Boolean(string="Agosto",default=True)
    septiembre = fields.Boolean(string="Septiembre",default=True)
    octubre = fields.Boolean(string="Octubre",default=True)
    noviembre = fields.Boolean(string="Noviembre",default=True)
    diciembre = fields.Boolean(string="Diciembre",default=True)
    cobrar = fields.Boolean(string="Cobrar",default=True)
    facturar = fields.Boolean(string="Facturar",default=True)

    #-------HISTORICO--------
    jornada_anterior_id=fields.Many2one('jornada','Jornada A.',copy=False, index=True)
    seccion_anterior_id=fields.Many2one('seccion','Sección A.',copy=False, index=True)
    curso_anterior_id=fields.Many2one('curso','Curso A.',copy=False, index=True)
    paralelo_anterior_id=fields.Many2one('paralelo','Paralelo A.',copy=False, index=True)
    historico_id = fields.One2many('res.partner.historico','alumno_id',string="Historico")
    #RERV factura para controlar las facturas emitidas para el alumno
    factura_emitida_ids = fields.Many2many("academic.month", ondelete="restrict")


    @api.onchange('jornada_id')
    def onchange_jornada(self):
        for l in self:
            if l.tipo=='H':
                if l.jornada_id:
                    l.seccion_id=False
                    l.curso_id= False
                    l.paralelo_id = False

    @api.onchange('seccion_id')
    def onchange_seccion(self):
        for l in self:
            if l.tipo=='H':
                if l.seccion_id:
                    l.curso_id= False
                    l.paralelo_id = False

    @api.onchange('curso_id')
    def onchange_curso(self):
        for l in self:
            if l.tipo=='H':
                if l.curso_id:
                    l.paralelo_id = False

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            # if record.parent_id and not record.is_company:
            #     name = "%s, %s" % (record.parent_name, name)
            # if context.get('show_address_only'):
            #     name = self._display_address(cr, uid, record, without_company=True, context=context)
            # if context.get('show_address'):
            #     name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
            # name = name.replace('\n\n','\n')
            # name = name.replace('\n\n','\n')
            # if context.get('show_email') and record.email:
            #     name = "%s <%s>" % (name, record.email)  
            res.append((record.id, name))
        return res

    @api.model
    def create(self, vals):
        valor=0
        try:
            if vals['tipo']=='H':
                while True:
                    seq = self.env['ir.sequence'].next_by_code('res.partner') or ''
                    obj_data = self.env['res.partner'].search([('codigo_alumno','=',seq)])
                    obj_secuence = self.env['ir.sequence'].search([('code','=','res.partner')])
                    if len(obj_data)!=0:
                        self.env.cr.execute("update ir_sequence set number_next='{0}' where code='res.partner'".format(obj_secuence.number_next_actual))
                    else:
                        if vals['codigo_auto']==True:
                            vals['codigo_alumno'] = seq
                        break
            a = super(respartner, self).create(vals)
        except Exception as e:
            a = super(respartner, self).create(vals)
        
        return a


    @api.one
    @api.depends('name')
    def _carga_pais(self):
        for l in self:
            if l.tipo!=False:
                obj_pais=self.env['configuracion'].search([('id_pais','!=',None)])
                l.country_id=obj_pais.id_pais.id
                l.state_id=obj_pais.id_provincia.id
                l.zip=l.country_id.codigo
                l.city=obj_pais.ciudad

    carga_pais = fields.Boolean(string="Cargo",compute='_carga_pais',readonly='0')

    #CAMPOS REUTILIZADOS 

    vat= fields.Char('TIN', help="Tax Identification Number. Check the box if this contact is subjected to taxes. Used by the some of the legal statements.",size=13)
    

    _defaults = {  
        'tipo': 'C',  
        }
    
    _sql_constraints = [
        ('cuenta_banco_uniq', 'unique(cuenta_banco)',
            'La cuenta de banco ya fue registrada!'),
    ]
    
    _sql_constraints = [
        ('codigo_alumno_uniq', 'unique(codigo_alumno)',
            'La codigo del alumno ya fue registrado!'),
    ]

    @api.constrains('vat','tipoid')
    def constrains_vat(self):
        for l in self:
            if l.vat!=False and l.tipo=='P':
                if len(l.vat) == l.tipoid.longitud:
                    _logger.info("Cedula - Vat - correcta")
                    return True
                else:
                    raise osv.except_osv(('Alerta'),("Numero de Identificación Incorrecto!"))
            else:
                _logger.info("Cedula - Vat - vacia")

    @api.constrains('cedula')
    def constrains_cedula(self):
        for l in self:
            if l.cedula!=False and l.tipo=='H':
                if len(l.cedula)== 10:
                    _logger.info("Cedula correcta")
                else:
                    raise osv.except_osv(('Alerta'),("Numero de Identificacion Incorrecto!"))
            else:
                _logger.info("Cedula vacia")
                return False

    

    def button_check_vat(self):
        return True

    def _construct_constraint_msg(self):
        def default_vat_check(cn, vn):
            # by default, a VAT number is valid if:
            #  it starts with 2 letters 
            #  has more than 3 characters
        #     return cn[0] in string.ascii_lowercase and cn[1] in string.ascii_lowercase
        # vat_country, vat_number = self._split_vat(self.browse(cr, uid, ids)[0].vat)
        # vat_no = "'CC##' (CC=Country Code, ##=VAT Number)"
        # error_partner = self.browse(cr, uid, ids, context=context)
        # if default_vat_check(vat_country, vat_number):
        #     vat_no = _ref_vat[vat_country] if vat_country in _ref_vat else vat_no
        #     if self.pool['res.users'].browse(cr, uid, uid).company_id.vat_check_vies:
        #         return '\n' + _('The VAT number [%s] for partner [%s] either failed the VIES VAT validation check or did not respect the expected format %s.') % (error_partner[0].vat, error_partner[0].name, vat_no)
        # return '\n' + _('The VAT number [%s] for partner [%s] does not seem to be valid. \nNote: the expected format is %s') % (error_partner[0].vat, error_partner[0].name, vat_no)
            return True
        return True

    def check_vat(self, cr, uid, ids, context=None):

        return True


    _constraints = [(check_vat, 'CHECK(1=1)', ["vat"])]

