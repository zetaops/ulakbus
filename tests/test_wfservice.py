from tests.test_utils import get_worfklow_path
from zengine.engine import ZEngine

__author__ = 'Evren Esat Ozkan'


def test_simple():
    wf3 = ZEngine(get_worfklow_path('simple_login'), )
    result = wf3.run()

    assert True == result
