# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Ceza, HizmetKurs
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import Personel
from ulakbus.lib.cache import HitapPersonelGirisBilgileri


class TestCase(BaseTestCase):
    def test_hitap_islemleri(self):
        personel_id = "OI3vq7rWIaTdSNUj4KwSBpeHMrc"
        personel = Personel.objects.get(personel_id)

        HitapPersonelGirisBilgileri(personel_id).delete()
        self.prepare_client('/hitap_islemleri', username='ulakbus')
        resp = self.client.post(id=personel_id, model="HizmetKurs", param="personel_id",
                                wf="hitap_islemleri")
        assert resp.json['forms']['schema']['title'] == "Hitap Servisi Giriş Bilgileri"
        resp = self.client.post(form={"hitap_k_adi": 'asada',"hitap_parola": 'as','ilerle':1})
        assert resp.json['forms']['schema']['title'] == "İşlem Seçeneği"

        self.prepare_client('/hitap_islemleri', username='ulakbus')
        resp = self.client.post(id=personel_id, model="HizmetKurs", param="personel_id",
                                wf="hitap_islemleri")
        assert resp.json['forms']['schema']['title'] == "İşlem Seçeneği"

        kayit_sayisi = HizmetKurs.objects.filter(personel_id=personel_id,sync=1).count()

        resp = self.client.post(form={"hitap_bilgileri": 1}, cmd='hitap_bilgileri')
        assert len(resp.json['forms']['objects']) == kayit_sayisi + 1
        assert resp.json['forms']['schema']['title'] == "Hitap Kurs Bilgileri"
        assert resp.json['forms']['schema']['properties']['senkronize']['title'] == "Hitap İle Senkronize Et"











