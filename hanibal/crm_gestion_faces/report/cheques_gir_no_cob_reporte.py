# -*- encoding: utf-8 -*-

from openerp.report import report_sxw
import openerp.pooler


class conciliacion_bancaria_c(report_sxw.rml_parse):
    
    ESTADOS = {
            'draft':'Borrador',
            'proforma':'Pro-Forma',
            'posted':'Contabilizado',
            'cancel':'Cancelado',
            'open':'Abierto',
            'confirmed':'Confirmado'
            }
            
    ESTADO = {
            'no':'Movimientos',
            'estado_ch':'Custodios VL',
            'estado_ch_otros':'Custodios Otros',
            'estado_ch_rise':'Custodios RISE'
            }
            
            
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(conciliacion_bancaria_c, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            
            'cuentas' :self._cuentas,
            'get_cont':self._get_cont,
            'resultante' :self._resultante,
            'resultante_todo' :self._resultante_todo,
            
            'proyectos':self._proyectos,
            
            
            'get_desde':self._get_desde,
            'get_hasta':self._get_hasta,
            'get_desdeu':self._get_desdeu,
            'get_hastau':self._get_hastau,
            'get_corte':self._get_corte,
            'get_retorno':self._get_retorno,
            'valores':self._valor,
            'get_saldo':self._get_salini,
            'reset_total_cheques':self._reset_total_cheques,
            'suma_total':self._suma_total,
            'convert':self._convert,
            'convierto':self._convierto,            
            'get_cuenta': self._get_cuenta,
            'get_banco': self._get_banco,
            'deposito':self._deposito,
            'conver': self._convertir_estado,
            'tra':self._tra,
            'total_ch':self._total_ch,
            'total_che':self._total_che,
            'reset_t_ch':self._reset_t_ch,
            
            'total_cheques':self._total_cheques,
            'total_reporte':self._total,
            'saldo_final':self._saldo_final,
        })
    
    lineas = {}
     
    def _cuentas(self, data ):
        
        banco= False
        if data.get('form', False) and data['form'].get('bank', False): 
            banco  = data['form']['bank'][0]
        
        cuenta = False
        if data.get('form', False) and data['form'].get('cuenta', False): 
            cuenta  = data['form']['cuenta'][0]

        estado = False
        if data.get('form', False) and data['form'].get('estado', False): 
            estado  = data['form']['estado']

        tipodiario= False
        if data.get('form', False) and data['form'].get('tipo_diario', False): 
            tipodiario  = data['form']['tipo_diario'][0]
            
            
        confirmados= False
        if data.get('form', False) and data['form'].get('confirmados', False): 
            confirmados  = data['form']['confirmados']    
    
        desde = False
        if data.get('form', False) and data['form'].get('desde', False):
            desde = data['form']['desde']
        
        hasta = False
        if data.get('form', False) and data['form'].get('hasta', False):
            hasta = data['form']['hasta']
            
        desdeu = False
        if data.get('form', False) and data['form'].get('desdeu', False):
            desdeu = data['form']['desdeu']
        
        hastau = False
        if data.get('form', False) and data['form'].get('hastau', False):
            hastau = data['form']['hastau']
            
       
        
        parametros = []
        param = []
        
        
        if banco:
            parametros.append("b.id = %s")
            param.append(banco)
        
        if confirmados:
            
            if confirmados == 'si':
                parametros.append("v.ver_banco = true")
            else:
                if confirmados == 'no':
                    parametros.append("v.ver_banco = false")
                else:
                    parametros.append("v.ver_banco is not null ")
        
        if cuenta:
            parametros.append("c.id = %s")
            param.append(cuenta)
            
        if tipodiario:
            parametros.append("m.id = %s")
            param.append(tipodiario)
        
        if estado:
            parametros.append("v.state = %s")
            param.append(estado)
            
        if desde and hasta:
            parametros.append("v.date between %s and %s ")
            param.append(desde)
            param.append(hasta)
        elif desde:
            parametros.append(" v.date >= %s ")
            param.append(desde)
        elif hasta:
            parametros.append("v.date <= %s ")
            param.append(hasta)

        if desdeu and hastau:
            parametros.append(" v.fecha_cobro between %s and %s ")
            param.append(desdeu)
            param.append(hastau)
        
        elif desdeu:
            parametros.append(" v.fecha_cobro >= %s ")
            param.append(desdeu)
            
        elif hastau:
            parametros.append(" v.fecha_cobro <= %s ")
            param.append(hastau)

        
        principal = """ select distinct v.ver_banco as verificacion , count (*) as contador
                    from account_voucher as v
                    left join payment_mode as m on m.journal = v.journal_id
                    left join account_journal as j on j.id = v.journal_id
                    left join res_partner_bank as c on c.id = m.bank_id
                    left join res_bank as b on b.id = c.bank
                    left join res_partner as p on p.id = v.partner_id """

        groupby = "\n group by v.ver_banco  "
        where = "\n where "
        query=''
        
        if (not parametros) or ( len(parametros) == 0 ):
            query = principal + groupby
        else:
            i=0
            for g in  parametros:
                if i==0:
                    where = where + g
                else: 
                    where = where +' and '+ g
                i=1
            query = principal + where + groupby
        
        param = tuple(param)
               
        self.cr.execute(query,param)
        lineas = self.cr.dictfetchall()
        return lineas
    
   
    def _resultante(self, data, confirmado_id ):
        
        banco= False
        if data.get('form', False) and data['form'].get('bank', False): 
            banco  = data['form']['bank'][0]
        
        cuenta = False
        if data.get('form', False) and data['form'].get('cuenta', False): 
            cuenta  = data['form']['cuenta'][0]
        
            
        tipodiario = False
        if data.get('form', False) and data['form'].get('tipo_diario', False): 
            tipodiario  = data['form']['tipo_diario'][0]
            
       
        desde = False
        if data.get('form', False) and data['form'].get('desde', False):
            desde = data['form']['desde']
            
        hasta = False
        if data.get('form', False) and data['form'].get('hasta', False):
            hasta = data['form']['hasta']
            
        desdeu = False
        if data.get('form', False) and data['form'].get('desdeu', False):
            desdeu = data['form']['desdeu']
        
        hastau = False
        if data.get('form', False) and data['form'].get('hastau', False):
            hastau = data['form']['hastau']
            
            
        estado = False
        if data.get('form', False) and data['form'].get('estado', False):
            estado = data['form']['estado']
             
        
        parametros = []
        param = []

        
        if desde and hasta:
            parametros.append(" date between %s and %s ")
            param.append(desde)
            param.append(hasta)
        
        elif desde:
            parametros.append(" date >= %s ")
            param.append(desde)
            
        elif hasta:
            parametros.append(" date <= %s ")
            param.append(hasta)
