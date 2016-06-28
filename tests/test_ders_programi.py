# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models.ders_programi import GunZamanDilimleri, DataConflictError
from ulakbus.models import Unit
from zengine.lib.test_utils import BaseTestCase
import pytest


class TestCase(BaseTestCase):
    """
        Test GunZamanDilimleri modelinde, ayni gune sahip baslangic saat-dakika ve
        bitis saat-dakika zamanlarini kontrol eder. ilk basta cakismayan bir kayit girilir.
        sonraki girilen zaman dilimlerinin bu kayit ile cakismasi beklenir. En sonda ise
        girilen test datalari silinir.
    """
    def test_ders_programi(self):
        unit = Unit.objects.get('EGGB7oyHWn8gVJnOlvqhzy1YCVV')
        zaman = GunZamanDilimleri()
        zaman.birim = unit
        zaman.gun = 7
        zaman.baslama_saat = '09'
        zaman.baslama_dakika = '12'
        zaman.bitis_saat = '11'
        zaman.bitis_dakika = '45'
        zaman.blocking_save()
        assert zaman.just_created

        with pytest.raises(DataConflictError) as exc:
            zaman1 = GunZamanDilimleri()
            zaman1.birim = unit
            zaman1.gun = 7
            zaman1.baslama_saat = '14'
            zaman1.baslama_dakika = '00'
            zaman1.bitis_saat = '12'
            zaman1.bitis_dakika = '30'
            zaman1.blocking_save()
        assert str(exc.value) in "Baslangic zamani bitis zamanindan buyuk olamaz."

        with pytest.raises(DataConflictError) as exc:
            zaman2 = GunZamanDilimleri()
            zaman2.birim = unit
            zaman2.gun = 7
            zaman2.baslama_saat = '07'
            zaman2.baslama_dakika = '00'
            zaman2.bitis_saat = '09'
            zaman2.bitis_dakika = '30'
            zaman2.blocking_save()
        assert str(exc.value) in "Baslangic bitis zamanlari onceki kayitlar ile cakismaktadir."

        zaman.delete()
        zaman1.delete()
        zaman2.delete()
