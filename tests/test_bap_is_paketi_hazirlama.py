# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPIs, BAPIsPaketi

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_is_paketi_hazirlama(self):
        form = {
            'Isler': [{'ad': 'Test İş',
                       'baslama_tarihi': '2017-04-11T21:00:00.000Z',
                       'bitis_tarihi': '2017-04-15T21:00:00.000Z'}],
            'ad': 'Test iş paketi adı',
            'baslama_tarihi': '10.04.2017',
            'bitis_tarihi': '24.04.2017',
            'kaydet': 1
        }

        self.prepare_client('/bap_is_paketi_hazirlama', username="bap_koordinasyon_birimi_1")
        resp = self.client.post()
        is_paketleri_sayisi = len(resp.json['is_paketi_takvimi']['is_paketleri'])
        self.client.post(form={'yeni_paket': 1})
        resp = self.client.post(form=form)

        assert len(resp.json['is_paketi_takvimi']['is_paketleri']) == is_paketleri_sayisi + 1

        BAPIs.objects.filter(ad='Test İş').delete()
        BAPIsPaketi.objects.filter(ad='Test iş paketi adı').delete()

        self.client.post(form={'yeni_paket': 1})
        form['baslama_tarihi'] = '30.04.2017'
        resp = self.client.post(form=form)

        assert resp.json['msgbox']['title'] == 'Kayıt Başarısız Oldu!'
        assert resp.json['msgbox']['msg'] == 'Bitiş tarihi, başlangıç tarihinden küçük olamaz'
