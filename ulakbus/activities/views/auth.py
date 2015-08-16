# -*-  coding: utf-8 -*-
"""Authentication views"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import field
from zengine.lib.views import SimpleView

from zengine.lib.exceptions import HTTPBadRequest, HTTPUnauthorized
from ulakbus.models import User
from zengine.lib.forms import JsonForm


class LoginForm(JsonForm):
    TYPES = {'password': 'password'}
    username = field.String("Username")
    password = field.String("Password")


def Logout(current):
    current.session.delete()


class Login(SimpleView):
    def _do(self):
        try:
            username = self.current.input['login_crd']['username']
            password = self.current.input['login_crd']['password']
        except KeyError:
            raise HTTPBadRequest("Eksik bilgi girdiniz",
                                 "Lütfen kullanıcı adınızı ve parolanızı giriniz")
        try:
            self.current.task_data[
                'IS'].login_successful = self.current.auth.authenticate(
                username, password)

        except IndexError:
            raise HTTPUnauthorized('Giriş bilgileri hatalı',
                                   "Girdiğiniz kullanıcı adı ya da parola ile "
                                   "eşleşen bir kullanıcı kaydı bulamadık")

    def _show(self):
        self.current.session['dfdf'] = 'sdfdf'
        # self.current.session.save()
        if 'user_id' not in self.current.session:
            self.current.output['forms'] = LoginForm(
                types={"password": "password"}).serialize()
        else:
            self.current.output['error'] = "Zaten giriş yapmış durumdasınız"
