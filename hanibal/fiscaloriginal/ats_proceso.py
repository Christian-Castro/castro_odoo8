# -*- encoding: utf-8 -*-

from openerp.osv import osv,fields
from xml.dom import minidom
from calendar import monthrange
import base64,time
import datetime


class fiscal_ats_proceso(osv.osv):
    
    
    
    Mes = [
             ('01','Enero'),
             ('02','Febrero'), 
             ('03','Marzo'),
             ('04','Abril'),
             ('05','Mayo'),
             ('06','Junio'),
             ('07','Julio'),
             ('08','Agosto'),
             ('09','Septiembre'),
             ('10','Octubre'),
             ('11','Noviembre'),
             ('12','Diciembre')
            ]
    
    ESTADOS = [
                ('draft','Borrador'),
                ('abierto','Abierto'),
                ('cerrado','Cerrado'),
              ]
    
    def _get_company_id(self, cr, uid, data, context=None):
        usuario = self.pool.get('res.users').browse(cr,uid,uid,context)
        return usuario.company_id.id
    
    _name = 'fiscal.ats_proceso'
    
    _columns = {
                
            'anio_id':fields.many2one('account.fiscalyear','Año',required=True),
            'mes' : fields.selection(Mes,'Mes',required=True),
            'company_id': fields.many2one('res.company', 'Empresa', required=True),
            'compras': fields.one2many('fiscal.ats_compras','atsproceso_id','Compras'),
            'ventas': fields.one2many('fiscal.ats_ventas','atsproceso_id','Ventas'),
            'anulados': fields.one2many('fiscal.comprobantesanulados','atsproceso_id','Anulados'),
            'emision':fields.one2many('fiscal.ats_ventaptoemision','atsproceso_id','Punto Emision'),
            'procesacompras' : fields.boolean('procesa Compras', required=True),
            'procesaventas' : fields.boolean('Calculo Ventas', required=True),
            'procesaanulados' : fields.boolean('Calculo Anulado', required=True),
            'procesaventasptoemision' : fields.boolean('Calculo Punto Emision', required=True),
            'fechacerrado' : fields.date('Fecha de Cierre',),
            'name':fields.char("name"),
            'state': fields.selection(ESTADOS,'Estado', select=True, readonly=True),
            'xml_filename': fields.char('Archivo XML'),
            'xml_binary': fields.binary('Archivo XML'),
        }

    _defaults = {    
            'state' : 'draft',
            'name' : 'Anexos',
            'procesacompras' : True,
            'procesaventas' : True,
            'procesaanulados' : True,
            'procesaventasptoemision':True,
            'company_id': _get_company_id,
        }
    
  
    def genera_archivo(self, cr, uid, ids, context=None):
        
        content = self.toxml(cr,uid,ids,context=None)
        file_name = "Anexo_SRI_"+str(time.strftime('%Y-%m-%d'))+".xml"
        return self.write(cr, uid, ids, {
            'xml_filename': file_name,
            'xml_binary': base64.encodestring(content)
        }, context=context)
    
    def _get_nombre_mes(self,mes):
        return dict(self.Mes)[mes]        
    
    def cerrar_ats(self,cr,uid,ids,context):
        values = {'state':'cerrado','fechacerrado':'now()'}
        self.write(cr,uid,ids,values)
        return True   
    
    def proceso_nuevamente(self,cr,uid,ids,context):
        return self.ats_procesar(cr,uid,ids,context)
    
    def ats_procesar(self, cr, uid, ids,context):
        
        contex={}
        ats_obj = self.browse(cr, uid, ids, contex)[0]
        anio = ats_obj.anio_id.name
        mes  = ats_obj.mes
        si_ventas   = ats_obj.procesaventas
        si_compras  = ats_obj.procesacompras
        si_anulados = ats_obj.procesaanulados
        si_ventasptoemision = ats_obj.procesaventasptoemision
        
        if si_compras:
            self._procesa_compras(cr,uid,ats_obj.id,anio,mes)
        if si_ventas:
            self._procesa_ventas(cr,uid,ats_obj.id,anio,mes)
        if si_anulados:
            self._procesa_anulados(cr,uid,ats_obj.id,anio,mes)
        if si_ventasptoemision:
            self._procesa_ventasptoemision(cr,uid,ats_obj.id,anio,mes)
        values = {'state':'abierto'}
        self.write(cr,uid,ids,values)
        return True

    def _procesa_compras(self,cr,uid,ident,anio,mes,):
        
        delete_reembolsos = """ delete from fiscal_ats_reembolsos where id in (
                                select ar.id from fiscal_ats_reembolsos ar, fiscal_ats_compras ac, fiscal_ats_proceso ap
                                where ap.id = ac.atsproceso_id and
                                ac.id = ar.reembolsos_ids
                                and ap.id = %s ) """
        cr.execute(delete_reembolsos,(ident,))
        cr.commit()
        
        delete_detalleair = """ DELETE FROM fiscal_ats_detalleair as det USING fiscal_ats_compras as ats
                    WHERE det.ats_compra_id = ats.id 
                    and ats.atsproceso_id = %s """
        
        borro_atscompra = """ delete from fiscal_ats_compras ats 
                    where ats.atsproceso_id = %s and ats.manual = False"""
                   
        querycompras =  """
                       insert into fiscal_ats_compras(invoice_id,create_uid,create_date,  
                  codsustento,tpidprov,idprov,tipocomprobante,fecharegistro,    
                  establecimiento,puntoemision,secuencial,fechaemision,autorizacion,  
                  basenograiva,baseimponible,baseimpgrav,montoice,montoiva,montoivacalc,  
                  valorretservicios,valorretbienes,valretserv100,estabretencion1,  
                  ptoemiretencion1,secretencion1 , autretencion1,fechaemiret1,docmodificado, tipodocmodificado_id,  
                  estabmodificado,ptoemimodificado,secmodificado, autmodificado,  
                  sustento_id,tipoidentificacion_id,tipocomprobante_id,atsproceso_id,partner_id, manual,
                  sritipopago_id , pais_id , dobletributacion , retenciondobletributacion)  
                  select fac.id, %s usuario, now() at time zone 'utc' fechacreacion, sust.codigofiscal sustentosri,  
                  tide.codigofiscalcompra tipoidentificacionsri, pro.vat ruc, 
                  
                  --doc.codigosri tipodocumentosri,
                  (select codigofiscal from fiscal_tipodocumento where id = COALESCE(fac.tipodocumento_id , doc.id)) as tipodocumentosri,
                   
                  fac.date_invoice fechafactura, fac.establecimientoprov establecimientofactura, 
                  fac.puntoemisionprov puntoemisionfactura, fac.secuencialprov secuencialfactura, 
                  fac.date_invoice fechacontabilizacion, fac.num_autfac autorizacionfactura,   
                  fac.baseninguniva baseninguniva, fac.baseivacero basecero, fac.baseivanocero basenocero,   
                  0 ice, amount_tax totaliva12, round((fac.baseivanocero*0.12),2),  
                  coalesce((select sum(abs(r.amount))    
                             from fiscal_retencion_ln as r    
                                         where r.invoice_id = fac.id    
                              and r.tipo = 'iva'    
                              and ROUND(abs(r.porcentaje),2)  = 0.70) 
                 ,0 )retencionivaservicios,  
                     coalesce((select sum(abs(r.amount))  
                                         from fiscal_retencion_ln as r  
                                        where r.invoice_id = fac.id  
                              and r.tipo = 'iva' 
                              and ROUND(abs(r.porcentaje),2) = 0.30) 
                 ,0 )retencionivabienes, 
                    coalesce((select sum(abs(r.amount))   
                                     from fiscal_retencion_ln as r   
                                    where r.invoice_id = fac.id   
                          and r.tipo = 'iva'    
                          and ROUND(abs(r.porcentaje),2) = 1.00)   
                  ,0 )retencioniva100, 
                        fac.establecimiento              establecimientoretencion, 
                        fac.puntoemision                 puntoemisionretencion, 
                        fac.secuencial                   secuencialretencion, 
                        "Numautorizacion"           numautorizacionretencion, 
                        fac.date_invoice         fecharetencion, 
                        '0'                 documentomodificado, 
                        null                tipodocmodificado_id, 
                        '000'                 estabmodificado, 
                        '000'                 ptoemisionmodificado, 
                        '0'                 secmodificado, 
                        '000'                 autmodificado, 
                         sust.id            sustento_id,  
                         pro.tipoid  tipoidentificacion_id, 
                         doc.id                tipocomprobante_id,  
                         %s                    atsproceso_id,  
                         pro.id                partner_id,  
                         False                 manual, 

                         fac.fiscaltipopago_id    tipopago_id,
                                                fac.pais_id        pais_id,
                                                coalesce(fac.dobletributacion,'NA') AS dobletributacion,
                                                coalesce(fac.retenciondobletributacion,'NA') as retenciondobletributacion
                                                 
                  from account_invoice                        fac, 
                      res_partner                         pro, 
                     fiscal_tipoidentificacion              tide, 
                     fiscal_tipodocumento         doc, 
                     fiscal_sustentotributario    sust, 
                     account_journal           jor 
                  where     pro.id  = fac.partner_id 
                      and tide.id = pro.tipoid 
                      and sust.id = fac.sustentotributario_id 
                      and jor.id = fac.journal_id 
                      and doc.id = jor.tipodocumentosri_id 
                      and fac.state in ('open','paid') 
                      and fac.type = 'in_invoice' 
                      and extract(year from fac.date_invoice) = %s
                      and extract(month from fac.date_invoice) = %s
                      and jor.tipodocumentosri_id is not null 
                        """

        querydetalleair =   """ insert into fiscal_ats_detalleair_cp( create_uid, create_date, ats_compra_id, codretair,
                                                             baseimpair, porcentajeair, valretair)
                             select  %s create_uid, now() at time zone 'utc' create_date, ats.id ats_compra_id,
                                     ret.codigo codretair, ret.base_amount baseimpair,
                                     (abs(ret.porcentaje)*100)::integer porcentajeair, abs(ret.amount) valorretair
                             from fiscal_retencion_ln ret
                             inner join fiscal_ats_compras ats on (ats.invoice_id = ret.invoice_id)
                             where ret.tipo='fte'
                                   and extract(year from ats.fecharegistro) = %s
                                   and extract(month from ats.fecharegistro) = %s 
                                   and ats.atsproceso_id = %s """
        
        
        queryformapago= """ 
                        insert into fiscal_ats_comprasfpagos( create_uid, create_date, fpagos_id , formapago_id)
                        select %s create_uid, now() at time zone 'utc' create_date , ats.id ats_compra_id , invp.formapago_id 
                        from fiscal_invoice_fpagos invp 
                        inner join fiscal_ats_compras ats on (ats.invoice_id = invp.invoice_ids)
                        where extract(year from ats.fecharegistro) = %s
                                   and extract(month from ats.fecharegistro) = %s
                                   and ats.atsproceso_id = %s       """
        cr.execute(delete_detalleair,(ident,))
        cr.execute(borro_atscompra,(ident,))
        cr.execute(querycompras,(uid,ident,anio,mes))
        cr.execute(querydetalleair,(uid,anio,mes,ident,))
        cr.execute(queryformapago,(uid,anio,mes,ident,))
        
        self._procesa_reembolsos(cr, uid, ident, anio, mes)
        self._proceso_duplicado(cr, uid, ident, anio, mes)
        
        
        
    def _proceso_duplicado(self,cr,uid,id,anio,mes,):
        
        cr.execute(""" select distinct(ats_compra_id) as id from fiscal_ats_detalleair_cp """)
        res = cr.dictfetchall()
        for i in res:
            cr.execute(""" SELECT codretair , ats_compra_id,sum(baseimpair) AS baseimpair,porcentajeair,valretair 
                            from fiscal_ats_detalleair_cp where ats_compra_id =  %s
                            group by codretair,ats_compra_id,porcentajeair,valretair """,(i['id'],))
            dt = cr.dictfetchall()
            for l in dt:
                cr.execute(""" INSERT INTO fiscal_ats_detalleair 
                            ( create_uid,codretair,ats_compra_id,baseimpair,porcentajeair,valretair) 
                            VALUES (%s,%s,%s,%s,%s,%s)"""
                            ,(1,l['codretair'],l['ats_compra_id'],l['baseimpair'],l['porcentajeair'],l['valretair']))
                cr.commit()
        cr.execute(""" delete from fiscal_ats_detalleair_cp """)
        return True
        
    def _procesa_reembolsos(self,cr,uid,ident,anio,mes,):
        
        queryreembolsos = """ select * from fiscal_ats_compras where 
                                atsproceso_id in 
                                            (select id from fiscal_ats_proceso 
                                            where anio = %s and mes = %s )  """
        
        cr.execute(queryreembolsos,(anio,mes))
        res = cr.dictfetchall()
        for i in res:
            ai = self.pool.get('account.invoice').browse(cr, uid, i['invoice_id'])
            if len(ai.reembolsos_id) > 0:
                sql = "SELECT id FROM facturas_reembolsos where invoice_id = %s"
                cr.execute(sql,(ai.id,))
                res = cr.dictfetchall()
                for r in res:
                    queryreembolsos_ins = """ INSERT INTO fiscal_ats_reembolsos(
                                    create_uid, create_date, write_date, write_uid, tarifa_no_iva_re,reembolsos_ids,
                                    tipodocumento_id_re, ivacero_re, establecimiento_re, puntoemision_re, monto_ice_re,
                                    secuencial_re, identificacion_pro_re, tipoid_re, autorizacion_re,fecha_emision_re,monto_exe_reembolso, iva_dif_cero_re, 
                                    monto_iva_re)
                                    SELECT create_uid, create_date, write_date, write_uid, tarifa_no_iva, %s ,
                                    tipodocumento_id,ivacero, establecimiento,   puntoemision,monto_ice ,lpad(secuencial,9,'0') as secuencial,
                                    identificacion_pro, tipoid,autorizacion,  fecha_emision,monto_exe_reembolso, iva_dif_cero,
                                    monto_iva
                                    FROM facturas_reembolsos where id = %s """  
                    cr.execute(queryreembolsos_ins,(i['id'],r['id']) )
                
                
    def _procesa_ventas (self, cr, uid, ident,anio,mes):
       
        cr.execute("delete from fiscal_ats_ventas where atsproceso_id = %s and manual = False", (ident,) )
        cr.execute(""" 
                CREATE OR REPLACE VIEW fiscal_resumenventas AS 
                    SELECT to_char(fac.date_invoice::timestamp with time zone, 'yyyy'::text) AS anio,
                    to_char(fac.date_invoice::timestamp with time zone, 'mm'::text) AS mes, 
                    tide.codigofiscalventa AS tipoidentificacionsri, cli.vat AS numeroidentificacion, 
                    --tdoc.codigosri AS tipodocumentosri,
                    (select codigofiscal from fiscal_tipodocumento where id = COALESCE(fac.tipodocumento_id , tdoc.id)) as tipodocumentosri,
                    /*CASE WHEN fac.type = 'out_refund' THEN COALESCE(fac.baseninguniva, 0::numeric) * -1 
                         ELSE COALESCE(fac.baseninguniva, 0::numeric) 
                         END AS baseninguniva,
                    CASE WHEN fac.type = 'out_refund' THEN COALESCE(fac.baseivacero, 0::numeric) * -1 
                         ELSE COALESCE(fac.baseivacero, 0::numeric) END AS basecero,
                    CASE WHEN fac.type = 'out_refund' THEN COALESCE(fac.baseivanocero, 0::numeric) * -1 
                         ELSE COALESCE(fac.baseivanocero, 0::numeric) END AS basenocero,
                     CASE WHEN fac.type = 'out_refund' THEN COALESCE(fac.amount_tax, 0::numeric) * -1 
                         ELSE COALESCE(fac.amount_tax, 0::numeric) END AS montoiva,*/
                    COALESCE(fac.baseninguniva, 0::numeric) AS baseninguniva,      
                    COALESCE(fac.baseivacero, 0::numeric) AS basecero, 
                    COALESCE(fac.baseivanocero, 0::numeric) AS basenocero, 
                    COALESCE(fac.amount_tax, 0::numeric) AS montoiva, 
                    (select 
                    amount
                    from account_voucher_line where voucher_id in (
                    select 
                    ( select v.id 
                    from account_voucher v, account_journal j 
                    where v.state='posted' and v.journal_id = j.id and v.id = voucher_id and j.categoria_reporte='rti' )
                    from account_voucher_line where move_line_id in (
                    select id from account_move_line where ref in(
                    select number from account_invoice where id = fac.id)) ) 
                    and numerofac in (select numerofac from account_invoice where id = fac.id) ) AS montoivaretenido,
                    (select 
                    amount
                    from account_voucher_line where voucher_id in (
                    select 
                    ( select v.id 
                    from account_voucher v, account_journal j 
                    where v.state='posted' and v.journal_id = j.id and v.id = voucher_id and j.categoria_reporte='rtf' )
                    from account_voucher_line where move_line_id in (
                    select id from account_move_line where ref in(
                    select number from account_invoice where id = fac.id)) ) 
                    and numerofac in (select numerofac from account_invoice where id = fac.id) ) AS montorentaretenido,
                    tide.id AS tipoidentificacion_id, cli.id AS partner_id, 
                    COALESCE(fac.tipodocumento_id , tdoc.id) AS tipodocumento_id, false AS manual
                     , fac.establecimiento
                     , fac.parte_relacionada
                    FROM account_invoice fac,
                     fiscal_tipodocumento tdoc,
                     res_partner cli,
                     fiscal_tipoidentificacion tide,
                      fiscal_puntoemision pemi
                    WHERE 
                    (fac.state::text = ANY (ARRAY['open'::character varying::text, 'paid'::character varying::text])) 
                    AND fac.type in ('out_invoice','out_refund')
                    AND cli.company_id = fac.company_id 
                    AND cli.id = fac.partner_id 
                    AND tide.id = cli.tipoid 
                    AND pemi.id = fac.puntoemision_id 
                    AND pemi.tipodocumento_id = tdoc.id
                    ORDER BY to_char(fac.date_invoice::timestamp with time zone, 'mm'::text),
                     tide.sigla, to_char(fac.date_invoice::timestamp with time zone, 'yyyy'::text), tdoc.codigofiscal;
                    """)
        
        cr.execute("""
                insert  into fiscal_ats_ventas (
                     tipoidentificacionsri ,  
                     numeroidentificacion,  
                     tipodocumentosri, 
                     baseninguniva, 
                     basecero, 
                     basenocero, 
                     montoiva, 
                     montoivacalc, 
                     montoivaretenido, 
                     montorentaretenido, 
                     tipoidentificacion_id, 
                     partner_id, 
                     tipodocumento_id, 
                     manual, 
                     numerocomprobantes, 
                     atsproceso_id ,
                     establecimiento,
                     parte_relacionada) 
            SELECT 
                 tipoidentificacionsri,  
                 numeroidentificacion,  
                 tipodocumentosri,  
                 sum(baseninguniva),  
                 sum(basecero),  
                 sum(basenocero),  
                 sum(montoiva),  
                 round(sum(basenocero)*0.12,2),  
                 COALESCE(round(sum(montoivaretenido),2),'0.00') AS montoivaretenido, 
                 COALESCE(round(sum(montorentaretenido),2),'0.00') AS montorentaretenido, 
                 tipoidentificacion_id,  
                 partner_id,  
                 tipodocumento_id,
                 manual, 
                 count(*),
                 %s,
                 establecimiento ,
                 parte_relacionada
               FROM fiscal_resumenventas 
               where anio = %s and mes = %s
         group by anio,  
                 mes, 
                 tipoidentificacionsri, 
                 numeroidentificacion, 
                 tipodocumentosri,  
                 tipoidentificacion_id,  
                 partner_id,  
                 tipodocumento_id,  
                 manual,
                 establecimiento ,
                 parte_relacionada
                 ORDER BY establecimiento """, (ident,anio, mes))  
        
    def _procesa_ventasptoemision (self, cr, uid, ident,anio,mes):
        
        cr.execute("delete from  fiscal_ats_ventaptoemision where atsproceso_id = %s and manual = False", (ident,) )
        
        cr.execute(""" insert into fiscal_ats_ventaptoemision ( total, establecimiento , manual , atsproceso_id )
                        select SUM( CASE WHEN tipodocumentosri = '04' THEN (baseninguniva * -1)
                                 ELSE baseninguniva 
                                END ) 
                                +
                               SUM( CASE WHEN tipodocumentosri = '04' THEN (basecero * -1)
                                 ELSE basecero 
                                END ) 
                                +
                               SUM( CASE WHEN tipodocumentosri = '04' THEN (basenocero * -1)
                                ELSE basenocero 
                                END ) AS total,
                            establecimiento ,
                            False ,
                            %s  
                        FROM fiscal_ats_ventas
                        where 
                        establecimiento  in (select distinct establecimiento from fiscal_resumenventas) 
                        and atsproceso_id = %s
                        and tipodocumentosri != '41'
                        GROUP BY establecimiento
                        """,(ident,ident))
        return True
   
        
    def _procesa_anulados (self, cr, uid, ident,anio, mes):
        
        lastday = monthrange(int(anio), int(mes))[1]
        desde = anio+'-'+mes+'-'+'01'
        hasta = anio+'-'+mes+'-'+str(lastday)

        query = """ select tip.codigofiscal as tipocomprobante, fac.establecimiento, fac.puntoemision, 
                 fac.secuencial as secuencialinicio, fac.secuencial as secuencialfin, 
                 "Numautorizacion" as autorizacion, fac.puntoemision_id, 
                 tip.id as tipodocumento_id, %s as atsproceso_id, False as manual 
                 from account_invoice as fac 
                 inner join account_journal as jou on jou.id = fac.journal_id 
                 inner join fiscal_tipodocumento as tip on tip.id = jou.tipodocumento_id 
                 where fac.type='out_invoice' 
                 and fac.state='cancel' 
                 and fac.date_invoice between %s and %s 
                 order by fac.puntoemision, fac.establecimiento, fac.secuencial"""
        
        cr.execute(query,(ident,desde,hasta))
        anulados = cr.dictfetchall()
        
        anterior=None
        lista=[]
        for a in anulados:
            if(anterior==None):
                anterior = a
            else:               
                inicio = int(a['establecimiento']+a['puntoemision']+a['secuencialinicio'])
                siguiente = int(anterior['establecimiento']+anterior['puntoemision']+anterior['secuencialfin'])+1
                            
                if(siguiente == inicio):
                    anterior['secuencialfin'] = a['secuencialfin']
                else:
                    lista.append(anterior)
                    anterior = a
        if anterior:
            lista.append(anterior)
        
        anulados_obj = self.pool.get('fiscal.comprobantesanulados')
        cr.execute("delete from fiscal_comprobantesanulados where atsproceso_id = %s and manual=False",(ident,))
        for a in lista:            
            anulados_obj.create(cr,uid,a)        
        
    def toxml(self,cr,uid,ident,context=None):
        atscompras_obj = self.pool.get('fiscal.ats_compras')
        atsventas_obj = self.pool.get('fiscal.ats_ventas')
        comprobantesanulados_obj = self.pool.get('fiscal.comprobantesanulados')
        ventasptoemision_obj = self.pool.get('fiscal.ats_ventaptoemision')
        usuario = self.pool.get('res.users').browse(cr,uid,uid)
        atsproceso_obj = self.pool.get('fiscal.ats_proceso')
        atsproceso = atsproceso_obj.browse(cr, uid, ident)[0]


        doc = minidom.Document()
        iva = doc.createElement('iva')
        doc.appendChild(iva)
        
        node = doc.createElement('TipoIDInformante')
        iva.appendChild(node)
        txt = doc.createTextNode(str('R'))
        node.appendChild(txt)
        
        if not usuario.company_id.partner_id.vat:
            raise osv.except_osv('Error de Configuración!','Falta ingresar número de identificación de la compañia')
        else:
            node = doc.createElement('IdInformante')
            iva.appendChild(node)
            txt = doc.createTextNode(usuario.company_id.partner_id.vat)
            node.appendChild(txt)
        
        node = doc.createElement('razonSocial')
        iva.appendChild(node)
        txt = doc.createTextNode(usuario.company_id.partner_id.name)
        node.appendChild(txt)
        
        node = doc.createElement('Anio')
        iva.appendChild(node)
        txt = doc.createTextNode(atsproceso.anio_id.name)
        node.appendChild(txt)
        
        node = doc.createElement('Mes')
        iva.appendChild(node)
        txt = doc.createTextNode(atsproceso.mes)
        node.appendChild(txt)

        #CAMBIOS
        if not atsproceso.emision:
            establecimiento = '001'
            total_ventas = 0.00
        else:
            establecimiento = atsproceso.emision[0].establecimiento
            total_ventas = float(atsproceso.emision[0].total)
        
        node = doc.createElement('numEstabRuc')
        iva.appendChild(node)
        txt = doc.createTextNode(str(establecimiento))
        node.appendChild(txt)
        #CAMBIOS
        
        node = doc.createElement('totalVentas')
        iva.appendChild(node)
        txt = doc.createTextNode(str("%.2f" % total_ventas))
        node.appendChild(txt)
        
        node = doc.createElement('codigoOperativo')
        iva.appendChild(node)
        txt = doc.createTextNode(str('IVA'))
        node.appendChild(txt)
        
        if atsproceso.compras:
            compras = atscompras_obj.toxml(atsproceso.compras)
            if compras:
                iva.appendChild(compras)
        
        if atsproceso.ventas:
            ventas = atsventas_obj.toxml(atsproceso.ventas)
            if ventas:
                iva.appendChild(ventas)
        
        if atsproceso.emision:
            emision = ventasptoemision_obj.toxml(atsproceso.emision)
            if emision:
                iva.appendChild(emision)
        
        if atsproceso.anulados:
            anulados = comprobantesanulados_obj.toxml(atsproceso.anulados)
            if anulados:
                iva.appendChild(anulados)
        
        return doc.toprettyxml(encoding='UTF-8')
    
