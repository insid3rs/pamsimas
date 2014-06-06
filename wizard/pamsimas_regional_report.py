from openerp.osv import fields, osv

class pamsimas_regional_report(osv.osv_memory):
    
    _name = "pamsimas.regional.report"
    _description = "Regional User Report"
    
    _columns = {
        'receiver_name' : fields.char('FullName'),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}
        
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['name'], context=context)
        res = res and res[0] or {}
        res['name'] = res['name'][0]
        
        datas['form'] = res
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pamsimas.report_transfer',
            'datas': datas,
       }
        
        #datas = {
        #     'ids': context.get('active_ids',[]),
        #     'model': 'pamsimas.transfer',
        #     'form': self.read(cr, uid, ids[0], context=context)
        #}
        #return {
        #    'type': 'ir.actions.report.xml',
        #    'report_name': 'pamsimas.report_transfer',
        #    'datas': datas,
        #}

pamsimas_regional_report()
    
    
