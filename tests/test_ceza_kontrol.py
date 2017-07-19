# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Ceza
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import Personel, User
from dateutil.relativedelta import relativedelta
from datetime import datetime


class TestCase(BaseTestCase):
    def test_ceza_kontrol(self):

        user = User.objects.get(username="ulakbus")
        self.prepare_client('/idari_ceza_kontrol', user=user)
        resp = self.client.post()
        ceza_suresi = datetime.now() - relativedelta(years=5)
        ceza_sayisi = Ceza.objects.filter(baslama_tarihi__lte=ceza_suresi).count()

        if ceza_sayisi < 1:
            assert resp.json['forms']['schema']['title'] == "Ceza Bulunamadı"
        else:
            p = Personel.objects.get(ad="İsmet", soyad="Tarhan")
            c = Ceza(personel=p, dosya_sira_no="9876543210", acilis_tarihi="21.01.2012", baslama_tarihi="03.02.2012",
                     bitis_tarihi="21.04.2017")
            c.save()

            assert resp.json['object_title'] == "Ceza Görüntüleme Formu"
            resp = self.client.post(data_key=c.key, cmd="sil")
            assert resp.json['forms']['schema']['title'] == "Ceza Silme Onay Form"
            resp = self.client.post(form={'iptal': 1}, cmd="iptal")
            assert resp.json['object_title'] == "Ceza Görüntüleme Formu"
            resp = self.client.post(data_key=c.key, cmd="sil")
            resp = self.client.post(form={'onayla': 1}, cmd="onayla")
            if ceza_sayisi==1:
                assert resp.json['forms']['schema']['title'] == "Ceza Bulunamadı"
                c.blocking_delete()
            else:
                assert resp.json['object_title'] == "Ceza Görüntüleme Formu"
                c.blocking_delete()





