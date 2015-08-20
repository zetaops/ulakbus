# -*-  coding: utf-8 -*-
import os
from time import sleep
from pyoko.model import model_registry
from werkzeug.test import Client
from zengine.server import app
from ulakbus.models import User, AbstractRole, Role

__author__ = 'Evren Esat Ozkan'


def get_worfklow_path(wf_name):
    return "%s/workflows/%s.zip" % (
        os.path.dirname(os.path.realpath(__file__)), wf_name)


from pprint import pprint
import json


class RWrapper(object):
    def __init__(self, *args):
        self.content = list(args[0])
        self.code = args[1]
        self.headers = list(args[2])
        try:
            self.json = json.loads(self.content[0])
            self.token = self.json.get('token')
        except:
            self.json = None

    def raw(self):
        pprint(self.code)
        pprint(self.json)
        pprint(self.headers)
        pprint(self.content)


class TestClient(object):
    def __init__(self, workflow):
        self.workflow = workflow
        self._client = Client(app, response_wrapper=RWrapper)
        self.user = None
        self.token = None

    def set_workflow(self, workflow):
        self.workflow = workflow

    def post(self, conf=None, **data):
        """
        by default data dict encoded as json and
        content type set as application/json
        :param data: post data,
        :return: tuple with 3 items :
        """

        conf = conf or {}
        make_json = not conf.pop('no_json', False)

        if '_data' in conf:
            data = conf.pop('_data')

        if make_json:
            conf['content_type'] = 'application/json'
            if 'token' not in data and self.token:
                data['token'] = self.token
            data = json.dumps(data)
        wrapper = self._client.post(self.workflow, data=data, **conf)
        self.token = wrapper.token
        return wrapper


RESPONSES = {"get_login_form": {
    'forms': {'model': {'username': None,
                        'password': None},
              'form': ['username', 'password'],
              'schema': {'required': ['username',
                                      'password'],
                         'type': 'object',
                         'properties': {
                             'username': {
                                 'type': 'string',
                                 'title': 'Username'},
                             'password': {
                                 'type': 'password',
                                 'title': 'Password'}},
                         'title': 'LoginForm'}},
    'is_login': False},
    "successful_login": {u'screen': u'dashboard',
                         u'is_login': True}}

# encrypted form of test password (123)
user_pass = '$pbkdf2-sha512$10000$nTMGwBjDWCslpA$iRDbnITHME58h1/eVolNmPsHVq' \
            'xkji/.BH0Q0GQFXEwtFvVwdwgxX4KcN/G9lUGTmv7xlklDeUp4DD4ClhxP/Q'


class BaseTestCase:
    """
    preapre_client() varsayilan olarak bir kullanici yaratip sisteme giris yapar.
    """
    client = None

    @classmethod
    def prepare_client(self, workflow_name, reset=False, login=True):
        """

        :param workflow_name: change or set workflow name
        :param reset: create a new client
        :param login: login to system
        :return:
        """
        if not self.client or reset:
            self.client = TestClient(workflow_name)
        else:
            self.client.set_workflow(workflow_name)

        if login and self.client.user is None:
            self.client.set_workflow("simple_login")
            abs_role, new = AbstractRole.objects.get_or_create(id=1,
                                                               name='W.C. Hero')
            self.client.user, new = User.objects.get_or_create(
                username='test_user', password=user_pass)
            if new:
                Role(user=self.client.user, abstract_role=abs_role).save()
                sleep(1)
            self._do_login()
            self.client.set_workflow(workflow_name)

    @classmethod
    def _do_login(self):
        resp = self.client.post()


        output = resp.json
        del output['token']
        assert output == RESPONSES["get_login_form"]
        data = {"login_crd": {"username": "user", "password": "123"},
                "cmd": "do"}
        resp = self.client.post(**data)
        output = resp.json
        del output['token']
        assert output == RESPONSES["successful_login"]
        self.client.token = ''
