# -*-  coding: utf-8 -*-
"""project settings"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
__author__ = 'Evren Esat Ozkan'

import os.path

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# path of the activity modules which will be invoked by workflow tasks
ACTIVITY_MODULES_IMPORT_PATH = 'ulakbus.activities'
# absolute path to the workflow packages
WORKFLOW_PACKAGES_PATH = os.path.join(BASE_DIR, 'workflows')

#PYOKO SETTINGS
RIAK_SERVER = 'localhost'
RIAK_PROTOCOL = 'http'
RIAK_PORT = '8098'

REDIS_SERVER = '127.0.0.1:6379'
