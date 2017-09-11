# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models.bap.bap import BAPGenel


class TestCase(BaseTestCase):
    def test_bap_kasa_girisi(self):
        # bap_mali_koordinator_1 kullanıcısı alınır.
        user = User.objects.get(username='bap_mali_koordinator_1')
        # Bap Mali listeleme iş akışını başlatır.
        self.prepare_client('/bap_kasa_girisi', user=user)
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == 'Kasa İşlem Geçmişi'
        resp = self.client.post(cmd="ekle")
        assert resp.json['forms']['schema']['title'] == 'Lütfen Kasa Girişi Yapınız'
        resp = self.client.post(form={'para_miktari': 750, 'giris_tarihi': "03.08.2017"},
                                cmd="kaydet")
        assert resp.json['forms']['schema']['title'] == 'Kasa Girişi Onay Form'
        resp = self.client.post(cmd='iptal')
        assert resp.json['forms']['schema']['title'] == 'Kasa İşlem Geçmişi'
        resp = self.client.post(cmd="ekle")
        assert resp.json['forms']['schema']['title'] == 'Lütfen Kasa Girişi Yapınız'
        resp = self.client.post(form={'para_miktari': 750, 'giris_tarihi': "03.08.2017"},
                                cmd="kaydet")
        assert resp.json['forms']['schema']['title'] == 'Kasa Girişi Onay Form'
        resp = self.client.post(cmd='onayla')
        assert resp.json['forms']['schema']['title'] == 'Kasa Giriş Kaydı'
        resp = self.client.post(form={'tamam': 1})
        assert resp.json['forms']['schema']['title'] == 'Kasa İşlem Geçmişi'
