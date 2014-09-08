{
    "name"  : "Pamsimas",
    "version"   : "1.0",
    "depends"   : ['base','web'],
    "author"    : "Ramanandha Pradana",
    "category"  : "Custom Application",
    "description"   : """
    Pamsimas Application            
    """,

    "data"      : ['security/pamsimas_security.xml',
                   'security/ir.model.access.csv',
                   'pamsimas_workflow.xml',
                   'wizard/pamsimas_transfer_confirmation.xml',
                   'wizard/pamsimas_regional_report.xml',
                   'wizard/pamsimas_firm_report.xml',
                   'wizard/pamsimas_pmu_report.xml',
                   'wizard/pamsimas_import_link.xml',
                   'wizard/pamsimas_bank_report.xml',
                   'pamsimas_view.xml'],
    "css" : [
        'static/src/css/modified_theme.css',
    ],
    "js" : [
        'static/src/js/modified_theme.js',
    ],
    "qweb" : [
        'static/src/xml/modified_theme.xml',
    ],
    "demo"      : [],
    "installable"   : True,
    "auto_install"  : False,

}
