# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from lxml import etree
import StringIO
import cStringIO
import base64
from datetime import datetime
import os
import re
import time
from interface import report_rml
import preprocess
import logging
import openerp.pooler as pooler
import openerp.tools as tools
import zipfile
import common
from ctypes import *
import copy
import subprocess
import tempfile
import inspect
from openerp.osv.fields import float as float_field, function as function_field, datetime as datetime_field
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


_logger = logging.getLogger(__name__)


rml_parents = {
    'tr':1,
    'li':1,
    'story': 0,
    'section': 0
}

rml_tag="para"

sxw_parents = {
    'table-row': 1,
    'list-item': 1,
    'body': 0,
    'section': 0,
}

html_parents = {
    'tr' : 1,
    'body' : 0,
    'div' : 0
    }
sxw_tag = "p"

rml2sxw = {
    'para': 'p',
}

def convert_sxw_odt_2_pdf(stream,input_ext,output_ext):
    # Save stream to a temp file.
    f1 = tempfile.NamedTemporaryFile(suffix = '.%s' % input_ext, delete=False)
    f1.write(stream)
    f1.flush()
    f1_name = f1.name
    f1.close()

    # Pdf output file name.
    f2_name = f1_name + '.' + output_ext
    
    # Call documentconverter script.
    if os.name == 'nt':
        p = subprocess.Popen('"%s\\LibreOffice 3.6\\program\\python.exe" "%s\\documentconverter.py" "%s" %s "%s" pdf' % (
            os.environ["ProgramFiles"], 
            os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
            f1_name,
            input_ext,
            f2_name), shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        p = subprocess.Popen('python %s/documentconverter.py %s %s %s pdf' % (
            os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),
            f1_name,
            input_ext,
            f2_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print line,
    if (p.wait() != 0):
        raise Exception('Failed to convert the %s file to pdf.' % input_ext)

    # Read output file.
    f2_file = open(f2_name, "rb")
    res=f2_file.read()
    f2_file.close()

    # Delete temp file.
    os.remove(f1_name)
    os.remove(f2_name)

    # Return content of the output file which is the pdf file.
    return res

def get_date_length(date_format=DEFAULT_SERVER_DATE_FORMAT):
    return len((datetime.now()).strftime(date_format))

class _format(object):
    def set_value(self, cr, uid, name, object, field, lang_obj):
        self.object = object
        self._field = field
        self.name = name
        self.lang_obj = lang_obj

class _float_format(float, _format):
    def __init__(self,value):
        super(_float_format, self).__init__()
        self.val = value or 0.0

    def __str__(self):
        digits = 2
        if hasattr(self,'_field') and getattr(self._field, 'digits', None):
            digits = self._field.digits[1]
        if hasattr(self, 'lang_obj'):
            return self.lang_obj.format('%.' + str(digits) + 'f', self.name, True)
        return str(self.val)

class _int_format(int, _format):
    def __init__(self,value):
        super(_int_format, self).__init__()
        self.val = value or 0

    def __str__(self):
        if hasattr(self,'lang_obj'):
            return self.lang_obj.format('%.d', self.name, True)
        return str(self.val)

class _date_format(str, _format):
    def __init__(self,value):
        super(_date_format, self).__init__()
        self.val = value and str(value) or ''

    def __str__(self):
        if self.val:
            if getattr(self,'name', None):
                date = datetime.strptime(self.name[:get_date_length()], DEFAULT_SERVER_DATE_FORMAT)
                return date.strftime(str(self.lang_obj.date_format))
        return self.val

class _dttime_format(str, _format):
    def __init__(self,value):
        super(_dttime_format, self).__init__()
        self.val = value and str(value) or ''

    def __str__(self):
        if self.val and getattr(self,'name', None):
            return datetime.strptime(self.name, DEFAULT_SERVER_DATETIME_FORMAT)\
                   .strftime("%s %s"%(str(self.lang_obj.date_format),
                                      str(self.lang_obj.time_format)))
        return self.val


_fields_process = {
    'float': _float_format,
    'date': _date_format,
    'integer': _int_format,
    'datetime' : _dttime_format
}

#
# Context: {'node': node.dom}
#
class browse_record_list(list):
    def __init__(self, lst, context):
        super(browse_record_list, self).__init__(lst)
        self.context = context

    def __getattr__(self, name):
        res = browse_record_list([getattr(x,name) for x in self], self.context)
        return res

    def __str__(self):
        return "browse_record_list("+str(len(self))+")"

class rml_parse(object):
    def __init__(self, cr, uid, name, parents=rml_parents, tag=rml_tag, context=None):
        if not context:
            context={}
        self.cr = cr
        self.uid = uid
        self.pool = pooler.get_pool(cr.dbname)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        self.localcontext = {
            'user': user,
            'setCompany': self.setCompany,
            'repeatIn': self.repeatIn,
            'setLang': self.setLang,
            'setTag': self.setTag,
            'removeParentNode': self.removeParentNode,
            'format': self.format,
            'formatLang': self.formatLang,
            'lang' : user.company_id.partner_id.lang,
            'translate' : self._translate,
            'setHtmlImage' : self.set_html_image,
            'strip_name' : self._strip_name,
            'time' : time,
            'display_address': self.display_address,
            # more context members are setup in setCompany() below:
            #  - company_id
            #  - logo
        }
        self.setCompany(user.company_id)
        self.localcontext.update(context)
        self.name = name
        self._node = None
        self.parents = parents
        self.tag = tag
        self._lang_cache = {}
        self.lang_dict = {}
        self.default_lang = {}
        self.lang_dict_called = False
        self._transl_regex = re.compile('(\[\[.+?\]\])')

    def setTag(self, oldtag, newtag, attrs=None):
        return newtag, attrs

    def _ellipsis(self, char, size=100, truncation_str='...'):
        if len(char) <= size:
            return char
        return char[:size-len(truncation_str)] + truncation_str

    def setCompany(self, company_id):
        if company_id:
            self.localcontext['company'] = company_id
            self.localcontext['logo'] = company_id.logo
            self.rml_header = company_id.rml_header
            self.rml_header2 = company_id.rml_header2
            self.rml_header3 = company_id.rml_header3
            self.logo = company_id.logo

    def _strip_name(self, name, maxlen=50):
        return self._ellipsis(name, maxlen)

    def format(self, text, oldtag=None):
        return text.strip()

    def removeParentNode(self, tag=None):
        raise GeneratorExit('Skip')

    def set_html_image(self,id,model=None,field=None,context=None):
        if not id :
            return ''
        if not model:
            model = 'ir.attachment'
        try :
            id = int(id)
            res = self.pool.get(model).read(self.cr,self.uid,id)
            if field :
                return res[field]
            elif model =='ir.attachment' :
                return res['datas']
            else :
                return ''
        except Exception:
            return ''

    def setLang(self, lang):
        self.localcontext['lang'] = lang
        self.lang_dict_called = False
        for obj in self.objects:
            obj._context['lang'] = lang

    def _get_lang_dict(self):
        pool_lang = self.pool.get('res.lang')
        lang = self.localcontext.get('lang', 'en_US') or 'en_US'
        lang_ids = pool_lang.search(self.cr,self.uid,[('code','=',lang)])[0]
        lang_obj = pool_lang.browse(self.cr,self.uid,lang_ids)
        self.lang_dict.update({'lang_obj':lang_obj,'date_format':lang_obj.date_format,'time_format':lang_obj.time_format})
        self.default_lang[lang] = self.lang_dict.copy()
        return True

    def digits_fmt(self, obj=None, f=None, dp=None):
        digits = self.get_digits(obj, f, dp)
        return "%%.%df" % (digits, )

    def get_digits(self, obj=None, f=None, dp=None):
        d = DEFAULT_DIGITS = 2
        if dp:
            decimal_precision_obj = self.pool.get('decimal.precision')
            ids = decimal_precision_obj.search(self.cr, self.uid, [('name', '=', dp)])
            if ids:
                d = decimal_precision_obj.browse(self.cr, self.uid, ids)[0].digits
        elif obj and f:
            res_digits = getattr(obj._columns[f], 'digits', lambda x: ((16, DEFAULT_DIGITS)))
            if isinstance(res_digits, tuple):
                d = res_digits[1]
            else:
                d = res_digits(self.cr)[1]
        elif (hasattr(obj, '_field') and\
                isinstance(obj._field, (float_field, function_field)) and\
                obj._field.digits):
                d = obj._field.digits[1] or DEFAULT_DIGITS
        return d

    def formatLang(self, value, digits=None, date=False, date_time=False, grouping=True, monetary=False, dp=False, currency_obj=False):
        """
            Assuming 'Account' decimal.precision=3:
                formatLang(value) -> digits=2 (default)
                formatLang(value, digits=4) -> digits=4
                formatLang(value, dp='Account') -> digits=3
                formatLang(value, digits=5, dp='Account') -> digits=5
        """
        if digits is None:
            if dp:
                digits = self.get_digits(dp=dp)
            else:
                digits = self.get_digits(value)

        if isinstance(value, (str, unicode)) and not value:
            return ''

        if not self.lang_dict_called:
            self._get_lang_dict()
            self.lang_dict_called = True

        if date or date_time:
            if not str(value):
                return ''

            date_format = self.lang_dict['date_format']
            parse_format = DEFAULT_SERVER_DATE_FORMAT
            if date_time:
                value = value.split('.')[0]
                date_format = date_format + " " + self.lang_dict['time_format']
                parse_format = DEFAULT_SERVER_DATETIME_FORMAT
            if isinstance(value, basestring):
                # FIXME: the trimming is probably unreliable if format includes day/month names
                #        and those would need to be translated anyway. 
                date = datetime.strptime(value[:get_date_length(parse_format)], parse_format)
            elif isinstance(value, time.struct_time):
                date = datetime(*value[:6])
            else:
                date = datetime(*value.timetuple()[:6])
            if date_time:
                # Convert datetime values to the expected client/context timezone
                date = datetime_field.context_timestamp(self.cr, self.uid,
                                                        timestamp=date,
                                                        context=self.localcontext)
            return date.strftime(date_format)

        res = self.lang_dict['lang_obj'].format('%.' + str(digits) + 'f', value, grouping=grouping, monetary=monetary)
        if currency_obj:
            if currency_obj.position == 'after':
                res='%s %s'%(res,currency_obj.symbol)
            elif currency_obj and currency_obj.position == 'before':
                res='%s %s'%(currency_obj.symbol, res)
        return res

    def display_address(self, address_browse_record):
        return self.pool.get('res.partner.address')._display_address(self.cr, self.uid, address_browse_record)

    def repeatIn(self, lst, name,nodes_parent=False):
        ret_lst = []
        for id in lst:
            ret_lst.append({name:id})
        return ret_lst

    def _translate(self,text):
        lang = self.localcontext['lang']
        if lang and text and not text.isspace():
            transl_obj = self.pool.get('ir.translation')
            piece_list = self._transl_regex.split(text)
            for pn in range(len(piece_list)):
                if not self._transl_regex.match(piece_list[pn]):
                    source_string = piece_list[pn].replace('\n', ' ').strip()
                    if len(source_string):
                        translated_string = transl_obj._get_source(self.cr, self.uid, self.name, ('report', 'rml'), lang, source_string)
                        if translated_string:
                            piece_list[pn] = piece_list[pn].replace(source_string, translated_string)
            text = ''.join(piece_list)
        return text

    def _add_header(self, rml_dom, header='external'):
        if header=='internal':
            rml_head =  self.rml_header2
        elif header=='internal landscape':
            rml_head =  self.rml_header3
        else:
            rml_head =  self.rml_header

        head_dom = etree.XML(rml_head)
        for tag in head_dom:
            found = rml_dom.find('.//'+tag.tag)
            if found is not None and len(found):
                if tag.get('position'):
                    found.append(tag)
                else :
                    found.getparent().replace(found,tag)
        return True

    def set_context(self, objects, data, ids, report_type = None):
        self.localcontext['data'] = data
        self.localcontext['objects'] = objects
        self.localcontext['digits_fmt'] = self.digits_fmt
        self.localcontext['get_digits'] = self.get_digits
        self.datas = data
        self.ids = ids
        self.objects = objects
        if report_type:
            if report_type=='odt' :
                self.localcontext.update({'name_space' :common.odt_namespace})
            else:
                self.localcontext.update({'name_space' :common.sxw_namespace})

        # WARNING: the object[0].exists() call below is slow but necessary because
        # some broken reporting wizards pass incorrect IDs (e.g. ir.ui.menu ids)
        if objects and len(objects) == 1 and \
            objects[0].exists() and 'company_id' in objects[0] and objects[0].company_id:
            # When we print only one record, we can auto-set the correct
            # company in the localcontext. For other cases the report
            # will have to call setCompany() inside the main repeatIn loop.
            self.setCompany(objects[0].company_id)

class sxw_odt_parse(object):
    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.name = name
        self.context = context
        self.pool = pooler.get_pool(cr.dbname)

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)

        # Function here that is commented out are from the class rml_parse from 
        # the file report_sxw.py. They are commented out because they have not
        # been implemented so far in this new version of the report engine. Also,
        # some function may not apply to the new system such as setHtmlImage.
        self.localcontext = {
            'user': user,
            #'setCompany': self.setCompany,
            'repeatIn': self.repeatIn,
            'repeatInTable': self.repeatInTable,
            'setLang': self.setLang,
            #'setTag': self.setTag,
            'removeParentNode': self.removeParentNode,
            'format': self.format,
            'formatLang': self.formatLang,
            'lang' : user.company_id.partner_id.lang,
            'translate' : self._translate,
            #'setHtmlImage' : self.set_html_image,
            'strip_name' : self._strip_name,
            'time' : time,
            'display_address': self.display_address,
            
            # more context members are setup in setCompany() below:
            #  - company_id
            #  - logo
        }
        self.setCompany(user.company_id)
        self.is_repeatIn = False
        self.is_repeatInTable = False
        self.is_removeParentNode = False

        self.lang_dict = {}
        self.default_lang = {}
        self.lang_dict_called = False
        self._transl_regex = re.compile('(\[\[.+?\]\])')

    def set_context(self, objects, data, ids, report_type = None):
        self.localcontext['data'] = data
        self.localcontext['objects'] = objects
        self.localcontext['digits_fmt'] = self.digits_fmt
        self.localcontext['get_digits'] = self.get_digits
        self.datas = data
        self.ids = ids
        self.objects = objects

        if data['report_type'] == 'odt':
            self.tag__drop_down = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}drop-down'
            self.tag__label     = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}label'
            self.tag__value     = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}value'
            self.tag__table     = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table'
            self.tag__table_row = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row'
            self.parent_tag = {
                'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
                'style' : 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
                'text'  : 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
                'table' : 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
                'draw'  : 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
                'fo'    : 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
                'xlink' : 'http://www.w3.org/1999/xlink',
                'dc'    : 'http://purl.org/dc/elements/1.1/',
                'meta'  : 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0',
                'number': 'urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0',
                'svg'   : 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0',
                'chart' : 'urn:oasis:names:tc:opendocument:xmlns:chart:1.0',
                'dr3d'  : 'urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0',
                'math'  : 'http://www.w3.org/1998/Math/MathML',
                'form'  : 'urn:oasis:names:tc:opendocument:xmlns:form:1.0',
                'script': 'urn:oasis:names:tc:opendocument:xmlns:script:1.0',
                'ooo'   : "http://openoffice.org/2004/office",
                'ooow'  : "http://openoffice.org/2004/writer",
                'oooc'  : "http://openoffice.org/2004/calc",
                'dom'   : "http://www.w3.org/2001/xml-events",
                'xforms' : "http://www.w3.org/2002/xforms",
                'xsd'   : "http://www.w3.org/2001/XMLSchema",
                'xsi'   : "http://www.w3.org/2001/XMLSchema-instance",
                'rpt'   : "http://openoffice.org/2005/report",
                'of'    : 'urn:oasis:names:tc:opendocument:xmlns:of:1.2',
                'xhtml' : "http://www.w3.org/1999/xhtml",
                'grddl' : "http://www.w3.org/2003/g/data-view#",
                'tableooo' : "http://openoffice.org/2009/table",
                'field' : 'urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0'
            }
        elif data['report_type'] == 'sxw':
            self.tag__drop_down = '{http://openoffice.org/2000/text}drop-down'
            self.tag__label     = '{http://openoffice.org/2000/text}label'
            self.tag__value     = '{http://openoffice.org/2000/text}value'
            self.tag__table     = '{http://openoffice.org/2000/table}table'
            self.tag__table_row = '{http://openoffice.org/2000/table}table-row'
            self.parent_tag = {
                'office': 'http://openoffice.org/2000/office',
                'style' : 'http://openoffice.org/2000/style',
                'text'  : 'http://openoffice.org/2000/text',
                'table' : 'http://openoffice.org/2000/table',
                'draw'  : 'http://openoffice.org/2000/drawing',
                'fo'    : 'http://www.w3.org/1999/XSL/Format',
                'xlink' : 'http://www.w3.org/1999/xlink',
                'dc'    : 'http://purl.org/dc/elements/1.1/',
                'meta'  : 'http://openoffice.org/2000/meta',
                'number': 'http://openoffice.org/2000/datastyle',
                'svg'   : 'http://www.w3.org/2000/svg',
                'chart' : 'http://openoffice.org/2000/chart',
                'dr3d'  : 'http://openoffice.org/2000/dr3d',
                'math'  : 'http://www.w3.org/1998/Math/MathML',
                'form'  : 'http://openoffice.org/2000/form',
                'script': 'http://openoffice.org/2000/script',
                'ooo'   : "http://openoffice.org/2004/office",
                'ooow'  : "http://openoffice.org/2004/writer",
                'oooc'  : "http://openoffice.org/2004/calc",
                'dom'   : "http://www.w3.org/2001/xml-events",
                'xforms' : "http://www.w3.org/2002/xforms",
                'xsd'   : "http://www.w3.org/2001/XMLSchema",
                'xsi'   : "http://www.w3.org/2001/XMLSchema-instance",
                'rpt'   : "http://openoffice.org/2005/report",
                'of'    : 'urn:oasis:names:tc:opendocument:xmlns:of:1.2',
                'xhtml' : "http://www.w3.org/1999/xhtml",
                'grddl' : "http://www.w3.org/2003/g/data-view#",
                'tableooo' : "http://openoffice.org/2009/table",
                'field' : 'urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0'
            }
        else:
            raise Exception('report_type not supported.')

        # WARNING: the object[0].exists() call below is slow but necessary because
        # some broken reporting wizards pass incorrect IDs (e.g. ir.ui.menu ids)
        if objects and len(objects) == 1 and \
            objects[0].exists() and 'company_id' in objects[0] and objects[0].company_id:
            # When we print only one record, we can auto-set the correct
            # company in the localcontext. For other cases the report
            # will have to call setCompany() inside the main repeatIn loop.
            self.setCompany(objects[0].company_id)

    def process(self, node):
        _node = node
        i = 0
        while i < len(_node):
            child = _node[i]
            if (child.tag == self.tag__drop_down
                    and len(child) == 2
                    and child[0].tag == self.tag__label
                    and child[1].tag == self.tag__label):

                t = child[1].get(self.tag__value)
                fieldinput = t[2:-2]
                #print 'Evaluating field: %s' % fieldinput
                fieldvalue = eval(fieldinput.replace(u"\xa0", u" "), self.localcontext)
                #print 'fieldvalue: %s' % str(fieldvalue)

                _node.remove(child)
                i -= 1
                if self.is_repeatIn == True:
                    self.repeatIn_value = fieldvalue
                elif self.is_repeatInTable == True:
                    self.repeatInTable_value = fieldvalue
                elif self.is_removeParentNode != True:
                    if fieldvalue != False:
                        if _node.text != None:
                            _node.text = '%s%s' % (_node.text, unicode(fieldvalue))
                        else:
                            _node.text = '%s' % unicode(fieldvalue)
            else:
                r_node = self.process(child)
                if self.is_repeatIn == True:
                    self.is_repeatIn = False
                    r_repeatIn_name = self.repeatIn_name
                    r_repeatIn_value = self.repeatIn_value

                    indexchild = _node.index(child)
                    # If the remaining node as no child, remove it.
                    if len(r_node) == 0:
                        _node.remove(child)

                    # Create a empty element to store all the following child
                    # including itself if needed.
                    root = etree.Element("root")                        
                    while indexchild < len(_node):
                        root.append(_node[indexchild])

                    if r_repeatIn_name in self.localcontext:
                        tmp = self.localcontext[r_repeatIn_name]
                    else:
                        tmp = None

                    # Iterate using the value set by the function repeatIn when 
                    # it was executed when we did the eval.
                    for t in r_repeatIn_value:
                        self.localcontext[r_repeatIn_name] = t[r_repeatIn_name]
                        r2_node = self.process(copy.deepcopy(root))

                        # There is no need to check if 'r' is a repeatIn as it 
                        # use a dummy node. If there is a repeeatIn that is a 
                        # direct child of self.node of this class, it will be 
                        # processed inside r.process().
                        for child2 in r2_node:
                            _node.append(child2)

                    if tmp != None:
                        self.localcontext[r_repeatIn_name] = tmp
                    else:
                        del self.localcontext[r_repeatIn_name]

                    # We have to break. We added multiple item to self.node 
                    # and there is no way to find where it is at right now.
                    # Also, all following node should the one that we just 
                    # added. This will mean that we will process those element
                    # twice. Also, there is no after element as we added 
                    # everything that was after the repeatIn.
                    break
                elif self.is_repeatInTable == True:
                    self.is_repeatInTable = False
                    r_repeatInTable_name = self.repeatInTable_name
                    r_repeatInTable_value = self.repeatInTable_value

                    indexchild = _node.index(child)
                    # If the remaining node as no child, remove it.
                    if len(r_node) == 0:
                        _node.remove(child)

                    # Check if the repeatInTable is just before a table. If it's the 
                    # case, we will just repeat the row instead. If there is no table
                    # after, it<s just ignored.
                    if _node[indexchild].tag == self.tag__table:
                        # Search for table:table-row in child.
                        element_table = _node[indexchild]
                        j = 0
                        while j < len(element_table):
                            if element_table[j].tag == self.tag__table_row:
                                row = element_table[j]
                                element_table.remove(row)

                                # Iterate using the value set by the function repeatIn when 
                                # it was executed when we did the eval.
                                for t in r_repeatInTable_value:
                                    self.localcontext[r_repeatInTable_name] = t[r_repeatInTable_name]
                                    r2_node = self.process(copy.deepcopy(row))

                                    # There is no need to check if 'r' is a repeatIn as it 
                                    # use a dummy node. If there is a repeeatIn that is a 
                                    # direct child of self.node of this class, it will be 
                                    # processed inside r.process().
                                    element_table.append(r2_node)

                                break
                            j += 1
                elif self.is_removeParentNode == True:
                    if child.tag == self.removeParentNode_tag:
                        self.is_removeParentNode = False
                    _node.remove(child)
                    i -= 1
                #else:
                    # If it's not a repeatIn nor a removeParentNode, just copy
                    # the node back inside the child.
                    #_node[i] = copy.deepcopy(r_node)
            i += 1
        return _node

    def repeatIn(self, lst, name, nodes_parent=False):
        self.is_repeatIn = True  # Will stay true for the rest of the node.
        self.repeatIn_name = name
        #print 'lst: %s' % str(lst)
        ret_lst = []
        for id in lst:
            ret_lst.append({name:id})
        return ret_lst

    def repeatInTable(self, lst, name, nodes_parent=False):
        self.is_repeatInTable = True  # Will stay true for the rest of the node.
        self.repeatInTable_name = name
        #print 'lst: %s' % str(lst)
        ret_lst = []
        for id in lst:
            ret_lst.append({name:id})
        return ret_lst

    def removeParentNode(self, tag=None):
        if tag == 'para':
            tag = 'text:p'
        if tag == 'tr':
            tag = 'table:table-row'
        if tag == 'blockTable':
            tag = 'table:table'
        t = tag.split(':')
        self.removeParentNode_tag = '{%s}%s' % (self.parent_tag[t[0]], t[1])
        self.is_removeParentNode = True

    # Not tested
    def setCompany(self, company_id):
        if company_id:
            self.localcontext['company'] = company_id
            self.localcontext['logo'] = company_id.logo
            #self.rml_header = company_id.rml_header
            #self.rml_header2 = company_id.rml_header2
            #self.rml_header3 = company_id.rml_header3
            self.logo = company_id.logo

    # Not tested
    def _ellipsis(self, char, size=100, truncation_str='...'):
        if len(char) <= size:
            return char
        return char[:size-len(truncation_str)] + truncation_str

    # Not tested
    def _strip_name(self, name, maxlen=50):
        return self._ellipsis(name, maxlen)

    # Not tested
    def format(self, text, oldtag=None):
        return text.strip()

    # Not tested
    def setLang(self, lang):
        self.localcontext['lang'] = lang
        self.lang_dict_called = False
        for obj in self.objects:
            obj._context['lang'] = lang

    # Not tested
    def _get_lang_dict(self):
        pool_lang = self.pool.get('res.lang')
        lang = self.localcontext.get('lang', 'en_US') or 'en_US'
        lang_ids = pool_lang.search(self.cr,self.uid,[('code','=',lang)])[0]
        lang_obj = pool_lang.browse(self.cr,self.uid,lang_ids)
        self.lang_dict.update({'lang_obj':lang_obj,'date_format':lang_obj.date_format,'time_format':lang_obj.time_format})
        self.default_lang[lang] = self.lang_dict.copy()
        return True

    # Not tested
    def digits_fmt(self, obj=None, f=None, dp=None):
        digits = self.get_digits(obj, f, dp)
        return "%%.%df" % (digits, )

    # Not tested
    def get_digits(self, obj=None, f=None, dp=None):
        d = DEFAULT_DIGITS = 2
        if dp:
            decimal_precision_obj = self.pool.get('decimal.precision')
            ids = decimal_precision_obj.search(self.cr, self.uid, [('name', '=', dp)])
            if ids:
                d = decimal_precision_obj.browse(self.cr, self.uid, ids)[0].digits
        elif obj and f:
            res_digits = getattr(obj._columns[f], 'digits', lambda x: ((16, DEFAULT_DIGITS)))
            if isinstance(res_digits, tuple):
                d = res_digits[1]
            else:
                d = res_digits(self.cr)[1]
        elif (hasattr(obj, '_field') and\
                isinstance(obj._field, (float_field, function_field)) and\
                obj._field.digits):
                d = obj._field.digits[1] or DEFAULT_DIGITS
        return d
    
    # Not tested
    def formatLang(self, value, digits=None, date=False, date_time=False, grouping=True, monetary=False, dp=False, currency_obj=False):
        """
            Assuming 'Account' decimal.precision=3:
                formatLang(value) -> digits=2 (default)
                formatLang(value, digits=4) -> digits=4
                formatLang(value, dp='Account') -> digits=3
                formatLang(value, digits=5, dp='Account') -> digits=5
        """
        if digits is None:
            if dp:
                digits = self.get_digits(dp=dp)
            else:
                digits = self.get_digits(value)

        if isinstance(value, (str, unicode)) and not value:
            return ''

        if not self.lang_dict_called:
            self._get_lang_dict()
            self.lang_dict_called = True

        if date or date_time:
            if not str(value):
                return ''

            date_format = self.lang_dict['date_format']
            parse_format = DEFAULT_SERVER_DATE_FORMAT
            if date_time:
                value = value.split('.')[0]
                date_format = date_format + " " + self.lang_dict['time_format']
                parse_format = DEFAULT_SERVER_DATETIME_FORMAT
            if isinstance(value, basestring):
                # FIXME: the trimming is probably unreliable if format includes day/month names
                #        and those would need to be translated anyway. 
                date = datetime.strptime(value[:get_date_length(parse_format)], parse_format)
            elif isinstance(value, time.struct_time):
                date = datetime(*value[:6])
            else:
                date = datetime(*value.timetuple()[:6])
            if date_time:
                # Convert datetime values to the expected client/context timezone
                date = datetime_field.context_timestamp(self.cr, self.uid,
                                                        timestamp=date,
                                                        context=self.localcontext)
            return date.strftime(date_format)

        res = self.lang_dict['lang_obj'].format('%.' + str(digits) + 'f', value, grouping=grouping, monetary=monetary)
        if currency_obj:
            if currency_obj.position == 'after':
                res='%s %s'%(res,currency_obj.symbol)
            elif currency_obj and currency_obj.position == 'before':
                res='%s %s'%(currency_obj.symbol, res)
        return res

    # Not tested
    def display_address(self, address_browse_record):
        return self.pool.get('res.partner.address')._display_address(self.cr, self.uid, address_browse_record)

    # Not tested
    def _translate(self,text):
        lang = self.localcontext['lang']
        if lang and text and not text.isspace():
            transl_obj = self.pool.get('ir.translation')
            piece_list = self._transl_regex.split(text)
            for pn in range(len(piece_list)):
                if not self._transl_regex.match(piece_list[pn]):
                    source_string = piece_list[pn].replace('\n', ' ').strip()
                    if len(source_string):
                        translated_string = transl_obj._get_source(self.cr, self.uid, self.name, ('report', 'rml'), lang, source_string)
                        if translated_string:
                            piece_list[pn] = piece_list[pn].replace(source_string, translated_string)
            text = ''.join(piece_list)
        return text

