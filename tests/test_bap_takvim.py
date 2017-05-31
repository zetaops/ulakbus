# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from ulakbus.models import BAPProjeTurleri, BAPTakvim

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_takvim(self):

        proje_turu = BAPProjeTurleri()
        proje_turu.ad = 'test_bap_takvim_proje_turu'
        proje_turu.save()

        self.prepare_client('/bap_takvim', username="bap_koordinasyon_birimi_1")
        resp = self.client.post()
        takvim_sayisi = len(resp.json['objects'])
        genel_takvim_form = {
            'OnemliTarihler': [
                {'aciklama': 1,
                 'baslangic_tarihi': '2017-04-02T21:00:00.000Z',
                 'bitis_tarihi': '2017-06-14T21:00:00.000Z'}],
            'donem': 1,
            'takvim_aciklama': 'Test Genel Takvim Açıklama',
            'kaydet': 1}

        proje_tur_takvim_form = {
            'OnemliTarihler': [
                {'aciklama': 2,
                 'baslangic_tarihi': '2017-04-02T21:00:00.000Z',
                 'bitis_tarihi': '2017-06-14T21:00:00.000Z'},
                {'aciklama': 2,
                 'baslangic_tarihi': '2017-04-02T21:00:00.000Z',
                 'bitis_tarihi': '2017-06-14T21:00:00.000Z'}
            ],
            'ProjeTuru': [
                {'proje_turu_id': proje_turu.key},
            ],
            'donem': 2,
            'takvim_aciklama': 'Test Proje Tur Takvim Ekle 2. Donem',
            'kaydet': 1
        }
        # Genel takvim ekleme
        self.client.post(wf='bap_takvim', form={'genel_takvim': 1}, cmd='add_edit_form')
        resp = self.client.post(form=genel_takvim_form)
        assert takvim_sayisi + 1 == len(resp.json['objects'])

        obj = BAPTakvim.objects.get(takvim_aciklama='Test Genel Takvim Açıklama')

        # Duzenleme
        self.client.post(wf='bap_takvim', object_id=obj.key, cmd='add_edit_form')
        genel_takvim_form['OnemliTarihler'][0]['aciklama'] = 2
        genel_takvim_form['donem'] = 2
        genel_takvim_form['takvim_aciklama'] = 'Test Genel Takvim Açıklama Düzenlenme'

        self.client.post(form=genel_takvim_form)

        obj.reload()

        assert obj.OnemliTarihler[0].aciklama == 2
        assert obj.donem == 2
        assert obj.takvim_aciklama == 'Test Genel Takvim Açıklama Düzenlenme'

        # silme
        self.client.post(wf='bap_takvim', object_id=obj.key, cmd='confirm_deletion')
        resp = self.client.post(form={'confirm': 1}, cmd='delete')
        assert takvim_sayisi == len(resp.json['objects'])

        ##################

        # proje turune gore takvim ekleme
        self.client.post(wf='bap_takvim', form={'proje_tur_takvim': 1}, cmd='add_edit_form')
        resp = self.client.post(form=proje_tur_takvim_form)
        assert takvim_sayisi + 1 == len(resp.json['objects'])

        obj = BAPTakvim.objects.get(takvim_aciklama='Test Proje Tur Takvim Ekle 2. Donem')

        # Duzenleme
        self.client.post(wf='bap_takvim', object_id=obj.key, cmd='add_edit_form')
        proje_tur_takvim_form['OnemliTarihler'] = [{'aciklama': 2,
                                                    'baslangic_tarihi': '2017-04-02T21:00:00.000Z',
                                                    'bitis_tarihi': '2017-06-14T21:00:00.000Z'}]
        proje_tur_takvim_form['takvim_aciklama'] = 'Test Proje Tür Takvim Ekle 2. Dönem Düzenleme'

        self.client.post(form=proje_tur_takvim_form)

        obj.reload()

        assert len(obj.OnemliTarihler) == 1
        assert obj.takvim_aciklama == 'Test Proje Tür Takvim Ekle 2. Dönem Düzenleme'

        # silme
        self.client.post(wf='bap_takvim', object_id=obj.key, cmd='confirm_deletion')
        resp = self.client.post(form={'confirm': 1}, cmd='delete')
        assert takvim_sayisi == len(resp.json['objects'])

        proje_turu.blocking_delete()
