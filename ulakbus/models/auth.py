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
    username = field.String("Username")
    password = field.String("Password")

    def set_password(self, raw_password):
        self.password = pbkdf2_sha512.encrypt(raw_password, rounds=10000, salt_size=10)

    def check_password(self, raw_password):
        return pbkdf2_sha512.verify(raw_password, self.password)
