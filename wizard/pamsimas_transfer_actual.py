#<button name="%(action_pamsimas_transfer_actual)d"  type="action"  icon="gtk-ok"  context="{'transfer_id': active_id, 'transfer_actual':transfer_actual,'name':name}"/>
from openerp.osv import fields, osv

class TempTransferActual(osv.osv_memory):
    
    def confirm_transaction(self, cr, uid, ids, context=None): 
        wizard_obj = self.browse(cr, uid, ids[0], context=contecontract_transfer_actual_idxt)
        wizard_id = [wizard_obj.contract_transfer_actual_ids]
        print [wizard_obj.transfer_id]
        print wizard_id
        print 'oi2'
        #transfer_obj = self.pool.get('pamsimas.transfer')
        contract_obj = self.pool.get('pamsimas.contract')
        #contracts = contract_obj.browse(cr, uid, context_id, context=context)
        
        #print wizard_obj.transfer_received
        #print wizard_obj.transfer_contract_ids
        
        #contract_obj.write(cr, uid, wizard_id, {'contract_transfer_actual_ids' :  wizard_obj.contract_transfer_actual_ids
        #                                        }, context)
        return {}
    
    def transfer_confirm(self, cr, uid, ids, context=None):
        # set to "confirmed" state
        print "WOOOOOOOOO"
        return {}
    
    def refresh_data(self, cr, uid, ids, context=None):
        wizard_obj = self.browse(cr, uid, ids[0], context=context)
        wizard_id = wizard_obj.transfer_id
        print wizard_id   
        print wizard_obj.contract_transfer_actual_ids
            
        contract_data = [{'name': t.name, 'debit': t.debit, 'contract_transfer_actual_id':wizard_id}
                        for t in wizard_obj.contract_transfer_actual_ids]
        
        print contract_data
        contract_obj = self.pool.get('pamsimas.contract')
        
        print wizard_id
        contract_obj.write(cr, uid, wizard_id,{'contract_transfer_actual_ids': [(0, 0, data) for data in contract_data]},context)
        
        return {False} 
    
    def _get_active_sessions(self, cr, uid, context):
        if context.get('active_model') == 'pamsimas.contract':
            temp_active_id = context.get('active_ids', False)
            return temp_active_id[0]
        return False
        
    def _get_transfer_actual_ids(self, cr, uid, context):
        if context.get('active_model') == 'pamsimas.contract':
            context_id = context.get('active_ids', False)
            print context_id
            
            tempObj = self.pool.get('pamsimas.transferactual').search(cr, uid, [])
            
            contract_obj = self.pool.get('pamsimas.contract')
            
            #contracts = contract_obj.browse(cr, uid, context_id, context=context)
            #for p in contracts:
            #    print "====================",p.contract_transfer_actual_ids
            #    print 'oi'
            #    #print contracts.contract_transfer_actual_ids
            #    return p.contract_transfer_actual_ids
            
            return tempObj
        return False
        
    
    _name = 'pamsimas.temptransferactual'
    _description = 'Temporary Transfer Actual'
    _columns = {
        'transfer_id'   : fields.integer('Transfer ID'),
        'contract_transfer_actual_ids': fields.one2many('pamsimas.transferactual','contract_transfer_actual_id','Transfer Actual Item', ondelete='set null'),
        'transfer_actual'   : fields.float('Expenditure Amount', digits=(0,0)),
        'name'          : fields.many2one('pamsimas.contractitem', 'Contract Type', ondelete='cascade'),
        
    }
    
    _defaults = {
        #'transfer_id'           : lambda self, cr, uid, context: context.get('transfer_id', False),
        'transfer_id'             : _get_active_sessions,
        'transfer_actual'         : lambda self, cr, uid, context: context.get('transfer_actual', False),
        'name'  : lambda self, cr, uid, context: context.get('name', False),
        'contract_transfer_actual_ids' : _get_transfer_actual_ids,
        #'contract_transfer_actual_ids' : lambda self, cr, uid, context: context.get('contract_transfer_actual_idss', []),
    }
    
    
    
    
    