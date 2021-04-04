# -*- coding: utf-8 -*-

from openerp import models,fields,api,_
import logging
import base64
import io
import time
import commands
import os
import datetime
from datetime import datetime
from openerp.exceptions import ValidationError, except_orm
import reporte_concilacion
from openerp.osv.osv import osv

_logger = logging.getLogger(__name__)
from tempfile import *
import openerp.addons.decimal_precision as dp
class Concilacion(models.Model):
    _name = "concilacion.bancaria.ans"

    binario_txt = fields.Binary(string="Archivo a Cargar")
    nombre_txt = fields.Char(string="Nombre txt")
    saldo = fields.Float('Saldo Inicial',digits=(12,2))


    @api.multi
    def validacion(self):
        obj = self.env['extracto.bancario.ans'].search(['|',('state','=','pre'),('state','=','draft')])
        if not obj:
            self.import_field()
            return True
        else:
            raise ValidationError('Debe conciliar el registro anterior para poder ingresar uno nuevo')
            return False
    @api.multi
    def import_field(self):
        fielobj = TemporaryFile("w+b")
        fielobj.write(base64.decodestring(self.binario_txt))
        fielobj.seek(0)
        i = 1
        banco = ""
        cuenta = ""
        fecha_inicial = ""
        fecha_final = ""
        nombre_cliente = ""
        nombre_oficial = ""
        fecha = ""
        ref = ""
        lugar = ""
        detalle = ""
        secuencial = ""
        signo = ""
        valor = ""
        saldo_d = ""
        saldo_c = ""
        descripcion = ""

        obj_extracto = self.env['extracto.bancario.ans']
        obj_parametro = self.env['extracto.conf.ans'].search([])
        for l in fielobj.readlines():
            dato = l.split("\t")
            if i == 1:
                banco = dato[0]
            if i == 2:
                cuenta = dato[1].split("'")[1]
            if i == 3:
                fecha_inicial = dato[1].split("'")[1]
                #_logger.info(str(fecha_inicial) + " "+str(i) )
            if i == 4:
                fecha_final = dato[1].split("'")[1]
                #_logger.info(str(fecha_inicial) + " " + str(i))

            if i == 5:
                nombre_cliente = dato[1]
                #_logger.info(str(fecha_inicial) + " " + str(i))

            if i == 6:
                nombre_oficial = dato[1]
                #_logger.info(str(fecha_inicial) + " " + str(i))

            if i == 8:
                #_logger.info(str(fecha_inicial) + " " + str(i))

                fecha_inicial = datetime.strptime(fecha_inicial, '%m/%d/%Y').date()
                fecha_final = datetime.strptime(fecha_final, '%m/%d/%Y').date()
                obj_consulta = self.env['extracto.bancario.ans'].search([('banco','=',str(banco)),('fecha_inicial','>=',str(fecha_inicial)),('fecha_final','<=',str(fecha_final))])
                if obj_consulta:
                    i += 1
                    raise ValidationError('Ya existe Valor')
                    continue
                else:
                    obj_xls = obj_extracto.create({'banco': banco, 'cuenta': cuenta,
                                               'fecha_inicial': fecha_inicial,
                                               'fecha_final': fecha_final,
                                               'nombre_cliente': nombre_cliente,
                                               'nombre_oficial': nombre_oficial,
                                               'archivo':  self.binario_txt,
                                               'saldo_inicial': self.saldo,
                                               'texto': 'Archivo.txt',
                                                })
            if i >= 9:
                id = dato[0]
                fecha = dato[1]
                fecha = datetime.strptime(fecha, '%m/%d/%Y').date()
                if not fecha_inicial <= fecha <= fecha_final:
                    raise ValidationError('Debe corregir bien la fecha del registro ', dato[0])
                ref = dato[2]
                lugar = dato[3]
                detalle = dato[4].split("'")[1]
                secuencial = dato[5].split("'")[1]
                signo = dato[6]
                valor = float(dato[7].replace(",",""))
                saldo_d = float(dato[8].replace(",",""))
                saldo_c = float(dato[9].replace(",",""))
                descripcion = dato[10]

                obj_consulta = self.env['detalle.extracto.bancario.ans'].search([('numero','=',id),('fecha','=',str(fecha))])
                if obj_consulta:
                    i += 1
                    raise ValidationError('Ya existe Valor')
                    break
                else:
                    tipo = 0
                    for j in obj_parametro:
                         if j.cadena_bus in descripcion:
                            tipo = j.id

                    if tipo == 0:
                        raise ValidationError('No se pudo indentificar a este campo como movimiento: '+str(descripcion))
                        break



                    obj_detalle = self.env['detalle.extracto.bancario.ans'].create({
                        'numero': id,
                        'fecha': fecha,
                        'ref': ref,
                        'lugar': lugar,
                        'detalle': detalle,
                        'secuencial': secuencial,
                        'signo': signo,
                        'valor': valor,
                        'saldo_d': saldo_d,
                        'saldo_c': saldo_c,
                        'descripcion':descripcion,
                        'extracto_id': obj_xls.id,
                        'parametro_id':tipo,
                    })
            i += 1
        return {'name':_('Concilacion'),'view_type': 'form'
            ,'view_mode':'tree,form'
            ,'res_model':'extracto.bancario.ans'
            ,'view_id':False
            , 'type': 'ir.actions.act_window'
                ,'target':'current'
                ,'nodestroy': True}

