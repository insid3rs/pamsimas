from openerp.osv import osv, fields

class Firm(osv.osv):
    _name   = 'pamsimas.firm'
    _description = 'Pamsimas Firm'
    _columns    = {
        'name'          : fields.char('Firm', size=128, required = True),
        'description'   : fields.text('Description'),
        
    }

class RegionalUser(osv.osv):
    _name           = 'pamsimas.regionaluser'
    _description    = 'Regional User'
    _columns         = {
        'name'          : fields.char('User', size=128, required = True),
        'position'      : fields.char('Position', size=128, required = True),
        'roms'          : fields.char('ROMS', size=128, required = True),
        'office_code'   : fields.char('Office Code', size=128, required = True),
        'description'   : fields.text('Description'),
    }

class Position(osv.osv):
    _name   = 'pamsimas.position'
    _description = 'Position'
    _columns    = {
        'name'          : fields.char('Position', size=128, required = True),
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
        'description'   : fields.text('Description'),
    }
    
class City(osv.osv):
    _name           = 'pamsimas.city'
    _description    = 'Province'
    _columns         = {
        'name'          : fields.char('City/Kabupaten', size=128, required = True),
        'description'   : fields.text('Description'),
    }

class Contract(osv.osv):
    _name           = 'pamsimas.contract'
    _description    = 'Transaction Type'
    _columns         = {
        'name'          : fields.char('Contract Type', size=128, required = True),
        'description'   : fields.text('Description'),
    }
    
class Transfer(osv.osv):
    _name   = 'pamsimas.transfer'
    _description = 'Pamsimas Transfer'
    _columns    = {
        'name'          : fields.char('Transfer', size=128, required = True),
        'description'   : fields.text('Description'),
        
    }
    
class TransferConfirmation(osv.osv):
    _name   = 'pamsimas.transferconfirmation'
    _description = 'Pamsimas Transfer Confirmation'
    _columns    = {
        'name'          : fields.char('Transfer Confirmation', size=128, required = True),
        'description'   : fields.text('Description'),
        
    }


