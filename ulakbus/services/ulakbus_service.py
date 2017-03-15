# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zato.server.service import Service
from pyoko.lib.utils import un_camel


class UlakbusService(Service):
    @classmethod
    def get_name(cls):
        return un_camel(cls.__name__, dash='-')
