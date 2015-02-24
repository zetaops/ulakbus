# -*-  coding: utf-8 -*-
"""Authentication views"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
__author__ = 'Evren Esat Ozkan'

from falcon.errors import HTTPBadRequest

from zaerp.modules.forms import get_form
from zaerp.modules.auth.student import authenticate


def do_login(current):
    try:
        login_credentials = current.request.context.jsonin.login_crd
    except KeyError:
        raise HTTPBadRequest("Missing login data")
    user = authenticate(login_credentials)
    is_login_successful = bool(user)
    if is_login_successful:
        current.request.context.jsonout = {'success': True}
        current.request.session['user'] = user
    current.task.data['is_login_successful'] = is_login_successful


def show_login(current):
    if 'user' not in current.request.session:
        current.request.context['result']['forms'] = get_form('student_login_form')
    else:
        current.request.context['show_user_message'] = "Zaten giriş yapmış durumdasınız"
