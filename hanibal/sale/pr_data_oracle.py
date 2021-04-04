# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

"""
@author: ARNEGSIS S.A.
"""

import unicodedata
from openerp import api
from openerp.osv import osv,fields


class proces_data_oracle(osv.osv):
    
    _name='proces.data.oracle'
    
    _columns = {
        'name': fields.char('Order Reference',)
              }
    
    #NOVEDADE
    
    @api.multi
    def _update_proforma(self,):
        print 'PROFORMA INFO'
        self._cr.execute("SELECT * FROM sale_order WHERE estado_informativo = 'NO PROCESADO' ")
        for l in self._cr.dictfetchall():
            self._cr.execute( "UPDATE sale_order SET state = 'draft' WHERE id = %s ",( l['id'],) )
            self._cr.execute( "UPDATE sale_order_line SET state = 'draft' WHERE order_id = %s ",( l['id'],) )
            self._cr.commit()
	    #IDENTIFICAR EL CAMPO act_id ESTE CAMBIA EN CADA BASE
            self._cr.execute(""" update wkf_workitem set act_id = 10 where id in 
                                (select max(id) from wkf_workitem where inst_id in
                                (select id from wkf_instance where res_id = %s  )) """,( l['id'],) )
            self._cr.commit()
            self._cr.execute( "UPDATE sale_order SET estado_informativo = 'No procesado' WHERE id = %s ",( l['id'],) )
            self._cr.commit()
  
            
            
    @api.multi
    def _run_process(self,):
        
        self._run_informacion_cot()
        self._producto_unidades()
        self._producto()
        self._product_stock()
        self._vendedores()
        self._partners()
        self._lista_precios_cab()
        self._lista_precios_det()
        self._partners_street()
        self._update_proforma()
	print 'END'
    
    #ACTUALIZA EL CAMPO INFO DE LA COTIZACION
    @api.multi
    def _run_informacion_cot(self,):
        print 'UPDATE INFORMACION - NOVEDADES'
        self._cr.execute(""" select *
                             FROM web_side_ven_pfa_g 
                             where pfac_migrado = 'S' AND pfac_migraestado = 'S' ; """)
        res = self._cr.dictfetchall()
        if len(res) >= 1:
            for l in res:
		print 'ingresa a hacer esto igual'
                obj_order = self.env['sale.order'].browse(int(l['pfac_idweb']))
                #obj_order.write({'estado_informativo':str(l['pfac_estadoinformativo']),
                #                 'novedades':str(l['pfac_novedades'])})
		update_sale_order = """ UPDATE sale_order SET estado_informativo = %s , novedades = %s WHERE id = %s """
                print 'update_sale_order'
                print update_sale_order
		#print str(l['pfac_estadoinformativo']) , str(l['pfac_novedades']) , obj_order.id
                self._cr.execute( update_sale_order , ( str(l['pfac_estadoinformativo']) , str(l['pfac_novedades']) , obj_order.id ) )

                update = """ UPDATE web_side_ven_pfa_g set pfac_migraestado = 'N' 
                                where pfac_idweb = %s  """
                self._cr.execute( update , ( int(l['pfac_idweb']), ) )
                self._cr.commit()
        return True
    
    
    @api.multi
    def _producto_unidades(self,):
        
        print 'UNIDADES MEDIDA'
        opu = self.env['product.uom']
        self._view(3)
        sql=""" select * 
                from web_side_inv_uni_temp """
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
      
        for p in res:
            if  self._consulta(p['uni_codigo'],5) >= 1 :
                dct={'name':p['uni_codigo'],'rounding': 0.01,'factor':1.0,'uom_type': 'reference'
                    ,'category_id': 1 }
                opu.browse( self._consulta(p['uni_codigo'],6) ).write(dct)
                self._actualizar( p['uni_codigo']  , 3 )
            else:
                dct={'name':p['uni_codigo'],'rounding': 0.01,'factor':1.0,'uom_type': 'reference'
                    ,'category_id': 1 }
                opu.create(dct)
                self._actualizar( p['uni_codigo']  , 3 )
   
        self._dropear(3)
        return True
    
    
    @api.multi
    def _producto(self,):

        print 'PRODUCTO' 
        self._view(4)
        sql=""" select *
                from web_side_inv_art_temp """
        self._cr.execute(sql)
        p = self._cr.dictfetchall()
         
        for res in p:
            if  self._consulta( res['art_codigo'],7 ) >= 1 :
                update_a = """ UPDATE product_product set name_template = %s , default_code = %s ,active  = %s
                                where default_code = %s  """
                self._cr.execute( update_a , (  self.elimina_tildes(res['art_des']) 
                                                , res['art_codigo'] 
                                                , self._activo( str(res['art_estado']) ) 
                                                , res['art_codigo'] ) )
                update_b = """ UPDATE product_template set name = %s , default_code = %s ,active  = %s, list_price = %s ,categ_id = %s 
                                where default_code = %s  """

                self._cr.execute( update_b , (  self.elimina_tildes(res['art_des']) 
                                                , res['art_codigo'] 
                                                , self._activo( str(res['art_estado']) )    
                                                , float(res['precio'])      
                                                #, res['art_codigo']                        
                                                , str(self._clasificacion(res['acla_codvcla']))
                                                , res['art_codigo']  ) )

