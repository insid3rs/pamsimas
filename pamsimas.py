from openerp.osv import osv, fields
    
class res_users(osv.Model):
    _inherit = 'res.users'
    _order = 'user_type'
    
    def onchange_get_position(self, cr, uid, ids, user_type, context=None):
        
        obj = self.pool.get('res.groups')
        category_id = obj.search(cr, uid, [('category_id.name', 'ilike', 'Pamsimas')], context=context)
        category = obj.browse(cr, uid, category_id, context=context)
        
        #print "=============="+user_type
        res ={}
        for o in category:
            #print o.id
            if o.id == user_type:
                self.write(cr, uid, ids, { 'groups_id' : [(4, o.id)] })
            else:    
                self.write(cr, uid, ids, { 'groups_id' : [(3, o.id)] })
        
        for o in category:
            #print o.name
            if (o.id == user_type) & (o.name == 'Regional'):
                print 'regional'
                res['position'] = 'roms'
            if (o.id == user_type) & (o.name != 'Regional'):
                res['position'] = False
                res['office'] = False
                print 'not regional'
        
            
        return {'value':res} 
    
    def onchange_get_office(self, cr, uid, ids, position, context=None):
        
        if position == False:
            return {}
        
        office = []
        
        obj = self.pool.get('pamsimas.regional')
        office_id = obj.search(cr, uid, [], context=context)
        offices = obj.browse(cr, uid, office_id, context=context)
        
        res ={} 
        res['office'] = 0
        #for o in offices:
        #    print o.name
        #    res['office'] = o.roms.name
            
        if position == "roms":
            domain = [('roms','!=',False),('province','=',False),('city','=',False)]
        if position == "province":
            domain = [('roms','!=',False),('province','!=',False),('city','=',False)]
        if position == "city":
            domain = [('roms','!=',False),('province','!=',False),('city','!=',False)]
            
        #return {'value': res}
        return {'value':res, 'domain': {'office': domain}}
    
    
    _columns = {
        'user_type'     : fields.many2one('res.groups', 'Group'),
        'roms'          : fields.many2one('pamsimas.roms', 'Roms'),
        'position'      : fields.selection((('roms', 'Roms'), ('province','Province'), ('city','City/Kabupaten')),'Position'),
        'office'        : fields.many2one('pamsimas.regional', 'Office'),
        'receiver_bank' : fields.char('Bank Name'),
        'receiver_bank_no': fields.char('Bank Acc Number'),
        'receiver_name' : fields.char('FullName'),
        'thp'           : fields.float('Minimum THP', digits=(0,0)),
    }
    

class ROMS(osv.osv):
    _name           = 'pamsimas.roms'
    _description    = 'ROMS'
    _columns         = {
        'name'          : fields.char('ROMS', size=128, required = True),
        'roms'          : fields.one2many('pamsimas.regional', 'roms', 'Roms', ondelete='cascade'),
        
        #'description'   : fields.text('Description'),
        #'prov_ids': fields.one2many(obj.prov)
    }
    
class Province(osv.osv):
    _name           = 'pamsimas.province'
    _description    = 'Province'
    _columns         = {
        'name'          : fields.char('Province', size=128, required = True),
        #'roms'          : fields.many2one('pamsimas.roms','Roms', ondelete='cascade'),
        #'description'   : fields.text('Description'),
        #'rom_id': fields.many2one(objrom)
        #'city_ids': fields.one2many(obj.city)
    }
    
class City(osv.osv):
    _name           = 'pamsimas.city'
    _description    = 'Province'
    _columns         = {
        'name'          : fields.char('City/Kabupaten', size=128, required = True),
        #'roms'          : fields.many2one('pamsimas.roms','Roms', ondelete='cascade'),
        #'province'      : fields.many2one('pamsimas.province','Province', ondelete='cascade'),
        #'description'   : fields.text('Description'),
        #'prov_id':fields.many2one(prov)
    }
    
    def check_roms(self, cr, uid, ids, province, context=None):
        province_obj = self.pool.get("pamsimas.province")
        roms = province_obj.browse(cr, uid, [province], context=context)
        res = {}
        for p in roms:
            #print "====================",p.roms.id
            res['roms']=p.roms.id
        return {'value': res} 
    
