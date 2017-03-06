# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time
from ulakbus.models import Personel
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def test_yeni_personel(self):

        self.prepare_client('/personel_yeni_personel', username='personel_isleri_1')

        self.client.post()
        resp = self.client.post(form={'tckn': '12345678911'})

        assert resp.json['msgbox']['title'] == "Personel Kayıt Uyarısı"
        assert resp.json['object']['fields'][0][u'Kişi Bilgileri'] == u"""**Adı**: Ali
                              **Soyad**: Atabak
                              **Doğum Tarihi**: 01.01.1992
                              """
        assert resp.json['object']['fields'][0][u'Adres Bilgileri'] == u"""**İl**: Izmir
                             **İlçe**: Urla
                             **Adres**: Test acik adres
                             """
        resp = self.client.post(cmd='kaydet')

        assert resp.json['msgbox']['title'] == u'Ali Atabak Başarı İle Kaydedildi'

        time.sleep(1)
        Personel.objects.get(tckn="12345678911").blocking_delete()
