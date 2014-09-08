from openerp.osv import fields, osv

class pamsimas_bank_report(osv.osv_memory):
    
    
    _name = "pamsimas.bank.report"
    _description = "Bank Report"
    
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
        
        print datas
        
        #return {
        #    'type': 'ir.actions.report.xml',
        #    'report_name': 'pamsimas.bank_report',
        #    'datas': datas,
        #}
        
        return True

pamsimas_bank_report()
    
    
