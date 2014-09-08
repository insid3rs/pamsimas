from openerp.osv import fields, osv

class pamsimas_firm_report(osv.osv_memory):
    
    def onchange_get_office(self, cr, uid, ids, position, context=None):
        
        office = []
        
        obj = self.pool.get('pamsimas.regional')
        office_id = obj.search(cr, uid, [], context=context)
        offices = obj.browse(cr, uid, office_id, context=context)
        
        res ={} 
        res['office'] = 0
        
        username = self.pool.get('res.users').browse(cr,uid,uid).name
            
        if position == "roms":
            domain = [('roms','=',username),('province','=',False),('city','=',False)]
        if position == "province":
            domain = [('roms','=',username),('province','!=',False),('city','=',False)]
        if position == "city":
            domain = [('roms','=',username),('province','!=',False),('city','!=',False)]
            
        return {'value':res, 'domain': {'office': domain}} 
    
    def onchange_get_officer(self, cr, uid, ids, office_id, context=None):
        
        if office_id == False:
            return {}
        
        obj = self.pool.get('res.users')
        user_id = obj.search(cr, uid, [], context=context)
        users = obj.browse(cr, uid, user_id, context=context)
        
        res ={} 
        res['officer_name'] = 0
        
        domain = [('office','=',office_id)]
        
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
    
    
    _name = "pamsimas.firm.report"
    _description = "Firm User Report"
    
    _columns = {
        'name'          : fields.char('Name'),
        'transfer'      : fields.many2one('pamsimas.transfer', 'Transfer List'),
        'status'        : fields.selection((('confirmed', 'Confirmed'), ('draft','Not Confirmed')),'Status'),        
        'periode_start' : fields.date('Periode Start'),
        'periode_stop'  : fields.date('Periode Stop'),
        'total_transfer': fields.float('Total', digits=(0,0)),
        'total_received': fields.float('Total', digits=(0,0)),
        
        'position'      : fields.selection((('roms', 'Roms'), ('province','Province'), ('city','City/Kabupaten')),'Position'),
        'office'        : fields.many2one('pamsimas.regional', 'Office'),
        'officer_name'  : fields.many2one('res.users', 'Officer Name'),
    }
    
    _defaults = {
        'total_transfer' : 0,
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}
            
        datas = {'ids': context.get('active_ids', []),
                 'model' : 'pamsimas.transfer'}
        res = self.read(cr, uid, ids, ['name','transfer','status','periode_start','periode_stop','total_transfer','total_received','position','office','officer_name'], context=context)
        res = res and res[0] or {}
        res['transfer'] = res['transfer']
        datas['form'] = res
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pamsimas.firm_report_transfer',
            'datas': datas,
       }
        

pamsimas_firm_report()
    
    
