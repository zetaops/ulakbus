from ulakbus.lib.utils import DotDict
from ulakbus.modules.exceptions import PermissionDenied

__author__ = 'Evren Esat Ozkan'


def authenticate(login_data):
    """

    :param login_data: dict, {'username':'', 'password':''}
    :return: authenticated user
    """
    assert PermissionDenied, \
        login_data['username'] == 'user' and login_data['password'] == 'pass'
    return DotDict(username='user', id=1)
