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
from openerp.tools.translate import _
import re

class crm_lead2opportunity_partner(osv.osv_memory):
    _name = 'crm.lead2opportunity.partner'
    
    _inherit = 'crm.lead2opportunity.partner'

    
    def action_apply(self, cr, uid, ids, context=None):
        
        """
        Convert lead to opportunity or merge lead and opportunity and open
        the freshly created opportunity view.
        """
        if context is None:
            context = {}

        lead_obj = self.pool['crm.lead']

        w = self.browse(cr, uid, ids, context=context)[0]
        if w.partner_id.customer == False :
            raise osv.except_osv(('Warning!'), ('Para continuar debe aprobarse el Prospecto como Cliente'))
        print len(w.partner_id.child_ids),'CUANTOS TENGO'
        if len(w.partner_id.child_ids) < 1 :
            raise osv.except_osv(('Warning!'), ('Para continuar el Cliente debe tener creado contactos'))
        
        opp_ids = [o.id for o in w.opportunity_ids]
        vals = {
            'section_id': w.section_id.id,
        }
        
        if w.partner_id:
            vals['partner_id'] = w.partner_id.id
        if w.name == 'merge':
            lead_id = lead_obj.merge_opportunity(cr, uid, opp_ids, context=context)
            lead_ids = [lead_id]
            lead = lead_obj.read(cr, uid, lead_id, ['type', 'user_id'], context=context)
            if lead['type'] == "lead":
                context = dict(context, active_ids=lead_ids)
                vals.update({'lead_ids': lead_ids, 'user_ids': [w.user_id.id]})
                self._convert_opportunity(cr, uid, ids, vals, context=context)
            elif not context.get('no_force_assignation') or not lead['user_id']:
                vals.update({'user_id': w.user_id.id})
                lead_obj.write(cr, uid, lead_id, vals, context=context)
        else:
            #9/9/2018
            lead_ids = context.get('active_ids', [])
            lead = lead_obj.browse(cr, uid, lead_ids, context=context)
            if not lead.contacto_id :
                raise osv.except_osv(('Warning!'), ('Para continuar defina contacto en la iniciativa'))
            #9/9/2018
            vals.update({'lead_ids': lead_ids, 'user_ids': [w.user_id.id]})
            self._convert_opportunity(cr, uid, ids, vals, context=context)

        return self.pool.get('crm.lead').redirect_opportunity_view(cr, uid, lead_ids[0], context=context)

   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

