# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

def tl_curreny(c):
    return '{:20,.2f}'.format(float(c)).replace(',', '_').replace('.', ',').replace('_', '.')
