# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from io import BytesIO

from pyoko import form
from zengine.lib.forms import JsonForm
from zengine.views.base import BaseView
import re
from ulakbus.lib.pdfdocument.document import PDFDocument


FILENAME_RE = re.compile(r'[^A-Za-z0-9\-\.]+')

class Reporter(BaseView):
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
        pdf = PDFDocument(f)
        pdf.init_report()
        pdf.h1(self.get_title())
        pdf.table(objects)
        pdf.generate()
        self.current.response.body = f.getvalue()

    def convert_choices(self, choices_dict_list):
        return dict([(d['value'], d['name']) for d in choices_dict_list])

    def get_headers(self):
        return self.HEADERS

    def get_title(self):
        return self.TITLE

    def get_objects(self):
        raise NotImplementedError