class Regional(osv.osv):
    
    def update_detail(self, cr, uid, ids, detail_code, detail_name, detail_type, context=None): 
        
        if detail_type == "roms":
            obj = self.pool.get("pamsimas.roms")
        if detail_type == "province":
            obj = self.pool.get("pamsimas.province")
        if detail_type == "city":
            obj = self.pool.get("pamsimas.city")
        
        roms = obj.browse(cr, uid, [detail_name], context=context)
        detail = ""
        if (detail_code != False) and (detail_name != False):
            for p in roms:
                detail = detail_code + " - " + p.name
            #print detail
        res ={}
        res['detail']=detail
        return {'value': res}
    
    def get_roms(self, cr, uid, ids, field_name, args, context=None):
        res={}
        user_list=[]
        obj_regional = self.pool.get("pamsimas.regional")
        ids_regional = obj_regional.search(cr, uid, [])
        #res = obj_regional.read(cr, uid, ['name', 'id'], context)
        res = obj_regional.browse(cr, uid, [ids_regional], context=context)
        
        #obj_roms = self.pool.get("pamsimas.roms")
        #ids_roms = obj_roms.search(cr, uid, [('name', '=', 34)])
        return res
    
    _name           = 'pamsimas.regional'
    _description    = 'Region'
    _rec_name = 'detail'
    _order = 'name asc'
    _columns         = {
        'name'          : fields.char('Regional ID', required = True, domain="[('name', 'in', [roms])]" ),
        'detail'        : fields.char('Detail'),
        'roms'          : fields.many2one('pamsimas.roms', 'Roms', ondelete='cascade'),
        'province'      : fields.many2one('pamsimas.province', 'Province', ondelete='cascade'),
        'city'          : fields.many2one('pamsimas.city','City', ondelete='cascade'),
        'description'   : fields.text('Description'),
}
    