#---------------------------------------------
        if desdeu and hastau:
            parametros.append(" fec_giro between %s and %s ")
            param.append(desdeu)
            param.append(hastau)
        
        elif desdeu:
            parametros.append(" fec_giro >= %s ")
            param.append(desdeu)
            
        elif hastau:
            parametros.append(" fec_giro <= %s ")
            param.append(hastau)

        
        if estado:
            parametros.append(" state = %s ")
            param.append(estado)
        
        
        if banco:
            parametros.append("b_id = %s")
            param.append(banco)
                
        if cuenta:
            parametros.append("c_id = %s")
            param.append(cuenta)
      
            
        if tipodiario:
            parametros.append("m_id = %s")
            param.append(tipodiario)
                      
        #orderby = "\n ORDER BY 10,5,11 "
        #principal = """ select distinct estado_ch from conciliacion_bancaria  """
        #where = "\n where ver_banco = " +str(confirmado_id) + ' '
        #for g in  parametros:
        #    where = where +' and '+ g
        #query = principal + where + str('order by 1 desc')
        #self.cr.execute(query ,param)
        #lineas = self.cr.dictfetchall()
        
        print confirmado_id,'<-------------'
        principal = """ select *  from conciliacion_bancaria where estado_ch = 't' """
        where = "\n and ver_banco = " +str(confirmado_id) + ' '
        for g in  parametros:
            where = where +' and '+ g
        query = principal + where +' '+ str('order by 1 desc')
        
        self.cr.execute(query ,param)
        lineas = self.cr.dictfetchall()
        
        
        principal = """ select *  from conciliacion_bancaria where estado_ch_rise = 't' """
        where = "\n and ver_banco = " +str(confirmado_id) + ' '
        for g in  parametros:
            where = where +' and '+ g
        query = principal + where +' '+ str('order by 1 desc')
        self.cr.execute(query ,param)
        lineas_a = self.cr.dictfetchall()
        
        
        
        principal = """ select *  from conciliacion_bancaria where estado_ch_otros = 't' """
        where = "\n and ver_banco = " +str(confirmado_id) + ' '
        for g in  parametros:
            where = where +' and '+ g
        query = principal + where +' '+ str('order by 1 desc')
        self.cr.execute(query ,param)
        lineas_b = self.cr.dictfetchall()
        
        
        
        
        
        principal = """ select *  from conciliacion_bancaria where estado_ch_rise = 'f' and estado_ch_otros = 'f' and estado_ch = 'f' """
        where = "\n and ver_banco = " +str(confirmado_id) + ' '
        for g in  parametros:
            where = where +' and '+ g
        query = principal + where +' '+ str('order by 1 desc')
        self.cr.execute(query ,param)
        lineas_c = self.cr.dictfetchall()
        
        dct=[]
        if len(lineas) > 0 : 
            r = {'custodio': 'estado_ch' }
            dct.append(r)
        if len(lineas_a) > 0 : 
            s = {'custodio': 'estado_ch_rise' }
            dct.append(s)
        if len(lineas_b) > 0 :
            t = {'custodio': 'estado_ch_otros' }
            dct.append(t)
        if len(lineas_c) > 0 :
            u = {'custodio': 'no' }
            dct.append(u)
            
        return dct
    
