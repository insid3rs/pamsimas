import datetime
import time

from openerp import pooler
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _

from report_webkit import webkit_report


class firm_report_transfer(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(firm_report_transfer, self).__init__(cr, uid, name, context=context)
        self.transfer=False
        self.localcontext.update({'time'        : time, 
                                  'get_object':self._get_object,
                                  'get_transfer'    : self._get_transfer,
                                  'get_total_transfer' : self._get_total_transfer,
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
        
        if ((form['status'] != False) & (form['officer_name'] != False)): 
            if (form['status'] == 'confirmed'):
                transfer_id = obj.search(self.cr, self.uid, ['&',('state', '=', 'confirmed'),('officer_name', '=', form['officer_name'][0])], context=self.localcontext)
            if (form['status'] == 'draft'):
                transfer_id = obj.search(self.cr, self.uid, ['&',('state', '=', 'draft'),('officer_name', '=', form['officer_name'][0])], context=self.localcontext)
        if ((form['status'] != False) & (form['officer_name'] == False)):
            print "masuk"
            if (form['status'] == 'confirmed'):
                transfer_id = obj.search(self.cr, self.uid, [('state', '=', 'confirmed')], context=self.localcontext)
            if (form['status'] == 'draft'):
                transfer_id = obj.search(self.cr, self.uid, [('state', '=', 'draft')], context=self.localcontext)
        if ((form['status'] == False) & (form['officer_name'] != False)):
            transfer_id = obj.search(self.cr, self.uid, [('officer_name', '=', form['officer_name'][0])], context=self.localcontext)
        if ((form['status'] == False) & (form['officer_name'] == False)):
            transfer_id = obj.search(self.cr, self.uid, [], context=self.localcontext)
                
        transfer = obj.browse(self.cr, self.uid, transfer_id, context=self.localcontext)
         
        return transfer
    
    def _get_total_transfer(self, form):
        obj = self.pool.get('pamsimas.transfer')
        
        print form['status']
        print form['officer_name']
        
        if ((form['status'] != False) & (form['officer_name'] != False)): 
            if (form['status'] == 'confirmed'):
                transfer_id = obj.search(self.cr, self.uid, ['&',('state', '=', 'confirmed'),('officer_name', '=', form['officer_name'][0])], context=self.localcontext)
            if (form['status'] == 'draft'):
                transfer_id = obj.search(self.cr, self.uid, ['&',('state', '=', 'draft'),('officer_name', '=', form['officer_name'][0])], context=self.localcontext)
        if ((form['status'] != False) & (form['officer_name'] == False)):
            print "masuk"
            if (form['status'] == 'confirmed'):
                transfer_id = obj.search(self.cr, self.uid, [('state', '=', 'confirmed')], context=self.localcontext)
            if (form['status'] == 'draft'):
                transfer_id = obj.search(self.cr, self.uid, [('state', '=', 'draft')], context=self.localcontext)
        if ((form['status'] == False) & (form['officer_name'] != False)):
            transfer_id = obj.search(self.cr, self.uid, [('officer_name', '=', form['officer_name'][0])], context=self.localcontext)
        if ((form['status'] == False) & (form['officer_name'] == False)):
            transfer_id = obj.search(self.cr, self.uid, [], context=self.localcontext)
                
        transfer = obj.browse(self.cr, self.uid, transfer_id, context=self.localcontext)
        
        total_received = 0
        
        for i in transfer:
            #print i.transfer_received
            total_received += i.transfer_received
        
        return total_received
        

report_sxw.report_sxw('report.pamsimas.firm_report_transfer', 
                      'pamsimas.transfer', 
                      'addons/pamsimas/report/pamsimas_firm_report.rml', 
                      parser=firm_report_transfer, 
                      header=False)