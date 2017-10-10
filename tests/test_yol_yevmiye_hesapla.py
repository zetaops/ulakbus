# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models.personel import Personel


class TestCase(BaseTestCase):
    def test_yol_yevmiye_hesapla(self):
        # derece ve ek_gosterge None gelmemesi için
        self.object = Personel.objects.get(key="UuXR8pmKQNzfaPHB2K5wxhC7WDo")
        user = User.objects.get(username='personel_isleri_1')
        self.prepare_client('/yol_yevmiye_hesapla', user=user)
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == 'Lütfen Tüm Alanları Eksiksiz Doldurun'
        # form için gerekli bilgilerin gönderilmesi
        resp = self.client.post(
            form={'konaklama_gun_sayisi': 180, 'yolculuk_km': 1000, 'tasit_ucreti': 90,
                  'yolculuk_gun_sayisi': 1, 'birey_sayisi': 0},
            cmd="hesapla")
        #buradaki birey_sayisi bakmakla yükümlü olduğu birey sayısıdır
        assert resp.json['forms']['schema']['title'] == 'Toplam Masraflar'
        resp = self.client.post(form={'tamam': 1})
        assert resp.json['forms']['schema']['title'] == 'Lütfen Tüm Alanları Eksiksiz Doldurun'
