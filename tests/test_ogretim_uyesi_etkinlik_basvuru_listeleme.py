# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPEtkinlikProje
from ulakbus.models import BAPGundem
from ulakbus.models import User

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_ogretim_uyesi_etkinlik_basvuru_listeleme(self):
        user = User.objects.get(username='ogretim_uyesi_1')
        etkinlik_sayisi = BAPEtkinlikProje.objects.all(basvuru_yapan=user.personel.okutman).count()
        self.prepare_client('/bap_ogretim_uyesi_etkinlik_basvuru_listele', user=user)
        resp = self.client.post()
        assert len(resp.json['objects']) == etkinlik_sayisi + 1

        resp = self.client.post(cmd='goruntule', object_id='Yt4VkZQfnt9XEiSnMcZvUKUWSj')

        assert resp.json['object_title'] == 'Bilimsel Etkinliklere Katılım Desteği : Çay ' \
                                            'Yaprağı Paradoksunda Akışkanlar Mekaniğinin Yeri | ' \
                                            'Henife Şener'

        resp = self.client.post(form={'listeye_don': 1})

        assert resp.json['forms']['schema']['title'] == 'Bilimsel Etkinliklere Katılım Destekleri'
