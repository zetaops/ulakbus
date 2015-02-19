from modules.api_server.middlewares import *


__author__ = 'Evren Esat Ozkan'

SESSION_OPTIONS = {
    'session.cookie_expires': True,
    'session.type': 'ext:redis',
    'session.url': '127.0.0.1:6379',
    'auto': True,
}

ENABLED_MIDDLEWARES = [
    RequireJSON(),
    JSONTranslator(),
    SessionMiddleware(),
]

WORKFLOW_SERVICES_PATH = ''
