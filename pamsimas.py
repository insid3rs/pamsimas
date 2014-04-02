from openerp.osv import osv, fields

class Firm(osv.osv):
    _name   = 'pamsimas.firm'
    _description = 'Pamsimas Firm'
    _columns    = {
        'name'          : fields.char('Firm', size=128, required = True),
        'roms'          : fields.char('ROMS', size=128, required = True),
        'description'   : fields.text('Description'),
        
    }

class RegionalUser(osv.osv):
    _name           = 'pamsimas.regionaluser'
    _description    = 'Regional User'
    _columns         = {
        'name'          : fields.char('User', size=128, required = True),
        'roms'          : fields.char('ROMS', size=128, required = True),
        'province'      : fields.char('Province', size=128, required = True),
        'city'          : fields.char('City', size=128, required = True),
        'description'   : fields.text('Description'),
    }

class ROMS(osv.osv):
    _name           = 'pamsimas.roms'
    _description    = 'ROMS'
    _columns         = {
        'name'          : fields.char('ROMS', size=128, required = True),
        'description'   : fields.text('Description'),
    }
    
class Province(osv.osv):
    _name           = 'pamsimas.province'
    _description    = 'Province'
    _columns         = {
        'name'          : fields.char('Province', size=128, required = True),
        'roms'          : fields.many2one('pamsimas.roms','Roms', ondelete='cascade'),
        'description'   : fields.text('Description'),
    }
    
class City(osv.osv):
    _name           = 'pamsimas.city'
    _description    = 'Province'
    _columns         = {
        'name'          : fields.char('City/Kabupaten', size=128, required = True),
        'roms'          : fields.many2one('pamsimas.roms','Roms', ondelete='cascade'),
        'province'      : fields.many2one('pamsimas.province','Province', ondelete='cascade'),
        'description'   : fields.text('Description'),
    }

class Contract(osv.osv):
    _name           = 'pamsimas.contract'
    _description    = 'Transaction Type'
    _columns         = {
        'name'          : fields.char('Contract Type', size=128, required = True),
        'subcontract'   : fields.char('Sub-Contract', size=128),
        'contract_value': fields.char('Contract Value', size=128),
        'contract_value_alocated' : fields.char('Alocated Fund', size=128),
        'description'   : fields.text('Description'),
        'contract_ids'  : fields.many2many('pamsimas.transferconfirmation','transfer_contract_rel', 'transfer_contract_ids', 'contract_ids',  'Transfer Contract'),
        
    }
    
class Transfer(osv.osv):
    _name   = 'pamsimas.transfer'
    _description = 'Pamsimas Transfer'
    _columns    = {
        'name'          : fields.char('Transfer', size=128, required = True),
        'no_bukti_transfer' : fields.char('No Bukti Transfer', size=128, required = True),
        'date'          : fields.date('Date'),
        'roms'          : fields.many2one('pamsimas.roms','Roms', ondelete='cascade'),
        'province'      : fields.many2one('pamsimas.province','Province', ondelete='cascade'),
        'city'          : fields.many2one('pamsimas.city','City', ondelete='cascade'),
        
        'period'        : fields.date('Period of Transaction'),
        'receiver_bank' : fields.char('Receiver Bank', size=128, required = True),
        'receiver_bank_no': fields.char('Receiver Account Number', size=128, required = True),
        'receiver_name' : fields.char('Receiver Name', size=128, required = True),
        'transfer_amount' : fields.char('Transfer Amount', size=128, required = True),
        'description'   : fields.text('Description'),
        
    }
    
class TransferConfirmation(osv.osv):
    _name   = 'pamsimas.transferconfirmation'
    _description = 'Pamsimas Transfer Confirmation'
    _columns    = {
        'name'          : fields.char('Transfer', size=128, required = True),
        'no_bukti_transfer' : fields.char('No Bukti Transfer', size=128, required = True),
        'date'          : fields.date('Date'),
        'roms'          : fields.many2one('pamsimas.roms','Roms', ondelete='cascade'),
        'province'      : fields.many2one('pamsimas.province','Province', ondelete='cascade'),
        'city'          : fields.many2one('pamsimas.city','City', ondelete='cascade'),
        
        'period'        : fields.date('Period of Transaction'),
        'receiver_bank' : fields.char('Receiver Bank', size=128, required = True),
        'receiver_bank_no': fields.char('Receiver Account Number', size=128, required = True),
        'receiver_name' : fields.char('Receiver Name', size=128, required = True),
        'transfer_received_date' : fields.date('Transfer Received Date'),
        'transfer_received' : fields.char('Transfer Received', size=128, required = True),
        
        'transfer_contract_ids'  : fields.many2many('pamsimas.contract','transfer_contract_rel', 'contract_ids', 'transfer_contract_ids', 'Transfer Contract'),
        'contract_value_alocated' : fields.char('Alocated Fund', size=128, required = True),
        
    }


