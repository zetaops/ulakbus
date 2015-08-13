# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import field
from pyoko.model import Model
from passlib.hash import pbkdf2_sha512


class User(Model):
    username = field.String("Username", index=True)
    password = field.String("Password")

    def __unicode__(self):
        return "User %s" % self.username

    def __repr__(self):
        return "User_%s" % self.key

    def set_password(self, raw_password):
        self.password = pbkdf2_sha512.encrypt(raw_password, rounds=10000,
                                              salt_size=10)

    def check_password(self, raw_password):
        return pbkdf2_sha512.verify(raw_password, self.password)

    def get_permissions(self):
        return []

    def has_permission(self, perm):
        return False


class AuthBackend(object):
    def __init__(self, session):
        self.session = session


    def get_user(self):
        if self.session:
            if 'user_data' in self.session:
                self.user = User()
                self.user.set_data(self.session['user_data'])
                if 'user_id' in self.session:
                    self.user.key = self.session['user_id']
            elif 'user_id' in self.session:
                self.user = User.objects.get(self.session['user_id'])
        else:
            self.user = User()
        return self.user

    def set_user(self, user):
        self.user = user
        self.session['user_id'] = self.user.key
        self.session['user_data'] = self.user.clean_data()
        self.session['user_permissions'] = self.user.get_permissions()

    def authenticate(self, username, password):
        user = User.objects.filter(username=username).get()
        is_login_successful = user.check_password(password)
        if is_login_successful:
            self.set_user(user)
        return is_login_successful
