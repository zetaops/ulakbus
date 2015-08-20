# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Employee
from zengine.lib.forms import JsonForm
from zengine.lib.views import SimpleView


def List(current):
    current.output['employees'] = []
    for employee in Employee.objects.filter().data():
        data = employee.data
        current.output['employees'].append(
            {"data": data, "key": employee.key})


def Show(current):
    key = current.input['object_id']
    employee = Employee.objects.get(key)
    if len(employee) > 0:
        current.output['employee'] = Employee.objects.get(key)
    else:
        current.output['employee'] = []


class Edit(SimpleView):
    def _show(self):
        if self.current.input.get('object_id'):
            employee_id = self.current.input['object_id']
            serialized_form = JsonForm(Employee.objects.get(employee_id), customized_types={"birth_date": "string"}).serialize()
        else:
            serialized_form = JsonForm(Employee()).serialize()
        self.current.output['forms'] = serialized_form


    def _do(self):
        employee_id = self.current.input.get('object_id')
        if employee_id:
            employee = Employee.objects.get(employee_id)
        else:
            employee = Employee()
        employee._load_data(self.current.input['form'])
        employee.save()
        self.current['task'].data['IS'].opertation_successful = True