#----------------------------------------------------------------------------------

    def _resultante_todo(self, data, confirmado_id,estados_cheques ):
        
        if estados_cheques == 'no':
            estados_cheques = "estado_ch = 'f' and estado_ch_rise = 'f' and estado_ch_otros = 'f' "
        
        if estados_cheques == 'estado_ch':
            estados_cheques = "estado_ch = 't' "
        
        if estados_cheques == 'estado_ch_otros':
            estados_cheques = "estado_ch_otros = 't' "
            
        if estados_cheques == 'estado_ch_rise':
            estados_cheques = "estado_ch_rise = 't' "
        
        
        banco= False
        if data.get('form', False) and data['form'].get('bank', False): 
            banco  = data['form']['bank'][0]
        
        cuenta = False
        if data.get('form', False) and data['form'].get('cuenta', False): 
            cuenta  = data['form']['cuenta'][0]
        
            
        tipodiario = False
        if data.get('form', False) and data['form'].get('tipo_diario', False): 
            tipodiario  = data['form']['tipo_diario'][0]
            
        desde = False
        if data.get('form', False) and data['form'].get('desde', False):
            desde = data['form']['desde']
            
        hasta = False
        if data.get('form', False) and data['form'].get('hasta', False):
            hasta = data['form']['hasta']
            
        desdeu = False
        if data.get('form', False) and data['form'].get('desdeu', False):
            desdeu = data['form']['desdeu']
        
        hastau = False
        if data.get('form', False) and data['form'].get('hastau', False):
            hastau = data['form']['hastau']
            
        estado = False
        if data.get('form', False) and data['form'].get('estado', False):
            estado = data['form']['estado']
             
        
        parametros = []
        param = []

        
        if desde and hasta:
            parametros.append(" date between %s and %s ")
            param.append(desde)
            param.append(hasta)
        
        elif desde:
            parametros.append(" date >= %s ")
            param.append(desde)
            
        elif hasta:
            parametros.append(" date <= %s ")
            param.append(hasta)


        if desdeu and hastau:
            parametros.append(" fec_giro between %s and %s ")
            param.append(desdeu)
            param.append(hastau)
        
        elif desdeu:
            parametros.append(" fec_giro >= %s ")
            param.append(desdeu)
            
        elif hastau:
            parametros.append(" fec_giro <= %s ")
            param.append(hastau)

        
        if estado:
            parametros.append(" state = %s ")
            param.append(estado)
        
        
        if banco:
            parametros.append("b_id = %s")
            param.append(banco)
                
        if cuenta:
            parametros.append("c_id = %s")
            param.append(cuenta)
      
            
        if tipodiario:
            parametros.append("m_id = %s")
            param.append(tipodiario)
                      
        orderby = "\n ORDER BY 10,5,11 "
        principal = """ select * from conciliacion_bancaria  """
        where = "\n where ver_banco =  '"+str(confirmado_id)+"' and  "+str(estados_cheques)+" "
            
        for g in  parametros:
            where = where +' and '+ g
        query = principal + where + orderby
        self.cr.execute(query ,param)
        lineas = self.cr.dictfetchall()        
        return lineas

