# -*-  coding: utf-8 -*-
from time import sleep
from wsgiref import simple_server
from zengine.dispatcher import app
from tests.deep_eq import deep_eq
from tests.models import Employee
from zengine.lib.forms import AngularForm
from tests.test_utils import BaseTestCase
from ulakbus.models import User

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


def test_simple():
    serialized_form = AngularForm(Employee()).serialize()
    # assert serialized_empty_test_employee['model'] == serialized_form['model']
    assert deep_eq(serialized_empty_test_employee, serialized_form,
                   _assert=True)


login_form_response = {
    'forms': {'model': {'username': None, 'password': None},
              'form': ['username', 'password'],
              'schema': {'required': ['username', 'password'],
                         'type': 'object', 'properties': {
                      'username': {'type': 'string',
                                   'title': 'Username'},
                      'password': {'type': 'password',
                                   'title': 'Password'}},
                         'title': 'LoginForm'}},
    'is_login': False}


class TestCase(BaseTestCase):
    def test_real_login(self):
        self.prepare_client('simple_login')
        # User.objects._clear_bucket()
        # sleep(1)
        # u = User(username='user')
        # u.set_password('123')
        # u.save()
        # sleep(1)
        resp = self.client.post()
        print(resp.json)
        # assert resp.json == login_form_response
