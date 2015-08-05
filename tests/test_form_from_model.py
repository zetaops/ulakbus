from tests.deep_eq import deep_eq
from tests.models import Employee
from zengine.lib.forms import AngularForm
__author__ = 'Evren Esat Ozkan'

serialized_empty_test_employee = {
    'model': {'birth_date': '', 'last_name': None,
              'first_name': None, 'staff_type': None},
    'form': ['first_name', 'last_name', 'staff_type', 'birth_date'],
    'schema': {'required': ['first_name','staff_type', 'birth_date', 'last_name'],
               'type': 'object',
               'properties': {'birth_date': {'type': 'date', 'title': 'Do\xc4\x9fum Tarihi'},
                              'last_name': {'type': 'string', 'title': 'Soyad\xc4\xb1'},
                              'first_name': {'type': 'string', 'title': 'Ad\xc4\xb1'},
                              'staff_type': {'type': 'string',
                                             'title': 'Personel T\xc3\xbcr\xc3\xbc'}},
               'title': 'Employee'}}


def test_simple():


    serialized_form = AngularForm(Employee()).serialize()
    # assert serialized_empty_test_employee['model'] == serialized_form['model']
    assert deep_eq(serialized_empty_test_employee, serialized_form,_assert=True )
