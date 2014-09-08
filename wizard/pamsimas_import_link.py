from openerp.osv import fields, osv

class importlink(osv.osv_memory):
    
    def transfer_confirm(self, cr, uid, ids, context=None):
        # set to "confirmed" state
        print "WOOOOOOOOO"
        return {}
    
    def _get_default_url(self, cr, uid, context=None):
        url = "../img/input_format_final_roms1.xlsx"
        return url    
    
    _name           = 'pamsimas.importlink'
    _description    = 'Import Excel Link'
    _columns         = {
        'desc'              : fields.char('Untuk mendownload format import transfer, klik link di bawah berdasarkan roms masing-masing', readonly="True"),
        'import_urlR1'      : fields.char('Roms 1', help ="""Click the url to download the documents"""),
        'import_urlR2'      : fields.char('Roms 2', help ="""Click the url to download the documents"""),
        'import_urlR3'      : fields.char('Roms 3', help ="""Click the url to download the documents"""),
        'import_urlR4'      : fields.char('Roms 4', help ="""Click the url to download the documents"""),
        'import_urlR5'      : fields.char('Roms 5', help ="""Click the url to download the documents"""),
        'import_urlR6'      : fields.char('Roms 6', help ="""Click the url to download the documents"""),
        'import_urlR7'      : fields.char('Roms 7', help ="""Click the url to download the documents"""),
        'desc2'             : fields.char('Setelah mendownload file format tersebut, save kembali file tersebut ke dalam format .csv agar dapat di import', readonly="True"),
    }
    
    _defaults = {
        'import_urlR1'       : "http://localhost/smartsight/import%20format/input_format_final_roms1.xlsx",
        'import_urlR2'       : "http://localhost/smartsight/import%20format/input_format_final_roms2.xlsx",
        'import_urlR3'       : "http://localhost/smartsight/import%20format/input_format_final_roms3.xlsx",
        'import_urlR4'       : "http://localhost/smartsight/import%20format/input_format_final_roms4.xlsx",
        'import_urlR5'       : "http://localhost/smartsight/import%20format/input_format_final_roms5.xlsx",
        'import_urlR6'       : "http://localhost/smartsight/import%20format/input_format_final_roms6.xlsx",
        'import_urlR7'       : "http://localhost/smartsight/import%20format/input_format_final_roms7.xlsx",
    }
    