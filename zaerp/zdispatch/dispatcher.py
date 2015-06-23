# -*-  coding: utf-8 -*-
"""falcon dispatcher configuration"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
__author__ = 'Evren Esat Ozkan'

import falcon
from zaerp.lib.utils import DotDict
from beaker.middleware import SessionMiddleware
from beaker_extensions import redis_
from zaerp.zdispatch import middlewares

SESSION_OPTIONS = {
    'session.cookie_expires': True,
    'session.type': redis_,
    'session.url': '127.0.0.1:6379',
    'auto': True,
}

ENABLED_MIDDLEWARES = [
    middlewares.RequireJSON(),
    middlewares.JSONTranslator(),
    middlewares.SessionMiddleware(),
]

class ZRequest(falcon.Request):
    context_type = DotDict

falcon_app = falcon.API(middleware=ENABLED_MIDDLEWARES, request_type=ZRequest)
app = SessionMiddleware(falcon_app, SESSION_OPTIONS)