class Transfer(osv.osv):
    
    def update_state(self, cr, uid, ids, context=None):
        res ={} 
        res['state'] = 'confirmed'
        self.write(cr, uid, ids, { 'state' : 'confirmed' })
        return {'value':res} 
    
    def onchange_get_office(self, cr, uid, ids, position, context=None):
        
        office = []
        
        obj = self.pool.get('pamsimas.regional')
        office_id = obj.search(cr, uid, [], context=context)
        offices = obj.browse(cr, uid, office_id, context=context)
        
        res ={} 
        res['office'] = 0
        #for o in offices:
        #    print o.name
        #    res['office'] = o.roms.name
        
        
        username = self.pool.get('res.users').browse(cr,uid,uid).name
        #print "#####"+username    
            
        if position == "roms":
            domain = [('roms','=',username),('province','=',False),('city','=',False)]
        if position == "province":
            domain = [('roms','=',username),('province','!=',False),('city','=',False)]
        if position == "city":
            domain = [('roms','=',username),('province','!=',False),('city','!=',False)]
            
        #return {'value': res}
        return {'value':res, 'domain': {'office': domain}} 
    
    def onchange_get_officer(self, cr, uid, ids, office_id, context=None):
        
        if office_id == False:
            return {}
        
        obj = self.pool.get('res.users')
        user_id = obj.search(cr, uid, [], context=context)
        users = obj.browse(cr, uid, user_id, context=context)
        
        res ={} 
        res['officer_name'] = 0
        
        #print users.office.detail
        
        domain = [('office','=',office_id)]
        
        #print office
        #for o in users:
        #    print o.office.id
        #    res['office'] = o.roms.name
            
        #return {'value': res}
        return {'value':res, 'domain': {'officer_name': domain}}
    
    def onchange_get_officer_user(self, cr, uid, ids, user_input_id, context=None):
        
        if user_input_id == False:
            return {}
        
        obj = self.pool.get('res.users')
        user_id = obj.browse(cr, uid, [user_input_id], context=context)
        
        res = {}
        for p in user_id:
            res['receiver_bank']=p.receiver_bank
            res['receiver_name']=p.receiver_name
            res['receiver_bank_no']=p.receiver_bank_no
            res['thp']=p.thp


        return {'value':res}  
    
    def onchange_get_transferactual(self, cr, uid, ids, transfer_selection, context=None):
        print transfer_selection
        res ={} 
           
        tempObj = self.pool.get('pamsimas.transferactual').search(cr, uid, [('context_transfer', '=', transfer_selection)]) 
        print tempObj
        res['transfer_actual_ids']=tempObj
           
        return {'value':res} 
    
    
    def print_report(self, cr, uid, ids, context=None):
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'pamsimas.transfer',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pamsimas.report_transfer',
            'datas': datas,
        }

    def onchange_amandment(contract_amandment):
        res={}
        return res
        
    def _get_office(self, cr, uid, ids, field_name, arg, context=None):
        res ={}
        
        obj = self.pool.get('res.users')
        office_obj = obj.browse(cr, uid, uid, context=context)
        
        
        test = self.pool.get('res.users').browse(cr, uid, uid, context=context).office.detail
        #print test
        #print office_obj.office.detail
        
        for line in self.browse(cr, uid, ids, context):
                res[line.id] = office_obj.office.detail

        return res
    
    def test_button(self, cr, uid, ids, context=None):
        
        
        
        actual_selection = []
        contract_ids = self.pool.get('pamsimas.contract').search(cr, uid, [])
        for p in self.pool.get('pamsimas.contract').browse(cr, uid, contract_ids):
            actual_selection.append((0,0,{'id':p.id,
                                          'name':p.name
                              }))
        
        print actual_selection
        
        res = {}
        res['actualshow']= True
        return self.write(cr, uid, ids, {'actualshow': True}, context=context)
    
    def updateactual_transfer(self, cr, uid, ids, transfer_contract_ids, context=None): 
        
        #ini yang bikin dobel
        #self.pool.get('pamsimas.transfer').write(cr,uid,ids,{'transfer_contract_ids':transfer_contract_ids})
        
        
        tempContractItemID = self.pool.get('pamsimas.contract').search(cr, uid, [('contract_id','in',ids)])
        tempContractItemObj = self.pool.get('pamsimas.contract').browse(cr, uid, tempContractItemID)
        total = 0
        for o in tempContractItemObj:
            total = total + o.transfer_actual
        
        res ={}
        res['transfer_contract_ids']=transfer_contract_ids
        res['transfer_actual_received']=total
        
        return {'value':res} 
    
    
    
    
    
    _name   = 'pamsimas.transfer'
    _description = 'Pamsimas Transfer' 
    _order = 'state desc, date desc'
    _columns    = {
        'name'          : fields.char('No Bukti Transfer', size=128),
        'state'         : fields.selection([('draft','Not confirmed'),('confirmed','Confirmed'),('actual','Actual Confirmed')],'State',required=True,readonly=True, track_visibility='onchange'),
        
        'date'          : fields.date('Date'),
        'roms'          : fields.many2one('pamsimas.roms','Roms', ondelete='cascade'),
        'province'      : fields.many2one('pamsimas.province','Province', ondelete='cascade'),
        'city'          : fields.many2one('pamsimas.city','City', ondelete='cascade'),
        
        'position'      : fields.selection((('roms', 'Roms'), ('province','Province'), ('city','City/Kabupaten')),'Position'),
        'office'        : fields.many2one('pamsimas.regional', 'Office'),
        'officer_name'  : fields.many2one('res.users', 'Officer Name'),
        'thp'           : fields.float('Minimum THP', digits=(0,0)),
        
        'receiver_bank' : fields.char('Receiver Bank'),
        'receiver_bank_no'  : fields.char('Receiver Account Number'),
        'receiver_name'     : fields.char('Receiver Name'),
        'transfer_amount'   : fields.float('Transfer Amount', digits=(0,0)),
        
        'transfer_received_date'    : fields.date('Transfer Received Date'),
        'transfer_received' : fields.float('Total Received Amount', digits=(0,0)),
        'transfer_received_total'   : fields.float('Total Received Transfer', digits=(0,0)),
        
        'transfer_actual_received_date'    : fields.date('Actual Transfer Received Date'),
        'transfer_actual_received' : fields.float('Total Actual Expenditure Amount', digits=(0,0)),
        'transfer_actual_received_total'   : fields.float('Total Actual Transfer Received', digits=(0,0)),
        
        'contract_amandment'        : fields.many2one('pamsimas.contractamandment', 'Contract Amandment'),
        'transfer_contract_ids' : fields.one2many('pamsimas.contract','contract_id','Transfer Contract', ondelete='cascade'),
        'transfer_selection'        : fields.many2one('pamsimas.contract', 'Contract Item'),
        
        'description'   : fields.text('Description'),
        'sender_id'     : fields.char('Sender', invisible=True),
        
        'temp_office'   : fields.function(_get_office, string="temp office", type='char'),
        
        'transfer_actual_ids': fields.one2many('pamsimas.transferactual','transfer_actual_id', 'Transfer Actual Item', ondelete='cascade', invisible=True),
        #'transfer_actual_ids' : fields.many2many('pamsimas.transferactual','res_transferactual_rel','name','transfer_actual_id'),
        'transfer_bukubank' : fields.many2one('pamsimas.bukubank', 'Buku Bank', ondelete='cascade'),
        
        'actualshow' : fields.boolean('Actual Show'),
    }
    
    _defaults = {
        'state': 'draft',
        'sender_id':  lambda self, cr, uid, context: context.get('uid', False),
        'transfer_amount' : '',
        'actualshow' : False,
    }
    
    def transfer_confirm(self, cr, uid, ids, context=None):
        # set to "confirmed" state
        
        total_transfer_received = 0
        total_contract_received = 0
        
        for line1 in self.browse(cr, uid, ids, context):
            #print line1.transfer_received
            total_transfer_received = line1.transfer_received
            
            for line2 in line1.transfer_contract_ids:
                #print line2.received_contract_value
                total_contract_received += line2.received_contract_value

        if(total_transfer_received != total_contract_received):
            res = {}
            #return {'warning':{'title':'warning','message':'Negative margin on this line'}}
            raise osv.except_osv(("Warning"),("Adanya perbedaan jumlah antara Total Received Amount Confirmation dan Total Received Amount pada Contract"))
        else:
            return self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
 
    def transfer_confirm_actual(self, cr, uid, ids, context=None):
        # set to "confirmed" state
        
        total_actual_transfer_received = 0
        total_actual_contract_received = 0
        
        for line1 in self.browse(cr, uid, ids, context):
            #print line1.transfer_received
            total_actual_transfer_received = line1.transfer_actual_received
            
            for line2 in line1.transfer_contract_ids:
                #print line2.received_contract_value
                total_actual_contract_received += line2.transfer_actual

        if(total_actual_transfer_received != total_actual_contract_received):
            res = {}
            #return {'warning':{'title':'warning','message':'Negative margin on this line'}}
            raise osv.except_osv(("Warning"),("Adanya perbedaan jumlah antara Actual Total Received Amount Confirmation dan Actual Total Received Amount pada Contract"))
        else:
            return self.write(cr, uid, ids, {'state': 'actual'}, context=context)


