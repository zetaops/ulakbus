# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User, ZamanCetveli, DerslikZamanPlani
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def test_zaman_tablo(self):

        usr = User.objects.get(username='ders_programi_koordinatoru_1')
        self.prepare_client('/ogretim_elemani_zaman_tablosu', user=usr)
        resp = self.client.post()
        assert len(resp.json['ogretim_elemani_zt']['uygunluk_durumu']) == 15

        oe_change_key = 'AYgISJuQZftqTFSvkCv2lhDKvea'
        oe_change_durum = 2

        item = {'key': oe_change_key,
                'durum': oe_change_durum}

        self.client.post(cmd='degistir', change=item)
        zc = ZamanCetveli.objects.get(oe_change_key)

        assert zc.durum == 2

        zc.durum = 1
        zc.save()

        item = {'key': '5oumFDZlwPmjGmYpUPi7q7XBQVB'}
        resp = self.client.post(cmd='personel_sec', secili_og_elemani=item)

        assert resp.json['ogretim_elemani_zt']['oe_key'] == '5oumFDZlwPmjGmYpUPi7q7XBQVB'

    def test_derslik_zaman_tablosu(self):
        usr = User.objects.get(username='ders_programi_koordinatoru_1')
        self.prepare_client('/derslik_zaman_tablosu', user=usr)
        resp = self.client.post()
        assert len(resp.json['derslik_zaman_tablosu']) == 4

        derslik_key = '6Gj98J50zhRpqhjEQGlMxrL3SgF'
        derslik_durum = 3

        item = {'key': derslik_key,
                'durum': derslik_durum}

        self.client.post(cmd='kaydet', change=item)

        dz = DerslikZamanPlani.objects.get(derslik_key)
        assert dz.derslik_durum == 3

        dz.derslik_durum = 2
        dz.save()

        item = {'key': 'Rrm9587Fjzf5kMOtZBKn0Nl9UES'}
        resp = self.client.post(cmd='derslik_degistir', secili_derslik=item)

        assert resp.json['derslik_zaman_tablosu']['derslik_key'] == 'Rrm9587Fjzf5kMOtZBKn0Nl9UES'
