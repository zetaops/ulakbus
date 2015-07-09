# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models.personel import Employee
from ulakbus.modules.forms import AngularForm
from ulakbus.lib.views import SimpleView

from falcon.errors import HTTPBadRequest


def List(current):
    current['request'].context['result']['employees'] = []
    for employee in Employee.objects.filter().data():
        current['request'].context['result']['employees'].append(
            {"data": employee.data, "key": employee.key})


def Show(current):
    key = current['request'].context['data']['object_id']
    employee = Employee.objects.get(key)
    if len(employee) > 0:
        current['request'].context['result']['employee'] = Employee.objects.get(key)
    else:
        current['request'].context['result']['employee'] = []


class Edit(SimpleView):
    def _show(self):
        if self.current['request'].context['data'].get('object_id'):
            employee_id = self.current['request'].context['data']['object_id']
            serialized_form = AngularForm(Employee.objects.get(employee_id), types={"birth_date": "string"}).serialize()
        else:
            serialized_form = AngularForm(Employee(), types={"birth_date": "string"}).serialize()
        self.current['request'].context['result']['forms'] = serialized_form


    def _do(self):
        employee_id = self.current['request'].context['data'].get('object_id')
        if employee_id:
            employee = Employee.objects.get(employee_id)
        else:
            employee = Employee()
        employee._load_data(self.current['request'].context['data']['form'])
        employee.save()
        self.current['task'].data['IS'].opertation_successful = True

