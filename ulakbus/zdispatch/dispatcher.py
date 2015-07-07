# -*-  coding: utf-8 -*-
"""falcon dispatcher configuration"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.conf import settings

__author__ = 'Evren Esat Ozkan'

import falcon
from ulakbus.lib.utils import DotDict
from beaker.middleware import SessionMiddleware
import beaker
from beaker_extensions import redis_
from ulakbus.zdispatch import middlewares

beaker.session.type = redis_
beaker.session.url = settings.REDIS_SERVER

SESSION_OPTIONS = {
    'session.cookie_expires': True,
    # 'session.type': redis_,
    # 'session.url': '127.0.0.1:6379',
    'auto': True,
}

ENABLED_MIDDLEWARES = [
    middlewares.RequireJSON(),
    middlewares.JSONTranslator(),
    middlewares.CORS(),
    # middlewares.SessionMiddleware(),
]

class ZRequest(falcon.Request):
    context_type = DotDict

falcon_app = falcon.API(middleware=ENABLED_MIDDLEWARES, request_type=ZRequest)
app = SessionMiddleware(falcon_app, SESSION_OPTIONS, environ_key="session")
