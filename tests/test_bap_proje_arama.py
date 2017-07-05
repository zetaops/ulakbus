#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from datetime import datetime

from ulakbus.models import BAPProje
from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_proje_arama(self):
        user = User.objects.get(username='ulakbus')
        self.prepare_client('/bap_proje_arama', user=user)
        self.client.post()

        # A1001: Test Proje Tur Adi turu forma eklenir
        form = {
            "proje_turu": "Kvu9MRWA52accYwKfWKegtZr2BA",
            "bitis_tarihi_baslangic": None,
            "bitis_tarihi_bitis": None
        }
        # A1001: Test Proje Tur Adi turundeki proje sayisi alinir
        proje_sayisi = BAPProje.objects.filter(tur_id='Kvu9MRWA52accYwKfWKegtZr2BA').count()

        # Form submit edilir
        resp = self.client.post(form=form)

        # Response'da gorunen proje sayisi ile mevcut proje sayisi kontrol edilir
        if proje_sayisi == 0:
            assert 'objects' not in resp.json
        else:
            assert len(resp.json['objects']) - 1 == proje_sayisi

        # Tarihler forma girilir.
        form = {
            "proje_turu": None,
            "bitis_tarihi_baslangic": "08.06.2017",
            "bitis_tarihi_bitis": "25.06.2017"
        }

        bas = datetime(2017, 6, 8)
        bit = datetime(2017, 6, 25)

        proje_sayisi = BAPProje.objects.filter(bitis_tarihi__range=[bas, bit]).count()

        # Form submit edilir.
        resp = self.client.post(form=form)

        # Response'da gorunen proje sayisi ile mevcut proje sayisi kontrol edilir
        if proje_sayisi == 0:
            assert 'objects' not in resp.json
        else:
            assert len(resp.json['objects']) - 1 == proje_sayisi

        # Aranacak metin girilir.
        aranacak_metin = "robot"
        form = {
            "bitis_tarihi_baslangic": None,
            "bitis_tarihi_bitis": None,
            "aranacak_metin": aranacak_metin
        }

        proje_sayisi = BAPProje.objects.search_on('ad', 'anahtar_kelimeler', 'konu_ve_kapsam',
                                                  contains=aranacak_metin).count()
        # Form submit edilir.
        resp = self.client.post(form=form)

        # Response'da gorunen proje sayisi ile mevcut proje sayisi kontrol edilir
        if proje_sayisi == 0:
            assert 'objects' not in resp.json
        else:
            assert len(resp.json['objects']) - 1 == proje_sayisi