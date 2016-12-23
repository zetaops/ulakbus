# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from io import BytesIO
from zengine.lib.translation import gettext as _, gettext_lazy
import six
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.base import BaseView
import re
import base64
from datetime import datetime

try:
    from ulakbus.lib.pdfdocument.document import PDFDocument, register_fonts_from_paths
except:
    print("Warning: Reportlab module not found")

from ulakbus.lib.s3_file_manager import S3FileManager


class ReporterRegistry(type):
    registry = {}
    _meta = None

    def __new__(mcs, name, bases, attrs):
        # for key, prop in attrs.items():
        #     if hasattr(prop, 'view_method'):
        if name == 'Reporter':
            ReporterRegistry._meta = attrs['Meta']
            if 'Meta' not in attrs:
                attrs['Meta'] = type('Meta', (object,), ReporterRegistry._meta.__dict__)
            else:
                for k, v in ReporterRegistry._meta.__dict__.items():
                    if k not in attrs['Meta'].__dict__:
                        setattr(attrs['Meta'], k, v)

        new_class = super(ReporterRegistry, mcs).__new__(mcs, name, bases, attrs)
        if name != 'Reporter':
            ReporterRegistry.registry[name] = new_class
        return new_class

    @staticmethod
    def get_reporters():
        return [{"text": v.get_title(),
                 "wf": 'generic_reporter',
                 "model": k,
                 "kategori": 'Raporlar',
                 "param": 'id'} for k, v in ReporterRegistry.registry.items()]

    @staticmethod
    def get_permissions():
        return [("report.%s" % k, v.get_title(), "") for k, v in ReporterRegistry.registry.items()]

    @staticmethod
    def get_reporter(name):
        return ReporterRegistry.registry[name]


FILENAME_RE = re.compile(r'[^A-Za-z0-9\-\.]+')


@six.add_metaclass(ReporterRegistry)
class Reporter(BaseView):
    TITLE = ''

    class Meta:
        pass

    def __init__(self, current):

        super(Reporter, self).__init__(current)
        self.cmd = current.input.get('cmd', 'show')
        # print("CMD", self.cmd)
        if self.cmd == 'show':
            self.show()
        elif self.cmd == 'printout':
            self.printout()

    class ReportForm(JsonForm):
        printout = fields.Button(gettext_lazy(u"Yazdır"), cmd="printout")

    def show(self):
        objects = self.get_objects()
        frm = self.ReportForm(current=self.current, title=self.get_title())
        if objects:
            frm.help_text = ''
            if isinstance(objects[0], dict):
                self.output['object'] = {'fields': objects, 'type': 'table-multiRow'}
            else:
                objects = dict((k, str(v)) for k, v in objects)
                self.output['object'] = objects

        else:
            frm.help_text = _(u'Kayıt bulunamadı')
            self.output['object'] = {}

        self.set_client_cmd('form', 'show')
        self.output['forms'] = frm.serialize()
        self.output['forms']['constraints'] = {}
        self.output['forms']['grouping'] = []
        self.output['meta'] = {}

    def printout(self):
        register_fonts_from_paths('Vera.ttf',
                                  'VeraIt.ttf',
                                  'VeraBd.ttf',
                                  'VeraBI.ttf',
                                  'Vera')
        objects = self.get_objects()
        f = BytesIO()
        pdf = PDFDocument(f, font_size=14)
        pdf.init_report()
        pdf.h1(self.tr2ascii(self.get_title()))

        ascii_objects = []
        if isinstance(objects[0], dict):
            headers = objects[0].keys()
            ascii_objects.append([self.tr2ascii(h) for h in headers])
            for obj in objects:
                ascii_objects.append([self.tr2ascii(k) for k in obj.values()])
        else:
            for o in objects:
                ascii_objects.append((self.tr2ascii(o[0]), self.tr2ascii(o[1])))
        pdf.table(ascii_objects)
        pdf.generate()
        download_url = self.generate_temp_file(
            name=self.generate_file_name(),
            content=base64.b64encode(f.getvalue()),
            file_type='application/pdf',
            ext='pdf'
        )
        self.set_client_cmd('download')
        self.output['download_url'] = download_url

    @staticmethod
    def generate_temp_file(name, content, file_type, ext):
        f = S3FileManager()
        key = f.store_file(name=name, content=content, type=file_type, ext=ext)
        return f.get_url(key)

    def generate_file_name(self):
        return "{0}-{1}".format(
            FILENAME_RE.sub('-', self.tr2ascii(self.get_title()).lower()),
            datetime.now().strftime("%d.%m.%Y-%H.%M.%S")
        )

    @staticmethod
    def convert_choices(choices_dict_list):
        result = []
        for d in choices_dict_list:
            try:
                k = int(d[0])
            except:
                k = d[0]
            result.append((k, d[1]))
        return dict(result)

    def get_headers(self):
        return self.HEADERS

    @classmethod
    def get_title(cls):
        return six.text_type(cls.TITLE)

    def get_objects(self):
        raise NotImplementedError

    def tr2ascii(self, inp):
        inp = six.text_type(inp)
        shtlst = [
            ('ğ', 'g'),
            ('ı', 'i'),
            ('İ', 'I'),
            ('ç', 'c'),
            ('ö', 'o'),
            ('ü', 'u'),
            ('ş', 's'),
            ('Ğ', 'G'),
            ('Ş', 'S'),
            ('Ö', 'O'),
            ('Ü', 'U'),
            ('Ç', 'C'),
        ]
        for t, a in shtlst:
            inp = inp.replace(t, a)
        return inp


def ReportDispatcher(current):
    ReporterRegistry.get_reporter(current.input['model'])(current)