class Extracto_bancario(models.Model):
    _name = "extracto.bancario.ans"

    def _get_all_invoice(self):
        return self.env['account.move'].search([('state','=','posted'),('estado_concilacion','=','no')])

    def _get_all_move_2(self):
        id_journal = []
        for l in self.extracto_line_debito:
            if not id_journal:
                id_journal.append(l.parametro_id.journal_id.id)
            else:
                if not id_journal == l.parametro_id.journal_id.id:
                    id_journal.append(l.parametro_id.journal_id.id)
        obj = self.env['account.move'].search([('state','=','posted')
                                                  ,('estado_concilacion','=','no'),('journal_id','in',id_journal)])
        return obj
    def _get_all_debitos(self):
        id_journal = []
        for l in self.extracto_line_debito:
            if not id_journal:
                id_journal.append(l.parametro_id.journal_id.id)
            else:
                if not id_journal == l.parametro_id.journal_id.id:
                    id_journal.append(l.parametro_id.journal_id.id)
        obj = self.env['account.move'].search(
            [('state', '=', 'posted'),('date', '<', self.fecha_final),"|", ('estado_concilacion', '=', 'no'),('estado_concilacion', '=', 'pre'), ('journal_id', 'in', id_journal)])
        _logger.info(obj)
        return obj
    def _get_all_creditos(self):
        id_journal = []
        for l in self.extracto_line_credito:
            if not id_journal:
                id_journal.append(l.parametro_id.journal_id.id)
            else:
                if not id_journal == l.parametro_id.journal_id.id:
                    id_journal.append(l.parametro_id.journal_id.id)
        obj = self.env['account.move'].search(
            [('state', '=', 'posted'),('date', '<', self.fecha_final), "|", ('estado_concilacion', '=', 'no'),('estado_concilacion', '=', 'pre'), ('journal_id', 'in', id_journal)])
        return obj
    def _get_all_depositos(self):
        id_journal = []
        for l in self.extracto_line_depositos:
            if not id_journal:
                id_journal.append(l.parametro_id.journal_id.id)
            else:
                if not id_journal == l.parametro_id.journal_id.id:
                    id_journal.append(l.parametro_id.journal_id.id)
        obj = self.env['account.move'].search(
            [('state', '=', 'posted'),('date', '<', self.fecha_final),"|", ('estado_concilacion', '=', 'no'),('estado_concilacion', '=', 'pre'), ('journal_id', 'in', id_journal)])
        return obj
    def _get_all_cheques(self):
        id_journal = []
        for l in self.extracto_line_cheques:
            if not id_journal:
                id_journal.append(l.parametro_id.journal_id.id)
            else:
                if not id_journal == l.parametro_id.journal_id.id:
                    id_journal.append(l.parametro_id.journal_id.id)
        obj = self.env['account.move'].search(
            [('state', '=', 'posted'),('date', '<', self.fecha_final), "|", ('estado_concilacion', '=', 'no'),('estado_concilacion', '=', 'pre'), ('journal_id', 'in', id_journal)])
        return obj

    def _get_all_ordenes(self):
        id_journal = []
        for l in self.extracto_line_ordenes:
            if not id_journal:
                id_journal.append(l.parametro_id.journal_id.id)
            else:
                if not id_journal == l.parametro_id.journal_id.id:
                    id_journal.append(l.parametro_id.journal_id.id)
        obj = self.env['account.move'].search(
            [('state', '=', 'posted'),('date', '<', self.fecha_final), "|", ('estado_concilacion', '=', 'no'),('estado_concilacion', '=', 'pre'), ('journal_id', 'in', id_journal)])
        return obj

    def _get_account(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False),
                                                                     ('company_id', '=', user.company_id.id)], limit=1)
        return accounts and accounts[0] or False
    
    def _obtener_mes(self):
	for obj in self:
   	   fecha = datetime.strptime(obj.fecha_inicial, '%Y-%m-%d')
	   mes = fecha.date()
	   #mes = obj.fecha_inicial.strftime("%B")
	   #ano = mes.strftime("%Y")
	   #mes = self.mes_actual(mes.strftime("%B"))
	   obj.ano_periodo = mes.strftime("%Y")
	   mes = self.mes_actual(mes.strftime("%B"))
	   obj.mes_periodo = mes

    def mes_actual(self,date):
	meses = {'January':'Enero','February':'Febrero','March':'Marzo','April':'Abril','May':'Mayo','June':'Junio'
		,'July':'Julio','August':'Agosto','September':'Septiembe','October':'Octubre','November':'Noviembre','December':'Diciembre'}
	return meses[date]	   

    banco = fields.Char(readonly=True)
    cuenta = fields.Char(readonly=True)
    fecha_inicial = fields.Date(readonly=True)
    fecha_final = fields.Date(readonly=True)
    nombre_cliente = fields.Char(readonly=True)
    nombre_oficial = fields.Char(readonly=True)
    estado = fields.Selection([('1','Conciliado'),('2','No Conciliado')], default="2")
    archivo = fields.Binary(string="Archivo Subido")
    texto = fields.Char(string='Nombre Archivo')
    mes_periodo = fields.Char(string='Mes',readonly=True,compute=_obtener_mes,store=False)
    ano_periodo = fields.Char(string='Año',readonly=True,compute=_obtener_mes,store=False)
    saldo_inicial = fields.Float('Saldo Inicial',digits=(12,2))
    extracto_line_debito = fields.One2many('detalle.extracto.bancario.ans','extracto_id'
                                    ,domain=[('parametro_id.tipo_mov','=','ND')],copy=True)
    extracto_line_credito = fields.One2many('detalle.extracto.bancario.ans','extracto_id'
                                            ,domain=[('parametro_id.tipo_mov','=','NC')],copy=True)
    extracto_line_depositos = fields.One2many('detalle.extracto.bancario.ans','extracto_id'
                                            ,domain=[('parametro_id.tipo_mov','=','DEP')],copy=True)
    extracto_line_cheques = fields.One2many('detalle.extracto.bancario.ans', 'extracto_id'
                                              , domain=[('parametro_id.tipo_mov', '=', 'CHE')], copy=True)
    extracto_line_ordenes = fields.One2many('detalle.extracto.bancario.ans', 'extracto_id'
                                            , domain=[('parametro_id.tipo_mov', '=', 'ORD')], copy=True)

    chart_account_id = fields.Many2one('account.account', string='Plan de Cuentas', required=True,
                                        domain=[('parent_id', '=', False)])
    nombre_xls = fields.Char(string="Nombre del Archivo")
    binario_xls = fields.Binary(sting="Archivo Del Binario")
    nombre_txt = fields.Char(string="Nombre del Pdf")
    binario_pdf = fields.Binary(sting="Archivo PDF")
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('pre', 'Abierto'),
        ('con', 'Conciliado'),
        ('error', 'Error'),
        ('cancel', 'Cancelled'),
    ], string='Estado', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    _defaults = {
        'chart_account_id': _get_account
    }


    move_id_credito = fields.Many2many('account.move',relation="custom_account_move_credito",column1="id"
                                       ,column2="move_id_credito",string="Movimientos Creditos",ondelete="restrict")

    move_id_debito = fields.Many2many('account.move',string="Movimientos",copy=True,ondelete="restrict")

    move_id_deposito = fields.Many2many('account.move',relation="custom_account_move_deposito"
                                         ,column1="id",column2="move_id_deposito",string="Depositos",copy=True,ondelete="restrict")

    move_id_ordenes = fields.Many2many('account.move', relation="custom_account_move_ordenes"
                                        , column1="id", column2="move_id_ordenes", string="Ordenes de 						Pago",copy=True,ondelete="restrict")

    #move_id_cheques = fields.Many2many('account.voucher',string="Cheques"
                                       #,copy=True,ondelete="restrict")
    
    move_id_cheques = fields.Many2many('account.move',relation="custom_account_move_cheques",string="Cheques"
                                       ,column1="id", column2="move_id_cheques",copy=True,ondelete="restrict")
    """
    @api.multi
    def unlink(self):
        if self.state == 'pre':
            raise ValidationError('No se puede eliminar tiene registros pendientes')
        else:
            return super(Extracto_bancario, self).unlink()
    
    @api.onchange('move_id_debito')
    @api.multi
    def enviar_datos(self):
        id = []
        valor = 0
        ident = 0
        for obj in self.move_id_debito:
            _logger.info(self.move_id_debito[ident].detalle_extracto)
            for o in obj:
                for j in o.detalle_extracto:
                    for l in j:
                        valor += l.valor
                if valor > o.amount:
                    self.move_id_debito[ident].write({'detalle_extracto': [(6,False,[])]})
                    warning = {'title':'Advertencia!','message':'Debe corregir valores'}
                    return {'warning':warning}
                valor = 0
            ident += 1
    """
    @api.multi
    def write(self, vals):

        estado = False
        if 'move_id_debito' in vals:
            repetidores = []
            indetificador = []
	    for obj in self.move_id_debito:
		for l in obj.detalle_extracto:
		   l.write({'error_estado':''})
            for l in vals['move_id_debito']:
                id = l[1]
                if len(l) > 2:
                    if l[2] != False:
                       indentificadores = []
                       if 'detalle_extracto' in l[2]:
                           for j in l[2]['detalle_extracto']:
                               if j[2]:
                                   valor = 0
                                   for k in self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])]):
                                       indentificadores.append(k.id)
                                       valor += k.valor
                                   consulta = self.env['account.move'].search([('id', '=', id)])
				   consultar = self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])])
                                   consulta.write({'estado_error': 'si'})
                                   #e = "pre"
                                   estado = "pre"
				   #Los preconcilias
				   l[2]['estado_concilacion'] = "pre"
                                   if consulta.total_conciliar == valor and valor != 0:
                                        l[2]['estado_concilacion'] = "pre"
					_logger.info("estado 1 : "+str(estado))
				   #Validar valores diferentes
				   if consulta.total_conciliar != valor and valor != 0 :
				       #l[2]['estado_concilacion'] = "pre"
                                       l[2]['estado_error'] = "red"
                                       #self.state = "error"
                                       estado = "error"
				       _logger.info("estado 2 : "+str(estado))
                                   # VALIDA REPETICIONES
				   for w in j[2]:
		                           if not w in repetidores:
						_logger.info("j2: "+str(j[2]))
						repetidores.append(w)
		                                indetificador.append(id)
						_logger.info("REPETIDOR :"+str(repetidores)+ "  Identificador "+str(indetificador))
		                           else:
		                                #consulta.write({'estado_error': 'azul'})
						#l[2]['estado_concilacion'] = "no"
						l[2]['estado_error'] = "azul"
						for c in consultar:
						    c.write({'error_estado': 'Documentos repetidos'})
		                                #self.state = "error"
		                                estado = "error"
		                                identi = 0
		                                for mov in repetidores:
		                                   if j[2] == mov and indetificador[identi] != id:
		                                       consulta = self.env['account.move'].search(
		                                           [('id', '=', indetificador[identi])])
		                                       consulta.write({'estado_error': 'azul'})
						       for c in consulta:
							  c.write({'error_estado': 'Documentos repetidos'})
		                                   identi += 1
						_logger.info("estado 3 : "+str(estado))
                                   #VALIDA LOS ELIMINADOS
                                   if consulta.detalle_extracto:
                                       for p in consulta.detalle_extracto:
                                           if not p.id in j[2]:
					      consulta_rapida =  self.env['account.move'].search([('detalle_extracto.id','=',p.id),('id','!=',id)])
					      _logger.info("consulta_rapida: "+str(consulta_rapida))
					      if not len(consulta_rapida) > 0:
						 p.write({'estado': 'no'})
						 consulta.write({'estado_error':'si'})
					      elif len(consulta_rapida) > 1:
						 consulta.write({'estado_error':'azul'})
					      elif len(consulta_rapida) == 1:
						 valor = 0
						 for l in consulta_rapida.detalle_extracto:
						     valor += l.valor
                                                 _logger.info("valor: "+str(valor))
						 _logger.info("consulta_rapida total "+str(consulta_rapida.total_conciliar))
						 if valor == consulta_rapida.total_conciliar and valor != 0:
						     consulta.write({'estado_error':'si'})
						     consulta_rapida.write({'estado_error':'si'})
						 elif valor != consulta_rapida.total_conciliar and valor != 0:
						     consulta.write({'estado_error':'si'})
					      	     consulta_rapida.write({'estado_error':'red'})
						     
                                              
                                           _logger.info(p.estado)
                                   #GUARDAR LOS REGISTROS DETALLES COMO PRE CONCILIADO
                                   for j in consultar:
                                       j.write({'estado':'pre'})
				   _logger.info("estado final : "+str(estado))
                               else:
                                   l[2]['estado_concilacion'] = "no"
                                   consulta = self.env['account.move'].search([('id', '=', id)])
                                   consulta.write({'estado_error': 'si'})
                                   #self.state = "pre"
                                   estado = "pre"
                                   for obj in self.move_id_debito:
				       _logger.info(obj)
                                       if id == obj.id:
					   _logger.info(id)
                                           for j in obj.detalle_extracto:
                                               consulta = self.env['account.move'].search(
                                                   [('detalle_extracto.id', '=', j.id)])
                                               _logger.info(len(consulta))
                                               _logger.info(obj.estado_error)
                                               if not len(consulta) > 1:
						   _logger.info("SI ENTRA"+str(consulta))
                                                   j.write({'estado': 'no'})
						   obj.write({'estado_error':'si'})

                                               else:
						   _logger.info("NO ENTRA"+str(consulta))
                                                   for l in consulta:
						       for j in l.detalle_extracto:
							  j.write({'estado':'no'})
						       l.write({'estado_error': 'si'})
						   dic = {'move_id_debito':vals['move_id_debito']}
						   super(Extracto_bancario, self).write(dic) 
							#PREGUNTAR SI AUN TIENE ALGUIEN ESE DETALLE DE INFORME   
						   consulta_nueva = self.env['account.move'].search(
                                                   [('detalle_extracto.id', '=', j.id)])
						   _logger.info("consulta 1:"+str(consulta_nueva))
						   if not len(consulta_nueva) > 1:
							if len(consulta_nueva) != 0:
								valor = 0
						 		for l in consulta_nueva.detalle_extracto:
						     		   valor += l.valor
                                                 		if valor == consulta_nueva.total_conciliar and valor != 0:
						  		   #consulta.write({'estado_error':'si'})
						    		   consulta_nueva.write({'estado_error':'si'})
						 		elif valor != consulta_nueva.total_conciliar and valor != 0:
						     		    #consulta.write({'estado_error':'si'})
					      	     		    consulta_nueva.write({'estado_error':'red'})
								for l in consulta_nueva:
								   for j in l.detalle_extracto:	
								       j.write({'estado':'pre'})
						   else:
 							for l in consulta_nueva:
							   l.write({'estado_error':'azul'})
							   for j in l.detalle_extracto:	
							      l.write({'error_estado':'Documento repetido'}) 
						       
                                       if obj.estado_error != 'si':
                                           estado = "error"
                                   #self.state = estado

        if 'move_id_credito' in vals:
            repetidores = []
            indetificador = []
	    for obj in self.move_id_credito:
		for l in obj.detalle_extracto:
		   l.write({'error_estado':''})
            for l in vals['move_id_credito']:
                id = l[1]
                if len(l) > 2:
                    if l[2] != False:
                       indentificadores = []
                       if 'detalle_extracto' in l[2]:
                           for j in l[2]['detalle_extracto']:
                               if j[2]:
                                   valor = 0
                                   for k in self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])]):
                                       indentificadores.append(k.id)
                                       valor += k.valor
                                   consulta = self.env['account.move'].search([('id', '=', id)])
				   consultar = self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])])
                                   consulta.write({'estado_error': 'si'})
                                   #e = "pre"
                                   estado = "pre"
				   #Los preconcilias
				   l[2]['estado_concilacion'] = "pre"
                                   if consulta.total_conciliar == valor and valor != 0:
                                        l[2]['estado_concilacion'] = "pre"
					_logger.info("estado 1 : "+str(estado))
				   #Validar valores diferentes
				   if consulta.total_conciliar != valor and valor != 0 :
				       #l[2]['estado_concilacion'] = "pre"
                                       l[2]['estado_error'] = "red"
                                       #self.state = "error"
                                       estado = "error"
				       _logger.info("estado 2 : "+str(estado))
                                   # VALIDA REPETICIONES
				   for w in j[2]:
		                           if not w in repetidores:
						_logger.info("j2: "+str(j[2]))
						repetidores.append(w)
		                                indetificador.append(id)
						_logger.info("REPETIDOR :"+str(repetidores)+ "  Identificador "+str(indetificador))
		                           else:
		                                #consulta.write({'estado_error': 'azul'})
						#l[2]['estado_concilacion'] = "no"
						l[2]['estado_error'] = "azul"
						for c in consultar:
						    c.write({'error_estado': 'Documentos repetidos'})
		                                #self.state = "error"
		                                estado = "error"
		                                identi = 0
		                                for mov in repetidores:
		                                   if j[2] == mov and indetificador[identi] != id:
		                                       consulta = self.env['account.move'].search(
		                                           [('id', '=', indetificador[identi])])
		                                       consulta.write({'estado_error': 'azul'})
						       for c in consulta:
							  c.write({'error_estado': 'Documentos repetidos'})
		                                   identi += 1
						_logger.info("estado 3 : "+str(estado))
                                   #VALIDA LOS ELIMINADOS
                                   if consulta.detalle_extracto:
                                       for p in consulta.detalle_extracto:
                                           if not p.id in j[2]:
					      consulta_rapida =  self.env['account.move'].search([('detalle_extracto.id','=',p.id),('id','!=',id)])
					      _logger.info("consulta_rapida: "+str(consulta_rapida))
					      if not len(consulta_rapida) > 0:
						 p.write({'estado': 'no'})
						 consulta.write({'estado_error':'si'})
					      elif len(consulta_rapida) > 1:
						 consulta.write({'estado_error':'azul'})
					      elif len(consulta_rapida) == 1:
						 valor = 0
						 for l in consulta_rapida.detalle_extracto:
						     valor += l.valor
                                                 _logger.info("valor: "+str(valor))
						 _logger.info("consulta_rapida total "+str(consulta_rapida.total_conciliar))
						 if valor == consulta_rapida.total_conciliar and valor != 0:
						     consulta.write({'estado_error':'si'})
						     consulta_rapida.write({'estado_error':'si'})
						 elif valor != consulta_rapida.total_conciliar and valor != 0:
						     consulta.write({'estado_error':'si'})
					      	     consulta_rapida.write({'estado_error':'red'})
						     
                                              
                                           _logger.info(p.estado)
                                   #GUARDAR LOS REGISTROS DETALLES COMO PRE CONCILIADO
                                   for j in consultar:
                                       j.write({'estado':'pre'})
				   _logger.info("estado final : "+str(estado))
                               else:
                                   l[2]['estado_concilacion'] = "no"
                                   consulta = self.env['account.move'].search([('id', '=', id)])
                                   consulta.write({'estado_error': 'si'})
                                   #self.state = "pre"
                                   estado = "pre"
                                   for obj in self.move_id_credito:
				       _logger.info(obj)
                                       if id == obj.id:
					   _logger.info(id)
                                           for j in obj.detalle_extracto:
                                               consulta = self.env['account.move'].search(
                                                   [('detalle_extracto.id', '=', j.id)])
                                               _logger.info(len(consulta))
                                               _logger.info(obj.estado_error)
                                               if not len(consulta) > 1:
						   _logger.info("SI ENTRA"+str(consulta))
                                                   j.write({'estado': 'no'})
						   obj.write({'estado_error':'si'})

                                               else:
						   _logger.info("NO ENTRA"+str(consulta))
                                                   for l in consulta:
						       for j in l.detalle_extracto:
							  j.write({'estado':'no'})
						       l.write({'estado_error': 'si'})
						   dic = {'move_id_credito':vals['move_id_credito']}
						   super(Extracto_bancario, self).write(dic) 
							#PREGUNTAR SI AUN TIENE ALGUIEN ESE DETALLE DE INFORME   
						   consulta_nueva = self.env['account.move'].search(
                                                   [('detalle_extracto.id', '=', j.id)])
						   _logger.info("consulta 1:"+str(consulta_nueva))
						   if not len(consulta_nueva) > 1:
							if len(consulta_nueva) != 0:
								valor = 0
						 		for l in consulta_nueva.detalle_extracto:
						     		   valor += l.valor
                                                 		if valor == consulta_nueva.total_conciliar and valor != 0:
						  		   #consulta.write({'estado_error':'si'})
						    		   consulta_nueva.write({'estado_error':'si'})
						 		elif valor != consulta_nueva.total_conciliar and valor != 0:
						     		    #consulta.write({'estado_error':'si'})
					      	     		    consulta_nueva.write({'estado_error':'red'})
								for l in consulta_nueva:
								   for j in l.detalle_extracto:	
								       j.write({'estado':'pre'})
						   else:
 							for l in consulta_nueva:
							   l.write({'estado_error':'azul'})
							   for j in l.detalle_extracto:	
							      l.write({'error_estado':'Documento repetido'}) 
						       
                                       if obj.estado_error != 'si':
                                           estado = "error"
                                   #self.state = estado

        if 'move_id_deposito' in vals:
            repetidores = []
            indetificador = []
	    for obj in self.move_id_deposito:
		for l in obj.detalle_extracto:
		   l.write({'error_estado':''})
            for l in vals['move_id_deposito']:
                id = l[1]
                if len(l) > 2:
                    if l[2] != False:
                       indentificadores = []
                       if 'detalle_extracto' in l[2]:
                           for j in l[2]['detalle_extracto']:
                               if j[2]:
                                   valor = 0
                                   for k in self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])]):
                                       indentificadores.append(k.id)
                                       valor += k.valor
                                   consulta = self.env['account.move'].search([('id', '=', id)])
				   consultar = self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])])
                                   consulta.write({'estado_error': 'si'})
                                   #e = "pre"
                                   estado = "pre"
				   #Los preconcilias
				   l[2]['estado_concilacion'] = "pre"
                                   if consulta.total_conciliar == valor and valor != 0:
                                        l[2]['estado_concilacion'] = "pre"
					_logger.info("estado 1 : "+str(estado))
				   #Validar valores diferentes
				   if consulta.total_conciliar != valor and valor != 0 :
				       #l[2]['estado_concilacion'] = "pre"
                                       l[2]['estado_error'] = "red"
                                       #self.state = "error"
                                       estado = "error"
				       _logger.info("estado 2 : "+str(estado))
                                   # VALIDA REPETICIONES
				   for w in j[2]:
		                           if not w in repetidores:
						_logger.info("j2: "+str(j[2]))
						repetidores.append(w)
		                                indetificador.append(id)
						_logger.info("REPETIDOR :"+str(repetidores)+ "  Identificador "+str(indetificador))
		                           else:
		                                #consulta.write({'estado_error': 'azul'})
						#l[2]['estado_concilacion'] = "no"
						l[2]['estado_error'] = "azul"
						for c in consultar:
						    c.write({'error_estado': 'Documentos repetidos'})
		                                #self.state = "error"
		                                estado = "error"
		                                identi = 0
		                                for mov in repetidores:
		                                   if j[2] == mov and indetificador[identi] != id:
		                                       consulta = self.env['account.move'].search(
		                                           [('id', '=', indetificador[identi])])
		                                       consulta.write({'estado_error': 'azul'})
						       for c in consulta:
							  c.write({'error_estado': 'Documentos repetidos'})
		                                   identi += 1
						_logger.info("estado 3 : "+str(estado))
                                   #VALIDA LOS ELIMINADOS
                                   if consulta.detalle_extracto:
                                       for p in consulta.detalle_extracto:
                                           if not p.id in j[2]:
					      consulta_rapida =  self.env['account.move'].search([('detalle_extracto.id','=',p.id),('id','!=',id)])
					      _logger.info("consulta_rapida: "+str(consulta_rapida))
					      if not len(consulta_rapida) > 0:
						 p.write({'estado': 'no'})
						 consulta.write({'estado_error':'si'})
					      elif len(consulta_rapida) > 1:
						 consulta.write({'estado_error':'azul'})
					      elif len(consulta_rapida) == 1:
						 valor = 0
						 for l in consulta_rapida.detalle_extracto:
						     valor += l.valor
                                                 _logger.info("valor: "+str(valor))
						 _logger.info("consulta_rapida total "+str(consulta_rapida.total_conciliar))
						 if valor == consulta_rapida.total_conciliar and valor != 0:
						     consulta.write({'estado_error':'si'})
						     consulta_rapida.write({'estado_error':'si'})
						 elif valor != consulta_rapida.total_conciliar and valor != 0:
						     consulta.write({'estado_error':'si'})
					      	     consulta_rapida.write({'estado_error':'red'})
						     
                                              
                                           _logger.info(p.estado)
                                   #GUARDAR LOS REGISTROS DETALLES COMO PRE CONCILIADO
                                   for j in consultar:
                                       j.write({'estado':'pre'})
				   _logger.info("estado final : "+str(estado))
                               else:
                                   l[2]['estado_concilacion'] = "no"
                                   consulta = self.env['account.move'].search([('id', '=', id)])
                                   consulta.write({'estado_error': 'si'})
                                   #self.state = "pre"
                                   estado = "pre"
                                   for obj in self.move_id_deposito:
				       _logger.info(obj)
                                       if id == obj.id:
					   _logger.info(id)
                                           for j in obj.detalle_extracto:
                                               consulta = self.env['account.move'].search(
                                                   [('detalle_extracto.id', '=', j.id)])
                                               _logger.info(len(consulta))
                                               _logger.info(obj.estado_error)
                                               if not len(consulta) > 1:
						   _logger.info("SI ENTRA"+str(consulta))
                                                   j.write({'estado': 'no'})
						   obj.write({'estado_error':'si'})

                                               else:
						   _logger.info("NO ENTRA"+str(consulta))
                                                   for l in consulta:
						       for j in l.detalle_extracto:
							  j.write({'estado':'no'})
						       l.write({'estado_error': 'si'})
						   dic = {'move_id_deposito':vals['move_id_deposito']}
						   super(Extracto_bancario, self).write(dic) 
							#PREGUNTAR SI AUN TIENE ALGUIEN ESE DETALLE DE INFORME   
						   consulta_nueva = self.env['account.move'].search(
                                                   [('detalle_extracto.id', '=', j.id)])
						   _logger.info("consulta 1:"+str(consulta_nueva))
						   if not len(consulta_nueva) > 1:
							if len(consulta_nueva) != 0:
								valor = 0
						 		for l in consulta_nueva.detalle_extracto:
						     		   valor += l.valor
                                                 		if valor == consulta_nueva.total_conciliar and valor != 0:
						  		   #consulta.write({'estado_error':'si'})
						    		   consulta_nueva.write({'estado_error':'si'})
						 		elif valor != consulta_nueva.total_conciliar and valor != 0:
						     		    #consulta.write({'estado_error':'si'})
					      	     		    consulta_nueva.write({'estado_error':'red'})
								for l in consulta_nueva:
								   for j in l.detalle_extracto:	
								       j.write({'estado':'pre'})
						   else:
 							for l in consulta_nueva:
							   l.write({'estado_error':'azul'})
							   for j in l.detalle_extracto:	
							      l.write({'error_estado':'Documento repetido'}) 
						       
                                       if obj.estado_error != 'si':
                                           estado = "error"
                                   #self.state = estado

        if 'move_id_ordenes' in vals:
            repetidores = []
            indetificador = []
            for l in vals['move_id_ordenes']:
                _logger.info(l)
                id = l[1]
                if len(l) > 2:
                    if l[2] != False:
                       indentificadores = []
                       if 'detalle_extracto' in l[2]:
                           for j in l[2]['detalle_extracto']:
                               if j[2]:
                                   valor = 0
                                   consultar = self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])])
                                   for k in consultar:
                                       indentificadores.append(k.id)
                                       valor += k.valor
                                   consulta = self.env['account.move'].search([('id', '=', id)])
                                   consulta.write({'estado_error': 'si'})
                                   #self.state = "pre"
                                   estado = "pre"
				   if consulta.total_conciliar == valor and valor != 0 and consultar.ref == consulta.name:
                                        l[2]['estado_concilacion'] = "pre"
                                   if len(j[2]) > 1:
                                       consulta.write({'estado_error': 'red'})
                                       consultar.write({'error_estado': 'Solo una orden por movimiento'})
                                       # self.state = "error"
                                       estado = "error"
                                   if (consulta.total_conciliar != valor and valor != 0) or consultar.ref != consulta.name:
                                       consulta.write({'estado_error': 'red'})
                                       consultar.write({'error_estado': 'Revisar Valores y/o Numero de orden'})
                                       #self.state = "error"
                                       estado = "error"
                                   
                                   # VALIDA REPETICIONES
                                   if not j[2] in repetidores:
                                        repetidores.append(j[2])
                                        indetificador.append(id)
                                   else:
                                        consulta.write({'estado_error': 'azul'})
                                        consultar.write({'error_estado': 'Repetidos'})
                                        #self.state = "error"
                                        estado = "error"
                                        identi = 0
                                        for mov in repetidores:
                                            if j[2] == mov:
                                                consulta = self.env['account.move'].search(
                                                    [('id', '=', indetificador[identi])])
                                                consulta.write({'estado_error': 'azul'})
                                            identi += 1
                                   #GUARDAR LOS REGISTROS DETALLES COMO PRE CONCILIADO
                                   if consulta.detalle_extracto:
                                       for p in consulta.detalle_extracto:
                                           if not p.id in j[2]:
                                              k.write({'estado': 'no'})
                                           _logger.info(k.estado)
                                   consultar = self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])])
                                   for j in consultar:
                                       j.write({'estado':'pre'})
                               else:
                                   l[2]['estado_concilacion'] = "no"
                                   consulta = self.env['account.move'].search([('id', '=', id)])
                                   consulta.write({'estado_error': 'si'})
                                   estado = "pre"
                                   for obj in self.move_id_ordenes:
                                       if id == obj.id:
                                           for j in obj.detalle_extracto:
                                               consulta = self.env['account.move'].search(
                                                   [('detalle_extracto.id', '=', j.id)])
                                               _logger.info(len(consulta))
                                               # _logger.info(consulta.name)
                                               if not len(consulta) > 1:
                                                   j.write({'estado': 'no'})
                                               else:
                                                   for l in consulta:
                                                       l.write({'estado_error': 'si'})
                                       if obj.estado_error != 'si':
                                           estado = "error"
                                   #self.state = estado
        if 'move_id_cheques' in vals:
            repetidores = []
            indetificador = []
            for l in vals['move_id_cheques']:
                _logger.info(l)
                id = l[1]
                if len(l) > 2:
                    if l[2] != False:
                       indentificadores = []
                       if 'detalle_extracto' in l[2]:
                           for j in l[2]['detalle_extracto']:
                               if j[2]:
                                   valor = 0
                                   consultar = self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])])
                                   for k in consultar:
                                       indentificadores.append(k.id)
                                       valor += k.valor
                                   consulta = self.env['account.move'].search([('id', '=', id)])
                                   consulta.write({'estado_error': 'si'})
                                   #self.state = "pre"
                                   estado = "pre"
				   if consulta.total_conciliar == valor and valor != 0 and consultar.ref == consulta.name:
                                        l[2]['estado_concilacion'] = "pre"
                                   if len(j[2]) > 1:
                                       consulta.write({'estado_error': 'red'})
                                       consultar.write({'error_estado': 'Solo un cheques por movimiento'})
                                       # self.state = "error"
                                       estado = "error"
                                   if (consulta.total_conciliar != valor and valor != 0) or consultar.ref != consulta.name:
                                       consulta.write({'estado_error': 'red'})
                                       consultar.write({'error_estado': 'Revisar Valores y/o Numero de cheques'})
                                       #self.state = "error"
                                       estado = "error"
                                   
                                   # VALIDA REPETICIONES
                                   if not j[2] in repetidores:
                                        repetidores.append(j[2])
                                        indetificador.append(id)
                                   else:
                                        consulta.write({'estado_error': 'azul'})
                                        consultar.write({'error_estado': 'Repetidos'})
                                        #self.state = "error"
                                        estado = "error"
                                        identi = 0
                                        for mov in repetidores:
                                            if j[2] == mov:
                                                consulta = self.env['account.move'].search(
                                                    [('id', '=', indetificador[identi])])
                                                consulta.write({'estado_error': 'azul'})
                                            identi += 1
                                   #GUARDAR LOS REGISTROS DETALLES COMO PRE CONCILIADO
                                   if consulta.detalle_extracto:
                                       for p in consulta.detalle_extracto:
                                           if not p.id in j[2]:
                                              k.write({'estado': 'no'})
                                           _logger.info(k.estado)
                                   consultar = self.env['detalle.extracto.bancario.ans'].search([('id','in',j[2])])
                                   for j in consultar:
                                       j.write({'estado':'pre'})
                               else:
                                   l[2]['estado_concilacion'] = "no"
                                   consulta = self.env['account.move'].search([('id', '=', id)])
                                   consulta.write({'estado_error': 'si'})
                                   estado = "pre"
                                   for obj in self.move_id_cheques:
                                       if id == obj.id:
                                           for j in obj.detalle_extracto:
                                               consulta = self.env['account.move'].search(
                                                   [('detalle_extracto.id', '=', j.id)])
                                               _logger.info(len(consulta))
                                               # _logger.info(consulta.name)
                                               if not len(consulta) > 1:
                                                   j.write({'estado': 'no'})
                                               else:
                                                   for l in consulta:
                                                       l.write({'estado_error': 'si'})
                                       if obj.estado_error != 'si':
                                           estado = "error"
                                   #self.state = estado
        if estado:
            self.state = estado
	    #self.state = "pre"
	    _logger.info("Estado:" + str(self.state))
	    _logger.info("Variable Estado:" + str(estado))

        return super(Extracto_bancario, self).write(vals)


    @api.multi
    def pre_conciliar(self):
        if self.state != "pre" or self.state == "pre":
            self.cambiar_estado()
        obj = self._get_all_debitos()
        if obj:
            self.write({'move_id_debito': [(6,_, obj.ids)]})

        obj = self._get_all_creditos()
        if obj:
            self.write({'move_id_credito': [(6,_, obj.ids)]})

        obj = self._get_all_depositos()
        if obj:
            self.write({'move_id_deposito': [(6,_, obj.ids)]})

        obj = self._get_all_cheques()
        if obj:
            self.write({'move_id_cheques': [(6,_, obj.ids)]})

        obj = self._get_all_ordenes()
        if obj:
            self.write({'move_id_ordenes': [(6,_, obj.ids)]})
        obj = self.env['detalle.extracto.bancario.ans'].search([('estado', '=', 'pen'), ('id', '!=', self.id)])
        if obj:
            self.pendientes()
        #self.pre_conciliar_cheques(self.move_id_cheques)

    @api.multi
    def pendientes(self):
            obj_nd = self.env['detalle.extracto.bancario.ans'].search([('estado', '=', 'pen')])
            for l in obj_nd:
                l.write({'extracto_id':self.id,'estado':'no'})

    @api.multi
    def procesar_datos(self):
        for obj in self.move_id_cheques:
            if obj.estado_concilacion == "pre":
                consulta = self.env['account.voucher'].search([('id','=',obj.id)])
                _logger.info(consulta.move_id)
                if not consulta.move_id.detalle_extracto:
                    #consulta.write({'move_id.detalle_extracto': [(4,obj.detalle_extracto.ids)],'move_id.estado_concilacion':'pre'})
                    consulta.move_id.write({'detalle_extracto': [(4,obj.detalle_extracto.ids)]})
                    _logger.info(obj.detalle_extracto.ids)
                    _logger.info(consulta.move_id.detalle_extracto)
                    _logger.info(consulta.move_id.estado_concilacion)
                else:
                    #consulta.write({'move_id.detalle_extracto': [(6,False,obj.detalle_extracto.ids)],'move_id.estado_concilacion':'pre'})
                    consulta.move_id.write({'detalle_extracto': [(6,False, obj.detalle_extracto.ids)]})
                    _logger.info(obj.detalle_extracto.ids)
                    _logger.info(consulta.move_id.detalle_extracto)
                    _logger.info(consulta.move_id.estado_concilacion)



    @api.multi
    def pre_conciliar_ordenes(self):
        self.pre_conciliar_ordene(self.move_id_ordenes)

    @api.multi
    def pre_conciliar_notas_debitos(self):
        self.pre_conciliar_movimientos(self.move_id_debito,'ND')

    @api.multi
    def pre_conciliar_notas_credito(self):
        self.pre_conciliar_movimientos(self.move_id_credito,'NC')

    @api.multi
    def pre_conciliar_depositos(self):
        self.pre_conciliar_movimientos(self.move_id_deposito, 'DEP')

    @api.multi
    def pre_conciliar_cheque(self):
        self.pre_conciliar_cheques(self.move_id_cheques)

    @api.multi
    def limpiar_todo(self):
        for l in self.move_id_debito:
            for j in l.detalle_extracto:
                j.write({'estado':'no'})
            l.write({'estado_concilacion': 'no','detalle_extracto':[(6,False,[])],'estado_error':'si'})
	self.move_id_debito = [(6,False,[])]
        for l in self.move_id_credito:
            for j in l.detalle_extracto:
                j.write({'estado':'no'})
            l.write({'estado_concilacion': 'no', 'detalle_extracto': [(6, False, [])],'estado_error':'si'})
	self.move_id_credito = [(6,False,[])]
        for l in self.move_id_deposito:
            for j in l.detalle_extracto:
                j.write({'estado':'no'})
            l.write({'estado_concilacion': 'no', 'detalle_extracto': [(6, False, [])],'estado_error':'si'})
	self.move_id_deposito = [(6,False,[])]
        for l in self.move_id_ordenes:
            for j in l.detalle_extracto:
                j.write({'estado':'no'})
            l.write({'estado_concilacion': 'no', 'detalle_extracto': [(6, False, [])],'estado_error':'si'})
	self.move_id_ordenes = [(6,False,[])]
        for l in self.move_id_cheques:
           for j in l.detalle_extracto:
                j.write({'estado':'no'})
           l.write({'estado_concilacion': 'no', 'detalle_extracto': [(6, False, [])],'estado_error':'si'})
	self.move_id_cheques = [(6,False,[])]

    
        self.state = "draft"
        #self.pre_conciliar()
    @api.multi
    def consultar(self,fecha):
        dic = {}
        obj = self.env['account.move.line'].search([('account_id.id','=',514)])
        creditos = 0
        debitos = 0
        for l in obj:
            creditos += l.credit
            debitos += l.debit
        saldo = debitos - creditos
        if self.saldo_inicial < 1:
            dic['saldo'] = saldo
        else:
            dic['saldo'] = self.saldo_inicial

        obj = self.env['detalle.extracto.bancario.ans'].search(
            [('parametro_id.tipo_mov','=','NC'),('extracto_id.id','=',self.id),('estado','=','no')])
        dic['d_nc_e'] = obj

        saldo_nc = 0
        for l in obj:
            saldo_nc += l.valor
        dic['NC'] = saldo_nc

        obj = self.env['detalle.extracto.bancario.ans'].search(
            [('parametro_id.tipo_mov', '=', 'ND'), ('extracto_id.id', '=', self.id), ('estado', '=', 'no')])
        _logger.info(obj)
        dic['d_nd_e'] = obj
        saldo_nc = 0
        for l in obj:
            saldo_nc += l.valor
        dic['ND'] = saldo_nc

        obj = self.env['detalle.extracto.bancario.ans'].search(
            [('parametro_id.tipo_mov', '=', 'DEP'), ('extracto_id.id', '=', self.id), ('estado', '=', 'no')])
        _logger.info(obj)
        dic['d_dep_e'] = obj
        saldo_nc = 0
        for l in obj:
            saldo_nc += l.valor
        dic['DEP'] = saldo_nc

        obj = self.env['detalle.extracto.bancario.ans'].search(
            [('parametro_id.tipo_mov', '=', 'CHE'), ('extracto_id.id', '=', self.id), ('estado', '=', 'no')])
        _logger.info(obj)
        dic['d_che_e'] = obj
        saldo_nc = 0
        for l in obj:
            saldo_nc += l.valor
        dic['CHE'] = saldo_nc

	dic['ano'] = self.ano_periodo
	dic['mes'] = self.mes_periodo
        obj = self.env['detalle.extracto.bancario.ans'].search(
            [('parametro_id.tipo_mov', '=', 'ORD'), ('extracto_id.id', '=', self.id), ('estado', '=', 'no')])
        _logger.info(obj)
        dic['d_ord_e'] = obj
        saldo_ord = 0
        for l in obj:
            saldo_ord += l.valor
        dic['ORD'] = saldo_ord

        dic['d_nd_c'] = self.env['detalle.extracto.bancario.ans'].search([
            ('extracto_id.id', '=', self.id),('estado', '=', 'pre'),('parametro_id.tipo_mov', '=', 'ND')])
        dic['d_nc_c'] = self.env['detalle.extracto.bancario.ans'].search([
            ('extracto_id.id', '=', self.id), ('estado', '=', 'pre'), ('parametro_id.tipo_mov', '=', 'NC')])
        dic['d_dep_c'] = self.env['detalle.extracto.bancario.ans'].search([
            ('extracto_id.id', '=', self.id), ('estado', '=', 'pre'), ('parametro_id.tipo_mov', '=', 'DEP')])
        dic['d_che_c'] = self.env['detalle.extracto.bancario.ans'].search([
            ('extracto_id.id', '=', self.id), ('estado', '=', 'pre'), ('parametro_id.tipo_mov', '=', 'CHE')])
        dic['d_ord_c'] = self.env['detalle.extracto.bancario.ans'].search([
            ('extracto_id.id', '=', self.id), ('estado', '=', 'pre'), ('parametro_id.tipo_mov', '=', 'ORD')])

        dic['Banco'] = self.banco
        dic['Cuenta'] = self.cuenta
        dic['fecha_inicial'] = self.fecha_inicial
        dic['fecha_final'] = self.fecha_final
        dic['plan_cuenta'] = self.chart_account_id
        dic['usuario'] = self.env.user.name

        dic['d_che_b'] = self.env['account.move'].search([('state', '=', 'posted')
                                                             ,('date', '<', self.fecha_final)
                                                             ,('estado_concilacion', '=', 'no')
                                                        , ('journal_id.tipo_mov', '=', 'CHE')])





        dic['d_nc_b'] = self.env['account.move'].search([('state', '=', 'posted')
                                                             ,('date', '<', self.fecha_final)
                                                             ,('estado_concilacion', '=', 'no')
                                                             , ('journal_id.tipo_mov', '=', 'NC')])

        dic['d_nd_b'] = self.env['account.move'].search([('state', '=', 'posted')
                                                             ,('date', '<', self.fecha_final)
                                                             ,('estado_concilacion', '=', 'no')
                                                             , ('journal_id.tipo_mov', '=', 'ND')])

        dic['d_dep_b'] = self.env['account.move'].search([('state', '=', 'posted')
                                                             ,('date', '<', self.fecha_final)
                                                             ,('estado_concilacion', '=', 'no')
                                                             , ('journal_id.tipo_mov', '=', 'DEP')])

        dic['d_ord_b'] = self.env['account.move'].search([('state', '=', 'posted')
                                                             ,('date', '<', self.fecha_final)
                                                             ,('estado_concilacion', '=', 'no')
                                                             , ('journal_id.tipo_mov', '=', 'ORD')])

        for l in dic['d_che_b']:
            dic['CHE'] += l.amount or 0

        for l in dic['d_dep_b']:
            dic['DEP'] += l.total_conciliar or 0

        for l in dic['d_ord_b']:
            dic['ORD'] += l.total_conciliar or 0

        for l in dic['d_nd_b']:
            dic['ND'] += l.total_conciliar or 0

        estado = ""
        if self.state == "pre":
            estado = "ABIERTO"
        if self.state == "draft":
            estado = "BORRADOR"
        if self.state == "con":
            estado = "CONCILIADO"
        if self.state == "error":
            estado = "CON ERROR"
        dic['estado'] = estado

        return dic
    @api.one
    def generar_reportes(self):
	self.generar_excell()
	self.generar_pdf()

    
    def generar_excell(self):
        fp = io.BytesIO()
        dic = self.consultar(self.fecha_final)
        workbook = reporte_concilacion.crear_reporte_excell()
        reporte_concilacion.crear_encabezado(dic, workbook['sheet'], workbook['alineacion'], workbook['fuente'])
        #reporte_concilacion.encabezado_detalle(workbook['sheet'], workbook['alineacion'], workbook['fuente'])
        reporte_concilacion.detalle_saldos(dic,workbook['sheet'], workbook['alineacion'], workbook['fuente'])
        reporte_concilacion.cuerpo_detalle(dic,workbook['sheet'], workbook['alineacion'], workbook['fuente'])
        workbook['libro'].save(fp)
        filename = 'Reporte Concilacion Bancaria' + '.xlsx'
        self.nombre_xls = filename
        self.binario_xls = base64.b64encode(fp.getvalue())
        return True

    
    def generar_pdf(self):
        fp = io.BytesIO()
        dic = self.consultar(self.fecha_final)
        workbook = reporte_concilacion.crear_reporte_excell()
        reporte_concilacion.crear_encabezado(dic, workbook['sheet'], workbook['alineacion'], workbook['fuente'])
        # reporte_concilacion.encabezado_detalle(workbook['sheet'], workbook['alineacion'], workbook['fuente'])
        reporte_concilacion.detalle_saldos(dic, workbook['sheet'], workbook['alineacion'], workbook['fuente'])
        reporte_concilacion.cuerpo_detalle(dic, workbook['sheet'], workbook['alineacion'], workbook['fuente'])
        workbook['libro'].save(fp)
        filename_pdf = 'Informe' + '.xlsx'
        archivo_pdf = base64.b64encode(fp.getvalue())
        obj = self.env['ir.attachment']
        obj_xls = obj.create({'res_model': self.id, 'name': filename_pdf
                                 , 'datas': archivo_pdf, 'type': 'binary',
                              'datas_fname': filename_pdf})
        direccion_xls = obj._get_path(obj_xls.datas)[1]
        direccion = obj._get_path(obj_xls.datas)[0]
        nombre_bin = obj_xls.store_fname
        nombre_archivo = obj_xls.datas_fname
        separa = direccion_xls.rstrip(direccion)
        os.chdir(separa)
        os.rename(nombre_bin, nombre_archivo)
        commands.getoutput(""" libreoffice --headless --convert-to pdf *.xlsx""")
        with open(direccion_xls.rstrip(direccion) + '/' + nombre_archivo.split('.')[0] + '.pdf', "rb") as f:
            data = f.read()
            file = data.encode("base64")
        self.write({'nombre_txt': nombre_archivo.split('.')[0] + '.pdf', 'binario_pdf': file})
        os.rename(nombre_archivo, nombre_bin)
        obj_xls.unlink()

        return True


    @api.multi
    def conciliar(self):
        self.generar_reportes()
        for l in self.move_id_debito:
            for j in l.detalle_extracto:
                j.write({'estado': 'con'})
                l.write({'estado_concilacion': 'con'})
        for l in self.move_id_credito:
            for j in l.detalle_extracto:
                if j.estado == 'pre':
                    j.write({'estado': 'con'})
                    l.write({'estado_concilacion': 'con'})

        for l in self.move_id_deposito:
            for j in l.detalle_extracto:
                if j.estado == 'pre':
                    j.write({'estado': 'con'})
                    l.write({'estado_concilacion': 'con'})

        for l in self.move_id_ordenes:
            for j in l.detalle_extracto:
                if j.estado == 'pre':
                    j.write({'estado': 'con'})
                    l.write({'estado_concilacion': 'con'})

        for l in self.move_id_cheques:
            for j in l.detalle_extracto:
                if j.estado == 'pre':
                    j.write({'estado': 'con'})
                    l.write({'estado_concilacion': 'con'})
        self.write({'state':'con'})

        for l in self.extracto_line_debito:
            if l.estado == "no":
                l.write({'estado':'pen'})
        for l in self.extracto_line_credito:
            if l.estado == "no":
                l.write({'estado':'pen'})
        for l in self.extracto_line_cheques:
            if l.estado == "no":
                l.write({'estado':'pen'})
        for l in self.extracto_line_ordenes:
            if l.estado == "no":
                l.write({'estado':'pen'})
        for l in self.extracto_line_depositos:
            if l.estado == "no":
                l.write({'estado':'pen'})





    def pre_conciliar_movimientos(self,dic,mov):
        if dic:
            for obj in dic:
                for l in obj:
                    movimiento = self.consultar_move(l.date,mov,l.amount,l.journal_id.id)
                    if movimiento:
                        if len(movimiento) == 1:
                           movimiento[0].write({'estado':'pre'})
                           l.write({'detalle_extracto':[(6,_,movimiento.ids)], 'estado_concilacion': 'pre'})
                           obj.write({'estado_concilacion':'pre'})

    def pre_conciliar_ordene(self,dic):
        if dic:
            for obj in dic:
                for l in obj:
                    movimiento = self.consultar_ordenes(l.name,l.amount)
                    if movimiento:
                        if len(movimiento) == 1:
                           movimiento[0].write({'estado':'pre'})
                           l.write({'detalle_extracto':[(6,False,movimiento.ids)], 'estado_concilacion': 'pre'})
                           obj.write({'estado_concilacion:':'pre'})


    def consultar_ordenes(self,codigo,monto):
        obj = self.env['detalle.extracto.bancario.ans'].search([
            ('estado', '=', 'no'), ('parametro_id.tipo_mov', '=', 'ORD'), ('ref', '=', codigo), ('valor', '=', monto)])
        _logger.info(obj)
        return obj


    def pre_conciliar_cheques(self,dic):
        if dic:
            for obj in dic:
                for l in obj:
                    movimientos = self.consultar_mov_cheques(l.name,l.amount)
                    if len(movimientos) == 1:
                        movimientos[0].write({'estado':'pre'})
                        l.write({'estado_concilacion':'pre','detalle_extracto': [(6,_,movimientos.ids)]})
                        obj.write({'estado_concilacion':'pre'})

    def consultar_move(self,fecha,mov,monto,journal):
        obj = self.env['detalle.extracto.bancario.ans'].search([
            ('estado','=','no'),('fecha','=',str(fecha)),('parametro_id.tipo_mov','=',str(mov)),('valor','=',monto)
            ,('extracto_id','=',self.id),('parametro_id.journal_id','=',journal)])
        return obj

    def consultar_mov_cheques(self,codigo,monto):
        obj = self.env['detalle.extracto.bancario.ans'].search([
            ('estado','=','no'),('parametro_id.tipo_mov','=','CHE'),('ref','=',codigo),('valor','=',monto)])
        _logger.info(obj)
        return obj


    def cambiar_estado_pre(self,obj):
        obj.write({'estado':'pre'})

    def cambiar_estado(self):
        self.write({'state': 'pre'})




