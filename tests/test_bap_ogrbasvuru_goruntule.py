# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_ogrbasvuru_goruntule(self):
        # testin sadece proje özeti kısmı kontrol edildi diger aşamalar zaten test edilmişti
        # Öğretim üyesi kullanıcısı alınır.
        user_ou = User.objects.get(username='ogretim_uyesi_1')
        # Ogretim uyesi başvuru listeleme iş akışını başlatır.
        self.prepare_client('/bap_ogretim_uyesi_basvuru_listeleme', user=user_ou)
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'
        resp = self.client.post(cmd='goruntule', object_id='7cgd0VlkzHg0NKN2qxrvkdvSjcz')
        assert resp.json['forms']['schema']['title'] == 'Proje Özeti'
        resp = self.client.post(cmd='detay')
        assert resp.json['forms']['schema']['title'] == 'Proje Hakkında'
        resp = self.client.post(cmd='iptal')
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'