#----------------------------------------------------------------------------------
                            
    def _proyectos(self, cheque_id ):
        
        query = """ SELECT analytics_id as id
            from account_invoice_line where invoice_id in (
            select id
            from account_invoice 
            where replace(number,'/','') in (
            select ref from account_move_line where id in (
            select move_line_id
            from account_voucher_line 
            where voucher_id = %s
            )   )   ) 
                    group by analytics_id """
        self.cr.execute(query,(cheque_id,))
        res = self.cr.dictfetchall()
        mod_nom = []
        c = len(res)
        i = 0
        while i < c :
            nom_u = str(''+self._consulta_nombre(res[i]['id']) )
            mod_nom.append(nom_u)
            i += 1    
        TEXT = str("//".join(mod_nom))
        return TEXT

    def _consulta_nombre(self, pr_id ):
        self.cr.execute("select name from account_analytic_plan_instance where id = %s ",( pr_id ,))
        nom = self.cr.dictfetchall()
        return nom[0]['name']
#----------------------------------------------------------------------------------
    
    
    def _deposito(self, data ):
        
        banco= False
        if data.get('form', False) and data['form'].get('bank', False): 
            banco  = data['form']['bank'][0]
        
        cuenta = False
        if data.get('form', False) and data['form'].get('cuenta', False): 
            cuenta  = data['form']['cuenta'][0]
        
        corte = False
        if data.get('form', False) and data['form'].get('f_corte', False):
            corte = data['form']['f_corte']
           
        parametros = []
        param = []
                
        if corte:
            parametros.append(" registrobanco <= %s ")
            param.append(corte)
            
        if banco:
            parametros.append("b_id = %s")
            param.append(banco)
                
        if cuenta:
            parametros.append("c_id = %s")
            param.append(cuenta)


            
        ejecutar = """ CREATE OR REPLACE  VIEW conciliacion_bancaria AS 
                SELECT 
                     v.id AS ninterno,
                     p.name AS proveedor, 
                     v.amount AS total, 
                     v.ver_banco AS verificacion, 
                     v.veri_fecha AS fechaverifi, 
                     v.ver_regbanco AS registrobanco, 
                     v.number AS numero, 
                     v.pospago AS posfechado, 
                     v.amount * (-1)::numeric AS valor, 
                     v.date AS movi,
                     v.fecha_cobro as fec_giro,
                     'CHEQUES'::character varying AS tipomovimiento, 
                     v.state AS estado, 
                     p.id as p_id, 
                     b.id as b_id,
                     c.id as c_id, 
                     m.id as m_id, 
                     v.ver_banco as ver_banco,
                     v.date  date,
                     v.state  state,
                     coalesce(v.estado_ch,'f') estado_ch,
                     coalesce(v.estado_ch_otros,'f') estado_ch_otros,
                     coalesce(v.estado_ch_rise,'f') estado_ch_rise
                             
                 FROM account_voucher v
                 JOIN payment_mode m ON m.journal = v.journal_id
                 JOIN res_partner_bank c ON c.id = m.bank_id
                 JOIN res_bank b ON b.id = c.bank
                 JOIN res_partner p ON p.id = v.partner_id
            where v.state in ( 'posted','draft')
            and number not like '%/%' 
            and number not like '%B%' 
   
            UNION all
            
             SELECT  
                 v.id AS ninterno, 
                 COALESCE(p.name, ' - '::character varying) AS proveedor, 
                 det.amount AS total, 
                 true AS verificacion, 
                 det.date AS fechaverifi, 
                 det.date AS registrobanco, 
                 det.ref AS numero, 
                 false AS posfechado, 
                 det.amount AS valor, 
                 det.date AS movi,
                 det.date as fec_giro,
                  
                 upper(det.name::text)   AS tipomovimiento, 
                 v.state AS estado,

                 p.id AS p_id , 
                 b.id AS b_id, 
                 c.id AS c_id, 
                 m.id AS m_id, 
                 'True' AS ver_banco,
                 v.date  date,
                 v.state as state,
                 'f' as estado_ch,
                 'f' as estado_ch_otros,
                 'f' as estado_ch_rise
                  
               FROM account_bank_statement v
               LEFT JOIN account_journal tdiario ON tdiario.id = v.journal_id
               LEFT JOIN account_bank_statement_line det ON det.statement_id = v.id
               LEFT JOIN res_partner p ON p.id = det.partner_id
               JOIN payment_mode m ON m.journal = tdiario.id
               JOIN res_partner_bank c ON m.bank_id = c.id
               JOIN res_bank b ON b.id = c.bank  
               where v.state in ('open','confirm') """ 
               
        query= ''       
        if parametros:
            query = ejecutar
        else:
            query = ejecutar
           
        self.cr.execute(query)           
        
        principal = """ select  
                        sum(valor) as saldoini
                        from conciliacion_bancaria """
        
        principalr = """ select  
                        ( sum(total) - sum(total) )  as saldoini
                        from conciliacion_bancaria """

        
        where = "\n where ver_banco = true "
        query=''
        
        
        if banco and cuenta and not corte:
            query = principalr         
        else:
            i=0
            for g in  parametros:
                if i==0:
                    where = where +' and '+ g
                else: 
                    where = where +' and '+ g
                i=1
                query = principal + where 
        
        param = tuple(param)
        self.cr.execute(query,param)
        lineas = self.cr.dictfetchall()        
        return lineas
    
    
    def _get_banco(self, data):
    
        if data.get('form', False) and data['form'].get('bank', False): 
            id  = data['form']['bank'][0]
            return openerp.pooler.get_pool(self.cr.dbname).get('res.bank').browse(self.cr, self.uid, id).name
        return False
    
    def _get_cont(self,est):
        if est == 'posted':
            val = 'SI'
        else:
            val = 'NO'
        return val
    
    def _get_cuenta(self, data):
        
        if data.get('form', False) and data['form'].get('cuenta', False): 
            id  = data['form']['cuenta'][0]
            return openerp.pooler.get_pool(self.cr.dbname).get('res.partner.bank').browse(self.cr, self.uid, id).acc_number
        return False 
    
    
    def _get_desde(self, data):
        if data.get('form', False) and data['form'].get('desde', False):
            return data['form']['desde']
        return False

    def _get_hasta(self, data):
        if data.get('form', False) and data['form'].get('hasta', False):
            return data['form']['hasta']
        return False 