"""
obj = self._get_all_move_2()
        self.write({'move_id_credito':[(4,obj.ids)]})

"""
class Detalle_extracto_bancario(models.Model):
    _name = "detalle.extracto.bancario.ans"

    def _get_creditos(self):
        return [('state', '=', 'posted'), ('estado_concilacion', '=', 'no'), ('journal_id.tipo_mov', '=', 'NC')]
    def _get_debitos(self):
        return [('state', '=', 'posted'), ('estado_concilacion', '=', 'no'), ('journal_id.tipo_mov', '=', 'ND')]

    def _get_depositos(self):
        return [('state', '=', 'posted'), ('estado_concilacion', '=', 'no'), ('journal_id.tipo_mov', '=', 'DEP')]

    def _get_cheques(self):
        return [('state', '=', 'posted'), ('estado_concilacion', '=', 'no'), ('journal_id.tipo_mov', '=', 'CHE')]

    def separar_secuencial(self):
        for obj in self:
            secuencial = obj.secuencial
            obj.secuencial_part = secuencial[8:]


    def obtener_id_visualizador(self):
	for obj in self:
	   consulta = self.env['account.move'].search([('detalle_extracto','=',obj.id)])
	   obj.move_id = [(6,False,consulta.ids)]

    numero = fields.Integer(readonly=True)
    fecha = fields.Date()#readonly=True
    ref = fields.Char()#readonly=True
    lugar = fields.Char(readonly=True)
    detalle = fields.Char(readonly=True)
    secuencial = fields.Char(readonly=True)
    secuencial_part = fields.Char('Secuencial',compute=separar_secuencial,store=False,readonly=True)
    signo = fields.Char(readonly=True)
    valor = fields.Float(digits=dp.get_precision('Account'))#,readonly=True
    saldo_d = fields.Float('Saldo disponible',digits=dp.get_precision('Account'),readonly=True)
    saldo_c = fields.Float('Saldo contable',digits=dp.get_precision('Account'),readonly=True)
    descripcion = fields.Char(readonly=True)
    extracto_id = fields.Many2one('extracto.bancario.ans',string="Extracto Bancario",ondelete='cascade',index=True,readonly=True)
    parametro_id = fields.Many2one('extracto.conf.ans',string="Parametro de Busquedad",ondelete='cascade',index=True,readonly=True)
    journal = fields.Char('Diario',related='parametro_id.journal_id.name',store=True,readonly=True)
    estado = fields.Selection([('no','No Conciliado'),('con','Conciliado'),('pre','Pre conciliado'),('pen','Pendiente')],default="no")#,readonly=True
    move_id = fields.Many2many('account.move','detalle_extracto_account_move','detalle_extracto_id','detalle_id',string="Documento",readonly=True,on_delete="restrinct") # fields.Many2one('account.move',string="Documentos",readonly=True,index=True,on_delete="restrinct")
    diario = fields.Char('Diario',related='parametro_id.journal_id.name')
    error_estado = fields.Char('Error')#,default="Si"
    #move_id_debitos = fields.Many2many('account.move',string="Movimiento"
    #                                   ,ondelete="restrict",index=True)

    """
    @api.multi
    @api.onchange('move_id_debitos')
    def _on_change_debitos(self):
        id = []
        valor = 0

        for obj in self.move_id_debitos:
            for j in obj:
                for i in j.line_id:
                    valor += i.debit
                id.append(j.id)
        if self._origin.move_id_debitos:
            for j in self._origin.move_id_debitos:
                for i in j:
                    if id:
                        _logger.info( str(self._origin.move_id_debitos)+" "+str(id))
                        if i.id in id:
                            _logger.info('SE HIZO PRE')
                            i.write({'estado_concilacion':'pre'})
                        else:
                            _logger.info("SE HIZO NO")
                            i.write({'estado_concilacion':'no'})
                    else:
                        i.write({'estado_concilacion': 'no'})
        else:
            for i in self.move_id_debitos:
                for j in i:
                    _logger.info('PINTAR')
                    j.write({'estado_concilacion':'pre'})
        if self.valor < valor:
            res = {'warning':{
                'title':_('Warning'),
                'message':_('Corregir Valores'),
            }}
            return res
    """




