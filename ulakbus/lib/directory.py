# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import os
import datetime

def create_unitime_export_directory():
    current_date = datetime.datetime.now()
    directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
    export_directory = 'bin/dphs/data_exchange/' + directory_name
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)
    return export_directory
