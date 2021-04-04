# -*- coding: utf-8 -*-
import re

from openerp import models, fields, api
from openerp.exceptions import ValidationError, RedirectWarning
from openerp.osv.orm import except_orm
from openerp.osv import osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import copy
import logging
_logger = logging.getLogger(__name__)

# class pg1__notas_credito_cliente(models.Model):
#     _name = 'pg1__notas_credito_cliente.pg1__notas_credito_cliente'

#     name = fields.Char()
#nota_de_credito_ans
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Supplier Invoice
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Supplier Refund
}
class ErrorMessage(models.TransientModel):
    _name = 'pg2.mensaje'
    _description = 'HR employee wizard'
    message = fields.Text(string="Factura con saldo menos a la nota de credito", readonly=True, store=True)

class Invoices_lines_ans(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    def _computed_cant_facturada(self):
        cantidad_facturada = 0
        # cantidad_devuelta = 0
        if self.invoice_id.type == 'in_refund' or self.invoice_id.type == 'out_refund':
            invoices_obj = self.env['account.invoice'].search([('id', '=', self.invoice_id.factura.id)])
            for inv_line in invoices_obj.invoice_line:
                if self.product_id.id == inv_line.product_id.id:
                    cantidad_facturada += inv_line.quantity
                    #print("Cantidad facturada: {0}".format(cantidad_facturada))
        self.cantidad_facturada = cantidad_facturada

    type_computed = fields.Selection(string='Filed Label', related="invoice_id.type")
    cantidad_devuelta = fields.Float(string='Cantidad devuelta', digits=dp.get_precision('Account'))
    cantidad_facturada = fields.Float(string='Cantidad Facturada', compute=_computed_cant_facturada,
                                      digits=dp.get_precision('Account'))





class NotasCreditoCliente(models.Model):
    #ANS 
    _inherit = ['account.invoice']
    tipo = fields.Selection([
        ('nota_credito_cliente', 'Nota de Credito Cliente'),
        ('nota_credito_proveedor', 'Nota de Credito Proveedor'),#RERV nota credito proveedor agregado
    ])
	#RERV restric agregado para que no se pueda elimnar si tiene algo asociado
    factura = fields.Many2one('account.invoice',domain=[('id','=',0)], ondelete='restrict')#,domain="[('state','=','open'),('type','=','out_invoice'),('residual','!=',0 )]"
    description = fields.Char(required=False)
    establecimiento = fields.Char(size=3)
    puntoemision = fields.Char(size=3)
    secuencial = fields.Char(size=9)
    establecimiento_h = fields.Char(size=3)
    puntoemision_h = fields.Char(size=3)
    secuencial_h = fields.Char(size=9)
    codigo_autorizacion = fields.Char(size=43)
    is_filtro = fields.Boolean()
    alumno_id = fields.Many2one(comodel_name='res.partner', string='Alumno')
    escuela = fields.Boolean(string="Estructura escolar",default='True')
    baseivacero = fields.Float(compute='calculando', digits_compute=dp.get_precision('Account'), store=True ,string='Base Iva Cero', multi='all')
    baseivanocero = fields.Float(compute='calculando', digits_compute=dp.get_precision('Account'), store=True, string='Base Iva No Cero', multi='all')


    #RERV
    def default_get(self, cr, uid, fields, context=None):
        res = super(NotasCreditoCliente, self).default_get(cr, uid, fields, context=context)
        if 'type' in res:
            if res['type'] == 'out_refund':
                res.update({'tipo': 'nota_credito_cliente', 'number': 'Nota De Credito Cliente'})
            elif res['type'] == 'in_refund':
                res.update({'tipo': 'nota_credito_proveedor', 'number': 'Nota De Credito Proveedor'})
        return res

    #RERV
    def calculando(self, cr, uid, ids, name, args, context={}):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'baseivacero' : 0.0,
                'baseivanocero' : 0.0,
                'baseninguniva': 0.0,
                'totalretencion': 0.0,
                'total': 0.0,
                'descuento': 0.0,
                'iva':0.0,
            }
            # CAMBIO U1 18-02-2020
            for line in invoice.invoice_line:
                for tax in line.invoice_line_tax_id:
                    if tax.type == 'none':
                        res[invoice.id]['baseninguniva'] += line.price_subtotal
                    if str(tax.amount) == '0.12':
                        res[invoice.id]['baseivanocero'] += line.price_subtotal
                    if str(tax.amount) == '0.0':
                        res[invoice.id]['baseivacero'] += line.price_subtotal 
            
                res[invoice.id]['total'] += line.total
                #res[invoice.id]['descuento'] += line.descuento
                #res[invoice.id]['amount_untaxed'] += line.price_subtotal
                #res[invoice.id]['iva'] += line.valor_iva
            for line in invoice.tax_line:
                if line.amount > 0:
                    res[invoice.id]['amount_tax'] += line.amount
            for line in invoice.tax_line:
                #------------------------------------------- if line.amount > 0:
                    #------------- res[invoice.id]['baseivanocero'] += line.base
                #------------------------------------------ if line.amount == 0:
                    #--------------- res[invoice.id]['baseivacero'] += line.base
                if line.amount < 0:
                    res[invoice.id]['descuento'] += line.amount
            # CAMBIO U1 18-02-2020    

            for line in invoice.retencion_line:
                res[invoice.id]['totalretencion'] += line.amount
            
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']

        return res

    @api.multi
    def importar_nota_credito(self):
        for nota_id in self:
            dic = {
                'compania_cod': "DW",
                "compania_div": "DW",
                "tipo_movimiento": "D",
                "inventario_cod": "PT",
                "codigo_interno": nota_id.id,
                "tipo_factura_cod": "NCS",
                "tipo_factura_des": "Nota de crédito",
                "observacion": nota_id.comment,
                "identificacion_empresa": self.env.user.company_id.vat,
                "direccion_empresa": self.env.user.company_id.street,
                "nombre_cia": self.env.user.company_id.name,
                "cli_iden": nota_id.partner_id.vat,
                "cli_tiden": nota_id.partner_id.tipoid,
                "nombre_cliente": nota_id.partner_id.name,
                "direccion_cliente": nota_id.partner_id.street,
                "correo_electronico": nota_id.partner_id.email,
                "numero_credito": nota_id.numerofac,
                "fecha": nota_id.date_invoice,
                "coddocumento_afecta": nota_id.factura.numerofac,
                "tipodocumento_afecta": "F",
                "impuesto_porcentaje": "",
                "subtotal": nota_id.amount_untaxed,
                "descuento": nota_id.subtotal_descuento,
                "impuesto_monto": nota_id.amount_tax,
                "total": nota_id.amount_total,
                "comp_id": "",
            }
            self.importar_ncredito_electronica_det(dic['fecha'],dic['compania_div']
                                                   ,dic['tipo_movimiento'],dic['inventario_cod'],dic['codigo_interno']
                                                   ,dic['observacion'],dic['coddocumento_afecta'],nota_id.invoice_line)
    @api.multi
    def importar_ncredito_electronica_det(self,fecha,coddiv,tipomov,codinv,codfac,comment,numerofac,line_detalle):
        for line in line_detalle:
            dic = {
                'compania_cod': coddiv,
                "compania_div": coddiv,
                "tipo_movimiento": tipomov,
                "inventario_cod": codinv,
                "codigo_interno": codfac,
                "tipo_factura_cod": "NCS",
                "tipo_factura_des": "Nota de crédito",
                "observacion": comment,
                "fecha": fecha,
                "coddocumento_afecta": numerofac,
                "tipodocumento_afecta": "F",
                "articulo_codigo": line.id,
                "articulo_descripcion": line.name,
                "codigo_impuesto_sri": line.invoice_line_tax_id.id,
                "porcentaje_impuesto": "",
                "lote":"*",
                "cantidad_inventario": line.quantity,
                "unidad": line.uos_id,
                "precio": line.price_unit,
                "total" : line.price_subtotal,
                "descuento": 0.00,
                "ncredito_id": self.id
            }



    @api.multi
    def onchange_partner_id_c(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False, company_id=False):
        account_id = False
        payment_term_id = False
        fiscal_position = False
        bank_id = False

        p = self.env['res.partner'].browse(partner_id or False)
        if partner_id:
            rec_account = p.property_account_receivable
            pay_account = p.property_account_payable
            if company_id:
                if p.property_account_receivable.company_id and \
                        p.property_account_receivable.company_id.id != company_id and \
                        p.property_account_payable.company_id and \
                        p.property_account_payable.company_id.id != company_id:
                    prop = self.env['ir.property']
                    rec_dom = [('name', '=', 'property_account_receivable'), ('company_id', '=', company_id)]
                    pay_dom = [('name', '=', 'property_account_payable'), ('company_id', '=', company_id)]
                    res_dom = [('res_id', '=', 'res.partner,%s' % partner_id)]
                    rec_prop = prop.search(rec_dom + res_dom) or prop.search(rec_dom)
                    pay_prop = prop.search(pay_dom + res_dom) or prop.search(pay_dom)
                    rec_account = rec_prop.get_by_record(rec_prop)
                    pay_account = pay_prop.get_by_record(pay_prop)
                    if not rec_account and not pay_account:
                        action = self.env.ref('account.action_account_config')
                        msg = _(
                            'Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                        raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

            if type in ('out_invoice', 'out_refund'):
                account_id = rec_account.id
                payment_term_id = p.property_payment_term.id
            else:
                account_id = pay_account.id
                payment_term_id = p.property_supplier_payment_term.id
            fiscal_position = p.property_account_position.id

        result = {'value': {
            'account_id': account_id,
            'payment_term': payment_term_id,
            'fiscal_position': fiscal_position,
        }}

        if type in ('in_invoice', 'out_refund'):
            bank_ids = p.commercial_partner_id.bank_ids
            bank_id = bank_ids[0].id if bank_ids else False
            result['value']['partner_bank_id'] = bank_id
            result['domain'] = {'partner_bank_id': [('id', 'in', bank_ids.ids)]}

        if payment_term != payment_term_id:
            if payment_term_id:
                to_update = self.onchange_payment_term_date_invoice(payment_term_id, date_invoice)
                result['value'].update(to_update.get('value', {}))
            else:
                result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(bank_id)
            result['value'].update(to_update.get('value', {}))
        if type == 'out_refund':
            facturas = self.env['account.invoice'].search([('state','=','open')
                                                          ,('type','=','out_invoice')
                                                          ,('residual','!=',0)
                                                          ,('partner_id','=',partner_id)])
            _logger.info('Facturas :'+str(facturas.ids))
            if facturas:
                result['domain'] = {'factura': [('id','in',facturas.ids)]}
                _logger.info('Facturas :' + str(self.factura))

        result2 = {}
        if partner_id:
            p = self.env['res.partner'].browse(partner_id)
            result2 = {
                'num_autfac': p.num_autfac,
                'venc_autfac': p.venc_autfac,
                'num_autimpfac': p.num_autimpfac,
            }
        result['value'].update(result2)
        #RERV Domain agregado para alumno
        domain_alumno = self.onchange_domain_alumno(partner_id)
        result['domain'].update(domain_alumno)
        return result

    @api.multi
    # @api.onchange('invoice_line')
    def _onchange_invoice_line_p(invoice_id):
        print("================ inchangeinvoice_line> " + str(invoice_id))

    #@api.constrains('secuencial', 'puntoemision', 'establecimiento', 'Numautorizacion')
    def _verificar_campos(self):
        for record in self:
            if re.sfearch('[a-zA-Z]', record.secuencial):
                raise ValidationError("Este campo solo acepta valores numericos: Secuencial ")
            if re.search('[a-zA-Z]', record.puntoemision):
                raise ValidationError("Este campo solo acepta valores numericos: Punto de emision ")
            if re.search('[a-zA-Z]', record.establecimiento):
                raise ValidationError("Este campo solo acepta valores numericos: Establecimiento ")
            if re.search('[a-zA-Z]', record.Numautorizacion):
                raise ValidationError("Este campo solo acepta valores numericos: Autorizacion ")
    
    @api.multi
    def action_move_create(self):
        self.button_reset_taxes()
        #print 'dentro de action_move_create*************'
        if self.period(self.id) == 1:
            raise ValidationError('Fecha de comprobante no pertenece al periodo declarado')

        """ Creates invoice related analytics and financial move lines """

        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']
        retencion_line = self.env['fiscal.retencion.ln']

        for inv in self:
            # cambios de NELIO CIGUENCIA
			#RERV if modificado para que ingrese solo en nota de credito
            if (inv.type == 'out_refund' and inv.tipo == 'nota_credito_cliente') or (inv.type == 'in_refund' and inv.tipo == 'nota_credito_proveedor'):
                for line in inv.invoice_line:
                    if line.quantity == 0.000:
                        line.unlink()
                for line in inv.invoice_line:
                    total_resta = 0.00
                    #RERV modificado para que haga la resta bien
                    total_resta = float(line.cantidad_facturada - (line.cantidad_devuelta + line.quantity))
                    cantidad_restante = float(line.cantidad_facturada - line.cantidad_devuelta)
                    if total_resta < 0:
                        raise except_orm(_('Error!'), _(
                            "La cantidad de {0} es mayor a la cantidad restante. (Quedan {1})".format(
                                line.product_id.name, int(cantidad_restante))))
            # fin cambios de NELIO CIGUENCIA
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                from openerp import fields
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv)
            inv.check_tax_lines(compute_taxes)

            if inv.type == 'in_invoice':
                if not self.numeroret:
                    res = self.calcularSecuencial(inv)
                    ## anibal
                    #print 'tranquilos ya regrese con secuencial = ', res
                    inv.write(res)
                    # self.actualiza_secuencial(inv)

            if inv.type == 'out_invoice':
                ## anibal
                #print 'voy a calcular secuencial de factura ', self.numerofac
                ## anibal
                #print 'res = self.calcularSecuencial(inv) '
                if not self.numerofac:
					#RERV comentado me enceraba punto emision
                    res = self.calcularSecuencial(inv)
                    #print 'mira reeeeeeeeeeeeessss ', res
                    inv.write(res)
                    ## pongo esta linea a ver que pasa
                    self.actualiza_secuencial_factura(inv)
                    ## fin de   pongo esta linea a ver que pasa

            if inv.type == 'out_refund':
                ## anibal
                print 'voy a calcular secuencial de factura ', self.numerofac
                ## anibal
                #print 'res = self.calcularSecuencial(inv) '
                res = self.calcularSecuencial(inv)
                if not self.numerofac:
                    #RERV comentado me enceraba punto emision
                    # res = self.calcularSecuencial(inv)
                    print 'mira reeeeeeeeeeeeessss ', res
                    # inv.write(res)
                    ## pongo esta linea a ver que pasa
                    self.actualiza_secuencial_factura(inv)
                    ## fin de   pongo esta linea a ver que pasa



            if self.env['res.users'].has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (
                        inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _(
                        'Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _(
                        "Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type == 'in_invoice':
                iml += retencion_line.move_line_get(inv.id)
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.name or inv.supplier_invoice_number or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False
                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                                 _(
                                     'You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            move = account_move.with_context(ctx).create(move_vals)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            #CAMBIOS NELIO PARA LA RECONCILACION DE NOTAS DE CREDITO
			#RERV if agregado para que solo entre en nota de credito
            if (inv.type == 'out_refund' and inv.tipo == 'nota_credito_cliente') or (inv.type == 'in_refund' and inv.tipo == 'nota_credito_proveedor'):
                self.reconciliar(self.env.cr, self.env.uid, self.ids, self.env.context)
        self._log_event()
        return True


    @api.multi
    @api.onchange('factura')
    def mostrar_monto(self):
        self.partner_id = self.factura.partner_id
        self.invoice_line = [(6,0,[])]
        lista = []
        for line in self.factura.invoice_line:
            values = {
                'type': 'src',
                'name': line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'quantity': float(0),
                'price': line.price_subtotal,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'cantidad_devuelta': self.compute_cant_devuelta(line.product_id.id),
                'uos_id': line.uos_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                'invoice_line_tax_id': line.invoice_line_tax_id,
            }
            lista.append((0, 0, values))
        # print("Ids: {0}".format(line.id))
        self.invoice_line = lista
        self.journal_id = self.factura.journal_id
        self.account_id = self.factura.account_id.id
        # self.residual = self.factura.residual
        # self.origin = self.factura.number
        self.period_id = self.factura.period_id
        self.fiscal_position = self.factura.fiscal_position
        #RERV If agregado para que solo entre en nota credito proveedor
        if self.type == 'in_refund' and self.tipo == 'nota_credito_proveedor':
            self.establecimiento_h = self.factura.establecimiento
            self.puntoemision_h = self.factura.puntoemision
            self.secuencial_h = self.factura.secuencial

    # print(self.monto)

    @api.multi
    def button_reset_taxes_p(self, invoice):
        account_invoice_tax = self.env['account.invoice.tax']
        ctx = dict(self._context)
        #print("Esta ejecutando elfor")
        self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (invoice.id,))
        self.invalidate_cache()
        partner = invoice.partner_id
        if partner.lang:
            ctx['lang'] = partner.lang
        for taxe in account_invoice_tax.compute(invoice.with_context(ctx)).values():
            account_invoice_tax.create(taxe)
        # dummy write on self to trigger recomputations
        return self.with_context(ctx).write({'invoice_line': []})

    @api.model
    def create(self, values):
        #values['tipo'] = 'nota_credito_cliente'
        # _logger.info('valor a guardar'+str(self.type))
        record = super(NotasCreditoCliente, self).create(values)
        if 'tipo' in values:
            if values['tipo'] == 'nota_credito_cliente':
                self._cr.execute('select "id" from "account_invoice" order by "id" desc limit 1')
                last_id = self._cr.fetchone()
                invoices_obj = self.env['account.invoice'].search([('id', '=', last_id)])[0]
                self.env['account.invoice'].button_reset_taxes_p(invoices_obj)
        return record

    @api.multi
    def compute_cant_devuelta(self, id):
        cantidad_devuelta = 0
        # Nota de creditos de la factura

        if self.type == 'in_refund' or self.type == 'out_refund':
            invoices_obj = self.env['account.invoice'].search(
                [('type', '=', 'out_refund'), ('factura.id', '=', self.factura.id), ('state', '=', 'paid')])
            # print("Fuera del if {0}".format(invoices_obj))
            # print("ID DE LA FACTURA {0}".format(self.invoice_id.factura.id))
            if invoices_obj:
                # print("Dentro del If xD")
                for ntc in invoices_obj:
                    for invoice_line in ntc.invoice_line:
                        if invoice_line.product_id.id == id:
                            cantidad_devuelta += invoice_line.quantity

                    # print("===================================== {0}".format(ntc.number))
        # print("Cant devuelta: {0}".format(cantidad_devuelta))
        return cantidad_devuelta

    @api.one
    def write(self, vals):
        _logger.info('valor a guardar' + str(vals))
        record = super(NotasCreditoCliente, self).write(vals)
        #print(record)
        if self.type == 'in_refund':
            invoices_obj = self.env['account.invoice'].search([('id', '=', self.id)])[0]
            self.env['account.invoice'].button_reset_taxes_p(invoices_obj)
            #print(invoices_obj.id)
        # self.button_reset_taxes_p(self.id,self.partner_id.id)

        return record

    @api.multi
    def cancelar_refund(self):
        context = {}
        factura_cancelada = False
        pago_cancelado = False
        voucher = None
        voucher_obj = self.pool.get('account.voucher')
        self._cr.execute(
            "SELECT v.id FROM account_voucher as v join account_voucher_line as vl on v.id = vl.voucher_id where vl.name = %s",
            (self.number,))

        voucher = self._cr.fetchone()
        _logger.info("ESTE::---------------"+str(self.number))
        voucher_lines_ids = []
        if voucher:
            # print("Voucher id: "+ str(voucher))
            pago_cancelado = voucher_obj.cancel_voucher(self._cr, self._uid, voucher, context=context)
        if pago_cancelado:
            # print("Factura Cancelada")
            factura_cancelada = self.action_cancel_draft()

    #RERV metodo modificado, cuando es nota de credito pasa a pagado
    @api.multi
    def action_cancel_draft(self):
        if ((self.env.context.get('type', False) == 'out_refund' and self.env.context.get('tipo', False) == 'nota_credito_cliente')
            or (self.env.context.get('type', False) == 'in_refund' and self.env.context.get('tipo', False) == 'nota_credito_proveedor')):
            self.write({'state': 'cancel'})
            self.delete_workflow()
            self.create_workflow()
        else:
            super(NotasCreditoCliente, self).action_cancel_draft()
        return True

    @api.multi
    def reconciliar(self, cr, uid, ids, context=None):
        res_currency = self.pool.get('res.currency')
        voucher_obj = self.pool.get('account.voucher')
        journal_obj_pool = self.pool.get('account.journal')
        voucher_line_pool = self.pool.get('account.voucher.line')
        move_lines = []

        for inv in self.browse(ids):
            journal_id = journal_obj_pool.search(cr, uid, [('nota_credito', '=', True)], limit=1)
            if not journal_id:
                raise osv.except_osv("Error Journal","No existe diario para realizar pagos de notas de credito")
            # Diario
            journal = journal_obj_pool.browse(cr, uid, journal_id, context=context)
            # Moneda
            company_currency = currency_id = journal.company_id.currency_id.id

            #print("Journal: " + str(journal))
            invoice_moves_ids = self.pool.get('account.invoice').search(cr, uid,
                                                                        [('id', 'in', [inv.id, inv.factura.id])])
            invoice_moves_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_moves_ids, context=context)
            vourcher_vals = {
                'date': inv.date_invoice,
                'journal_id': journal.id,
                'account_id': journal.default_credit_account_id.id,
                'period_id': inv.period_id.id,
                'currency_id': inv.currency_id.id,
                'company_id': inv.company_id.id,
                'state': 'draft',
                'amount': 0.0,
                'partner_id': inv.partner_id.id,
                'payment_option': 'without_writeoff',
                'type': 'receipt',
                'pay_now': 'pay_now'
            }

            voucher_id = self.pool.get('account.voucher').create(cr, uid, vourcher_vals, context=context)
            for facturas in invoice_moves_obj:
                id = None
                account = None
                monto_original = None
                monto_no_reconciliado = None
                date = None
                date_due = None
                res = {}
                for line in facturas.move_id.line_id:
					#RERV agregado payable para que ingrese cunado es proveedor
                    if line.account_id.type == 'receivable' or line.account_id.type == 'payable':
                        id = line.id
                        account = line.account_id.id
                        monto_original = res_currency.compute(cr, uid, company_currency, currency_id,
                                                              line.credit or line.debit or 0.0, context=context)
                        monto_no_reconciliado = res_currency.compute(cr, uid, company_currency, currency_id,
                                                                     abs(line.amount_residual), context=context)
                        date = line.date
                        date_due = line.date_maturity

                        res = {
                            'voucher_id': voucher_id,
                            'name': facturas.move_id.name,
                            'move_line_id': id,
                            'account_id': account,
                            'amount_original': monto_original,
                            'amount': inv.amount_total,
                            'amount_unreconciled': monto_no_reconciliado,
                            'date_original': date,
                            'date_due': date_due,
                            'currency_id': currency_id
                        }
				#RERV if modificado, facturas que ingresan credito cr, que salen dr debito
                if facturas.type in  ['out_refund', 'out_invoice']:
                    res['type'] = 'cr'
                else:
                    res['type'] = 'dr'
                voucher_line_pool.create(cr, uid, res, context=context)
            voucher_obj.action_move_line_create(cr, uid, [voucher_id], context=None)
            inv.state = 'paid'

    #RERV domain alumno
    @api.onchange('alumno_id')
    def onchange_domain_cliente(self):
        if self.alumno_id:
            if self.alumno_id.parent_id:
                result = {}
                result['domain'] = {'partner_id': [('id', '=', self.alumno_id.parent_id.id)]}
                return result
            else:
                result = {}
                result['domain'] = {'partner_id': [('id', '=', 0)]}
                return result                
        else:
            result = {}
            result['domain'] = {'partner_id': [('customer', '=', True), ('tipo', '!=', 'H')]}
            return result

    #RERV domain cliente
    def onchange_domain_alumno(self, partner_id):
        partner_id = self.env['res.partner'].search([('id', '=', partner_id)])
        if partner_id:
            if partner_id.child_ids:
                result = {'alumno_id': [('id', 'in', partner_id.child_ids.ids)]}
                return result
            else:
                result = {'alumno_id': [('id', '=', 0)]}
                return result    
        else:
            result = {'alumno_id': [('customer', '=', True), ('tipo', '=', 'H')]}
            return result

    #RERV
    @api.multi
    def validar_nota_credito_cliente(self):
        self.validar_nuevo()

    #RERV
    @api.multi
    def validar_nota_credito_proveedor(self):
        self.validar_nuevo()

class InheritJournal(models.Model):
	_inherit = 'account.journal'
	nota_credito = fields.Boolean(string='nota_credito')


