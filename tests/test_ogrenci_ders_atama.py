# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import OgrenciProgram, OgrenciDersi, Donem
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_ogrenci_ders_atama(self):
        """
        Öğrenci ders atama iş akışının ilk adımında öğrencinin
        kayıtlı olduğu programlardan biri seçilir.

        Veritabanından öğrenciye ait  çekilen program sayısı ile
        sunucudan dönen program sayısının eşitliği karşılaştırılıp
        test edilir.

        Veritabanından öğrenciye ait çekilen öğrenci dersi sayısı
        ile sunucudan dönen öğrenci dersi sayısının eşitliği
        karşılaştırılıp test edilir.

        İkinci adımında öğrencinin kayıtlı olduğu dersler listelenir
        ve yeni ders eklenir.

        Eklenen ders öğrencinin kayıtlı olduğu derslerde yok ise:

        - Ders kaydının eklenip eklenmediğ test edilir.
        - Sunucudan dönen cevapta msgbox'ın olup olmadığı test edilir.

        Eklenen ders öğrencinin kayıtlı olduğu derslerde var ise;
        ``self.client.current.task_data['cmd'] = 'ders_listele'`` olması beklenir.

        """
        # Kullanıcıya login yaptırılır.
        self.prepare_client('/ogrenci_ders_atama', username='ogrenci_isleri_1')
        resp = self.client.post(id="RnKyAoVDT9Hc89KEZecz0kSRXRF",
                                param="ogrenci_id",
                                filters={'ogrenci_id': {'values': ["RnKyAoVDT9Hc89KEZecz0kSRXRF"],
                                                        'type': "check"}})

        # Öğrencinin kayıtlı olduğu programlar.
        op = OgrenciProgram.objects.filter(ogrenci_id="RnKyAoVDT9Hc89KEZecz0kSRXRF")

        # Veritabanından öğrenciye ait  çekilen program sayısı ile
        # sunucudan dönen program sayısının eşitliği karşılaştırılıp test edilir.
        assert len(resp.json['forms']['form'][2]['titleMap']) == len(op)

        # Öğrenci programı seçilir.
        resp = self.client.post(form={'program': "UEGET7qn9CDj9VEj4n0nbQ7m89d", 'sec': 1})

        # Öğrencinin kayıtlı olduğu dersler.
        od = OgrenciDersi.objects.filter(ogrenci_program_id="UEGET7qn9CDj9VEj4n0nbQ7m89d",
                                         donem=Donem.guncel_donem())

        len_of_od = len(od)

        # Veritabanından öğrenciye ait  çekilen öğrenci dersi sayısı ile
        # sunucudan dönen öğrenci dersi sayısının eşitliği karşılaştırılıp
        # test edilir.

        assert len(resp.json['forms']['model']['Dersler']) == len_of_od

        # Yeni ders kaydı eklenir.
        dersler = [{'ders_adi': "Hukuk Stajı-A110 175", 'key': "TumPjkBBhmLfr6OliLR4GEVpfzi"},
                   {'key': "8G8yOtYattpuxjLbX8SkrAQS2D0",
                    'ders_adi': "İmalat Sistemlerinde Rassal Modeller-A509 25"}, ]

        resp = self.client.post(form={'ileri': 1, 'Dersler': dersler})

        # Sunucudan dönen cevapta msgbox'ın olup olmadığı test edilir.
        assert 'msgbox' in resp.json

        ogrenci_dersi = OgrenciDersi.objects.filter(
            ogrenci_program_id="UEGET7qn9CDj9VEj4n0nbQ7m89d", donem=Donem.guncel_donem())
        time.sleep(1)

        # Dersin kaydeilip kaydedilmediği test edilir.
        assert len(ogrenci_dersi) == len_of_od + 2

        # İş akışı tekrardan başlatılır.
        self.client.set_path('/ogrenci_ders_atama')
        self.client.post(
            id="RnKyAoVDT9Hc89KEZecz0kSRXRF",
            param="ogrenci_id",
            filters={'ogrenci_id': {'values': ["RnKyAoVDT9Hc89KEZecz0kSRXRF"], 'type': "check"}})
        # Öğrenci programı seçilir.
        self.client.post(form={'program': "UEGET7qn9CDj9VEj4n0nbQ7m89d", 'sec': 1})

        # Öğrencinin kayıtlı olduğu derslerden biri tekrar seçilir.
        dersler = [{'ders_adi': "Hukuk Stajı-A110 175", 'key': "TumPjkBBhmLfr6OliLR4GEVpfzi"},
                   {'key': "8G8yOtYattpuxjLbX8SkrAQS2D0",
                    'ders_adi': "İmalat Sistemlerinde Rassal Modeller-A509 25"},
                   {'key': "JVyg2mfRPpprbrIqndCtaIq69js",
                    'ders_adi': "İmalat Sistemlerinde Rassal Modeller-M105 199"}]

        self.client.post(form={'ileri': 1, 'Dersler': dersler})

        # ders_listele adımında olup olmadığı test edilir.
        assert self.client.current.task_data['cmd'] == 'ders_listele'

        # İş akışı tekrardan başlatılır.
        self.client.set_path('/ogrenci_ders_atama')
        self.client.post(
            id="RnKyAoVDT9Hc89KEZecz0kSRXRF",
            param="ogrenci_id",
            filters={'ogrenci_id': {'values': ["RnKyAoVDT9Hc89KEZecz0kSRXRF"], 'type': "check"}})

        # Öğrenci programı seçilir.
        self.client.post(form={'program': "UEGET7qn9CDj9VEj4n0nbQ7m89d", 'sec': 1})

        # Öğrencinin kayıtlı olduğu derslerden biri formdan kaldırılır,
        # aynı derse ait başka sube eklenir.
        dersler = [{'key': "3VIGIsbbms9F2tyA0FQASIhDC8M", 'ders_adi': "Hukuk Stajı-C607 290"},
                   {'key': "8G8yOtYattpuxjLbX8SkrAQS2D0",
                    'ders_adi': "İmalat Sistemlerinde Rassal Modeller-A509 25"}]

        self.client.post(form={'ileri': 1, 'Dersler': dersler})

        # ders_listele adımında olup olmadığı test edilir.
        assert self.client.current.task_data['cmd'] == 'ders_listele'

        # test sonucu eklenen datalar silinir.
        OgrenciDersi.objects.filter(sube_id='TumPjkBBhmLfr6OliLR4GEVpfzi').delete()
        OgrenciDersi.objects.filter(sube_id='8G8yOtYattpuxjLbX8SkrAQS2D0').delete()
