# -*-  coding: utf-8 -*-
import os
from time import sleep
from pyoko.model import model_registry
from werkzeug.test import Client
from zengine.log import getlogger
from zengine.server import app
from ulakbus.models import User, AbstractRole, Role



def get_worfklow_path(wf_name):
    return "%s/workflows/%s.zip" % (
        os.path.dirname(os.path.realpath(__file__)), wf_name)


from pprint import pprint
import json

# TODO: TestClient and BaseTestCase should be moved to Zengine,
# but without automatic handling of user logins

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
        """
        this is a wsgi test client based on werkzeug.test.Client

        :param str workflow: workflow name
        """
        self.workflow = workflow
        self._client = Client(app, response_wrapper=RWrapper)
        self.user = None
        self.token = None

    def set_workflow(self, workflow):
        self.workflow = workflow
        self.token = ''

    def post(self, conf=None, **data):
        """
        by default data dict encoded as json and
        content type set as application/json

        :param dict conf: additional configs for test client's post method.
                          pass "no_json" in conf dict to prevent json encoding
        :param data: post data,
        :return: RWrapper response object
        :rtype: RWrapper
        """
        conf = conf or {}
        make_json = not conf.pop('no_json', False)
        if make_json:
            conf['content_type'] = 'application/json'
            if 'token' not in data and self.token:
                data['token'] = self.token
            data = json.dumps(data)
        response_wrapper = self._client.post(self.workflow, data=data, **conf)
        # update client token from response
        self.token = response_wrapper.token
        return response_wrapper


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
    log = getlogger()
    @classmethod
    def prepare_client(self, workflow_name, reset=False, login=True):
        """
        setups the workflow, logins if necessary

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
                {"password": user_pass}, username='test_user')
            if new:
                Role(user=self.client.user, abstract_role=abs_role).save()
                sleep(1)
            self._do_login()
            self.client.set_workflow(workflow_name)

    @classmethod
    def _do_login(self):
        """
        logs in the test user with test client

        """
        resp = self.client.post()
        output = resp.json
        del output['token']
        assert output == RESPONSES["get_login_form"]
        data = {"login_crd": {"username": "test_user", "password": "123"},
                "cmd": "do"}
        resp = self.client.post(**data)
        output = resp.json
        del output['token']
        assert output == RESPONSES["successful_login"]

