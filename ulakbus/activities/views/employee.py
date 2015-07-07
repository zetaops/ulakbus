# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models.personel import Employee
from ulakbus.modules.forms import AngularForm
from ulakbus.lib.views import SimpleView

from falcon.errors import HTTPBadRequest

def manage(current):


class List(SimpleView):

    def _do(self):
        self.current.request.context['result'] = {'success': True}

    def _show(self):
        self.current['request'].context['result']['employees'] = []
        for employee in Employee.objects.filter().data():
            self.current['request'].context['result']['employees'].append(employee.data)


class Show(SimpleView):

    def _do(self):
        self.current.request.context['result'] = {'success': True}

    def _show(self):
        self.current['request'].context['result']['forms'] = get_form('student_login_form')


class Edit(SimpleView):

    def _do(self):
        self.current.request.context['result'] = {'success': True}

    def _show(self):
        serialized_form = AngularForm(Employee()).serialize()
        self.current['request'].context['result']['forms'] = serialized_form


class Save(SimpleView):

    def _do(self):
        self.current.request.context['result'] = {'success': True}

    def _show(self):
        self.current['request'].context['result']['forms'] = get_form('student_login_form')


class Preview(SimpleView):

    def _do(self):
        self.current.request.context['result'] = {'success': True}

    def _show(self):
        self.current['request'].context['result']['forms'] = get_form('student_login_form')