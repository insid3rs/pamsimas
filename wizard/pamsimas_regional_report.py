from openerp.osv import fields, osv

class pamsimas_regional_report(osv.osv_memory):
    
    _name = "pamsimas.regional.report"
    _description = "Regional User Report"
    
    _columns = {
        'name'          : fields.char('Name'),
        'transfer'      : fields.many2one('pamsimas.transfer', 'Transfer List'),
        'status'        : fields.selection((('confirmed', 'Confirmed'), ('draft','Not Confirmed')),'Status'),        
        'periode_start' : fields.date('Periode Start'),
        'periode_stop'  : fields.date('Periode Stop'),
        'total_transfer': fields.float('Total', digits=(0,0)),
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
        res = self.read(cr, uid, ids, ['name','transfer','status','periode_start','periode_stop','total_transfer'], context=context)
        res = res and res[0] or {}
        res['transfer'] = res['transfer']
        res['total_transfer'] = res['total_transfer']
        datas['form'] = res
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pamsimas.regional_report_transfer',
            'datas': datas,
       }
        
        
        
        #datas = {
        #     'ids': [],
        #     'model': 'pamsimas.transfer',
        #     'form': self.read(cr, uid, ids[0], context=context)
        #}
        #return {
        #    'type': 'ir.actions.report.xml',
        #    'report_name': 'pamsimas.report_transfer',
        #    'datas': datas,
        #}

pamsimas_regional_report()
    
    
