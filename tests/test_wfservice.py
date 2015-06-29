from zengine.utils import DotDict
from modules.forms import get_form
from server import Connector as workflow_connector
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
    req = make_request(session, do='show')
    wfc.on_post(req, resp=DotDict(), wf_name='simple_login')
    assert req['context']['result']['forms'] == get_form('student_login_form')
    make_request(session, do='do')
    wfc.on_post(req, resp=DotDict(), wf_name='simple_login')
    assert True
