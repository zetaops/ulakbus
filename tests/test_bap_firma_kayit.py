# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from ulakbus.models import User, BAPFirma
from zengine.lib.test_utils import BaseTestCase
from zengine.models import TaskInvitation, Message, WFInstance


class TestCase(BaseTestCase):
    """
    Firmaların firma bilgileri ve yetkili bilgisini girerek teklif verebilmek 
    için sisteme kayıt olma isteği yapmasını sağlayan iş akışıni test eder.

    """

    def test_bap_firma_kayit(self):
        mesaj_sayisi = Message.objects.count()
        davet_sayisi = TaskInvitation.objects.count()
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
                      'yetkili_e_posta': 'selim@sayan.fake_mail',
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
        firma_form['yetkili_e_posta'] = 'selim@sayan.fake_mail'
        resp = self.client.post(wf='bap_firma_kayit', form=firma_form)
        assert resp.json['forms']['schema']['title'] == "Firma Kaydı İşlem Mesajı"
        assert 'Grundig' in resp.json['forms']['form'][0]['helpvalue']

        time.sleep(1)
        assert BAPFirma.objects.count() == mevcut_firma_sayisi + 1
        assert User.objects.count() == mevcut_kullanici_sayisi + 1
        assert TaskInvitation.objects.count() == davet_sayisi + 1
        assert Message.objects.count() == mesaj_sayisi + 1
        assert 'Grundig' in Message.objects.filter().order_by()[0].body

        user = User.objects.get(username='selim_sayan')
        assert user.name == 'Selim'
        assert user.is_active == False
        firma = user.bap_firma_set[0].bap_firma
        assert firma.ad == 'Grundig'
        assert firma.vergi_no == '232132193213890'
        assert firma.durum == 1

        # firmanın başvurusunun koordinasyon birimine iletilmesi
        token = WFInstance.objects.filter().order_by()[0].key
        self.prepare_client('/bap_firma_proje_basvuru_degerlendirme',
                            username='bap_koordinasyon_birimi_1', token=token)
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == "Firma Başvuru Değerlendirmeleri"
        assert "Firma Adı" in resp.json['objects'][0]
        del resp.json['objects'][0]
        firma_adlari_list = [obj['fields'][0] for obj in resp.json['objects']]
        assert "Grundig" in firma_adlari_list

        WFInstance.objects.filter(wf_object=firma.key).delete()
        TaskInvitation.objects.all().order_by()[0].delete()
        Message.objects.all().order_by()[0].delete()
        user.blocking_delete()
        firma.blocking_delete()
