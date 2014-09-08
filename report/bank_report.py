import datetime
import time

from openerp import pooler
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _

from report_webkit import webkit_report


class bank_report_transfer(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(bank_report_transfer, self).__init__(cr, uid, name, context=context)
        self.transfer=False
        self.localcontext.update({'time'                : time, 
                                  'get_object'          :self._get_object,
                                  'get_transfer'        : self._get_transfer,
                                  'get_total_transfer'  : self._get_total_transfer,
                                  'get_total_received'  : self._get_total_received,
                                  })
    
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[])
        
        #for o in obj_data:
        #    print o.name
            
        return obj_data
    
    def _get_transfer(self, form):
        
        obj = self.pool.get('pamsimas.transfer')
        
        print form['status']
        print form['officer_name']
        print form['periode_start']
        
        domain_status = (1,'=',1)
        domain_officer = (1,'=',1)
        domain_periodestart = (1,'=',1)
        domain_periodestop = (1,'=',1)
        
        if(form['status'] != False):
            domain_status = ('state', '=', form['status'])
        
        if(form['periode_start'] != False):
            domain_periodestart = ('date', '>=', form['periode_start'])
            
        if(form['periode_stop'] != False):
            domain_periodestop = ('date', '<=', form['periode_stop'])    
        
        if(form['officer_name'] != False):
            domain_officer = ('officer_name', '=', form['officer_name'][0])
        
        if ((form['status'] == False) & (form['officer_name'] == False) & (form['periode_start'] == False) & (form['periode_stop'] == False)):
            transfer_id = obj.search(self.cr, self.uid, [], context=self.localcontext)
        else:
            transfer_id = obj.search(self.cr, self.uid, [domain_status,domain_officer,domain_periodestart,domain_periodestop], context=self.localcontext)        
        
        transfer = obj.browse(self.cr, self.uid, transfer_id, context=self.localcontext)
        
        return transfer
    
    def _get_total_transfer(self, form):
        obj = self.pool.get('pamsimas.transfer')
        
        
        domain_status = (1,'=',1)
        domain_officer = (1,'=',1)
        domain_periodestart = (1,'=',1)
        domain_periodestop = (1,'=',1)
        
        if(form['status'] != False):
            domain_status = ('state', '=', form['status'])
        
        if(form['periode_start'] != False):
            domain_periodestart = ('date', '>=', form['periode_start'])
            
        if(form['periode_stop'] != False):
            domain_periodestop = ('date', '<=', form['periode_stop'])    
        
        if(form['officer_name'] != False):
            domain_officer = ('officer_name', '=', form['officer_name'][0])
        
        if ((form['status'] == False) & (form['officer_name'] == False) & (form['periode_start'] == False) & (form['periode_stop'] == False)):
            transfer_id = obj.search(self.cr, self.uid, [], context=self.localcontext)
        else:
            transfer_id = obj.search(self.cr, self.uid, [domain_status,domain_officer,domain_periodestart,domain_periodestop], context=self.localcontext)        
        
        transfer = obj.browse(self.cr, self.uid, transfer_id, context=self.localcontext)
        
        total_received = 0
        
        for i in transfer:
            #print i.transfer_received
            total_received += i.transfer_amount
        
        return total_received
    
    def _get_total_received(self, form):
        obj = self.pool.get('pamsimas.transfer')
        
        
        domain_status = (1,'=',1)
        domain_officer = (1,'=',1)
        domain_periodestart = (1,'=',1)
        domain_periodestop = (1,'=',1)
        
        if(form['status'] != False):
            domain_status = ('state', '=', form['status'])
        
        if(form['periode_start'] != False):
            domain_periodestart = ('date', '>=', form['periode_start'])
            
        if(form['periode_stop'] != False):
            domain_periodestop = ('date', '<=', form['periode_stop'])    
        
        if(form['officer_name'] != False):
            domain_officer = ('officer_name', '=', form['officer_name'][0])
        
        if ((form['status'] == False) & (form['officer_name'] == False) & (form['periode_start'] == False) & (form['periode_stop'] == False)):
            transfer_id = obj.search(self.cr, self.uid, [], context=self.localcontext)
        else:
            transfer_id = obj.search(self.cr, self.uid, [domain_status,domain_officer,domain_periodestart,domain_periodestop], context=self.localcontext)        
        
        transfer = obj.browse(self.cr, self.uid, transfer_id, context=self.localcontext)
        
        total_received = 0
        
        for i in transfer:
            #print i.transfer_received
            total_received += i.transfer_received
        
        return total_received

report_sxw.report_sxw('report.pamsimas.bank_report_transfer', 
                      'pamsimas.transfer', 
                      'addons/pamsimas/report/pamsimas_bank_report.rml', 
                      parser=bank_report_transfer, 
                      header=False)