class Parametrizacion_conciliacion(models.Model):
    _name = "extracto.conf.ans"
    cadena_bus = fields.Char(required=True)
    tipo_mov = fields.Selection([('ORD','Orden de Pago'),('NC','Notas de Credito')
                                    ,('ND','Notas de Debito'),('CHE','Cheques'),('DEP','Depositos')],required=True)
    banco_id = fields.Many2one('res.bank',string="Banco",index=True,required=True)
    cuenta_id = fields.Many2one('account.account',string="Cuenta Contable",index=True,required=True)
    journal_id = fields.Many2one('account.journal',string="Tipo de Diario",required=True,index=True,on_delete="restrict")

class Account_move_line_concilacion(models.Model):
    _inherit = "account.move.line"
    _order = "estado_concilacion"
    _rec_name = "id"
    estado_concilacion = fields.Selection([
        ('si','Conciliado'),('no','No Conciliado'),('pre','Pre conciliado')
    ],default="no")

class account_journal_inherit(models.Model):
    _inherit = "account.journal"
    tipo_mov = fields.Selection([('ORD','Orden de Pago')
                                    ,('NC','Notas de Credito')
                                    ,('ND','Notas de Debito')
                                    ,('CHE','Cheques')
                                    ,('DEP','Depositos')],string="Movimiento Bancario")


