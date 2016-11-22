# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.lib.cache import Cache


class RolePermissionCache(Cache):
    PREFIX = 'PERM'

    def __init__(self, role_id):
        super(RolePermissionCache, self).__init__(role_id)


class GuncelDonem(Cache):
    """
    Güncel dönemin tutulduğu cache objesi.
    Cache'de güncel dönem datası varsa datalardan dönem objesi döndürür.
    Yoksa veritabanından güncel dönemi döndürür ve cache'e 1 saatlik güncel dönem datasını koyar.

    """

    PREFIX = 'GUNDON'

    def __init__(self):
        super(GuncelDonem, self).__init__('guncel_donem')

    def get_or_set(self):

        from ulakbus.models.ogrenci import Donem

        cache_data = self.get()

        if not cache_data:
            guncel_donem = Donem.objects.get(guncel=True)
            cache_data = guncel_donem.donem_fields_to_dict()
            self.set(cache_data, 360000)

        return cache_data
