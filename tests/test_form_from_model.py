from tests.models import Employee
from ulakbus.modules.forms import AngularForm

__author__ = 'Evren Esat Ozkan'

serialized_empty_test_employee = {
    'model': {'birth_date': '2015-07-06T00:00:00Z', 'archived': False, 'last_name': None,
              'first_name': None, 'staff_type': None},
    'form': ['archived', 'last_name', 'first_name', 'staff_type', 'birth_date'],
    'schema': {'required': ['archived', 'last_name', 'first_name', 'staff_type', 'birth_date'],
               'type': 'object',
               'properties': {'birth_date': {'type': 'date', 'title': 'Do\xc4\x9fum Tarihi'},
                              'archived': {'type': 'boolean', 'title': ''},
                              'last_name': {'type': 'string', 'title': 'Soyad\xc4\xb1'},
                              'first_name': {'type': 'string', 'title': 'Ad\xc4\xb1'},
                              'staff_type': {'type': 'string',
                                             'title': 'Personel T\xc3\xbcr\xc3\xbc'}},
               'title': 'Employee'}}


def test_simple():
    serialized_form = AngularForm(Employee()).serialize()
    assert serialized_empty_test_employee == serialized_form
