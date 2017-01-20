# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.widgets import personel_istatistik_bilgileri
from ulakbus.lib.akademik_faaliyet import akademik_performans_hesapla
from zengine.lib.cache import Cache


class RolePermissionCache(Cache):
    PREFIX = 'PERM'

    def __init__(self, role_id):
        super(RolePermissionCache, self).__init__(role_id)


class GuncelDonem(Cache):
    """
    Güncel dönemin tutulduğu cache nesnesi.
    """

    PREFIX = 'GUNDON'

    def __init__(self):
        super(GuncelDonem, self).__init__('guncel_donem')

    def get_or_set(self):
        """
        Cache'de güncel dönem datası varsa döndürür.
        Yoksa veritabanından güncel dönemi alıp cache'e set eder.
        Güncel dönem objesi dönemlik değişeceği için, set edilirken
        expire olma süresi 360000 yani 100 saat olarak belirlenmiştir.

        Returns: cache_data(dict): Güncel dönem nesnesinin fieldlarının dict hali.

        """

        from ulakbus.models.ogrenci import Donem

        cache_data = self.get()

        if not cache_data:
            guncel_donem = Donem.objects.get(guncel=True)
            cache_data = guncel_donem.donem_fields_to_dict()
            self.set(cache_data, 360000)

        return cache_data


class PersonelIstatistik(Cache):
    """

    """
    PREFIX = "PERIST"

    def __init__(self):
        super(PersonelIstatistik, self).__init__('personel_istatistik')

    def get_or_set(self):
        cache_data = self.get()

        if not cache_data:
            cache_data = personel_istatistik_bilgileri()
            self.set(cache_data, 8 * 60 * 60)

        return cache_data

class AkademikPerformans(Cache):
    """

    """
    PREFIX = "AKAPER"

    def __init__(self):
        super(AkademikPerformans, self).__init__('akademik_performans')

    def get_or_set(self):
        cache_data = self.get()

        if not cache_data:
            cache_data = akademik_performans_hesapla()
            self.set(cache_data, 8 * 60 * 60)

        return cache_data
