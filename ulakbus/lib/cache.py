# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import hashlib
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

    def get_data_to_cache(self):
        """
        Cache'de güncel dönem datası yoksa, get_or_set() metodu kendi içinde bu metodu çağırarak datayı cache'e koyar.
        Sonra da döndürür.
        """
        from ulakbus.models.ogrenci import Donem

        guncel_donem = Donem.objects.get(guncel=True)
        return guncel_donem.donem_fields_to_dict()


class PersonelIstatistik(Cache):
    """

    """
    PREFIX = "PERIST"

    def __init__(self):
        super(PersonelIstatistik, self).__init__('personel_istatistik')

    def get_data_to_cache(self):
        return personel_istatistik_bilgileri()


class AkademikPerformans(Cache):
    """

    """
    PREFIX = "AKAPER"

    def __init__(self):
        super(AkademikPerformans, self).__init__('akademik_performans')

    def get_data_to_cache(self):
        return akademik_performans_hesapla()


class ChoicesFromModel(Cache):
    """

    """
    PREFIX = "CFM"

    def __init__(self, key):
        super(ChoicesFromModel, self).__init__(key, serialize=True)


class DataModel(Cache):
    def __init__(self, model, filters=None):
        self.model = model
        self.filters = filters if filters else {}
        key = self.generate_key()
        super(DataModel, self).__init__(key, serialize=True)

    def generate_key(self):
        kw_string = "".join(["%s%s" % (k, v) for k, v in sorted(self.filters.items())])
        return hashlib.sha256("%s:%s" % (self.model._get_bucket_name(), kw_string)).hexdigest()


class ModelLabelValue(DataModel):
    """

    """
    PREFIX = "MLV"

    def get_data_to_cache(self):
        return [{"value": u.key, "label": u.name} for u in self.model.objects.all(**self.filters)]


class ModelQuery(DataModel):
    """

    """
    PREFIX = "DMQ"

    def get_data_to_cache(self):
        return [{"value": u.key, "label": u.name} for u in self.model.objects.all(**self.filters)]
