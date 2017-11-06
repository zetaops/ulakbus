# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from ulakbus.models import BAPProjeTurleri

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_proje_turleri(self):
        object_id = ''
        self.prepare_client('/bap_proje_turleri', username="bap_koordinasyon_birimi_1")
        resp = self.client.post()
        proje_turleri_sayisi = len(resp.json['objects'])
        for i in range(2):
            form = {'aciklama': "Test Aciklama",
                    'ad': "Test Tur Ad",
                    'butce_ust_limit': 2500,
                    'ileri': 1,
                    'kod': "Test Proje Tur Kod",
                    'max_sure': 8,
                    'min_sure': 4,
                    'gerceklestirme_gorevlisi_yurutucu_ayni_mi':True}

            belge_form = {'Belgeler': [{'ad': "Test Proje Turu Belge", 'gereklilik': True}],
                          'ileri': 1}

            form_sec_form = {'BapFormListesi': [{'ad': "Test Form",
                                                 'file': None,
                                                 'gereklilik': True,
                                                 'sec': True}],
                             'ileri': 1}

            object_form = {u'Projede Kullanılacak Belgeler': "Test Proje Turu Belge(Zorunlu)",
                           u'Projede Kullanılacak Formlar': "Test Form (Zorunlu)",
                           u'Proje tür kodu': "Test Proje Tur Kod",
                           u'Proje türüne dair açıklama': "Test Aciklama",
                           u'Proje türünün Adı': "Test Tur Ad",
                           u'Projenin maximum süreceği ay sayısı': "8",
                           u'Projenin minumum süreceği ay sayısı': "4",
                           u'Projenin üst limiti': "2500.0",
                           u"Projenin gerçekleştirme görevlisi ile yürütücüsü aynı kişi mi?":'Evet'}

            if i == 0:
                self.client.post(cmd='add_edit_form', form={'add': 1})
            else:
                resp = self.client.post(wf='bap_proje_turleri', cmd='add_edit_form',
                                        object_id=object_id)

                assert resp.json['forms']['model']['kod'] == "Test Proje Tur Kod"
                form['min_sure'] = 5
                belge_form['Belgeler'][0]['gereklilik'] = False
                object_form[u'Projede Kullanılacak Belgeler'] = "Test Proje Turu Belge(Zorunlu Değil)"
                object_form[u'Projede Kullanılacak Formlar'] = "Test Form (Zorunlu)"
                object_form[u'Projenin minumum süreceği ay sayısı'] = "5"

            resp = self.client.post(wf='bap_proje_turleri', form=form)

            assert 'Belgeler' in resp.json['forms']['model']

            resp = self.client.post(wf='bap_proje_turleri',
                                    form=belge_form)

            assert 'BapFormListesi' in resp.json['forms']['model']

            resp = self.client.post(wf='bap_proje_turleri',
                                    form=form_sec_form)

            assert proje_turleri_sayisi + 1 == len(resp.json['objects'])
            proje_tur_filter = {'kod': 'Test Proje Tur Kod',
                                'ad': 'Test Tur Ad',
                                'min_sure': 4,
                                'max_sure': 8,
                                'butce_ust_limit': 2500}
            if i == 1:
                proje_tur_filter['min_sure'] = 5

            time.sleep(1)

            proje_turu = BAPProjeTurleri.objects.filter(**proje_tur_filter)

            object_id = proje_turu[0].key

            resp = self.client.post(wf='bap_proje_turleri', cmd='show', object_id=object_id)

            for key, value in resp.json['object'].items():
                 assert object_form[key] == value
            self.client.post(wf='bap_proje_turleri', object_key=object_id, form={'tamam': 1})

        self.client.post(wf='bap_proje_turleri', cmd='delete', object_id=object_id)

        resp = self.client.post()

        assert proje_turleri_sayisi == len(resp.json['objects'])