class report_sxw(report_rml, preprocess.report):
    def __init__(self, name, table, rml=False, parser=rml_parse, header='external', store=False):
        report_rml.__init__(self, name, table, rml, '')
        self.name = name
        self.parser = parser
        self.header = header
        self.store = store
        self.internal_header=False
        if header=='internal' or header=='internal landscape':
            self.internal_header=True

    def getObjects(self, cr, uid, ids, context):
        table_obj = pooler.get_pool(cr.dbname).get(self.table)
        return table_obj.browse(cr, uid, ids, list_class=browse_record_list, context=context, fields_process=_fields_process)

    def create(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        if self.internal_header:
            context.update(internal_header=self.internal_header)
        # skip osv.fields.sanitize_binary_value() because we want the raw bytes in all cases
        context.update(bin_raw=True)
        pool = pooler.get_pool(cr.dbname)
        ir_obj = pool.get('ir.actions.report.xml')
        report_xml_ids = ir_obj.search(cr, uid,
                [('report_name', '=', self.name[7:])], context=context)
        if report_xml_ids:
            report_xml = ir_obj.browse(cr, uid, report_xml_ids[0], context=context)
        else:
            title = ''
            report_file = tools.file_open(self.tmpl, subdir=None)
            try:
                rml = report_file.read()
                report_type= data.get('report_type', 'pdf')
                class a(object):
                    def __init__(self, *args, **argv):
                        for key,arg in argv.items():
                            setattr(self, key, arg)
                report_xml = a(title=title, report_type=report_type, report_rml_content=rml, name=title, attachment=False, header=self.header)
            finally:
                report_file.close()
        if report_xml.header:
            report_xml.header = self.header
        report_type = report_xml.report_type
        if report_type in ['sxw','odt']:
            fnct = self.create_source_odt
        elif report_type in ['pdf','raw','txt','html']:
            fnct = self.create_source_pdf
        elif report_type=='html2html':
            fnct = self.create_source_html2html
        elif report_type=='mako2html':
            fnct = self.create_source_mako2html
        else:
            raise NotImplementedError(_('Unknown report type: %s') % report_type)
        fnct_ret = fnct(cr, uid, ids, data, report_xml, context)
        if not fnct_ret:
            return (False,False)
        return fnct_ret

    def create_source_odt(self, cr, uid, ids, data, report_xml, context=None):
        return self.create_single_odt(cr, uid, ids, data, report_xml, context or {})

    def create_source_html2html(self, cr, uid, ids, data, report_xml, context=None):
        return self.create_single_html2html(cr, uid, ids, data, report_xml, context or {})

    def create_source_mako2html(self, cr, uid, ids, data, report_xml, context=None):
        return self.create_single_mako2html(cr, uid, ids, data, report_xml, context or {})

    def create_source_pdf(self, cr, uid, ids, data, report_xml, context=None):
        if not context:
            context={}
        pool = pooler.get_pool(cr.dbname)
        attach = report_xml.attachment
        if attach:
            objs = self.getObjects(cr, uid, ids, context)
            results = []
            for obj in objs:
                aname = eval(attach, {'object':obj, 'time':time})
                result = False
                if report_xml.attachment_use and aname and context.get('attachment_use', True):
                    aids = pool.get('ir.attachment').search(cr, uid, [('datas_fname','=',aname+'.pdf'),('res_model','=',self.table),('res_id','=',obj.id)])
                    if aids:
                        brow_rec = pool.get('ir.attachment').browse(cr, uid, aids[0])
                        if not brow_rec.datas:
                            continue
                        d = base64.decodestring(brow_rec.datas)
                        results.append((d,'pdf'))
                        continue
                result = self.create_single_pdf(cr, uid, [obj.id], data, report_xml, context)
                if not result:
                    return False
                if aname:
                    try:
                        name = aname+'.'+result[1]
                        # Remove the default_type entry from the context: this
                        # is for instance used on the account.account_invoices
                        # and is thus not intended for the ir.attachment type
                        # field.
                        ctx = dict(context)
                        ctx.pop('default_type', None)
                        pool.get('ir.attachment').create(cr, uid, {
                            'name': aname,
                            'datas': base64.encodestring(result[0]),
                            'datas_fname': name,
                            'res_model': self.table,
                            'res_id': obj.id,
                            }, context=ctx
                        )
                    except Exception:
                        #TODO: should probably raise a proper osv_except instead, shouldn't we? see LP bug #325632
                        _logger.error('Could not create saved report attachment', exc_info=True)
                results.append(result)
            if results:
                if results[0][1]=='pdf':
                    from pyPdf import PdfFileWriter, PdfFileReader
                    output = PdfFileWriter()
                    for r in results:
                        reader = PdfFileReader(cStringIO.StringIO(r[0]))
                        for page in range(reader.getNumPages()):
                            output.addPage(reader.getPage(page))
                    s = cStringIO.StringIO()
                    output.write(s)
                    return s.getvalue(), results[0][1]
        return self.create_single_pdf(cr, uid, ids, data, report_xml, context)

    def create_single_pdf(self, cr, uid, ids, data, report_xml, context=None):
        if not context:
            context={}
        logo = None
        context = context.copy()
        title = report_xml.name
        rml = report_xml.report_rml_content
        # if no rml file is found
        if not rml:
            return False
        rml_parser = self.parser(cr, uid, self.name2, context=context)
        objs = self.getObjects(cr, uid, ids, context)
        rml_parser.set_context(objs, data, ids, report_xml.report_type)
        processed_rml = etree.XML(rml)
        if report_xml.header:
            rml_parser._add_header(processed_rml, self.header)
        processed_rml = self.preprocess_rml(processed_rml,report_xml.report_type)
        if rml_parser.logo:
            logo = base64.decodestring(rml_parser.logo)
        create_doc = self.generators[report_xml.report_type]
        pdf = create_doc(etree.tostring(processed_rml),rml_parser.localcontext,logo,title.encode('utf8'))
        return (pdf, report_xml.report_type)

    def create_single_odt(self, cr, uid, ids, data, report_xml, context=None):
        # data: {'report_type': u'odt'}
        # context: {
        #       'lang'              : u'en_US', 
        #       'active_ids'        : [1], 
        #       'tz'                : False, 
        #       'uid'               : 1, 
        #       'active_model'      : 'aceroq.project', 
        #       'section_id'        : False, 
        #       'bin_raw'           : True, 
        #       'project_id'        : False, 
        #       'active_id'         : 1
        # }
        # print "create_single_odt2: data: %s, context: %s" % (str(data), str(context))
        if not context:
            context={}
        context = context.copy()
        report_type = report_xml.report_type
        context['parents'] = sxw_parents
        binary_report_content = report_xml.report_sxw_content
        if isinstance(report_xml.report_sxw_content, unicode):
            # if binary content was passed as unicode, we must
            # re-encode it as a 8-bit string using the pass-through
            # 'latin1' encoding, to restore the original byte values.
            # See also osv.fields.sanitize_binary_value()
            binary_report_content = report_xml.report_sxw_content.encode("latin1")

        # Open the odt file.
        sxw_in = StringIO.StringIO(binary_report_content)
        sxw_zin = zipfile.ZipFile(sxw_in, mode='r')
        content_xml = sxw_zin.read('content.xml')

        # Process and execute the content field using "[[ ]]"" in the odt file.
        odt_dom = etree.XML(content_xml)
        objs = self.getObjects(cr, uid, ids, context)
        # TODO: Make work for multiple selection (Openerp doesn't support multiple file download... i think).
        odt_dom2 = self.parser(cr, uid, self.name, context)
        odt_dom2.set_context(objs, data, ids, report_xml.report_type)
        node = odt_dom2.process(odt_dom)
        odt = etree.tostring(node)

        # Save the xml back inside the odt file.
        sxw_out = StringIO.StringIO()
        sxw_zout = zipfile.ZipFile(sxw_out, mode='a', compression=zipfile.ZIP_DEFLATED)
        sxw_zout.writestr('content.xml', "<?xml version='1.0' encoding='UTF-8'?>" + \
                odt)

        # Copy all other files
        out_files = set(sxw_zout.namelist())
        for zf in sxw_zin.namelist():
            if zf in out_files:
                continue
            buf = sxw_zin.read(zf)
            sxw_zout.writestr(zf,buf)
        sxw_zin.close()
        sxw_in.close()

        sxw_zout.close()
        final_op = sxw_out.getvalue()
        sxw_out.close()

        # Convert the odt file to an another format if needed. This need 
        # OpenOffice to run in background because it will call it. 
        # On windows: soffice "-accept=socket,port=2002;urp;"
        # On linux:  /usr/lib/libreoffice/program/soffice --headless --accept="socket,port=2002;urp" --nofirststartwizard --display 0.0 &

        final_op = convert_sxw_odt_2_pdf(final_op,data['report_type'], "pdf")
        report_type = "pdf"
        return (final_op, report_type)

    def create_single_html2html(self, cr, uid, ids, data, report_xml, context=None):
        if not context:
            context = {}
        context = context.copy()
        report_type = 'html'
        context['parents'] = html_parents

        html = report_xml.report_rml_content
        html_parser = self.parser(cr, uid, self.name2, context=context)
        html_parser.parents = html_parents
        html_parser.tag = sxw_tag
        objs = self.getObjects(cr, uid, ids, context)
        html_parser.set_context(objs, data, ids, report_type)

        html_dom =  etree.HTML(html)
        html_dom = self.preprocess_rml(html_dom,'html2html')

        create_doc = self.generators['html2html']
        html = etree.tostring(create_doc(html_dom, html_parser.localcontext))

        return (html.replace('&amp;','&').replace('&lt;', '<').replace('&gt;', '>').replace('</br>',''), report_type)

    def create_single_mako2html(self, cr, uid, ids, data, report_xml, context=None):
        mako_html = report_xml.report_rml_content
        html_parser = self.parser(cr, uid, self.name2, context)
        objs = self.getObjects(cr, uid, ids, context)
        html_parser.set_context(objs, data, ids, 'html')
        create_doc = self.generators['makohtml2html']
        html = create_doc(mako_html,html_parser.localcontext)
        return (html,'html')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
