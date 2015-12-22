# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from io import BytesIO

import six
from reportlab.platypus import Table

from pyoko import form
from zengine.lib.forms import JsonForm
from zengine.views.base import BaseView
import re
from ulakbus.lib.pdfdocument.document import PDFDocument, register_fonts_from_paths


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

    class Meta:
        pass

    def __init__(self, current):
        register_fonts_from_paths('AndikaNewBasic.ttf',
                                  'AndikaNewBasic-I.ttf',
                                  'AndikaNewBasic-B.ttf',
                                  'AndikaNewBasic-BI.ttf',
                                  'AndikaNewBasic')
        super(Reporter, self).__init__(current)
        self.cmd = current.input.get('cmd', 'show')
        # print("CMD", self.cmd)
        if self.cmd == 'show':
            self.show()
        elif self.cmd == 'printout':
            self.printout()

    class ReportForm(JsonForm):
        printout = form.Button("Yazdır", cmd="printout")

    def show(self):
        headers = self.get_headers()
        objects = self.get_objects()
        self.set_client_cmd('form')
        self.output['forms'] = self.ReportForm(current=self.current,
                                               title=self.get_title()).serialize()
        self.output['forms']['constraints'] = {}
        self.output['forms']['grouping'] = {}
        self.output['meta'] = {}
        self.output['objects'] = [headers]
        for obj in objects:
            self.output['objects'].append(
                    {'fields': obj, 'key': None, 'actions': []},
            )

    def set_headers(self, as_attachment=True):
        self.current.response.set_header('Content-Type', 'application/pdf')
        self.current.response.set_header('Content-Disposition', '%s; filename="%s.pdf"' % (
            'attachment' if as_attachment else 'inline',
            FILENAME_RE.sub('-', self.get_title()),
        ))

    def printout(self):
        headers = self.get_headers()
        objects = self.get_objects()
        self.set_headers()
        f = BytesIO()
        pdf = PDFDocument(f, font_name='AndikaNewBasic', font_size=14)
        pdf.init_report()
        pdf.h1(self.tr2ascii(self.get_title()))

        # pdf.story.append(Table(objects))
        if len(objects[0]) == 2:
            ascii_objects = []
            for o in objects:
                ascii_objects.append((self.tr2ascii(o[0]), self.tr2ascii(o[1])))
            pdf.table(ascii_objects)
        else:
            pdf.table(objects)
        #     else:
        #         pdf.table(o)
        pdf.generate()
        self.current.response.body = f.getvalue()

    def convert_choices(self, choices_dict_list):
        result = []
        for d in choices_dict_list:
            try: k = int(d[0])
            except: k = d[0]
            result.append((k, d[1]))
        return dict(result)

    def get_headers(self):
        return self.HEADERS

    @classmethod
    def get_title(cls):
        return cls.TITLE

    def get_objects(self):
        raise NotImplementedError

    def tr2ascii(self, inp):
        inp = six.text_type(inp)
        shtlst = [
            ('ğ','g'),
            ('ı','i'),
            ('İ','I'),
            ('ç','c'),
            ('ö','o'),
            ('ü','u'),
            ('ş','s'),
            ('Ğ','G'),
            ('Ş','S'),
            ('Ö','O'),
            ('Ü','U'),
            ('Ç','C'),
        ]
        for t,a in shtlst:
            inp = inp.replace(t, a)
        return inp


def ReportDispatcher(current):
        ReporterRegistry.get_reporter(current.input['model'])(current)
