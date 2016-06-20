# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models import OgrenciProgram, Donem, DonemDanisman, Ogrenci
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.
    """

    def test_danisman_atama(self):
        """
        Danışman atama iş akışının ilk adımında öğrenci programı seçilir.

        Seçilen öğrenciye ait veritabanından dönen öğrenci programı sayısı ile
        sunucudan dönen öğrenci program sayısının eşitliği karşılaştırılıp test edilir.

        İkinci adımında ise atanacak danışman seçilir.

        Veritabanından dönen danışmanların sayısı ile sunucudan dönen danışmaların sayısının
        eşitliği karşılaştırılıp test edilir.

        Üçüncü adımında ise danışman kaydedilir.

        Mesaj kutusunda danışman ataması yapılan öğrencinin ad ve soyad bilgilerinin olup
        olmadığı test edilir.

        """

        # Kullanıcıya login yaptırılır.
        self.prepare_client('/danisman_atama', username='bolum_baskani_1')

        resp = self.client.post(id="RnKyAoVDT9Hc89KEZecz0kSRXRF",
                                model="OgrenciProgram",
                                param="ogrenci_id",
                                wf="danisman_atama",
                                filters={'ogrenci_id': {'values': ["KhFizqvCaZGtTloAZoPH1Uy98Pw"],
                                                        'type': "check"}})

        # Öğrenciye ait programlar db'den seçilir.
        op = OgrenciProgram.objects.filter(ogrenci_id='RnKyAoVDT9Hc89KEZecz0kSRXRF')

        # Veritabanından öğrenciye ait  çekilen program sayısı ile sunucudan dönen program sayısının
        # eşitliği karşılaştırılıp test edilir.
        assert len(resp.json['forms']['form'][2]['titleMap']) == len(op)

        # Öğrenci programı seçilir.
        resp = self.client.post(model='OgrenciProgram',
                                form={'program': "UEGET7qn9CDj9VEj4n0nbQ7m89d", 'sec': 1})

        guncel_donem = Donem.objects.filter(guncel=True)[0]
        # Öğrencinin kayıtlı olduğu öğrenci programlarından biri seçilir.
        program = op[0]
        # Döneme ve birime kayıtlı olan danışmanların listesini tutar.
        donem_danisman = DonemDanisman.objects.filter(donem=guncel_donem,
                                                      bolum=program.program.birim)

        # Veritabanından dönen dönem danışmanların sayısı ile sunucudan dönen dönem  danışmanlarının
        # sayısının eşitliğini karşılaştırıp test eder.
        assert len(donem_danisman) == len(resp.json['forms']['form'][2]['titleMap'])

        # Danışman seçilir.
        resp = self.client.post(model='OgrenciProgram',
                                form={'donem_danisman': 'Ids7zUWiSyeTC1qHmAFfqFCIWBV', 'sec': 1})

        ogrenci = Ogrenci.objects.get('RnKyAoVDT9Hc89KEZecz0kSRXRF')
        assert ogrenci.ad + ' ' + ogrenci.soyad in resp.json['msgbox']['msg']
