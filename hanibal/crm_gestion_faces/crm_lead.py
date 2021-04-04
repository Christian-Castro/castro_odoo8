# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp import api
import datetime

class crm_lead(osv.osv):
    
    _name="crm.lead"
    _inherit = 'crm.lead'
    
    _columns = {
        'ciudad_id':fields.many2one('ciudades','Ciudades'),
        'tipo_id':fields.many2one('tipo.opp','Tipo'),
	'estado':fields.selection( (('A','Aprobado'),('R','Rechazado')),'Estado' ),
        'detalle_ventas':fields.one2many('sale.order','venta_id','Cotizaciones'),
        'contacto_id':fields.many2one('res.partner','Contacto'),
	#11/9/2018
	'iniciativa':fields.boolean('Iniciativa'),	
    }
    #3-03-2018
    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            partner_name = (partner.parent_id and partner.parent_id.name) or (partner.is_company and partner.name) or False
            values = {
                'partner_name': partner_name,
                'contact_name': (not partner.is_company and partner.name) or False,
                'title': partner.title and partner.title.id or False,
                'street': partner.street,
                'street2': partner.street2,
                'ciudad_id': partner.ciudad_id.id,
                'state_id': partner.state_id and partner.state_id.id or False,
                'country_id': partner.country_id and partner.country_id.id or False,
                'email_from': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'fax': partner.fax,
                'zip': partner.zip,
                'function': partner.function,
		'user_id': partner.user_id.id,
            }
        return {'value': values}


    #DESDE

    #"""" EN ESTE CODIGO ME PERMITE ABRIR LA PANTALLA DE CLIENTES QUE SERIAN EL PROSPECTO PARA CREAR LOS CONTACTOS """"
    @api.multi
    def open_partner_contact(self,):
	if self.partner_id:
            """ Utility method used to add an "Open Parent" button in partner views """
            
            return {'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'res_id': self.partner_id.id,
                 'target': 'new',
		'context': {'default_prospectos': 't'},
                'flags': {'form': {'action_buttons': True}}}
	else:
	    raise osv.except_osv(('Warning!'),('Para poder crear contactos defina el cliente o prospecto primero'))  
    #HASTA

    #28-02-2018
    @api.multi
    def crear_contacto(self,):
	print 'PREAPRAR DESDE EL BOTON'
	if self.contact_name:
		obj_log=self.env['log.crm.gestion']
		self._cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(datetime.datetime.now(),self.create_date))
		preparar = self._cr.dictfetchall()[0]['tmp']
	
		d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(datetime.datetime.now(),self.create_date)
		self._cr.execute(d)
		res_d = self._cr.dictfetchall()[0]['dias']
		##h = """select 
		##	(select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )
		##	+
		##	(select extract ( minute from ('{0}'::timestamp - '{1}'::timestamp))  )
		##	+
		##	(select extract ( second from ('{0}'::timestamp - '{1}'::timestamp))  )
		##	as res
		##""".format(datetime.datetime.now(),self.create_date)

		h = """select 
		       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
		        +
		      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
		      as res
		""".format(datetime.datetime.now(),self.create_date)
		self._cr.execute(h)
		res_h = self._cr.dictfetchall()[0]['res']
                res_d = res_d + res_h

		##if res_h == 0 :
		##    res_h = 1
		##if res_h >= 1 :
		##    res_d = res_d + 1
		print res_d,'DIAS EN RES_D'
		fecha_iniciativa=self.create_date
		#25-02-2018
		#cliente exitsnte pero con pruebas
		self._cr.execute(""" select 
			coalesce(dias_identificar,0)
			 as dias
			from log_crm_gestion where registro_id = {0} """.format(self.id))
		dias_prepa=self._cr.dictfetchall()[0]['dias']
		if dias_prepa == 0:
		    self._cr.execute(""" select 
			fecha_prospecto
			from log_crm_gestion where registro_id = {0} """.format(self.id))
		    fecha_iniciativa=self._cr.dictfetchall()[0]['fecha_prospecto']
		#25-02-2018
	
		dct={'registro_id':self.id,
		 'usuario_crea':self.create_uid.id,
		 'fecha_iniciativa':fecha_iniciativa,
		 'fecha_contacto':datetime.datetime.now(),
		 'preparar':preparar,
		 'estado':'Preparar',
		 'dias_preparar':res_d,
		 }
		obj_log.search([('registro_id','=', self.id )]).write(dct)

		dct={'parent_id':self.partner_id.id,
		    'street':self.street,
		    'ciudad_id':self.ciudad_id.id,
		    'name':self.contact_name,
		    'type':'contact',
		    'monto_anual':0.0,
		    'monto_mensual':0.0}
		self.env['res.partner'].create(dct)
    #""" EN ESTA PARTE INICIO CON EL FLUJO , ESTO SERIA CON EL TEMA DE IDENTIFICAR """
    
    def create(self, cr, uid, vals, context=None):
        
        partner_id =False;res_d=0;res=0
        date_partner = False
        print date_partner,'date partner'
	#""" ESTA VALIDACION SE DA CUANDO YO SELECCIONO EL PROSPECTO EN LA INICIATIVA QUE ESTOY CREANDO """
        if vals.has_key('partner_id') == True:
            if vals['partner_id'] != False:
                partner_id = True
		""" EN ESTA PARTE OBTENGO LAS FECHAS CON LAS QUE VOY A TRABAJAR """
                date_partner = self.pool.get('res.partner').browse(cr,uid, vals['partner_id'] ).create_date
		# 2018/08/05		
		if datetime.datetime.strptime(date_partner,'%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
			date_partner = datetime.datetime.now()
		# 2018/08/05
		
		partner_com = self.pool.get('res.partner').browse(cr,uid, vals['partner_id'] ).user_id.id
        #""" EN ESTA PARTE INSTANCIO EL OBJETO DONDE SE VAN A GUARDAR LAS FECHA Y DIAS DE LA TABLA DE BITACORA """
        obj_log=self.pool.get('log.crm.gestion')
	#AQUI VALIDO QUE SI EXISTE EL PARTNER ES POR QUE TIENE FECHA DE PROSPECTO YA QUE LA FECHA DE LA INICIATIVA SI VA A EXISTIR
	#SINO EXISTE EL PARTNER SE GUARDA UN CERO	
        if partner_id == True :
		# EN ESTA LINEA DE CODIGO EJECUTO EL QUERY QUE ME RETORNA LOS DIAS DE DESFACE TOMANDO EN CUENTA LA FECHA DE CREACION DE LA
		# INICIATIVA CON LA FECHA DE CREACION DEL PROSPECTO LOS PARAMETRO LOS PONGO DENTRO DE LA FUNCION FORMAT SI QUIERES VER
		# COMO FUNCIONA CON LAS CADENAS DE TEXTO MIRA EN INTERNET PARA QUE ENTIENDAS MEJOR
		# EN ESTE PRIMER QUERY SI TE DAS CUENTA SACO EL TIEMPO DE DIFERENCIA
		sql ="""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as fecha """.format(datetime.datetime.now(),date_partner)
                cr.execute(sql)
                res = cr.dictfetchall()[0]['fecha']
		# EN ESTA PARTE TENGO UN QUERY EN EL CUAL SOLO OBTENGO LOS DIAS SI TE FIJAS ESTOY SOLO SACANDO LOS DIAS DE
		# DE LA FECHA DE DIFERENCIA EN EN CASO DE QUE EXISTAN
		d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(datetime.datetime.now(),date_partner)
		cr.execute(d)
                res_d = cr.dictfetchall()[0]['dias']
		# EN ESTE CASO TOMO SEGUN LO CONVERSADO LAS HORAS , MINUTOS Y SEGUNDOS YA QUE TODO ESTO CUENTA PARA QUE EXISTA O
		# SE TOME COMO UN DIA A CONTAR Y SE GRABE EN LA BASE DE DATOS , SI TE FIJAS ESTOY OBTENIENDO HORAS , MINUTOS
		# Y SEGUNDOS Y AI MISMO EN EL QUERY LOS SUMO Y SI ENTRE LA SUMA DE HORAS , MINUTOS Y SEGUNDOS ME DA UNO O MAS DE UNO
		# SE GRABA  EN LA BASE UN DIA
		#9/9/2018
		h = """select 
		       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
		        +
		      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
		      as res
		""".format(datetime.datetime.now(),date_partner)
		cr.execute(h)
                res_h = cr.dictfetchall()[0]['res']
		# res_h == 0 :
		#    res_h = 1
		#if res_h >= 1 :
		#    res_d = res_d + 1
                res_d = res_d + res_h
		
		print res_d,'DIAS EN RES_D'
	# AQUI EN ESTA PARTE LO QUE HAGO ES QUE LUEGO DE CREAR OBTENER EL ID DEL REGISTO CREADO PARA PODER GRABARLO EN LA TABLA DE 
	# BITACORA PARA SABER DE QUE INCIATIVA COMIENZA
        var = super(crm_lead, self).create(cr, uid, vals, context)
	# SE CREA EL DICCIONARIO DE DATOS PARA PODER MANDAR A CREAR EN NUEVO REGISTRO EN LA TABLA DE BITACORA

	print date_partner,'date partner final procesado'
        dct={    'registro_id':var,
                 'usuario_crea':uid,
                 'fecha_prospecto':date_partner,
                 'fecha_iniciativa':datetime.datetime.now(),
                 'identificar':res,
		 'estado':'Identificar',
		 'dias_identificar':res_d,

                 }
	# AQUI EFECTUO LA CREACION SI TE FIJAS LA PALABRA > OBJ_LOG < ES LA INSTANCIA DE LA TABLA DE BITACORA Y CON LA FUNCION CREATE
	# DETERMINO QUE ME CREE EN LA TABLA EL REGISTOR NUEVO CON LOS DATOS DEL DICCIONARIO ANTERIOR
        obj_log.create(cr, uid, dct, context)
        return var


		###es_prospecto = self.pool.get('res.partner').browse(cr,uid, vals['partner_id'] ).prospectos
		###if es_prospecto == True:
		###    date_partner = self.pool.get('res.partner').browse(cr,uid, vals['partner_id'] ).create_date
		###else:
		###    date_partner = datetime.datetime.now()
		###partner_com = self.pool.get('res.partner').browse(cr,uid, vals['partner_id'] ).user_id.id
        
        ###obj_log=self.pool.get('log.crm.gestion')
	#AQUI VALIDO QUE SI EXISTE EL PARTNER ES POR QUE TIENE FECHA DE PROSPECTO YA QUE LA FECHA DE LA INICIATIVA SI VA A EXISTIR
	#SINO EXISTE EL PARTNER SE GUARDA UN CERO	
       ### if partner_id == True :
	###	sql ="""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as fecha """.format(datetime.datetime.now(),date_partner)
        ###        cr.execute(sql)
         ###       res = cr.dictfetchall()[0]['fecha']
		
	###	d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(datetime.datetime.now(),date_partner)
	###	cr.execute(d)
        ###        res_d = cr.dictfetchall()[0]['dias']

		#h = """select 
	#		(select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )
	#		+
	#		(select extract ( minute from ('{0}'::timestamp - '{1}'::timestamp))  )
	#		+
	#		(select extract ( second from ('{0}'::timestamp - '{1}'::timestamp))  )
	#		as res
	#	""".format(datetime.datetime.now(),date_partner)
	###	h = """select 
	###	       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
	###	        +
	###	      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
	###	      as res
	###	""".format(datetime.datetime.now(),date_partner)


	###	cr.execute(h)
        ###        res_h = cr.dictfetchall()[0]['res']
		# res_h == 0 :
		#    res_h = 1
		#if res_h >= 1 :
		#    res_d = res_d + 1
        ###        res_d = res_d + res_h
	###	print res_d,'DIAS EN RES_D'
		
        ###var = super(crm_lead, self).create(cr, uid, vals, context)
        ###dct={    'registro_id':var,
        ###         'usuario_crea':uid,
        ###         'fecha_prospecto':date_partner,
        ###         'fecha_iniciativa':datetime.datetime.now(),
        ###         'identificar':res,
	###	 'estado':'Identificar',
	###	 'dias_identificar':res_d,

        ###         }
        ###obj_log.create(cr, uid, dct, context)
        ###return var
    #28-02-2018
    @api.one
    def aprobar_iniciativa(self):
	partner = self.env['res.partner']
	partner.search([('id','=', self.partner_id.id )]).write({'customer':True,'prospectos':False})
	self.write({'estado':'A'})


    @api.one
    def rechazar_iniciativa(self):
	partner = self.env['res.partner']
	partner.search([('id','=', self.partner_id.id )]).write({'customer':False,'prospectos':True})
	self.write({'estado':'R'})
    #28-02-2018
    #11/9/2018	
    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            partner_name = (partner.parent_id and partner.parent_id.name) or (partner.is_company and partner.name) or False
            values = {
                'partner_name': partner_name,
                'contact_name': (not partner.is_company and partner.name) or False,
                'title': partner.title and partner.title.id or False,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city,
                'state_id': partner.state_id and partner.state_id.id or False,
                'country_id': partner.country_id and partner.country_id.id or False,
                'email_from': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'fax': partner.fax,
                'zip': partner.zip,
                'function': partner.function,
		'contacto_id':None,
            }
        return {'value': values}
    #11/9/2018
    

    @api.multi
    def write(self,vals):
        #11/9/2018
        print vals,'VALS DE WRITE ESTO SALE'

	#12/9/2018 
	for lead in self:
	    if vals.has_key('stage_id') == False and lead.type != 'opportunity':
	
		if lead.type == 'opportunity' and lead.stage_id.name in ('Ganado','Won','Lost','Perdido'):
			raise osv.except_osv(('Warning!'),('No puede realizar cambios en este proceso cerrado '))
	#12/9/2018




	#for lead in self:
	#	print lead.type , lead.stage_id.name , 'AAA;]LLLLLLLLLLL'
	#	if lead.type == 'opportunity' and lead.stage_id.name in ('Ganado','Won','Lost','Perdido'):
	#		raise osv.except_osv(('Warning!'),('No puede realizar cambios en este proceso cerrado '))
        #11/9/2018


        

        
        partner_id =False
        date_partner = False
        date_contacto = False
       
        if vals.has_key('partner_id') == True:
            if vals['partner_id'] != False:
                partner_id = True
		#EN ESTA PARTE VALIDO QUE SI EXISTE EL PARTNER BUSCOLA FECHA DEL PROSPECTO PARA IDENTIFICAR                
		date_partner = self.env['res.partner'].search([('id','=', vals['partner_id'] )]).create_date
		
                self._cr.execute(""" select max(create_date) as fecha_contacto 
                            from res_partner where parent_id = {0} and create_date <= '{1}' """.format(vals['partner_id'],self.create_date))
                date_contacto = self._cr.dictfetchall()[0]['fecha_contacto']


        identificar,preparar='0','0'
	d=0;h=0;horas=0.0;hh=0;res_d=0
	# INSTANCIO OBJETO DE BITACORA
        obj_log=self.env['log.crm.gestion']
        datos=obj_log.search([('registro_id','=', self.id )])
	print 'ESTADO A INGRESA',len(datos)
        if len(datos) >= 1:
	    # VALIDO SI EXITEN LOS DATOS QUE NECESITO 
            if partner_id == True and self.create_date and date_contacto == False:
		print 'IDENTIFICAR'
		d=0;h=0;horas=0.0;hh=0
		# EM ESTA PARTE PONGO LAS FECHAS QUE DEBEN RESTARSE PARA OBTENER LOS DIAS 
                self._cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(self.create_date,date_partner))
                identificar = self._cr.dictfetchall()[0]['tmp']
		# OBTENGO EL DIA		
		d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(self.create_date,date_partner)
		self._cr.execute(d)
                res_d = self._cr.dictfetchall()[0]['dias']
		# VALIDO SI SE METE UN DIA MAS O QUEDA COMO UN DIA SI EXISTE HORA , MINUTOS O SEGUNDOS
		#9/9/2018
		###h = """select 
		###	(select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )
		###	+
		###	(select extract ( minute from ('{0}'::timestamp - '{1}'::timestamp))  )
		###	+
		###	(select extract ( second from ('{0}'::timestamp - '{1}'::timestamp))  )
		###	as res
		###""".format(self.create_date,date_partner)

		h = """select 
		       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
		        +
		      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
		      as res
		""".format(self.create_date,date_partner)

		self._cr.execute(h)
                res_h = self._cr.dictfetchall()[0]['res']
		###if res_h == 0 :
		###    res_h = 1
		###if res_h >= 1 :
		###    res_d = res_d + 1
		###print res_d,'DIAS EN RES_D'
                res_d = res_d + res_h

		dct={'registro_id':self.id,
                 'usuario_crea':self.create_uid.id,
                 'fecha_prospecto':date_partner,
                 'fecha_iniciativa':self.create_date,
                 'identificar':identificar,
                 'estado':'identificar',
		 'dias_identifica':res_d,
                 }
		# aqui con el objeto de bitacora instanciado y con el search busco la linea que corresponde a la iniciativa
		# voy a actualizar con el diccionario que esta arriba
                obj_log.search([('registro_id','=', self.id )]).write(dct)

            if date_contacto != None and date_contacto != False:
		print 'PREPARAR'
		d=0;h=0;horas=0.0;hh=0;

		if datetime.datetime.strptime(date_contacto[0:19],'%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
			date_contacto = self.create_date
                self._cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(date_contacto,self.create_date))
                preparar = self._cr.dictfetchall()[0]['tmp']
		if preparar == '': 
			preparar = '0' 		
		d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(date_contacto,self.create_date)
		self._cr.execute(d)
                res_d = self._cr.dictfetchall()[0]['dias']
		###h = """select 
		###	(select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )
		###	+
		###	(select extract ( minute from ('{0}'::timestamp - '{1}'::timestamp))  )
		###	+
		###	(select extract ( second from ('{0}'::timestamp - '{1}'::timestamp))  )
		###	as res
		###""".format(date_contacto,self.create_date)
		h = """select 
		       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
		        +
		      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
		      as res
		""".format(date_contacto,self.create_date)
		self._cr.execute(h)
                res_h = self._cr.dictfetchall()[0]['res']
                res_d = res_d + res_h
		###print res_h ,'ESTO ESTA EN RES H'
		###if res_h == 0 :
		###    res_h = 1
		###if res_h >= 1 :
		###    res_d = res_d + 1
		print res_d,'DIAS EN RES_D'
		fecha_iniciativa=self.create_date
		#25-02-2018
	        #cliente exitsnte pero con pruebas
	        self._cr.execute(""" select 
			coalesce(dias_identificar,0)
			 as dias
			from log_crm_gestion where registro_id = {0} """.format(self.id))
	        dias_prepa=self._cr.dictfetchall()[0]['dias']
	        if dias_prepa == 0:
		    self._cr.execute(""" select 
			fecha_prospecto
			from log_crm_gestion where registro_id = {0} """.format(self.id))
		    fecha_iniciativa=self._cr.dictfetchall()[0]['fecha_prospecto']
	        #25-02-2018
		
                dct={'registro_id':self.id,
                 'usuario_crea':self.create_uid.id,
                 'fecha_iniciativa':fecha_iniciativa,
                 'fecha_contacto':date_contacto,
                 'preparar':preparar,
		 'estado':'Preparar',
		 'dias_preparar':res_d,
                 }
                obj_log.search([('registro_id','=', self.id )]).write(dct)
	
	#13-03-2018
	var = 0

        if vals.has_key('detalle_ventas') == True:
	    for p in self.detalle_ventas:
		if p != False:
		    if p.tipo == 'fin':
		        var += 1
		        if var > 1:
			    raise osv.except_osv(('Warning!'),('NO puede definir mas de una OFERTA final '))
		        else:
			    print 'OK'
	var_u = 0
	if vals.has_key('detalle_ventas') == True:
		for p in vals['detalle_ventas']:
			if p[2] != False:
				if p[2]['tipo'] == 'fin':
				    var += 1
				    if var > 1:
				        raise osv.except_osv(('Warning!'),('NO puede definir mas de una orferta final '))
				    else:
				        print 'OK'
	#13-03-2018			
	#9/9/2018	
	#13/09/2018 OFERTA AQUISE VALIDA SI SE CREA UNA COTIZACION 
        if vals.has_key('ref') == True:
	    for p in self.detalle_ventas:
			print p,'ESTO ES EL VALOR DE PPPPPPPPPPPPPPPPPPP'
			if p != False:
				if p.tipo in ('fin','ini','uni'):
					date_order = self.env['sale.order'].search([('id','=', p.id )]).create_date
					self._cr.execute("""select max(create_date) as create_date from calendar_event where 
						opportunity_id = {0} and create_date <= '{1}' and otras_visitas = 'S' """.format(self.id,date_order))
					date_reunion = self._cr.dictfetchall()[0]['create_date']
					print 'ESTA ES LA FECHA DE REUNION DE PRUEBAS ',date_reunion
					if not date_reunion:
					    self._cr.execute("""select max(create_date) as create_date from calendar_event where 
					opportunity_id = {0} and create_date <= '{1}' and primera_visita = 't' """.format(self.id,date_order))
					    date_reunion = self._cr.dictfetchall()[0]['create_date']
					print date_reunion,'ESTO ES EL DATE DE REUNION PRIMERA VISITA'
					if date_reunion:
					    #25-02-2018
					    #esto es cuendo el prospecto quiere comprar rapido
					    self._cr.execute(""" select 
							coalesce(dias_seguimiento,0) 
							+ 
							coalesce(dias_pruebas,0) as dias
							from log_crm_gestion where registro_id = {0} """.format(self.id))
					    dias_seg_pru=self._cr.dictfetchall()[0]['dias']
					    if dias_seg_pru == 0:
						print 'ingresa por que no existe seguimiento ni pueebas y este el el valor',dias_seg_pru
						self._cr.execute(""" select 
							fecha_reunion
							from log_crm_gestion where registro_id = {0} """.format(self.id))
					        date_reunion=self._cr.dictfetchall()[0]['fecha_reunion']
					    self._cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(date_order,date_reunion))
					    oferta = self._cr.dictfetchall()[0]['tmp']
					    d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(date_order,date_reunion)
					    self._cr.execute(d)
					    res_d = self._cr.dictfetchall()[0]['dias']
					    h = """select 
					       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
						+
					      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
					      as res
					    """.format(date_order,date_reunion)
					    self._cr.execute(h)
					    res_h = self._cr.dictfetchall()[0]['res']
					    # res_h == 0 :
					    #    res_h = 1
					    #if res_h >= 1 :
					    #    res_d = res_d + 1
					    res_d = res_d + res_h
		
					    print res_d,'DIAS EN RES_D'

					    #25-02-2018
					    # prospecto referido quiere comprar sin visita y sin prueba
					    self._cr.execute(""" select 
							coalesce(dias_primera_visita,0) 
							+
							coalesce(dias_seguimiento,0) 
							+ 
							coalesce(dias_pruebas,0) as dias
							from log_crm_gestion where registro_id = {0} """.format(self.id))
					    dias_seg_pru=self._cr.dictfetchall()[0]['dias']
					    if dias_seg_pru == 0:
						print 'ingresa por que no existe seguimiento ni pueebas y este el el valor',dias_seg_pru
						date_reunion=self.create_date
					    #25-02-2018

					    #25-02-2018
					    #esto es cuendo el prospecto quiere comprar rapido
					    self._cr.execute(""" select 
							coalesce(dias_identificar,0) 
							+ 
							coalesce(dias_preparar,0) 
							+
							coalesce(dias_pruebas)as dias
							from log_crm_gestion where registro_id = {0} """.format(self.id))
					    dias_seg_pru=self._cr.dictfetchall()[0]['dias']
					    if dias_seg_pru == 0:
						
						date_reunion=self.create_date
					    #25-02-2018


					    dct={'fecha_oferta_final':date_order,
					       'fecha_reunion_pruebas':date_reunion,
					       'oferta':oferta,
					       'estado':'Oferta',
					       'dias_oferta':res_d,
					     }
				    	    obj_log.search([('registro_id','=', self.id )]).write(dct)
	#13/09/2018  CAMBIO PARA OFERTA	
        return super(crm_lead, self).write( vals)



    def case_mark_lost(self, cr, uid, ids, context=None):
        """ Mark the case as lost: state=cancel and probability=0
        """
        stages_leads = {}
	inicio,fin,unico,fecha_final,fecha_inicial = 0,0,0,'',''
	res_d=0
	obj_log=self.pool.get('log.crm.gestion')
        for lead in self.browse(cr, uid, ids, context=context):
	    for sale in lead.detalle_ventas:
	        print sale.tipo,'TIPOS'
		if sale.tipo == 'ini':
		    inicio=1
		    fecha_inicial = sale.create_date
		if sale.tipo == 'fin':
		    fin=1
		    fecha_final = sale.create_date
		if sale.tipo == 'uni':
		    fecha_final = sale.create_date
		    unico=1
	    if fecha_final != '' and fecha_inicial != '':
		if fecha_final < fecha_inicial:
		    raise osv.except_osv(('Warning!'),('La fecha inicial no puede ser mayor a la fecha final'))  
	    if unico ==0:
	        if inicio == 1 and fin == 1: 
			cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(datetime.datetime.now(),fecha_final))
			negociacion = cr.dictfetchall()[0]['tmp']
		        cr.execute("""select id from log_crm_gestion where registro_id = {0} """.format(ids[0]))
		        res_id = cr.dictfetchall()[0]['id']

			d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(datetime.datetime.now(),fecha_final)
			cr.execute(d)
			res_d = cr.dictfetchall()[0]['dias']
			h = """select 
					       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
						+
					      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
					      as res
		        """.format(datetime.datetime.now(),fecha_final)
			cr.execute(h)
			res_h = cr.dictfetchall()[0]['res']
			#if res_h == 0 :
		    	#    res_h = 1
			#if res_h >= 1 :
			#    res_d = res_d + 1
			#print res_d,'DIAS EN RES_D'
		        res_d = res_d + res_h
		
			print res_d,'DIAS EN RES_D'


			dct={'fecha_gan_perd':datetime.datetime.now(),
			
				'negociacion':negociacion,
				'estado':'Negociacion',
				'dias_negociacion':res_d,
				}
			obj_log.write(cr, uid, res_id, dct , context=context)
		else:
			raise osv.except_osv(('Warning!'),('Para poder cerrar la oportunidad debe existir una oferta inicial y final'))
	    print unico, inicio , fin , '<--------------------------------ppppp'
	    
	    if unico ==1 :
		if inicio == 0 and fin == 0:
			cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(datetime.datetime.now(),fecha_final))
			negociacion = cr.dictfetchall()[0]['tmp']
		        cr.execute("""select id from log_crm_gestion where registro_id = {0} """.format(ids[0]))
		        res_id = cr.dictfetchall()[0]['id']
		
			d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(datetime.datetime.now(),fecha_final)
			cr.execute(d)
		        res_d = cr.dictfetchall()[0]['dias']
			h = """select 
					       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
						+
					      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
					      as res
		        """.format(datetime.datetime.now(),fecha_final)
		        cr.execute(h)
		        res_h = cr.dictfetchall()[0]['res']
		        # res_h == 0 :
		        #    res_h = 1
		        #if res_h >= 1 :
		        #    res_d = res_d + 1
		        res_d = res_d + res_h

			print res_d,'DIAS EN RES_D'

			dct={'fecha_gan_perd':datetime.datetime.now(),
			
				'negociacion':negociacion,
				'estado':'Negociacion',
				'dias_negociacion':res_d,
				}
			obj_log.write(cr, uid, res_id, dct , context=context)
		else:
			raise osv.except_osv(('Warning!'),('Para poder cerrar la oportunidad debe solo unico'))  

            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 0.0), ('on_change', '=', True), ('sequence', '>', 1)], context=context)
            if stage_id:
                if stages_leads.get(stage_id):
                    stages_leads[stage_id].append(lead.id)
                else:
                    stages_leads[stage_id] = [lead.id]
            else:
                raise osv.except_osv(_('Warning!'),
                    _('To relieve your sales pipe and group all Lost opportunities, configure one of your sales stage as follow:\n'
                        'probability = 0 %, select "Change Probability Automatically".\n'
                        'Create a specific stage or edit an existing one by editing columns of your opportunity pipe.'))
        for stage_id, lead_ids in stages_leads.items():
            self.write(cr, uid, lead_ids, {'stage_id': stage_id}, context=context)
        return True

