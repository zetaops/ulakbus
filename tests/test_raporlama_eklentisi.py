# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Personel
from zengine.lib.test_utils import BaseTestCase
import datetime
from pyoko.manage import FlushDB, LoadData


class TestCase(BaseTestCase):
    def test_rapor_query(self):

        FlushDB(model='Personel').run()

        Personel(ad="İzzet", soyad="Altınmeşe", cinsiyet=1,
                 unvan=42648, dogum_tarihi=datetime.date(1950, 1, 1)).blocking_save()

        Personel(ad="Belkıs", soyad="Akkale", cinsiyet=2,
                 unvan=3975, dogum_tarihi=datetime.date(1960, 1, 1)).blocking_save()

        Personel(ad="Muazzez", soyad="Abacı", cinsiyet=2,
                 unvan=42648, dogum_tarihi=datetime.date(1947, 1, 1)).blocking_save()

        Personel(ad="Müslüm", soyad="Gürses", cinsiyet=1,
                 unvan=3975, dogum_tarihi=datetime.date(1954, 1, 1)).blocking_save()

        Personel(ad="Hakkı", soyad="Bulut", cinsiyet=1,
                 unvan=42647, dogum_tarihi=datetime.date(1950, 1, 1)).blocking_save()

        a = datetime.date(1950, 1, 1)
        b = datetime.date(1980, 1, 1)
        unvan_list = [3975, 42647]

        assert Personel.objects.filter(ad__startswith='M', cinsiyet=1, unvan__in=unvan_list, dogum_tarihi__range=[a, b])\
            .count() == 1

        assert Personel.objects.filter(ad__startswith='Ah', cinsiyet=2, unvan__in=[1, 2], dogum_tarihi__range=[a, b])\
            .count() == 0

        assert Personel.objects.filter(cinsiyet=2, dogum_tarihi__range=[a, b]).count() == 1

        assert Personel.objects.filter(cinsiyet=1, dogum_tarihi__range=[a, b], unvan__in=unvan_list).count() == 2

        FlushDB(model='Personel').run()

        LoadData(path="fixtures/personel.csv", update=True).run()








