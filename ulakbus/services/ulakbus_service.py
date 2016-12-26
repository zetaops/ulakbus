from zato.server.service import Service
from pyoko.lib.utils import un_camel


class UlakbusService(Service):

    @classmethod
    def get_name(cls):
        return un_camel(cls.__name__, dash='-')
