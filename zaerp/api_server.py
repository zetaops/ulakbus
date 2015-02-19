# import logging
from wsgiref import simple_server

import falcon
from beaker.middleware import SessionMiddleware
from beaker import cache as beaker_cache
from beaker_extensions.redis_ import RedisManager

from modules.settings import ENABLED_MIDDLEWARES, SESSION_OPTIONS
from modules.zengine.engine import ZEngine
beaker_cache.clsmap['ext:redis'] = RedisManager

__author__ = 'Evren Esat Ozkan'


class Dispatcher(object):
    # def __init__(self):
    # self.logger = logging.getLogger('dispatch.' + __name__)
    def __init__(self):
        self.engine = ZEngine()

    def __call__(self, req, resp, wf_name):
        self.engine.set_current(request=req, response=resp, workflow_name=wf_name)
        self.engine.load_or_create_workflow()
        self.engine.run()


app = falcon.API(middleware=ENABLED_MIDDLEWARES)

dispatch = Dispatcher()
app.add_route('^(?P<wf_name>\w+)/', dispatch)
app = SessionMiddleware(app, SESSION_OPTIONS)

# Useful for debugging problems in your API; works with pdb.set_trace()
if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
