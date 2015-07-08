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
            employee.data)


def Show(current):
    employee_id = current['request'].context['data']['object_id']
    employee = Employee.objects.get(employee_id)
    if len(employee) > 0:
        current['request'].context['result']['employee'] = Employee.objects.get(employee_id)
    else:
        current['request'].context['result']['employee'] = []


def Edit(current):
    if current['request'].context['data'].get('object_id'):
        employee_id = current['request'].context['data']['object_id']
        serialized_form = AngularForm(Employee.objects.get(employee_id), types={"birth_date": "string"}).serialize()
    else:
        serialized_form = AngularForm(Employee(), types={"birth_date": "string"}).serialize()
    current['request'].context['result']['forms'] = serialized_form


def Save(current):
    employee_id = current['request'].context['data']['object_id']
    employee = Employee.objects.get(employee_id)
    employee._load_data(current['request'].context['data']['form'])
    employee.save()
    current['request'].context['result']['success'] = True

