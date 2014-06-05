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
        #'user_type'    : fields.selection((('pmu', 'PMU'), ('firm','Firm'), ('regional','Regional')),'User Type', required = True),
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
    
    _name   = 'pamsimas.transfer'
    _description = 'Pamsimas Transfer' 
    _order = 'state desc, date desc'
    _columns    = {
        'name'          : fields.char('No Bukti Transfer', size=128, required = True),
        'state'         : fields.selection([('draft','Not confirmed'),('confirmed','Confirmed')],'State',required=True,readonly=True, track_visibility='onchange'),
        
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
        'transfer_received' : fields.float('Received Amount', digits=(0,0)),
        'transfer_received_total'   : fields.float('Total Received Transfer', digits=(0,0)),
        
        'transfer_contract_ids'  : fields.one2many('pamsimas.contract','contract_id','Transfer Contract', ondelete='cascade'),
        
        'description'   : fields.text('Description'),
        'sender_id'     : fields.char('Sender', invisible=True),
        
        'temp_office'   : fields.function(_get_office, string="temp office", type='char')
    }
    
    _defaults = {
        'state': 'draft',
        'sender_id':  lambda self, cr, uid, context: context.get('uid', False),
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
            #    print "masuuuk"
        
        return {'value':res}
    
    _name           = 'pamsimas.contract'
    _description    = 'Transaction Type'
    _columns         = {
        'name'          : fields.many2one('pamsimas.contractitem', 'Contract Type', ondelete='cascade'),
        'activity'      : fields.selection((('0',''),('1', 'Spot Checking Province to Disctict'), ('2', 'Spot Checking District to Village')), 'Activity'),
        'quantity'      : fields.integer('Quantity'),
        'unit'          : fields.char('Unit'),
        'contract_value': fields.float('Contract Value', digits=(0,0)),
        'received_contract_value' : fields.float('Received Amount', digits=(0,0)),
        'contract_value_total': fields.float('Total Value', digits=(0,0)),
        'description'   : fields.text('Description'),
        'contract_id'  : fields.many2one('pamsimas.transfer', 'Contract', ondelete='cascade'),
        #'contract_id'  : fields.many2one('pamsimas.transferconfirmation', 'Contract'),
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
    _columns         = {
        'name'          : fields.char('Contract Name'),
        'contract'      : fields.char('Contract Type'),
        'subcontract'   : fields.char('Sub-Contract'),
        'unit'          : fields.char('Unit'),
        'read_only'     : fields.boolean('Read Only'),
        'description'   : fields.text('Description'),
        
    }
