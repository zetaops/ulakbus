from pprint import pprint
from zengine.utils import DotDict
from ulakbus.modules.forms import get_form
from ulakbus.server import Connector as workflow_connector
from tests.test_utils import get_worfklow_path
from zengine.engine import ZEngine

__author__ = 'Evren Esat Ozkan'



class MockSessionStore(DotDict):
    def save(self):
        pass

def make_request(session_obj, **kwargs):
    req_dict = DotDict({'context': {'data': {}, 'result': {}}, 'session': session_obj})
    req_dict['context']['data'].update(kwargs)
    return DotDict(req_dict)



def test_simple():
    wfc = workflow_connector()
    session = MockSessionStore()
    req = make_request(session)
    resp = DotDict()
    wfc.on_post(req, resp=resp, wf_name='simple_login')
    assert req['context']['result']['forms'] == get_form('student_login_form')
    req= make_request(session, cmd='do', login_crd={'username':'user', 'password':'pass'})
    pprint(session)
    wfc.on_post(req, resp=DotDict(), wf_name='simple_login')
    # print(session)
    # print(req)
    assert session['user']['username'] == 'user'
    assert req['context']['result']['dashboard'] == 'Dashboard'