class TransferActual(osv.osv):
    
    def update_total_value_transferactual(self, cr, uid, ids, total_budget, invoice_todate, context=None): 
        total = total_budget - invoice_todate
        
        res ={}
        res['invoice_remaining']=total
        self.pool.get('pamsimas.contractbaseline_item').write(cr, uid, ids, {'invoice_remaining':total}, context=context)
        
        return {'value':res} 
    
    _name   = 'pamsimas.transferactual'
    _description = 'Pamsimas Actual Transfer' 
    _rec_name = 'debit'
    _columns    = {
        'name'          : fields.char('Transaction Name', size=128),
        'date'          : fields.date('Date'),
        'debit'         : fields.float('Expenses', digits=(0,0)),
        'kredit'        : fields.float('Income', digits=(0,0), invisible='1'),
        
        'contract_transfer_actual_id'  : fields.many2one('pamsimas.contract', 'Actual Transfer', ondelete='cascade', invisible='1'),
        'transfer_actual_id' : fields.many2one('pamsimas.transfer', 'Actual Transfer', ondelete='cascade', invisible='1'),
        
        'context_transfer' : fields.char('Context', invisible='1'),
    }
    
    _defaults = {
        'context_transfer'         : lambda self, cr, uid, context: context.get('context_transfer', False),
    }
    
    
