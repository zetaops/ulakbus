# -*-  coding: utf-8 -*-
"""project settings"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.settings import *

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

ZATO_SERVER = os.environ.get('ZATO_SERVER', 'http://localhost:44333')
