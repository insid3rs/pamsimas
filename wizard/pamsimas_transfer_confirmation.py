from openerp.osv import fields, osv

class transferConfirmation(osv.osv_memory):
    
    def confirm_transaction(self, cr, uid, ids, context=None): 
        wizard_obj = self.browse(cr, uid, ids[0], context=context)
        wizard_id = [wizard_obj.transfer_id]
        #print wizard_id[0]
        
        transfer_obj = self.pool.get('pamsimas.transfer')
        
        #print wizard_obj.transfer_received
        #print wizard_obj.transfer_contract_ids
        
        transfer_obj.write(cr, uid, wizard_id, {'transfer_received_date' :  wizard_obj.transfer_received_date, 
                                                'transfer_received' : wizard_obj.transfer_received, 
                                                'state': 'confirmed'
                                                }, context)
        return {}
    
    def transfer_confirm(self, cr, uid, ids, context=None):
        # set to "confirmed" state
        print "WOOOOOOOOO"
        return {}
    
    _name = 'pamsimas.transferconfirmation'
    _description = 'Transfer Confirmation'
    _columns = {
        'transfer_id'   : fields.char('Transfer ID'),
        'name'          : fields.char('No Bukti Transfer', size=128, required = True),
        'state'         : fields.selection([('draft','Not confirmed'),('confirmed','Confirmed')],'State',required=True,readonly=True),
        
        'date'          : fields.date('Date'),
        'roms'          : fields.many2one('pamsimas.roms','Roms', ondelete='cascade'),
        'province'      : fields.many2one('pamsimas.province','Province', ondelete='cascade'),
        'city'          : fields.many2one('pamsimas.city','City', ondelete='cascade'),
        
        'position'      : fields.selection((('roms', 'Roms'), ('province','Province'), ('city','City/Kabupaten')),'Position'),
        'office'        : fields.many2one('pamsimas.regional', 'Office'),
        
        'receiver_bank' : fields.char('Receiver Bank', size=128, required = True),
        'receiver_bank_no': fields.char('Receiver Account Number', size=128, required = True),
        'receiver_name' : fields.char('Receiver Name', size=128),
        
        'transfer_received_date' : fields.date('Transfer Received Date'),
        'transfer_received' : fields.char('Transfer Received'),
        
        
        'transfer_contract_ids'  : fields.one2many('pamsimas.contract','contract_id','Transfer Contract'),
        
        'description'   : fields.text('Description'),
    }
    
    _defaults = {
    'transfer_id'       : lambda self, cr, uid, context: context.get('transfer_id', False),
    'name'              : lambda self, cr, uid, context: context.get('name', False),
    'state'             : lambda self, cr, uid, context: context.get('state', False),
    'date'              : lambda self, cr, uid, context: context.get('date', False),
    'position'          : lambda self, cr, uid, context: context.get('position', False),
    'office'            : lambda self, cr, uid, context: context.get('office', False),
    'receiver_bank'     : lambda self, cr, uid, context: context.get('receiver_bank', False),
    'receiver_bank_no'  : lambda self, cr, uid, context: context.get('receiver_bank_no', False),
    'receiver_name'     : lambda self, cr, uid, context: context.get('receiver_name', False),
    'transfer_contract_ids' : lambda self, cr, uid, context: context.get('transfer_contract_ids', False)
    }
    