class Contract(osv.osv):
    def update_total_value(self, cr, uid, ids, quantity, contract_value, context=None): 
        total = 0
        if (quantity != False) and (quantity != False):
            total = quantity * contract_value
        res ={}
        res['contract_value_total']=total
        return {'value': res}
    
    def update_contract_detail(self, cr, uid, ids, in_name, context=None):
        
        
        contract_obj = self.pool.get("pamsimas.contractitem")
        contracts = contract_obj.browse(cr, uid, [in_name], context=context)
        res = {}
        for p in contracts:
            #print "====================",p.unit
            res['unit']=p.unit
            #if (p.name == 'Remunerasi'): 
            #    print "remunerasiiii"
        
        return {'value':res}
    
    def return_action_to_open(self, cr, uid, ids, context=None):
        res = {}
        total = 8888
        res['transfer_actual']=total
        print total
        return self.write(cr, uid, ids, {'transfer_actual': total}, context=context)
        
        
    def updateactual(self, cr, uid, ids, contract_transfer_actual_ids, context=None): 
        
        res ={}
        print contract_transfer_actual_ids
        
        
        tempTransActualID = self.pool.get('pamsimas.transferactual').search(cr, uid, [('contract_transfer_actual_id','in',ids)])
        tempTransActualObj = self.pool.get('pamsimas.transferactual').browse(cr, uid, tempTransActualID)
    
        print tempTransActualID
        print tempTransActualObj
    
        #self.pool.get('pamsimas.contract').unlink(cr, uid, tempTransActualID)
        #ini jg bikin duplikat
        #self.pool.get('pamsimas.contract').write(cr,uid,ids,{'contract_transfer_actual_ids':contract_transfer_actual_ids})
        
        total = 0
        for o in tempTransActualObj:
            #print o.debit
            total = total + o.debit
            #print total
            #print '==========='
            
            
        for o in contract_transfer_actual_ids:
            if(o[0] == 0):
                print o[2]['debit']
                total = total + o[2]['debit']
                
        print total
            
        
        
        self.pool.get('pamsimas.contract').write(cr, uid, ids,{'transfer_actual':total})
        
        res['transfer_actual']=total
        print 'totalnya' 
        print res['transfer_actual']
        
        return {'value':res}
    
    _name           = 'pamsimas.contract'
    _description    = 'Transaction Type'
    _rec_name = 'name'
    _columns         = {
        'name'          : fields.many2one('pamsimas.contractitem', 'Contract Type', ondelete='cascade'),
        'activity'      : fields.selection((('0',''),('1', 'Spot Checking Province to Disctict'), ('2', 'Spot Checking District to Village')), 'Activity'),
        'quantity'      : fields.integer('Quantity'),
        'unit'          : fields.char('Unit'),
        'contract_value': fields.float('Transfer Amount', digits=(0,0)),
        'received_contract_value' : fields.float('Received Amount', digits=(0,0)),
        'transfer_actual'   : fields.float('Expenditure Amount', digits=(0,0)),
        'contract_value_total': fields.float('Total Value', digits=(0,0)),
        'description'   : fields.text('Description'),
        'contract_id'  : fields.many2one('pamsimas.transfer', 'Contract', ondelete='cascade'),
        'contract_transfer_actual_ids': fields.one2many('pamsimas.transferactual','contract_transfer_actual_id','Transfer Actual Item', ondelete='cascade'),
        'contract_bukubank' : fields.many2one('pamsimas.bukubank', 'Buku Bank', ondelete='cascade'),
    }
    
    _defaults = {
        'activity': '0'
    }
    
