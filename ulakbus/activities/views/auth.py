# -*-  coding: utf-8 -*-
"""Authentication views"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import field
from ulakbus.lib.views import SimpleView

from falcon.errors import HTTPBadRequest, HTTPUnauthorized
from ulakbus.models import User
from ulakbus.modules.forms import AngularForm


class LoginForm(AngularForm):
    TYPES = {'password': 'password'}
    username = field.String("Username")
    password = field.String("Password")


def Logout(current):
    current.request.env['session'].delete()


class Login(SimpleView):
    def _do(self):
        try:
            username = self.current['request'].context['data']['login_crd']['username']
            password = self.current['request'].context['data']['login_crd']['password']
        except KeyError:
            raise HTTPBadRequest("Eksik bilgi girdiniz",
                                 "Lütfen kullanıcı adınızı ve parolanızı giriniz")
        try:
            user = User.objects.filter(username=username).get()

            is_login_successful = user.check_password(password)
            if is_login_successful:
                # self.current.request.context['result'] = {'success': True}
                self.current.request.env['session']['user_id'] = user.key
            self.current['task'].data['IS'].login_successful = is_login_successful

        except IndexError:
            raise HTTPUnauthorized('Giriş bilgileri hatalı',
                                   "Girdiğiniz kullanıcı adı ya da parola ile eşleşen bir "
                                   "kullanıcı kaydı bulamadık")

    def _show(self):
        if 'user_id' not in self.current['request'].env['session']:
            self.current['request'].context['result']['forms'] = LoginForm(
                types={"password": "password"}).serialize()
        else:
            self.current['request'].context['result']['error'] = "Zaten giriş yapmış durumdasınız"
