# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

import datetime
from openerp.osv import fields, osv
from openerp import api

class crm_phonecall(osv.osv):
    """ Model for CRM phonecalls """
    _name = "crm.phonecall"
    _inherit = "crm.phonecall"
    
    _columns = {
        'primera_llamada':fields.boolean('Es primera llamada?'),
        
    }
    
    _defaults = {  
        'primera_llamada': False,  
        }
    
    def create(self, cr, uid, vals, context=None):
        #11/9/2018
	for lead in self.pool.get('crm.lead').browse(cr,uid,[context['default_opportunity_id']],context):
		print lead.type , lead.stage_id.name , 'AAA;]LLLLLLLLLLL'
		if lead.type == 'opportunity' and lead.stage_id.name in ('Ganado','Won','Lost','Perdido'):
			raise osv.except_osv(('Warning!'),('No puede realizar cambios en este proceso cerrado '))
        #11/9/2018
	
        print context
        print vals,'Vals'
        res = '0';
	res_d=0
        obj_log = self.pool.get('log.crm.gestion')
        #obtengo la fecha de la reunion primera visita
        cr.execute(""" select fecha_reunion 
                from log_crm_gestion where registro_id = {0}""".format(context['default_opportunity_id']))
        fecha_reunion_p_visita = cr.dictfetchall()[0]['fecha_reunion']

        print fecha_reunion_p_visita,'reuion primera visita'
	# si existe la fecha de primera visita ingreso y calculo la diferencia entre
	# (primera llamada saliente) - la reunion (reunion de primera visita)
	cr.execute("""select count(*) as cantidad from crm_phonecall where opportunity_id = {0} and categ_id = 10 """.format(context['default_opportunity_id']))
        contados = cr.dictfetchall()[0]['cantidad']	
	if vals.has_key('categ_id') == True:
            if vals['categ_id'] == 10 and fecha_reunion_p_visita and contados == 0:
        	cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(datetime.datetime.now(),fecha_reunion_p_visita))
	        res = cr.dictfetchall()[0]['tmp']

		d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(datetime.datetime.now(),fecha_reunion_p_visita)
		cr.execute(d)
                res_d = cr.dictfetchall()[0]['dias']

		h = """select 
					       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
						+
					      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
					      as res
		""".format(datetime.datetime.now(),fecha_reunion_p_visita)
		cr.execute(h)
                res_h = cr.dictfetchall()[0]['res']
		res_d = res_d + res_h
		print res_d,'DIAS EN RES_D'
		
		#25-02-2018
	        #cliente existente pero con pruebas
	        cr.execute(""" select 
			count(*) as dias
			from log_crm_gestion where registro_id = {0} """.format(context['default_opportunity_id']))
	        dias_prepa=cr.dictfetchall()[0]['dias']
	        if dias_prepa == 0:
		    cr.execute("""select count(*) as cantidad from calendar_event where lead_id = {0}  """.format(context['default_opportunity_id']))
		    contados = cr.dictfetchall()[0]['cantidad']
		    if contados > 1:
		    	res_d = 1
	        #25-02-2018

		dct={'fecha_pllamada':datetime.datetime.now(),
		     'fecha_preunion':fecha_reunion_p_visita,
		     'seguimiento':res,
		     'estado':'Seguimiento',
		     'dias_seguimiento':res_d,
		}
            	vals['primera_llamada']='t'
            	cr.execute("""select id from log_crm_gestion where registro_id = {0} """.format(context['default_opportunity_id']))
            	idn = cr.dictfetchall()[0]['id']
            	obj_log.write(cr,uid,[idn],dct)

        return super(crm_phonecall, self).create(cr, uid, vals, context)
    

    @api.multi
    def write(self, vals):
        
        #11/9/2018
        print vals,'VALS DE WRITE ESTO SALE'
	for lead in self.opportunity_id:
		print lead.type , lead.stage_id.name , 'AAA;]LLLLLLLLLLL'
		if lead.type == 'opportunity' and lead.stage_id.name in ('Ganado','Won','Lost','Perdido'):
			raise osv.except_osv(('Warning!'),('No puede realizar cambios en este proceso cerrado '))
        #11/9/2018
        print vals,'Vals'
        res = '0';
	res_d=0
        obj_log = self.env['log.crm.gestion']
        #obtengo la fecha de la reunion primera visita
        self._cr.execute(""" select fecha_reunion 
                from log_crm_gestion where registro_id = {0}""".format(self.opportunity_id.id))
        fecha_reunion_p_visita = self._cr.dictfetchall()[0]['fecha_reunion']

        print fecha_reunion_p_visita,'reuion primera visita'
	# si existe la fecha de primera visita ingreso y calculo la diferencia entre
	# (primera llamada saliente) - la reunion (reunion de primera visita)
	self._cr.execute("""select count(*) as cantidad from crm_phonecall where opportunity_id = {0} and categ_id = 10 """.format(self.opportunity_id.id))
        contados = self._cr.dictfetchall()[0]['cantidad']	
	if vals.has_key('categ_id') == True:
            if vals['categ_id'] == 10 and fecha_reunion_p_visita and contados >= 1:
        	self._cr.execute("""select ('{0}'::timestamp - '{1}'::timestamp)::varchar as tmp """.format(datetime.datetime.now(),fecha_reunion_p_visita))
	        res = self._cr.dictfetchall()[0]['tmp']

		d = """select extract (day from ('{0}'::timestamp - '{1}'::timestamp)) as dias """.format(datetime.datetime.now(),fecha_reunion_p_visita)
		self._cr.execute(d)
                res_d = self._cr.dictfetchall()[0]['dias']

		h = """select 
					       round((select extract (hour from ('{0}'::timestamp - '{1}'::timestamp)) )/24 
						+
					      (select extract ( minute from ( '{0}'::timestamp - '{1}'::timestamp))  )/1440)
					      as res
		""".format(datetime.datetime.now(),fecha_reunion_p_visita)
		self._cr.execute(h)
                res_h = self._cr.dictfetchall()[0]['res']
		res_d = res_d + res_h
		print res_d,'DIAS EN RES_D'
		
		#25-02-2018
	        #cliente existente pero con pruebas
	        self._cr.execute(""" select 
			count(*)  as dias
			from log_crm_gestion where registro_id = {0} """.format(self.opportunity_id.id))
	        dias_prepa=self._cr.dictfetchall()[0]['dias']
	        if dias_prepa == 0:
		    cr.execute("""select count(*) as cantidad from calendar_event where lead_id = {0}  """.format(self.opportunity_id.id))
		    contados =self._cr.dictfetchall()[0]['cantidad']
		    if contados > 1:
		    	res_d = 1
	        #25-02-2018

		dct={'fecha_pllamada':datetime.datetime.now(),
		     'fecha_preunion':fecha_reunion_p_visita,
		     'seguimiento':res,
		     'estado':'Seguimiento',
		     'dias_seguimiento':res_d,
		}
            	vals['primera_llamada']='t'
            	self._cr.execute("""select id from log_crm_gestion where registro_id = {0} """.format(self.opportunity_id.id))
            	idn = self._cr.dictfetchall()[0]['id']

		obj_log.search([('registro_id','=', idn )]).write(dct)

        return super(crm_phonecall, self).write(vals)

