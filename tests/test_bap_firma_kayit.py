# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from ulakbus.models import User, BAPFirma
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Firmaların firma bilgileri ve yetkili bilgisini girerek teklif verebilmek 
    için sisteme kayıt olma isteği yapmasını sağlayan iş akışıni test eder.

    """

    def test_bap_firma_kayit(self):
        User.objects.filter(username='selim_sayan').delete()
        self.prepare_client('/bap_firma_kayit', username='ulakbus')
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == 'Firma Bilgileri'
        assert 'faaliyet_belgesi' in resp.json['forms']['form']
        assert 'vergi_no' in resp.json['forms']['form']

        mevcut_firma_sayisi = BAPFirma.objects.count()
        mevcut_kullanici_sayisi = User.objects.count()

        firma_form = {'ad': 'Grundig',
                      'adres': 'yenipazar mahallesi',
                      'vergi_no': '232132193213890',
                      'isim': 'Selim',
                      'soyad': 'Sayan',
                      'k_adi': 'ulakbus',
                      'yetkili_e_posta': 'selim@sayan.slm',
                      'faaliyet_belgesi_verilis_tarihi': "31.05.2017"}

        # unique yetkili kullanıcı adı uyarısı
        resp = self.client.post(wf='bap_firma_kayit', form=firma_form)
        assert resp.json['msgbox']['title'] == "Mevcut Bilgi Uyarısı"
        assert "kullanıcı adı bilgisi, sistemimizde bulunmaktadır" in resp.json['msgbox']['msg']
        assert User.objects.count() == mevcut_kullanici_sayisi
        assert BAPFirma.objects.count() == mevcut_firma_sayisi

        # unique yetkili e-posta adresi uyarısı
        firma_form['k_adi'] = 'selim_sayan'
        firma_form['yetkili_e_posta'] = 'bap_firma@yetkilisi_1.com'
        resp = self.client.post(wf='bap_firma_kayit', form=firma_form)
        assert resp.json['msgbox']['title'] == "Mevcut Bilgi Uyarısı"
        assert "e-posta bilgisi, sistemimizde bulunmaktadır" in resp.json['msgbox']['msg']
        assert User.objects.count() == mevcut_kullanici_sayisi
        assert BAPFirma.objects.count() == mevcut_firma_sayisi

        # başarılı kayıt işlemi
        firma_form['yetkili_e_posta'] = 'selim@sayan.slm'
        resp = self.client.post(wf='bap_firma_kayit', form=firma_form)
        assert resp.json['forms']['schema']['title'] == "Firma Kaydı İşlem Mesajı"
        assert 'Grundig' in resp.json['forms']['form'][0]['helpvalue']

        assert BAPFirma.objects.count() == mevcut_firma_sayisi + 1
        assert User.objects.count() == mevcut_kullanici_sayisi + 1

        user = User.objects.get(username='selim_sayan')
        assert user.name == 'Selim'
        firma = user.bap_firma_set[0].bap_firma
        assert firma.ad == 'Grundig'
        assert firma.vergi_no == '232132193213890'
        assert firma.durum == 1

        user.blocking_delete()
        firma.blocking_delete()
