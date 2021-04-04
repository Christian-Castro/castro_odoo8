import pooler
#import wizard
import base64
import netsvc
from tools.translate import _
import time
from osv import osv, fields

class atsprocesowizard(osv.osv_memory):
    _name = 'atsprocesowizard'
    
    _columns = {
        'facturae':fields.binary('Facturae File', readonly=True),
        'facturae_fname':fields.char('File Name', size=64),
        'note':fields.text('Log'),    
    }
    
    def _get_facturae_fname(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        res = self._get_invoice_facturae_xml(cr, uid, data, context)
        return res['facturae_fname']
        
    def _get_facturae(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        res = self._get_invoice_facturae_xml(cr, uid, data, context)
        return res['facturae']
        
    _defaults = {
        'facturae_fname':_get_facturae_fname,
        'facturae':_get_facturae,    
    }
    
    def _get_invoice_facturae_xml(self, cr, uid, data, context=None):
        if not context:
            context = {}
        
        atsproceso_obj = self.pool.get('fiscal.ats_proceso')
        ids = data['active_ids']
        id = ids[0]
        atsproceso = atsproceso_obj.browse(cr, uid, [id], context=context)[0]
        xml_data = atsproceso.toxml()
        fdata = base64.encodestring( xml_data )
        fname_invoice='facturaxml.xml'
        return {'facturae': fdata, 'facturae_fname': fname_invoice,}
    
atsprocesowizard()
