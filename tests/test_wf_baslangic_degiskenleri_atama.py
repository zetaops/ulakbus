# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.cache import GuncelDonem
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models.ogrenci import Donem


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.
    """

    def test_wf_baslangic_ve_guncel_donem   (self):
        # guncel_donem_degistirme iş akışının propertysi test için init= True olarak belirlenmiştir.
        self.prepare_client('guncel_donem_degistirme', username='ulakbus')

        # İş akışı başlatılır.
        self.client.post()

        # 'wf_initial_values' keyinin olduğu kontrol edilir.
        assert 'wf_initial_values' in self.client.current.task_data

        # 'guncel_donem' keyinin olduğu kontrol edilir.
        assert 'guncel_donem' in self.client.current.task_data['wf_initial_values']

        # 'start_date' keyinin olduğu kontrol edilir.
        assert 'start_date' in self.client.current.task_data['wf_initial_values']

        # guncel_donem hesaplanırken parametre olarak current verilirse ve
        # 'wf_init_variables' içerisinde guncel_donem bilgisi varsa bu bilgi kullanılır.
        assert Donem.guncel_donem(self.client.current).key == \
               self.client.current.task_data['wf_initial_values']['guncel_donem']

        # Test başlamadan önce cache içerisinde bulunan data yedeklenir.
        cache_data = GuncelDonem('guncel_donem').get()

        # Cache temizlenir.
        GuncelDonem('guncel_donem').delete()

        # Temizlendiği kontrol edilir.
        assert GuncelDonem('guncel_donem').get() == None

        # Güncel dönem getirilir.
        guncel_donem = Donem.guncel_donem()

        # Dönemin veritabanından doğru getirildiği kontrol edilir.
        assert guncel_donem.key == Donem.objects.get(guncel=True).key

        # Güncel dönem veritabanından getirilirken, güncel dönem bilgisı cache'e de koyulur.
        # Cache'in boş olmadığı kontrol edilir.
        assert GuncelDonem('guncel_donem').get() is not None

        # Cache'e koyulan dönem bilgisinin güncel dönem olduğu kontrol edilir.
        assert GuncelDonem('guncel_donem').get()['key'] == guncel_donem.key

        # Güncel olmayan herhangi bir dönem alınır.
        guncel_olmayan_donem = Donem.objects.filter(guncel=False)[0]

        # Güncel dönem ile güncel olmayan dönemin farklı olduğu kontrol edilir.
        assert guncel_olmayan_donem.key != guncel_donem.key

        # Güncel olmayan bu bölümün veritabanı key bilgisi cache'e koyulur.
        GuncelDonem('guncel_donem').set({'key': guncel_olmayan_donem.key}, 1000)

        # Güncel dönem sorgusu yapıldığında, cache'de varsa önceliğin cache olduğu kontrol edilir.
        donem = Donem.guncel_donem()

        # Dönen dönemin sonucu cache'de bulunan dönem olduğu kontrol edilir.
        assert donem.key == guncel_olmayan_donem.key

        # propertysi olmayan bir iş akışı seçilir.
        self.prepare_client('zaman_dilimi_duzenle', username='ulakbus')

        # iş akışı başlatılır.
        self.client.post()

        # current task_data içerisinde 'wf_initial_values' keyinin olmadığı kontrol edilir.
        assert 'wf_initial_values' not in self.client.current.task_data

        # Yedeklenen cache datası tekrardan yerine koyulur.
        GuncelDonem('guncel_donem').set(cache_data,3600)