class ContractItem(osv.osv):
    def update_detail(self, cr, uid, ids, detail_contract, detail_subcontract, context=None): 
        detail = ""
        if (detail_contract != False) and (detail_subcontract != False):
            detail = detail_contract + " - " + detail_subcontract
        if (detail_contract != False) and (detail_subcontract == False):
            detail = detail_contract     
        res ={}
        res['name']=detail
        return {'value': res}
    
    _name           = 'pamsimas.contractitem'
    _description    = 'Contract Type'
    _rec_name = 'name'
    _columns         = {
        'name'          : fields.char('Contract Name'),
        'contract'      : fields.char('Contract Type'),
        'subcontract'   : fields.char('Sub-Contract'),
        'unit'          : fields.char('Unit'),
        'read_only'     : fields.boolean('Read Only'),
        'description'   : fields.text('Description'),
        
        'contractitem_id'  : fields.many2one('pamsimas.contractamandment', 'Amandment', ondelete='set null'),
    }
    
class ContractAmandment(osv.osv):
    
    def _get_default_contractids(self, cr, uid, context=None):
        tempObj = self.pool.get('pamsimas.contractitem').search(cr, uid, [])
        return tempObj
    
    def refresh_data(self, cr, uid, ids, context=None):
        
        res = {}
        res['contract_many2many']=self.pool.get('pamsimas.contractitem').search(cr, uid, [])
            
        return {'value':res} 
    
    _name           = 'pamsimas.contractamandment'
    _description    = 'Contract Amandment'
    _columns         = {
        'name'          : fields.char('Contract Amandment Name', required = True),
        'date_start'    : fields.date('Amandment Start', required = True),
        'date_end'      : fields.date('Amandment End', required = True),
        'description'   : fields.text('Description'),
        'roms'          : fields.many2one('pamsimas.roms', 'Roms', required = True),
        'contract_many2many' : fields.many2many('pamsimas.contractitem','res_contractitem_rel','name','contractitem_id'),
    }
    
    _defaults = {
        'contract_many2many' : _get_default_contractids,
    }
    
class ContractBaseline(osv.osv):
    def test(self, cr, uid, ids, saldo_awal, context=None): 
        total = 0
        cummulative_total = saldo_awal
        
        
        tempBaselineItemID = self.pool.get('pamsimas.contractbaseline_item').search(cr, uid, [('contract_baseline_id','in',ids)])
        tempBaselineItemObj = self.pool.get('pamsimas.contractbaseline_item').browse(cr, uid, tempBaselineItemID)
        for o in tempBaselineItemObj:
            total = total + o.invoice_remaining
        
        res ={}
        res['saldo_akhir']=total
        res['cummulative_saldo_akhir']=cummulative_total - total
        return {'value':res} 
    
    _name           = 'pamsimas.contractbaseline'
    _description    = 'Contract Baseline'
    _columns         = {
        'name'              : fields.char('Contract Baseline Name', required = True),
        'roms'              : fields.many2one('pamsimas.roms', 'Roms', required = True),
        'date_start'        : fields.date('Date Start', required = True),
        'date_end'          : fields.date('Date End', required = True),
        'contract_baseline_ids': fields.one2many('pamsimas.contractbaseline_item','contract_baseline_id','Contract Baseline Item', ondelete='cascade'),
        'saldo_awal'        : fields.float('Previous Cumulative Amount', digits=(0,0)),
        'saldo_akhir'       : fields.float('Current Balance', digits=(0,0)),
        'cummulative_saldo_akhir' : fields.float('Cummulative Balance', digits=(0,0)),
    }
    
    
class ContractBaselineItem(osv.osv):
    def update_total_value_baseline(self, cr, uid, ids, total_budget, invoice_todate, context=None): 
        total = total_budget - invoice_todate
        
        res ={}
        res['invoice_remaining']=total
        self.pool.get('pamsimas.contractbaseline_item').write(cr, uid, ids, {'invoice_remaining':total}, context=context)
        
        return {'value':res} 
    
    _name           = 'pamsimas.contractbaseline_item'
    _description    = 'Contract Baseline Item'
    _columns         = {
        #'name'              : fields.many2one('pamsimas.contractitem', 'Contract', required = True),
        'name'          : fields.selection((('dutytravel', 'Duty Travel'), 
                                            ('officespace','Office Space'), 
                                            ('utilities','Utilities Expenses'),
                                            ('officeequipment','Office Equipment'),
                                            ('vehiclerental', 'Vehicle Rental'),
                                            ('communication', 'Communication')),'Contract', required = True),
        'total_budget'      : fields.float('Contract Allocation', digits=(0,0)),
        'invoice_todate'    : fields.float('Invoice Up to This Month', digits=(0,0)),
        'invoice_remaining'    : fields.float('Remaining Contract', digits=(0,0)),
        'contract_baseline_id' : fields.many2one('pamsimas.contractbaseline', 'Baseline Item', ondelete='set null'),
       
    }
    
