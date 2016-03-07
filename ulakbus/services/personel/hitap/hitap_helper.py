# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'H.İbrahim Yılmaz (drlinux)'


class HitapHelper():


    def check_required_data(self, hitap_dict):
        for required_field in hitap_dict['required_fields']:
            try:
                if hitap_dict['fields'][required_field]:
                    pass
                else:
                    raise ValueError("required %s field's value is null" % (required_field))
            except KeyError:
                raise KeyError("required field %s not found in hitap service dict" % (
                    required_field))