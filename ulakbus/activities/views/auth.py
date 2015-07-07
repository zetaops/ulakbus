# -*-  coding: utf-8 -*-
"""Authentication views"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import field
from ulakbus.lib.views import SimpleView

from falcon.errors import HTTPBadRequest
from ulakbus.models import User
from ulakbus.modules.forms import AngularForm

class LoginForm(AngularForm):
    username = field.String("Username")
    password = field.String("Password")

class Login(SimpleView):

    def _do(self):
        try:
            login_credentials = self.current['request'].context['data']['login_crd']
        except KeyError:
            raise HTTPBadRequest("Missing login data")
        user = User.objects.filter(username=login_credentials['username']).get()

        is_login_successful = user.check_password(login_credentials['password'])
        if is_login_successful:
            # self.current.request.context['result'] = {'success': True}
            self.current.request.env['session']['user_id'] = user.key
            self.current.request.env['session'].save()
        self.current['task'].data['is_login_successful'] = is_login_successful

    def _show(self):
        if 'user' not in self.current['request'].env['session']:
            self.current['request'].context['result']['forms'] = LoginForm().serialize()
        else:
            self.current['request'].context[
                'show_user_message'] = "Zaten giriş yapmış durumdasınız"