fiscal_ats_proceso()


class fiscal_ats_compras(osv.osv):
    
    def calcularnumero(self, cr, uid, ids, name, args, context={}):       
        res = {}
        
        for atscompra in self.browse(cr, uid, ids, context=context):
            res[atscompra.id] = {
                'numerofac': '',
                'numeroret': '',
                'numeromod': '',
            }
            
            numerofac = atscompra.establecimiento+'-'+atscompra.puntoemision    +'-'+atscompra.secuencial
            numeroret = atscompra.estabretencion1+'-'+atscompra.ptoemiretencion1+'-'+atscompra.secretencion1
            numeromod = atscompra.estabmodificado+'-'+atscompra.ptoemimodificado+'-'+atscompra.secmodificado
            
            res[atscompra.id]['numerofac'] = numerofac
            res[atscompra.id]['numeroret'] = numeroret
            res[atscompra.id]['numeromod'] = numeromod

        return res
    
    
    _name = 'fiscal.ats_compras'
    
    _columns = {
            'invoice_id' : fields.many2one('account.invoice','Factura'),
            'codsustento' : fields.char('Sustento', size=5, required=True),
            'tpidprov' : fields.char('Tipo Identificación', size=5, required=True),
            'idprov' : fields.char('No. Identificación',size=13, required=True),
            'tipocomprobante' : fields.char('Tipo Comprobante',size=4, required=True),
            'fecharegistro':fields.date('Fecha Registro', required=True),
            'establecimiento' : fields.char('Establecimiento',size=4, required=True),
            'puntoemision' : fields.char('Punto de Emision',size=4, required=True),
            'secuencial' : fields.char('Secuencial',size=20, required=True),
            'fechaemision':fields.date('Fecha Emision',required=True),
            'autorizacion': fields.char('Numero de Autorizacion',size=100, required=True),
            'basenograiva' : fields.float    ('Base no objeto de IVA', digits=(8,2),required=True),
            'baseimponible' : fields.float('Base IVA 0%', digits=(8,2),required=True),
            'baseimpgrav' : fields.float('Base IVA dif. 0%', digits=(8,2),required=True),
            'montoice' : fields.float('Monto ICE', digits=(8,2),required=True),
            'montoiva' : fields.float('Monto IVA', digits=(8,2), required=True),
            'valorretbienes' : fields.float('Monto IVA Bienes', digits=(8,2), required=True),
            'valorretservicios' : fields.float('Monto IVA Servicios', digits=(8,2), required=True),
            'valretserv100' : fields.float('Ret. IVA 100 %', digits=(8,2), required=True),
            'detalle_air' : fields.one2many('fiscal.ats_detalleair','ats_compra_id','Detalle AIR'),
            'estabretencion1' : fields.char('Establecimiento Retencion',size=20, required=True),
            'ptoemiretencion1' : fields.char('Punto Emision de Retencion',size=20, required=True),
            'secretencion1' : fields.char('Secuencial Retencion',size=20,required=True),
            'autretencion1' : fields.char('Numero Autoriza Retencion',size=37, required=True),
            'fechaemiret1':fields.date('Fecha Emision Retencion',required=True),
            'docmodificado' : fields.char('Tipo Comprobante Modificado',size=20,required=True),
            'estabmodificado' : fields.char('Establecimiento Modificado',size=20,required=True),
            'ptoemimodificado' : fields.char('Punto emision Modificado',size=20,required=True),
            'secmodificado' : fields.char('Secuencial Modificado',size=20,required=True),
            'autmodificado' : fields.char('Autorizacion Modificado',size=20, required=True),
            'montoivacalc' : fields.float('Monto IVA', digits=(8,2), required=True),
            'sustento_id' : fields.many2one('fiscal.sustentotributario','Sustento Tributario',required=True),
            'tipoidentificacion_id' : fields.many2one('fiscal.tipoidentificacion','Tipo Identificacion',required=True),
            'tipocomprobante_id' : fields.many2one('fiscal.tipodocumento','Tipo Comprobante',required=True),
            'tipodocmodificado_id': fields.many2one('fiscal.tipodocumento','Documento Modificado'),
            'partner_id' : fields.many2one('res.partner','Proveedor',required=True),
            'atsproceso_id': fields.many2one('fiscal.ats_proceso','ATS Proceso',required=False,ondelete='cascade'),
            'siglatipoidentificacion': fields.related('tipoidentificacion_id','sigla', size=5, type='char', string='Sigla', store=False),
            'numerofac' : fields.function(calcularnumero,string='Comp. Venta',type='char',size=20,store=False,multi='all'),
            'numeroret' : fields.function(calcularnumero,string='Comp. Retencion',type='char',size=20,store=False,multi='all'),
            'numeromod' : fields.function(calcularnumero,string='Comp. Modificado',type='char',size=20,store=False,multi='all'),
            'manual' : fields.boolean('Manual', required=True),   
            'sri_ats_pagos_line':fields.one2many('fiscal.ats.comprasfpagos','fpagos_id','Pagos'),
            'sritipopago_id':fields.many2one('fiscal.tipopago','Tipo de Pago'),
            'pais_id':fields.many2one('res.country','Pais'),
            'dobletributacion': fields.selection([('SI','SI'),('NO','NO'),('NA','NA'),],select=True,string="Doble Tributacion"),
            'retenciondobletributacion': fields.selection([('SI','SI'),('NO','NO'),('NA','NA'),],select=True,string="Retencion Tributaria"),
            'bandera':fields.boolean('Bandera'),
            'reembolsos_id': fields.one2many('fiscal.ats.reembolsos','reembolsos_ids','Comprobante de Reembolso'),
      
        }
    
    _order = 'fechaemision'

    _defaults = {    
            
            'docmodificado' : '0',
            'estabmodificado' : '000',
            'ptoemimodificado' : '000',
            'secmodificado' : '0',
            'autmodificado' : '000',
            'manual': True,
            'tipodocmodificado_id': False,
        }
    
    
    def _formas_pago_ats(self,cr,uid,ids,context=None):
        identi_brw = self.browse(cr,uid,ids,context)
        for t in identi_brw:
            if t.sritipopago_id:
                total= t.basenograiva + t.baseimponible + t.baseimpgrav + t.montoice + t.montoiva
                if t.sri_ats_pagos_line and total < 1000 :
                    raise osv.except_osv('Error!','No Puede Defirnir Formas de pago a Facturas Menores a 1000 Dolares')
                    return True
                if total >= 1000 and not t.sri_ats_pagos_line:
                    raise osv.except_osv('Error!','Defina Formas de Pago a su Factura')
                    return True

            return True
        
    _constraints=[
                 (_formas_pago_ats,('Error en Formas de Pago'),['sritipopago_id'] )
                 ]
    
        
    def onchange_tipopago_id(self,cr,uid,ids,tipopago=False,context=None):
        result2={}
        if tipopago:
            cliente = self.pool.get('fiscal.tipopago').browse(cr,uid,tipopago)
            if cliente.identificador == '01':
                    result2['value']={
                                   'bandera': False  ,
                                   'pais_id':False,
                                   'dobletributacion':'NA',
                                   'retenciondobletributacion':'NA', }  
            if cliente.identificador == '02':
                    result2['value']={
                                   'bandera': True  ,
                                   'dobletributacion':'NO',
                                   'retenciondobletributacion':'NO',  }  
        return result2

    
    
    def onchange_trubutacion_id(self,cr,uid,ids,dobletributacion=False,context=None):
        result2={}
        if dobletributacion == 'SI':
            result2['value']={
                           'retenciondobletributacion': None , }
        else:
            result2['value']={
                           'retenciondobletributacion': 'NO' , }  
        return result2
    
    
    def onchange_sustento_id(self, cr, uid, ids, sustento_id):
        result = {}
        if sustento_id:
            p = self.pool.get('fiscal.sustentotributario').browse(cr, uid, sustento_id)
            result['value']= {
                        'codsustento' : p.codigosri,
                     }
        return result
    
        
    
    def onchange_tipocomprobante_id(self, cr, uid, ids, tipocomprobante_id):
        result = {}
        if tipocomprobante_id:
            p = self.pool.get('fiscal.tipodocumento').browse(cr, uid, tipocomprobante_id)
            
            result['value']= {
                        'tipocomprobante' : p.codigosri,
                     }

        return result
    
    def onchange_tipoidentificacion_id(self, cr, uid, ids, tipoidentificacion_id):
        result = {}
        if tipoidentificacion_id:
            p = self.pool.get('fiscal.tipoidentificacion').browse(cr, uid, tipoidentificacion_id)
            
            result['value']= {
                        'tpidprov' : p.codigosricompra,
                     }

        return result
    
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        result = {}
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
            result['value']= {
                        'idprov' : p.vat,
                        'tipoidentificacion_id': p.tipoid.id,
                        'tpidprov' : p.tipoid.codigosricompra,
                     }

        return result
    
    def onchange_tipodocmodificado_id(self, cr, uid, ids, tipodocmodificado_id):
        result = {}
        if tipodocmodificado_id:
            p = self.pool.get('fiscal.tipodocumento').browse(cr, uid, tipodocmodificado_id)
            
            result['value']= {
                        'docmodificado' : p.codigosri,
                        'estabmodificado' : '',
                        'ptoemimodificado' : '',
                        'secmodificado' : '',
                        'autmodificado' : '',
                     }
        else:
            result['value']= {
                        'docmodificado' : '0',
                        'estabmodificado' : '000',
                        'ptoemimodificado' : '000',
                        'secmodificado' : '0',
                        'autmodificado' : '000',
                     }

        return result
    
    def toxml(self,listacompras):        
        doc = minidom.Document()
        compras = doc.createElement('compras')
        doc.appendChild(compras)
        for compra in listacompras:
            detalle = doc.createElement('detalleCompras')
            compras.appendChild(detalle)
            
            node = doc.createElement('codSustento')
            detalle.appendChild(node)
            #txt = doc.createTextNode(compra.codsustento)
            txt = doc.createTextNode(compra.sustento_id.codigofiscal or compra.codsustento )
            node.appendChild(txt)
            
            node = doc.createElement('tpIdProv')
            detalle.appendChild(node)
            txt = doc.createTextNode(compra.tpidprov)
            node.appendChild(txt)
            
            node = doc.createElement('idProv')
            detalle.appendChild(node)
            txt = doc.createTextNode(compra.idprov)
            node.appendChild(txt)
            
            node = doc.createElement('tipoComprobante')
            detalle.appendChild(node)
            #txt = doc.createTextNode(compra.tipocomprobante)
            txt = doc.createTextNode(compra.tipocomprobante_id.codigofiscal)
            node.appendChild(txt)
            
            fecha=datetime.datetime.strptime(compra.fecharegistro, '%Y-%m-%d').date()
            fechas=fecha.strftime('%d/%m/%Y')
            node = doc.createElement('fechaRegistro')
            detalle.appendChild(node)
            txt = doc.createTextNode(fechas)
            node.appendChild(txt)
            
            node = doc.createElement('establecimiento')
            detalle.appendChild(node)
            txt = doc.createTextNode(compra.establecimiento)
            node.appendChild(txt)
            
            node = doc.createElement('puntoEmision')
            detalle.appendChild(node)
            txt = doc.createTextNode(compra.puntoemision)
            node.appendChild(txt)
            
            node = doc.createElement('secuencial')
            detalle.appendChild(node)
            txt = doc.createTextNode(compra.secuencial)
            node.appendChild(txt)
            
            fecha=datetime.datetime.strptime(compra.fechaemision, '%Y-%m-%d').date()
            fechas=fecha.strftime('%d/%m/%Y')
            node = doc.createElement('fechaEmision')
            detalle.appendChild(node)
            txt = doc.createTextNode(fechas)
            node.appendChild(txt)
            
            node = doc.createElement('autorizacion')
            detalle.appendChild(node)
            txt = doc.createTextNode(compra.autorizacion)
            node.appendChild(txt)
            
            node = doc.createElement('baseNoGraIva')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % compra.basenograiva)
            node.appendChild(txt)
            
            node = doc.createElement('baseImponible')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % compra.baseimponible)
            node.appendChild(txt)
            
            node = doc.createElement('baseImpGrav')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % compra.baseimpgrav)
            node.appendChild(txt)
            
            #CAMBIOS
            node = doc.createElement('baseImpExe')
            detalle.appendChild(node)
            txt = doc.createTextNode("0.00")
            node.appendChild(txt)
            #CAMBIOS
            
            node = doc.createElement('montoIce')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % compra.montoice)
            node.appendChild(txt)
            
            node = doc.createElement('montoIva')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % compra.montoivacalc)
            node.appendChild(txt)
            
            #CAMBIOS
            node = doc.createElement('valRetBien10')
            detalle.appendChild(node)
            txt = doc.createTextNode("0.00")
            node.appendChild(txt)
            
            node = doc.createElement('valRetServ20')
            detalle.appendChild(node)
            txt = doc.createTextNode("0.00")
            node.appendChild(txt)
            #CAMBIOS
            
            
            node = doc.createElement('valorRetBienes')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % compra.valorretbienes)
            node.appendChild(txt)
            
            
            node = doc.createElement('valorRetServicios')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % compra.valorretservicios)
            node.appendChild(txt)
            
            node = doc.createElement('valRetServ100')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % compra.valretserv100)
            node.appendChild(txt)
            
            #CAMBIOS
            a1=0.0
            if len(compra.reembolsos_id) > 0:
                for linea in compra.reembolsos_id:
                    
                    a1+=float(linea.ivacero_re)
                    a1+=float(linea.iva_dif_cero_re)
                    a1+=float(linea.tarifa_no_iva_re)
                    a1+=float(linea.monto_exe_reembolso)
                    
            #CAMBIOS 
            node = doc.createElement('totbasesImpReemb')
            detalle.appendChild(node)
            txt = doc.createTextNode( str(format(a1, '.2f')) )
            node.appendChild(txt)
            
            #node = doc.createElement('totbasesImpReemb')
            #detalle.appendChild(node)
            #txt = doc.createTextNode("0.00")
            #node.appendChild(txt)
            #CAMBIOS
            
            #DESDE AKI SRI-PAGOS
            
            nodepago = doc.createElement('pagoExterior')
            detalle.appendChild(nodepago)
            
            if not compra.sritipopago_id.identificador : 
                node = doc.createElement('pagoLocExt')
                nodepago.appendChild(node)
                txt = doc.createTextNode(str('NA'))
                node.appendChild(txt)
            else:
                node = doc.createElement('pagoLocExt')
                nodepago.appendChild(node)
                txt = doc.createTextNode(str(compra.sritipopago_id.identificador))
                node.appendChild(txt)
            if not compra.pais_id.code:
                node = doc.createElement('paisEfecPago')
                nodepago.appendChild(node)
                txt = doc.createTextNode(str('NA'))
                node.appendChild(txt)
            else:
                node = doc.createElement('paisEfecPago')
                nodepago.appendChild(node)
                txt = doc.createTextNode(str(compra.pais_id.code))
                node.appendChild(txt)
            
            
            node = doc.createElement('aplicConvDobTrib')
            nodepago.appendChild(node)
            txt = doc.createTextNode(str(compra.dobletributacion))
            node.appendChild(txt)
            
        
            node = doc.createElement('pagExtSujRetNorLeg')
            nodepago.appendChild(node)
            txt = doc.createTextNode(str(compra.retenciondobletributacion))
            node.appendChild(txt)
            
            #CAMBIO
            node = doc.createElement('pagoRegFis')
            nodepago.appendChild(node)
            txt = doc.createTextNode( str("NA") )
            node.appendChild(txt)
            #CAMBIO    
            
            if compra.sri_ats_pagos_line:
                
                nodeformapago = doc.createElement('formasDePago')
                detalle.appendChild(nodeformapago)
                
                for linea in compra.sri_ats_pagos_line:
                        node = doc.createElement('formaPago')
                        nodeformapago.appendChild(node)
                        txt = doc.createTextNode(str(linea.formapago_id.codigosri))
                        node.appendChild(txt)
            
