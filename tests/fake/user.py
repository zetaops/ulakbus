# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User
from .general import fake

__author__ = 'Ali Riza Keles'


def new_user(username=None, password=None, superuser=False):
    user = User(
            username=username or fake.user_name(),
            password=password or fake.password(),
            superuser=superuser
    )
    user.save()
    return user
