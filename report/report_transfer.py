import datetime
import time

from openerp.report import report_sxw
from report import report_sxw

from report_webkit import webkit_report

from osv import fields, osv

class report_transfer(report_sxw.rml_parse):
    _name = 'report.pamsimas.report_transfer'
    
    def __init__(self, cr, uid, name, context=None):
        super(report_transfer, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time, 
                                  'get_object' : self._get_object,})
    
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['form']['id']])
        return obj_data

report_sxw.report_sxw('report.pamsimas.report_transfer', 
                      'pamsimas.transfer', 
                      'addons/pamsimas/report/report_transfer.mako', 
                      parser=report_transfer)