#**********************************************************************************************
#************************************************************************
                delete = """ delete from product_taxes_rel where prod_id = %s """
                self._cr.execute(delete,( (self._consulta(res['art_codigo'], 18 ),) ))
                
                if res['porcentajeimpuesto'] == '14' or res['porcentajeimpuesto'] == '12' or res['porcentajeimpuesto'] == '0' :
                    self._cr.execute("INSERT INTO product_taxes_rel(prod_id, tax_id) VALUES (%s, %s);",
                                    ( (self._consulta(res['art_codigo'], 18 ),
                                      (self._consulta(res['porcentajeimpuesto'], 17 ) ))))
                self._actualizar( res['id']  , 4 )            
            else:
                self._producto_template(res)
                sql =""" INSERT INTO product_product
                (product_tmpl_id,name_template,default_code,active)
                VALUES
                (%s,%s,%s,%s) """
                self._cr.execute(sql,( self._consulta(res['art_codigo'], 10 ), res['art_des'],
                                       res['art_codigo'], self._activo(str(res['art_estado'])) ) )
                if res['porcentajeimpuesto'] == '14' or res['porcentajeimpuesto'] == '12' or res['porcentajeimpuesto'] == '0' :
                    self._cr.execute("INSERT INTO product_taxes_rel(prod_id, tax_id) VALUES (%s, %s);",
                                   ( (self._consulta(res['art_codigo'], 18 ),
                                     (self._consulta(res['porcentajeimpuesto'], 17 ) ))))
                self._actualizar( res['id']  , 4 )
        self._dropear(4)
        return True
    
    
    @api.multi
    def _partners(self,):
        
        print 'INICIO PARTNERS'
        orp = self.env['res.partner']
        self._view(1)
        sql=""" select * 
                from web_side_cli_cli_temp """
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
        
        for p in res:
	    if  self._consulta(p['clienteid'],1) >= 1 :
                dct={'name':p['razonsocial'],'vat':p['clienteid'],'notify_email':'always','street':p['direccionprincipal']
                    ,'ref':p['direccionprincipal2'],'phone':p['telefono1'],'mobile':p['telefono2'],'fax':p['fax'],
                    'email':p['correoprincipal'],'credit_limit':p['cupocredito'],'city':p['ciudadid']
                    ,'property_payment_term': 1 , 'user_id': self._consulta(p['vendedorid'], 4 ),
                    'property_product_pricelist': self._consulta(p['tipoprecio'], 12 )}
                orp.browse( self._consulta(p['clienteid'],2) ).write(dct)
                self._actualizar( p['id']  , 1 )
            else:
                dct={'id':p['clienteid'],'name':p['razonsocial'],'vat':p['clienteid'],'notify_email':'always','street':p['direccionprincipal']
                ,'ref':p['direccionprincipal2'],'phone':p['telefono1'],'mobile':p['telefono2'],'fax':p['fax'],
                'email':p['correoprincipal'],'credit_limit':p['cupocredito'],'city':p['ciudadid']
                ,'property_payment_term': 1 , 'is_company':True, 'user_id': self._consulta(p['vendedorid'], 4 ),
                'property_product_pricelist': self._consulta(p['tipoprecio'], 12 ) }
                orp.create(dct)
                self._actualizar( p['id']  , 1 )
       
        self._dropear(1)
        return True
    
    
    @api.multi
    def _partners_street(self,):
        
        print 'INICIO PARTNERS STREET'
        orp = self.env['res.partner']
        self._view(8)
        sql=""" select * 
                from web_side_cli_dire_temp """
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
        for p in res:
            self._cr.execute("select * from res_partner where vat = %s and is_company = 't' ",(p['dire_codcli'],) )
            prt = self._cr.dictfetchall()
            if len(prt) >= 1 :
	        if  self._consulta_tuple(p['dire_codcli'],p['dire_codigo'],1) >= 1 :
                    dct={'name':p['dire_dir'],
                         'vat':p['dire_codcli'],
                         'notify_email':'always',
                         'street':p['dire_dir'],
                         'phone':p['dire_telefono'],
                        'email':p['dire_email'],'credit_limit':prt[0]['credit_limit'],'city':p['dire_codloc']
                        ,'property_payment_term': 1 , 'user_id':prt[0]['user_id']
                         }

                    orp.browse( self._consulta_tuple(p['dire_codcli'],p['dire_codigo'],2) ).write(dct)
                    self._actualizar( p['dire_indice']  , 8 )
            	else:
                    dct={'name':p['dire_dir'],'vat':p['dire_codcli'],'notify_email':'always',
                    'street':p['dire_dir'],'street2':p['dire_codigo'],'phone':p['dire_telefono'],
                    'email':p['dire_email'],'credit_limit':prt[0]['credit_limit'],'city':p['dire_codloc']
                    ,'property_payment_term': 1 , 'is_company':False, 'user_id': prt[0]['user_id'],
                    'property_product_pricelist': orp.browse(prt[0]['id']).property_product_pricelist.id ,
                    'parent_id': prt[0]['id'], 'indice':p['dire_indice'] }
                    orp.create(dct)

                    self._actualizar( p['dire_indice']  , 8 )
        self._dropear(8)
        return True
    
            
    @api.multi
    def _product_stock(self,):
        
        print 'STOCK'
        self._view(5)
        sql=""" select * 
                from web_side_inv_bar_temp """
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
        for p in res:
            sql = """ UPDATE product_template set cantidad = %s where default_code = %s """
            self._cr.execute(sql, (p['bar_can_disp'],p['bar_codart']) )
            self._actualizar( p['bar_codart']  , 5 )
        self._dropear(5)
        return True
    
    
    @api.multi
    def _vendedores(self,):
        
        print 'INCIO VENDEDORES'
        lista = {}
        oru = self.env['res.users']
        self._view(2)
        sql=""" select *
                from web_side_age_age_temp """
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
       
        for v in res:
            if  self._consulta(v['age_codigo'], 3 ) >= 1 :
                dct = {'active':True,'company_id': 1 ,'alias_id': 1 , 'login':v['age_email'],'email':str(v['age_email']),'cargo':v['age_cargo'],'telefono':v['age_telefono'] }
                oru.browse( self._consulta(v['age_codigo'],4) ).write(dct)
                self._actualizar( v['id']  , 2 )
            else:
                lista = {'active':True,'company_id':1,'alias_id':1,'login':str(v['age_email']),'email':str(v['age_email']),
                         'codigo':v['age_codigo'],'cargo':v['age_cargo'],'name':v['age_des'],'telefono':v['age_telefono']}
                oru.create(lista)
                self._actualizar( v['id']  , 2 )
       
        self._dropear(2)
        return True
    
    
    @api.multi
    def _lista_precios_cab(self,):
        
        print 'LISTA DE PRECIOS CAB'
        self._view(6)
        sql=""" select *
                from web_side_ven_tpr_temp """
        self._cr.execute(sql)
        p = self._cr.dictfetchall()
      
        for res in p:
            if  self._consulta( res['tpr_codigo'],11 ) >= 1 :
                update_a = """ UPDATE product_pricelist set name = %s 
                                where default_code = %s  """
                self._cr.execute( update_a , (  self.elimina_tildes(res['tpr_des']) , res['tpr_codigo']  )  )
                update_b = """ UPDATE product_pricelist_version set name = %s 
                                where default_code = %s  """
                self._cr.execute( update_b , (  self.elimina_tildes(res['tpr_des']) , res['tpr_codigo'] )  )
                self._actualizar( res['tpr_indice']  , 6 )
            else:
                self._product_pricelist(res)
                sql =""" INSERT INTO product_pricelist_version
                (pricelist_id,name,active,default_code)
                VALUES
                (%s,%s,%s,%s) """
                self._cr.execute(sql,( self._consulta(res['tpr_codigo'], 12 ), 
                                            res['tpr_des'],
                                            True,
                                            res['tpr_codigo'] ) )
                self._actualizar( res['tpr_indice']  , 6 )
       
        self._dropear(6)
        return True
    
    
    @api.multi
    def _lista_precios_det(self,):
        
        print 'LISTA DE PRECIOS DET'
        self._view(7)
        sql=""" select *
                from web_side_inv_pre_temp """
        self._cr.execute(sql)
        p = self._cr.dictfetchall()
        for res in p:
            if  self._consulta_tuple( res['pre_codart'] , res['pre_codtpr'], 14 ) >= 1 :
		if str(res['pre_precio']) ==  '-1000.0':
			delete = """ delete from product_pricelist_item where name = %s and price_version_id = %s """
			self._cr.execute( delete , ( 
                                                self.elimina_tildes(res['pre_codart']),
						self._consulta(res['pre_codtpr'],15)
                                                  )  )
                #####################*****************************
                update_a = """ UPDATE product_pricelist_item set 
                                name = %s , price_surcharge = %s ,
                                product_id = %s 
                                where name = %s and price_version_id = %s """
                self._cr.execute( update_a , (  self.elimina_tildes(res['pre_codart']) ,
                                                res['pre_precio'],
                                                self._consulta(res['pre_codart'], 8 ),
                                                self.elimina_tildes(res['pre_codart']),
						self._consulta(res['pre_codtpr'],15)
                                                  )  )
                self._actualizar( res['tpr_indice']  , 7 )

                #################**anibal dice:**********************
                if res['pre_codtpr'] == 'PVI':
                  update_x = """ UPDATE product_template set list_price = %s 
                                where default_code = %s  """

                  self._cr.execute( update_x , (   float(res['pre_precio'])      
                                                 , res['pre_codart']  ) )
                ############****FIN ANIBAL DICE*******************

            else:
                self._product_pricelist_item(res)
                self._actualizar( res['tpr_indice']  , 7 )
        self._dropear(7)
        return True
    
    @api.multi
    def _product_pricelist(self,res):
        
        sql =""" INSERT INTO product_pricelist
                (name,type,currency_id,visible_discount,default_code,active)
                VALUES
                (%s,%s,%s,%s,%s,%s) """
        self._cr.execute(sql,( res['tpr_des'],'sale', 3 , True,res['tpr_codigo'],True ) )
        self._cr.commit()
    

    @api.multi
    def _product_pricelist_item(self,res):

        sql =""" INSERT INTO product_pricelist_item
        (price_version_id ,price_round ,price_min_margin,price_discount,price_surcharge,name,sequence
        ,base,min_quantity,product_id)
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
        self._cr.execute(sql,( self._consulta(res['pre_codtpr'], 13 ), 
                                    0.00,
                                    0.00,
                                    -1.0000,
                                    res['pre_precio'],
                                    res['pre_codart'],
                                    5,
                                    1,
                                    0,
                                    self._consulta(res['pre_codart'], 8 )
                                     ) )
        self._cr.commit()
            
    
    @api.multi
    def _producto_template(self,res):
        
        sql = """ INSERT INTO product_template (name,list_price,active,type,categ_id,purchase_ok,
                    sale_ok,company_id,uom_id,uom_po_id,uos_coeff,default_code)
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
        self._cr.execute(sql,(    self.elimina_tildes(res['art_des'])    , float(res['precio']), self._activo(str(res['art_estado']) ),
                              self._tipo(res['art_tipo']), self._clasificacion(res['acla_codvcla']), False, True, 1, self._unidad(res['art_coduni']),
                              self._unidad(res['art_coduni']), 1.000, res['art_codigo']  ))
        self._cr.commit()
    
    
    def elimina_tildes(self,s):
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

    def _clasificacion(self,s):
        if s == 'VIK':
          return 1
        else :
          return 3

        
    
    @api.multi
    def _activo(self,cod):
        
        if cod == 'L': 
            res = 't'
        else:
            res = 'f'
        return res
    
    @api.multi
    def _tipo(self,cod):
        res =''
        if cod == 'A': 
            res = 'product'
        elif res == 'S':
            res = 'service'
        return res
    
    
    @api.multi
    def _unidad(self,cod):
        
        sql = "select * from product_uom where name = '"+str(cod)+"' "
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
        return res[0]['id']
    
    @api.multi
    def _view(self,bnd):
        
        """ 1 --> PARTNERS ; 2 --> VENDEDORES ; 3--> UNIDADES MEDIDA ;
            4 --> PRODUCTOS ; 5 --> STOCK ; 6 --> LISTA DE PRECIOS CAB
            7 --> LISTA DE PRECIO DET ; 8--> DIRECCIONES PARTNERS""" 
        
        if bnd == 1 :
            view = """ create view web_side_cli_cli_temp as
                    (select * from web_side_cli_cli where migrado = 'N' ) """
            self._cr.execute(view)
        if bnd == 2 :
            view = """ create view web_side_age_age_temp as
                    (select * from web_side_age_age where age_migrado = 'N' AND age_email <> '' ) """
            self._cr.execute(view)
        if bnd == 3 :
            view = """ create view web_side_inv_uni_temp as
                    (select * from web_side_inv_uni where uni_migrado = 'N' ) """
            self._cr.execute(view)
        if bnd == 4 :
            view = """ CREATE view web_side_inv_art_temp AS
                    (select * from web_side_inv_art where migrado = 'N' ) """
            self._cr.execute(view)
        if bnd == 5 :
            view = """ CREATE view web_side_inv_bar_temp AS
                    (select * from web_side_inv_bar where bar_migrado = 'N' ) """
            self._cr.execute(view)
        if bnd == 6 :
            view = """ CREATE view web_side_ven_tpr_temp AS
                    (select * from web_side_ven_tpr where tpr_migrado = 'N' ) """
            self._cr.execute(view)
        
        if bnd == 7 :
            view = """ CREATE view web_side_inv_pre_temp AS
                    (select * from web_side_inv_pre where tpr_migrado = 'N' ) """
            self._cr.execute(view)
            
        if bnd == 8 :
            view = """ CREATE view web_side_cli_dire_temp AS
                    (select * from web_side_cli_dire where dire_migrado = 'N' ) """
            self._cr.execute(view)
        
        return True
        
    
    @api.multi
    def _consulta_tuple(self,ids,indice,bnd):
        """ 1,2 --> PARTNERS ; 14,15 LISTAS DE PRECIO  """
        if bnd == 1 :
            sql=""" select * from res_partner where is_company <> 't' and vat = %s and street2 = %s """
            self._cr.execute(sql,(str(ids),str(indice) ))
            res = self._cr.dictfetchall()
            cont = len(res)
        elif bnd == 2 :
            sql=""" select * from res_partner where is_company <> 't' and vat = %s and street2 = %s """
            self._cr.execute(sql,(str(ids),str(indice) ))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']

	if bnd == 14 :
            sql=""" select * from product_pricelist_item i,product_pricelist_version v where i.price_version_id = v.id and i.name = %s and v.default_code = %s"""
            self._cr.execute(sql,(str(ids),str(indice) ))
            res = self._cr.dictfetchall()
            cont = len(res)
        elif bnd == 15  :
            sql=""" select * from res_partner where  is_company <> 't' and vat = %s and street2 = %s """
            self._cr.execute(sql,(str(ids),str(indice) ))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
        return cont
    
   
    @api.multi
    def _consulta(self,ids,bnd):
        """ 1,2 --> PARTNERS ; 3,4 --> VENDEDORES ; 5,6 --> UNIDADES MEDIDA 
            7,8 --> PRODUCTOS -, 10 --> CONSULTA ID DE PRODUCTO TEMPLATE 
            ; 11,12,13 --> LITA DE PRECIOS DET;  14,15 -->  LISTA DE PRECIO CAB ; 16 --> COMERCIAL(VENDEDOR)
            17 --> IMPUESTOS , 18 --> ID PRODUCTO , 19 --> PARENT_ID PARTNER """
        if bnd == 1 :
            sql=""" select * from res_partner where is_company = 't' and vat = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            cont = len(res)
        elif bnd == 2 :
            sql=""" select * from res_partner where is_company = 't' and  vat = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
        
        if bnd == 3 :
            sql=""" select * from res_users where codigo = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            cont = len(res)
        if bnd == 4 :
            sql=""" select * from res_users where codigo = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
        
        if bnd == 5 :
            sql=""" select * from product_uom where name = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            cont = len(res)
        elif bnd == 6 :
            sql=""" select * from product_uom where name = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            cont = res[0]['id']
        
        if bnd == 7 :
            sql=""" select * from product_product where default_code = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            cont = len(res)
        elif bnd == 8 :
            sql=""" select * from product_product where default_code = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
        
        if bnd == 10 :

            sql=""" select * from product_template where default_code = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
            
        if bnd == 11 :
            sql=""" select * from product_pricelist where default_code = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            cont = len(res)
        if bnd == 12 :
            sql=""" select * from product_pricelist where default_code = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
        
        if bnd == 13 :
            sql=""" select * from product_pricelist_version where default_code = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
        
        
        if bnd == 14 :
            sql=""" select * from product_pricelist_item where name = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            cont = len(res)
        if bnd == 15 :
            sql=""" select * from product_pricelist_version where default_code = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
        
        if bnd == 16 :
            sql=""" select * from res_users where codigo = %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
            
        if bnd == 17 :
            sql=""" select * from account_tax where domain =  %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['id']
                
        if bnd == 18 :
            sql=""" select * from product_product where default_code =  %s """
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['product_tmpl_id']
        
        
        if bnd == 19 :
            sql="select min(id) as clave_id from res_partner where vat = %s AND is_company = 't' "
            self._cr.execute(sql,(str(ids),))
            res = self._cr.dictfetchall()
            if res == []:
                cont = None
            else:
                cont = res[0]['clave_id']
        
        return cont
    
    
    @api.multi
    def _actualizar(self,ids,bnd):
        """ 1 --> PARTNERS , 2 --> VENDEDORES , 3 --> UNIDADES MEDIDA ,
            4 --> PRODUCTOS , 5--> STOCK ; 6--> LISTA DE PRECIOS CAB ; 7 --> LISTA DE PRECIO DET;
            8 --> DIRECCIONES"""
        if bnd == 1:
            sql=""" update web_side_cli_cli set migrado = 'S' where id = %s """
            self._cr.execute(sql,(ids,))
        if bnd == 2:
            sql=""" update web_side_age_age set age_migrado = 'S' where id = %s """
            self._cr.execute(sql,(ids,))
        if bnd == 3:
            sql=""" update web_side_inv_uni set uni_migrado = 'S' where uni_codigo = %s and  uni_migrado = 'N' """
            self._cr.execute(sql,(ids,))
        if bnd == 4:
            sql=""" update web_side_inv_art set migrado = 'S' where id = %s """
            self._cr.execute(sql,(ids,))
        if bnd == 5:
            sql=""" update web_side_inv_bar set bar_migrado = 'S' where bar_codart = %s """
            self._cr.execute(sql,(ids,))
        if bnd == 6:
            sql=""" update web_side_ven_tpr set tpr_migrado = 'S' where tpr_indice = %s """
            self._cr.execute(sql,(ids,))
        if bnd == 7:
            sql=""" update web_side_inv_pre set tpr_migrado = 'S' where tpr_indice = %s """
            self._cr.execute(sql,(ids,))
        if bnd == 8:
            sql=""" update web_side_cli_dire set dire_migrado = 'S' where dire_indice= %s """
            self._cr.execute(sql,(ids,))
        return True
    
    @api.multi
    def _dropear(self,bnd):
        """ 1 --> PARTNERS , 2 --> VENDEDORES , 3 --> UNIDADES MEDIDA 
            4 --> PRODUCTOS ,5 -->  STOCK, 6 -->  LISTA DE PRECIOS CAB"""
        if bnd == 1 :
            sql=""" drop view web_side_cli_cli_temp """
            self._cr.execute(sql)
        if bnd == 2 :
            sql=""" drop view web_side_age_age_temp """
            self._cr.execute(sql)
        if bnd == 3 :
            sql=""" drop view web_side_inv_uni_temp """
            self._cr.execute(sql)
        if bnd == 4 :
            sql=""" drop view web_side_inv_art_temp """
            self._cr.execute(sql)
        if bnd == 5 :
            sql=""" drop view web_side_inv_bar_temp """
            self._cr.execute(sql)
        if bnd == 6 :
            sql=""" drop view web_side_ven_tpr_temp """
            self._cr.execute(sql)
        if bnd == 7 :
            sql=""" drop view web_side_inv_pre_temp """
            self._cr.execute(sql)
        if bnd == 8 :
            sql=""" drop view web_side_cli_dire_temp """
            self._cr.execute(sql)
        return True
        
