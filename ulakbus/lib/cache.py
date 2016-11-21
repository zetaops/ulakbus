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

    def __init__(self, guncel_donem):
        super(GuncelDonem, self).__init__(guncel_donem)

    def get_or_create(self):

        from ulakbus.models.ogrenci import Donem

        if self.get():
            return Donem(**self.get())
        else:
            guncel_donem = Donem.objects.get(guncel=True)
            donem_fields = {'ad': guncel_donem.ad,
                            'baslangic_tarihi': guncel_donem.baslangic_tarihi.strftime(
                                "%d.%m.%Y"),
                            'bitis_tarihi': guncel_donem.baslangic_tarihi.strftime(
                                "%d.%m.%Y"),
                            'guncel': guncel_donem.guncel,
                            'key': guncel_donem.key}

            self.set(donem_fields, 3600)
            return guncel_donem

# class Cache(Cache):
#     PREFIX = ''
#
#     overriding of init optional but helpful
#     def __init__(self, ):
#         super(, self).__init__()
