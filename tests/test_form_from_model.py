# -*-  coding: utf-8 -*-

from tests.deep_eq import deep_eq
# from tests.models import Employee
from zengine.lib.forms import JsonForm

__author__ = 'Evren Esat Ozkan'

serialized_empty_test_employee = {
    'model': {'birth_date': '', 'last_name': None,
              'first_name': None, 'staff_type': None},
    'form': ['first_name', 'last_name', 'staff_type', 'birth_date'],
    'schema': {
        'required': ['first_name', 'staff_type', 'birth_date', 'last_name'],
        'type': 'object',
        'properties': {
            'birth_date': {'type': 'date', 'title': 'Doğum Tarihi'},
            'last_name': {'type': 'string', 'title': 'Soyadı'},
            'first_name': {'type': 'string', 'title': 'Adı'},
            'staff_type': {'type': 'string',
                           'title': 'Personel Türü'}},
        'title': 'Employee'}}

#
# def test_simple():
#     serialized_form = JsonForm(Employee()).serialize()
#     # assert serialized_empty_test_employee['model'] == serialized_form['model']
#     assert deep_eq(serialized_empty_test_employee, serialized_form,
#                    _assert=True)