class BukuBank(osv.osv):
    def _get_default_contractids(self, cr, uid, context=None):
        tempTransferObj = self.pool.get('pamsimas.transfer').search(cr, uid, [('officer_name.id','=',uid)])
        tempObj = self.pool.get('pamsimas.contract').search(cr, uid, [('contract_id','in',tempTransferObj)])
        
        res = {}
        obj = []
        
        transferObj = self.pool.get('pamsimas.transfer').browse(cr, uid, tempTransferObj)
        for o in transferObj:
            obj.append({'name':o.name, 'amount':o.transfer_received, 'type':'transfer'})
        
        contractObj = self.pool.get('pamsimas.contract').browse(cr, uid, tempObj)
        for p in contractObj:
            obj.append({'name':p.name, 'amount':p.received_contract_value, 'type':'contract'})
        
        
        return tempObj
    
    def _get_default_transferids(self, cr, uid, context=None):
        tempTransferObj = self.pool.get('pamsimas.transfer').search(cr, uid, [('officer_name.id','=',uid)])
        return tempTransferObj
    
    def _get_default_idbukubank(self, cr, uid, context=None):
        
        tempTransferObj = self.pool.get('pamsimas.transfer').search(cr, uid, [('officer_name.id','=',uid)])
        tempObj = self.pool.get('pamsimas.contract').search(cr, uid, [('contract_id','=',tempTransferObj)])
        
        return tempObj
    
    def refresh_data_bukubank(self, cr, uid, ids, context=None):
        tempTransferObj = self.pool.get('pamsimas.transfer').search(cr, uid, [('officer_name.id','=',uid)])
        print tempTransferObj
        
        tempObj = self.pool.get('pamsimas.contract').search(cr, uid, [('contract_id','=',tempTransferObj)])
        tempBrowse = self.pool.get('pamsimas.contract').browse(cr, uid, tempObj, context=context)
        #for o in tempBrowse:
        #    print o.contract_id
        
        #print tempObj
        
        #tempBb = self.pool.get('pamsimas.bukubank').search(cr, uid, [ids])
        #print tempBb
        
        #self.pool.get('pamsimas.bukubank').write(cr, uid, ids, {'transfer_contract_ids':tempBrowse}, context=context)
        self.pool.get('pamsimas.bukubank').write(cr, uid, ids, {'contract_id_bukubank':tempObj}, context=context)
        
        domain = [('id','in',tempObj)]
            
        return {'domain': {'transfer_contract_ids': domain}}
    
    _name           = 'pamsimas.bukubank'
    _description    = 'Buku Bank'
    _columns         = {
        'name'              : fields.char('Name'),
        'date_start'        : fields.date('Date Start', required = True),
        'date_end'          : fields.date('Date End', required = True),
        'transfer_contract_ids' : fields.one2many('pamsimas.contract','contract_bukubank','Contract', ondelete='cascade' ),
        #'transfer_contract_ids' : fields.many2many('pamsimas.contract','res_contract_rel','name','contract_id'),
        'transfer_ids'      : fields.one2many('pamsimas.transfer','transfer_bukubank', 'Transfer', ondelete='cascade'),
        'contract_id_bukubank'  : fields.char('pamsimas.contract'),
    }
    _defaults = {
        'transfer_contract_ids' : _get_default_contractids,
        'transfer_ids' : _get_default_transferids,
        'contract_id_bukubank' : _get_default_idbukubank,
    }
    