#            HASTA AKI SRI-PAGOS
            
            nodeair = doc.createElement('air')
            detalle.appendChild(nodeair)
            
            for linea in compra.detalle_air:
                detalleair = doc.createElement('detalleAir')
                nodeair.appendChild(detalleair)
                
                node = doc.createElement('codRetAir')
                detalleair.appendChild(node)
                txt = doc.createTextNode(linea.codretair)
                node.appendChild(txt)
                
                node = doc.createElement('baseImpAir')
                detalleair.appendChild(node)
                txt = doc.createTextNode("%.2f" % linea.baseimpair)
                node.appendChild(txt)
                
                #CAMBIOS
                node = doc.createElement('porcentajeAir')
                detalleair.appendChild(node)
                txt = doc.createTextNode("%.2f" % linea.porcentajeair)
                node.appendChild(txt)
                #CAMBIOS
                
                node = doc.createElement('valRetAir')
                detalleair.appendChild(node)
                txt = doc.createTextNode("%.2f" % linea.valretair)
                node.appendChild(txt)
            #a
            if compra.estabretencion1 ==  '000' and compra.ptoemiretencion1 == '000' and compra.secretencion1 == '0':
                pass
            else:
                node = doc.createElement('estabRetencion1')
                detalle.appendChild(node)
                txt = doc.createTextNode(compra.estabretencion1)
                node.appendChild(txt)
            
            
                node = doc.createElement('ptoEmiRetencion1')
                detalle.appendChild(node)
                txt = doc.createTextNode(compra.ptoemiretencion1)
                node.appendChild(txt)
            
            
                node = doc.createElement('secRetencion1')
                detalle.appendChild(node)
                txt = doc.createTextNode(compra.secretencion1)
                node.appendChild(txt)
            
            
                node = doc.createElement('autRetencion1')
                detalle.appendChild(node)
                txt = doc.createTextNode(compra.autretencion1)
                node.appendChild(txt)
                
                fecha=datetime.datetime.strptime(compra.fechaemiret1, '%Y-%m-%d').date()
                fechas=fecha.strftime('%d/%m/%Y')
                node = doc.createElement('fechaEmiRet1')
                detalle.appendChild(node)
                txt = doc.createTextNode(fechas)
                node.appendChild(txt)
            #a
            
            if compra.docmodificado == '04' or compra.docmodificado == '05': 
            
                node = doc.createElement('docModificado')
                detalle.appendChild(node)
                txt = doc.createTextNode(compra.docmodificado)
                node.appendChild(txt)
                
                node = doc.createElement('estabModificado')
                detalle.appendChild(node)
                txt = doc.createTextNode(compra.estabmodificado)
                node.appendChild(txt)
                
                node = doc.createElement('ptoEmiModificado')
                detalle.appendChild(node)
                txt = doc.createTextNode(compra.ptoemimodificado)
                node.appendChild(txt)
                
                node = doc.createElement('secModificado')
                detalle.appendChild(node)
                txt = doc.createTextNode(compra.secmodificado)
                node.appendChild(txt)
                
                node = doc.createElement('autModificado')
                detalle.appendChild(node)
                txt = doc.createTextNode(compra.autmodificado)
                node.appendChild(txt)
            
            #---------------------------------------
            
            if len(compra.reembolsos_id) > 0:
                
                reembolsos = doc.createElement('reembolsos')
                detalle.appendChild(reembolsos)
                
                for linea in compra.reembolsos_id:
                    
                    reembolso = doc.createElement('reembolso')
                    reembolsos.appendChild(reembolso)
                    
                    node = doc.createElement('tipoComprobanteReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(linea.tipodocumento_id_re.codigofiscal))
                    node.appendChild(txt)
                    
                    node = doc.createElement('tpIdProvReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(linea.tipoid_re.codigofiscalcompra))
                    node.appendChild(txt)
                    
                    node = doc.createElement('idProvReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(linea.identificacion_pro_re))
                    node.appendChild(txt)
                    
                    node = doc.createElement('establecimientoReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(linea.establecimiento_re))
                    node.appendChild(txt)
                    
                    node = doc.createElement('puntoEmisionReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(linea.puntoemision_re))
                    node.appendChild(txt)
                    
                    node = doc.createElement('secuencialReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(linea.secuencial_re))
                    node.appendChild(txt)
                    
                    fecha=datetime.datetime.strptime(linea.fecha_emision_re, '%Y-%m-%d').date()
                    fechas=fecha.strftime('%d/%m/%Y')
                    node = doc.createElement('fechaEmisionReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode( fechas )
                    node.appendChild(txt)
                    
                    node = doc.createElement('autorizacionReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(linea.autorizacion_re))
                    node.appendChild(txt)
                    
                    
                    node = doc.createElement('baseImponibleReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode( str(format(linea.ivacero_re, '.2f')) )
                    node.appendChild(txt)
                    
                    node = doc.createElement('baseImpGravReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(format(linea.iva_dif_cero_re,'.2f')))
                    node.appendChild(txt)
                    
                    node = doc.createElement('baseNoGraIvaReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(format(linea.tarifa_no_iva_re,'.2f')))
                    node.appendChild(txt)
                    
                    node = doc.createElement('baseImpExeReemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(format(linea.monto_exe_reembolso,'.2f')))
                    node.appendChild(txt)
                    
                    
                    node = doc.createElement('montoIceRemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(format(linea.monto_ice_re,'.2f')))
                    node.appendChild(txt)
                    
                    node = doc.createElement('montoIvaRemb')
                    reembolso.appendChild(node)
                    txt = doc.createTextNode(str(format(linea.monto_iva_re,'.2f')))
                    node.appendChild(txt)
                
                #---------------------------------------
        

            
        return compras     
    
fiscal_ats_compras()

class fiscal_ats_comprasfpagos(osv.osv):
    _name='fiscal.ats.comprasfpagos'
    _columns={
              
              'fpagos_id':fields.many2one('fiscal.ats_compras',required=False,ondelete='cascade'),
              'formapago_id':fields.many2one('fiscal.formapago','Formas de pago'),
              
              }
    
fiscal_ats_comprasfpagos()

class fiscal_ats_reembolsos(osv.osv):
    
    _name = 'fiscal.ats.reembolsos'
    
    _columns={
        
        'reembolsos_ids': fields.many2one('fiscal.ats_compras','Comprobante de Reembolso',required=False,ondelete='cascade'),
        'tipoid_re': fields.many2one('fiscal.tipoidentificacion','Tipo Identificación'),
        'identificacion_pro_re':fields.char('Identificación Proveedor',size=20),
        'tipodocumento_id_re': fields.many2one( 'fiscal.tipodocumento','Tipo de Comprobante'),
        'establecimiento_re':fields.char('Establecimiento',size=3),
        'puntoemision_re':fields.char('Punto de Emisión',size=3),
        'secuencial_re':fields.char('Secuencial',size=9),
        'autorizacion_re':fields.char('No Autorización'),
        'fecha_emision_re':fields.date('Fecha de Autorización'),
        'ivacero_re':fields.float('Tarifa IVA 0%'),
        'iva_dif_cero_re':fields.float('Tarifa IVA diferente 0%'),
        'tarifa_no_iva_re':fields.float('Tarifa No Objeto de IVA'),
        'monto_exe_reembolso':fields.float('Monto exede reembolso'),
        'monto_ice_re':fields.float('Monto de ICE'),
        'monto_iva_re':fields.float('Monto IVA'),
        
    }

fiscal_ats_reembolsos()


import openerp.addons.decimal_precision as dp

class fiscal_ats_detalleair(osv.osv):
    _name = 'fiscal.ats_detalleair'
    
    _columns = {
            'codretair' : fields.char('Codigo de Retencion',size=64),
            'baseimpair' : fields.float('Base Imponible', digits_compute=dp.get_precision('Account')),
            'porcentajeair' : fields.integer('Porcentaje'),
            'valretair' : fields.float('Valor', digits_compute=dp.get_precision('Account')),            
            
            'ats_compra_id' : fields.many2one('fiscal.ats_compras','ATS Compra',ondelete='cascade'),            
        }

fiscal_ats_detalleair()

class fiscal_ats_detalleair_cp(osv.osv):
    _name = 'fiscal.ats_detalleair_cp'
    
    _columns = {
            'codretair' : fields.char('Codigo de Retencion',size=64),
            'baseimpair' : fields.float('Base Imponible', digits_compute=dp.get_precision('Account')),
            'porcentajeair' : fields.integer('Porcentaje'),
            'valretair' : fields.float('Valor', digits_compute=dp.get_precision('Account')),            
            
            'ats_compra_id' : fields.many2one('fiscal.ats_compras','ATS Compra',ondelete='cascade'),            
        }

fiscal_ats_detalleair_cp()


from openerp.osv import osv, fields
from xml.dom import minidom

class fiscal_ats_ventas(osv.osv):
    _name = 'fiscal.ats_ventas'

    def toxml(self, listaventas):        
        doc = minidom.Document()
        ventas = doc.createElement('ventas')
        doc.appendChild(ventas)
        for v in listaventas:
            detalle = doc.createElement('detalleVentas')
            ventas.appendChild(detalle)
            
            node = doc.createElement('tpIdCliente')
            detalle.appendChild(node)
            txt = doc.createTextNode(v.tipoidentificacionsri)
            node.appendChild(txt)
            
            node = doc.createElement('idCliente')
            detalle.appendChild(node)
            txt = doc.createTextNode(v.numeroidentificacion)
            node.appendChild(txt)
            
            if v.tipoidentificacionsri == '04' or v.tipoidentificacionsri == '05' or v.tipoidentificacionsri == '06': 
                #CAMBIOS
                node = doc.createElement('parteRelVtas')
                detalle.appendChild(node)
                txt = doc.createTextNode('NO')
                node.appendChild(txt)
                #CAMBIOS
            
            node = doc.createElement('tipoComprobante')
            detalle.appendChild(node)
            txt = doc.createTextNode(v.tipodocumentosri)
            node.appendChild(txt)
            
            node = doc.createElement('numeroComprobantes')
            detalle.appendChild(node)
            txt = doc.createTextNode(str(v.numerocomprobantes))
            node.appendChild(txt)
            
            node = doc.createElement('baseNoGraIva')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % v.baseninguniva)
            node.appendChild(txt)
            
            node = doc.createElement('baseImponible')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % v.basecero)
            node.appendChild(txt)
            
            node = doc.createElement('baseImpGrav')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % v.basenocero)
            node.appendChild(txt)
            
            node = doc.createElement('montoIva')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % v.montoivacalc)
            node.appendChild(txt)
            
            #CAMBIOS
            node = doc.createElement('montoIce')
            detalle.appendChild(node)
            txt = doc.createTextNode("0.00")
            node.appendChild(txt)
            #CAMBIOS
            
            
            node = doc.createElement('valorRetIva')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % v.montoivaretenido)
            node.appendChild(txt)
            
            node = doc.createElement('valorRetRenta')
            detalle.appendChild(node)
            txt = doc.createTextNode("%.2f" % v.montorentaretenido)
            node.appendChild(txt)
            
        return ventas
    
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        result = {}
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            
            result['value']= {
                        'numeroidentificacion' : p.vat,
                        'tipoidentificacion_id': p.tipoid.id,
                        'tipoidentificacionsri' : p.tipoid.codigosricompra,
                     }

        return result
    
    def onchange_tipoidentificacion_id(self, cr, uid, ids, tipoidentificacion_id):
        result = {}
        if tipoidentificacion_id:
            p = self.pool.get('fiscal.tipoidentificacion').browse(cr, uid, tipoidentificacion_id)
            
            result['value']= {
                        'tipoidentificacionsri' : p.codigosricompra,
                     }

        return result
    
    def onchange_tipocomprobante_id(self, cr, uid, ids, tipocomprobante_id):
        result = {}
        if tipocomprobante_id:
            p = self.pool.get('fiscal.tipodocumento').browse(cr, uid, tipocomprobante_id)
            
            result['value']= {
                        'tipodocumentosri' : p.codigosri,
                     }

        return result
    
    _columns = {
            'tipoidentificacionsri' : fields.char('Tipo Identificacion SRI',size=10, required=True),
            'numeroidentificacion' : fields.char('Numero Identificacion',size=50, required=True),
            'tipodocumentosri' : fields.char('Codigo SRI Documento',size=10, required=True),
            'baseninguniva' : fields.float    ('Base ningun iva', digits=(8,2), required=True),
            'basecero' : fields.float('Base Cero', digits=(8,2), required=True),
            'basenocero' : fields.float('Base Mayor que Cero', digits=(8,2), required=True),
            'montoiva' : fields.float('Monto IVA', digits=(8,2), required=True),
            'montoivaretenido' : fields.float('Monto IVA retenido', digits=(8,2), required=True),
            'montorentaretenido' : fields.float('Monto renta retenido', digits=(8,2), required=True),

            'tipoidentificacion_id':fields.many2one('fiscal.tipoidentificacion', 'Tipo Identificacion', required=True),
            'partner_id':fields.many2one('res.partner', 'Cliente', required=True),
            'tipodocumento_id':fields.many2one('fiscal.tipodocumento', 'Tipo Documento', required=True),
            'numerocomprobantes' : fields.integer('Numero de Comprobantes', required=True),
            
            'atsproceso_id':fields.many2one('fiscal.ats_proceso','ATS Proceso', required=True,ondelete='cascade'),
            'siglatipoidentificacion': fields.related('tipoidentificacion_id','sigla', size=5, type='char', string='Sigla', store=False),
            
            'manual': fields.boolean('Manual', required=True),
            'montoivacalc' : fields.float('Monto IVA', digits=(8,2), required=True),
            
            'establecimiento':fields.char('establecimiento',size=3),
            'parte_relacionada':fields.selection([('SI','SI'),('NO','NO')],select=True,string="Parte relacionada"),
        }
    
    _defaults = {
                 'manual':True,
                 'parte_relacionada':'NO',
                 }
        
fiscal_ats_ventas()