#------------------------------------------------------------    
    def _get_desdeu(self, data):
        if data.get('form', False) and data['form'].get('desdeu', False):
            return data['form']['desdeu']
        return False

    def _get_hastau(self, data):
        if data.get('form', False) and data['form'].get('hastau', False):
            return data['form']['hastau']
        return False 
    
    def _get_corte(self, data):
        if data.get('form', False) and data['form'].get('f_corte', False):
            return data['form']['f_corte']
        return False 

    
    def _convert(self , estado ):
        if not estado:
            valor = 'No'
        else:
            valor = 'SI'
        return valor
    
    def _convierto(self , estados ):
        if not estados:
            valores = 'no Confirmados '
        else:
            valores = 'Confirmados'
        return valores
     
    def _convertir_estado(self,tipo):
        if self.ESTADOS.has_key(tipo):
            return self.ESTADOS[tipo]
        return 'Otros'
    
    def _tra(self,tipo):
        if self.ESTADO.has_key(tipo):
            return self.ESTADO[tipo]

    total_cheques = 0.00
    total = 0.00
    tota_saldo = 0.00
    saldo = 0.00
    pri = 0
    seg = 0
    suma = 0
    sumado = 0.00
    total_c = 0.0
           
    def _valor(self, valor, cheque,cheque_a,cheque_b ):
        if str(cheque) == 'False' and str(cheque_a) == 'False' and str(cheque_b) == 'False' : 
            self.total_cheques = self.total_cheques + valor 
                 
    def _total_cheques(self):
        return self.total_cheques 
    
    def _reset_total_cheques(self):
        self.total_cheques = 0.0
        
    def _suma_total(self, valor ): 
        self.total = self.total - valor 
                 
    def _total(self):
        return self.total 

    
    def _get_salini(self , valor ):
        self.total_saldo = valor
    
    
    def _saldo_final(self):
        self.saldo = self.total_saldo - self.total
        return self.saldo 
    
    
    def _get_retorno(self,valor):
        self.suma += valor
        return self.suma
   
    def _total_che(self,val):
       
        self.total_c = self.total_c + val
    
    def _total_ch(self):
        return self.total_c
    
    def _reset_t_ch(self):
        self.total_c = 0.0 
    
    
        
report_sxw.report_sxw(
    'report.conciliacion.bancaria',
    'rt.conciliacion.bancaria',
    'addons/rt_verificacionbancaria/report/cheques_gir_no_cob_reporte.rml',
    parser=conciliacion_bancaria_c,header=False)

