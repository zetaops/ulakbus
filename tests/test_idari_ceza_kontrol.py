# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User, Ceza, Personel
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_idari_ceza_kontrol(self):
        user = User.objects.get(username="ulakbus")
        self.prepare_client('/idari_ceza_kontrol', user=user)
        personel = Personel.objects.get(key="OI3vq7rWIaTdSNUj4KwSBpeHMrc")
        ceza = Ceza(personel=personel, dosya_sira_no="1820201036", baslama_tarihi="27.01.2008", bitis_tarihi="04.01.2012",
                    takdir_edilen_ceza=1)
        ceza.blocking_save()
        ceza = Ceza(personel=personel, dosya_sira_no="1820201037", baslama_tarihi="15.01.2010", bitis_tarihi="03.01.2011",
                    takdir_edilen_ceza=2)
        ceza.blocking_save()
        resp = self.client.post()
        assert resp.json['object_title'] == "Personellere Ait 5 Yılı Geçen Cezaların Listesi"
        data_key = Ceza.objects.filter()[0].key
        resp = self.client.post(cmd="sil", data_key=data_key)
        assert resp.json['forms']['schema']['title'] == "Ceza Silme Onay Form"
        resp = self.client.post(form={'iptal': 1})
        assert resp.json['object_title'] == "Personellere Ait 5 Yılı Geçen Cezaların Listesi"
        resp = self.client.post(cmd="sil", data_key=data_key)
        assert resp.json['forms']['schema']['title'] == "Ceza Silme Onay Form"
        resp = self.client.post(form={'onayla': 1}, cmd="onayla")
        assert resp.json['object_title'] == "Personellere Ait 5 Yılı Geçen Cezaların Listesi"
        data_key = Ceza.objects.filter()[0].key
        resp = self.client.post(cmd="sil", data_key=data_key)
        assert resp.json['forms']['schema']['title'] == "Ceza Silme Onay Form"
        resp = self.client.post(form={'onayla': 1}, cmd="onayla")
        assert resp.json['forms']['schema']['title'] == "Personellere Ait 5 Yılı Geçen Ceza Bulunamadı"
