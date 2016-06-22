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

    def test_ders_programi(self):
        unit = Unit.objects.get('EGGB7oyHWn8gVJnOlvqhzy1YCVV')
        zaman = GunZamanDilimleri()
        zaman.birim = unit
        zaman.gun = 1
        zaman.baslama_saat = '09'
        zaman.baslama_dakika = '12'
        zaman.bitis_saat = '11'
        zaman.bitis_dakika = '45'
        zaman.save()
        assert zaman.just_created

        with pytest.raises(DataConflictError):
            zaman1 = GunZamanDilimleri()
            zaman1.birim = unit
            zaman1.gun = 1
            zaman1.baslama_saat = '14'
            zaman1.baslama_dakika = '00'
            zaman1.bitis_saat = '12'
            zaman1.bitis_dakika = '30'
            zaman1.save()

        with pytest.raises(DataConflictError):
            zaman2 = GunZamanDilimleri()
            zaman2.birim = unit
            zaman2.gun = 1
            zaman2.baslama_saat = '07'
            zaman2.baslama_dakika = '00'
            zaman2.bitis_saat = '09'
            zaman2.bitis_dakika = '30'
            zaman2.save()

        zaman.delete()
        zaman1.delete()
        zaman2.delete()
