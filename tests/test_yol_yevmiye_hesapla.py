# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_yol_yevmiye_hesapla(self):
        user = User.objects.get(username='bap_koordinasyon_birimi_1')
        self.prepare_client('/bap_yol_yevmiye_hesapla', user=user)
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == 'Lütfen Tüm Alanları Eksiksiz Doldurun'
        form_1 = {'konaklama_gun_sayisi': 180, 'yolculuk_km': 1000, 'tasit_ucreti': 90,
                  'yolculuk_gun_sayisi': 1, 'birey_sayisi': 0, 'derece': 7, 'ekgosterge': 1500}

        resp = self.client.post(form=form_1, cmd="hesapla")
        assert resp.json['forms']['schema']['title'] == 'Toplam Masraflar'
        resp = self.client.post(form={'tamam': 1})
        assert resp.json['forms']['schema']['title'] == 'Lütfen Tüm Alanları Eksiksiz Doldurun'


