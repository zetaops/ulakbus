# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'H.İbrahim Yılmaz (drlinux)'


class HitapHelper():
    """Hitap Helper
    Zato bazlı HITAP servisleri arasında paylaşımlı olarak kullanılan metodları barındıran classtır.

    """

    def check_required_data(self, hitap_dict):
        """Gelen ``hitap_dict` içindeki ``required_fields`` sözlük listesi içinde belirtilen servis
        tarafında servis tarafında gerekli olarak tanımlanmış alanların hem ``fields`` sözlüğü
        içinde tanımlı olup olmadığını hem de bu alanların değerinin null olmadığını kontrol
        eder.

        Args:
            hitap_dict (dict) : HITAP servisine gönderilmek üzere hazırlanmış sözlük listesi.

        """
        if hitap_dict['required_fields']:
            for required_field in hitap_dict['required_fields']:
                try:
                    if not hitap_dict['fields'][required_field]:
                        raise ValueError("required %s field's value is null" % (required_field))
                except KeyError:
                    raise KeyError("required field %s not found in hitap service dict" % (
                        required_field))
