from pprint import pprint
from time import sleep
from zengine.utils import DotDict
from ulakbus.activities.views.auth import LoginForm
from ulakbus.models import User
from ulakbus.server import Connector as workflow_connector

__author__ = 'Evren Esat Ozkan'


class MockSessionStore(DotDict):
    def save(self):
        pass


def make_request(session_obj, **kwargs):
    req_dict = DotDict({'context': {'data': {}, 'result': {}}, 'env': {'session': session_obj}})
    req_dict['context']['data'].update(kwargs)
    return DotDict(req_dict)


def test_add_user_then_login():
    existing = list(User.objects.filter(username='test_user').data())
    if existing:
        existing[0].delete()
        sleep(1)
    u = User(username='test_user')
    u.set_password('123123')
    u.save()
    sleep(1)
    wfc = workflow_connector()
    session = MockSessionStore()
    req = make_request(session)
    resp = DotDict()
    wfc.on_post(req, resp=resp, wf_name='simple_login')
    assert req['context']['result']['forms'] == LoginForm().serialize()
    req = make_request(session, cmd='do',
                       login_crd={'username': 'test_user', 'password': '123123'})
    wfc.on_post(req, resp=DotDict(), wf_name='simple_login')
    assert session['user_id'] == u.key
    assert req['context']['result']['screen'] == 'dashboard'
