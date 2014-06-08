import datetime
import time

from openerp import pooler
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _

from report_webkit import webkit_report


class report_transfer(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(report_transfer, self).__init__(cr, uid, name, context=context)
        self.transfer=False
        self.localcontext.update({'time'        : time, 
                                  'get_object':self._get_object,
                                  'get_transfer'    : self._get_transfer,
                                  })
    
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[])
        
        for o in obj_data:
            print o.name
            
        return obj_data
    
    def _get_transfer(self, form):
        lst = []
        vals = {}
        
        print form
        
        obj = self.pool.get('pamsimas.transfer')
        transfer_id = obj.search(self.cr, self.uid, [], context=self.localcontext)
        transfer = obj.browse(self.cr, self.uid, transfer_id, context=self.localcontext)
        
        for i in transfer:
            print i.name
        
        #qtys = 1

        #for i in range(1,6):
        #    if form['qty'+str(i)]!=0:
        #        vals['qty'+str(qtys)] = str(form['qty'+str(i)]) + ' units'
        #    qtys += 1
        #lst.append(vals)
        
        
        
        
        #pricelist = self.pool.get('pamsimas.transfer')
        return transfer
        

report_sxw.report_sxw('report.pamsimas.report_transfer', 
                      'pamsimas.transfer', 
                      'addons/pamsimas/report/pamsimas_regional_report.rml', 
                      parser=report_transfer)