#28-02-2018

    def case_mark_won(self, cr, uid, ids, context=None):
        """ Mark the case as won: state=done and probability=100
        """
	inicio,fin,unico,fecha_final,fecha_inicial,fecha_unico = 0,0,0,'','',''
	#23/08/2018
	#VALIDA SI EXISTE UNA REUNION DE PRIMERA VISITA SINO LA DEBE CREAR
	cr.execute(""" select count(*) as contados 
                            from calendar_event where lead_id = {0} and 
			primera_visita = 't' """.format(ids[0]))
       	contados = cr.dictfetchall()[0]['contados']
	print contados
	if int(contados) < 1:
		 raise osv.except_osv(('Alerta!'),('Para poder marcar como ganada la oportunidad debe tener creada al menos una reunion de primera visita'))  
	#23/08/2018
	#aqui valido para crear la primera visita solo si obtengo la fecha del contacto creado antes de crear la iniciativa


	res_d=0
	obj_log=self.pool.get('log.crm.gestion')
        stages_leads = {}
        for lead in self.browse(cr, uid, ids, context=context):
	    for sale in lead.detalle_ventas:
	        print sale.tipo,'TIPOS'
		if sale.tipo == 'ini':
		    inicio=1
		    fecha_inicial = sale.create_date
		if sale.tipo == 'fin':
		    fin=1
		    fecha_final = sale.create_date
		if sale.tipo == 'uni':
		    unico=1
		    fecha_final = sale.create_date
	    if fecha_final != '' and fecha_inicial != '':
		if fecha_final < fecha_inicial:
		    raise osv.except_osv(('Warning!'),('La fecha inicial no puede ser mayor a la fecha final'))  
	    if unico ==0:
	    	if inicio == 1 and fin == 1: 
			cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(datetime.datetime.now(),fecha_final))
			negociacion = cr.dictfetchall()[0]['tmp']
		        cr.execute("""select id from log_crm_gestion where registro_id = {0} """.format(lead.id))
		        res_id = cr.dictfetchall()[0]['id']

			d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(datetime.datetime.now(),fecha_final)
			cr.execute(d)
		        res_d = cr.dictfetchall()[0]['dias']

			h = """select 
					       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
						+
					      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
					      as res
		        """.format(datetime.datetime.now(),fecha_final)
		        cr.execute(h)
		        res_h = cr.dictfetchall()[0]['res']
		        # res_h == 0 :
		        #    res_h = 1
		        #if res_h >= 1 :
		        #    res_d = res_d + 1
		        res_d = res_d + res_h


			print res_d,'DIAS EN RES_D'		
		       
			dct={'fecha_gan_perd':datetime.datetime.now(),
			
				'negociacion':negociacion,
				'estado':'Negociacion',
				'dias_negociacion':res_d,
				}
			obj_log.write(cr, uid, res_id, dct , context=context)

		else:
			raise osv.except_osv(('Warning!'),('Para poder cerrar la oportunidad debe existir una oferta inicial y final'))  
	    print unico, inicio , fin , '<--------------------------------ppppp'
	    if unico ==1: 
		if inicio == 0 and fin == 0:
			cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(datetime.datetime.now(),fecha_final))
			negociacion = cr.dictfetchall()[0]['tmp']
		        cr.execute("""select id from log_crm_gestion where registro_id = {0} """.format(ids[0]))
		        res_id = cr.dictfetchall()[0]['id']

			d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(datetime.datetime.now(),fecha_final)
			cr.execute(d)
		        res_d = cr.dictfetchall()[0]['dias']

			h = """select 
					       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
						+
					      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
					      as res
			""".format(datetime.datetime.now(),fecha_final)
			cr.execute(h)
		        res_h = cr.dictfetchall()[0]['res']
			res_d = res_d + res_h
			print res_d,'DIAS EN RES_D'	

			dct={'fecha_gan_perd':datetime.datetime.now(),
			
				'negociacion':negociacion,
				'estado':'Negociacion',
				'dias_negociacion':res_d,
				}
			obj_log.write(cr, uid, res_id, dct , context=context)
		else:
		    raise osv.except_osv(('Warning!'),('Para poder cerrar la oportunidad debe solo unico'))  
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 100.0), ('on_change', '=', True)], context=context)
            if stage_id:
                if stages_leads.get(stage_id):
                    stages_leads[stage_id].append(lead.id)
                else:
                    stages_leads[stage_id] = [lead.id]
            else:
                raise osv.except_osv(_('Warning!'),
                    _('To relieve your sales pipe and group all Won opportunities, configure one of your sales stage as follow:\n'
                        'probability = 100 % and select "Change Probability Automatically".\n'
                        'Create a specific stage or edit an existing one by editing columns of your opportunity pipe.'))
        for stage_id, lead_ids in stages_leads.items():
            self.write(cr, uid, lead_ids, {'stage_id': stage_id}, context=context)
        return True 
#28-02-2018

    def action_schedule_meeting(self, cr, uid, ids, context=None):
        """
        Open meeting's calendar view to schedule meeting on current opportunity.
        :return dict: dictionary value for created Meeting view
        """
        lead = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        partner_ids = [self.pool['res.users'].browse(cr, uid, uid, context=context).partner_id.id]
        if lead.partner_id:
            partner_ids.append(lead.partner_id.id)
        res['context'] = {
            'search_default_opportunity_id': lead.type == 'opportunity' and lead.id or False,
            'default_opportunity_id': lead.type == 'opportunity' and lead.id or False,
            'default_partner_id': lead.partner_id and lead.partner_id.id or False,
            'default_partner_ids': partner_ids,
            'default_section_id': lead.section_id and lead.section_id.id or False,
            'default_name': lead.name,
            'default_lead_id':lead.id,
        }
        return res
        