class Account_move_concilacion(models.Model):
    _inherit = "account.move"
    def calcular_conciliados(self):
        for i in self:
            sum = 0
            objeto = self.env['extracto.conf.ans'].search([('journal_id','=',i.journal_id.id)],limit=1)
            if objeto:
                for j in i.line_id:
                    for l in j:
                        if l.account_id.id == objeto.cuenta_id.id:
                            if l.journal_id.tipo_mov == "CHE" or l.journal_id.tipo_mov == "ND" or l.journal_id.tipo_mov == "ORD":
                                sum += l.credit
                            if l.journal_id.tipo_mov == "NC" or l.journal_id.tipo_mov == "DEP":
                                sum += l.debit
            i.total_conciliar = sum

    def obtener_empresa(self):
        for i in self:
            sum = ""
            objeto = self.env['extracto.conf.ans'].search([('journal_id','=',i.journal_id.id)],limit=1)
            if objeto:
                for j in i.line_id:
                    for l in j:
                        if l.account_id.id == objeto.cuenta_id.id:
                            sum = l.partner_id.name
            i.company_char = sum


    detalle_extracto = fields.Many2many('detalle.extracto.bancario.ans','detalle_extracto_account_move','detalle_id','detalle_extracto_id',string="Movimiento Extracto",index=True,on_delete="restrict")  #fields.One2many('detalle.extracto.bancario.ans','move_id',string="Movimiento Extracto")
    company_char = fields.Char('Proveedor',compute=obtener_empresa,readonly=True,store=False)
    estado_concilacion = fields.Selection([
        ('con', 'Conciliado'), ('no', 'No Conciliado'),('pre','Procesado')
    ], default="no",string="Conciliacion Bancaria")
    estado_error = fields.Selection([('red', 'Error'), ('azul', 'Error'),('si','Sin error')],default="si")

    total_conciliar = fields.Float(compute=calcular_conciliados,readonly=True,store=False)

    def button_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if not line.journal_id.update_posted:
                raise ValidationError(_('You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
            if line.estado_concilacion == "pre" or line.estado_concilacion == "con":
                raise ValidationError(_('No puedes modificar registros que tenga concilaciones .'))
        if ids:
            cr.execute('UPDATE account_move '\
                       'SET state=%s '\
                       'WHERE id IN %s', ('draft', tuple(ids),))
            self.invalidate_cache(cr, uid, context=context)
        return True


class Account_voucher_concilacion(models.Model):
    _inherit = "account.voucher"
    _order = "estado_concilacion"
    _rec_name = "id"
    detalle_extracto = fields.Many2many('detalle.extracto.bancario.ans',string="Movimiento Extracto"
                                        ,index=True,on_delete="restrict")
    estado_concilacion = fields.Selection([
        ('con', 'Conciliado'), ('no', 'No Conciliado'),('pre','Pre conciliado')
    ], default="no")
    estado_error = fields.Selection([('red', 'Error'), ('azul', 'Error'),('si', 'Sin error')], default="si")



