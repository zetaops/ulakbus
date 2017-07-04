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
        User.objects.filter(username='deneme_k_adi').delete()
        mevcut_firma = BAPFirma.objects.get('8wRLFH1pfFVEtVjmZSxtPjZVyaF')

        self.prepare_client('/bap_firma_kayit', username='ulakbus')
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == 'Firma Bilgileri'
        assert 'faaliyet_belgesi' in resp.json['forms']['form']
        assert 'vergi_no' in resp.json['forms']['form']

        mevcut_firma_sayisi = BAPFirma.objects.count()
        mevcut_kullanici_sayisi = User.objects.count()

        firma_form = {'ad': 'DenemeFirma',
                      'adres': 'yenipazar mahallesi',
                      'vergi_no': '',
                      'vergi_dairesi': '',
                      'e_posta': 'kocakiletisim@fakemail.kocakiletisim',
                      'isim': 'DenemeKullanici',
                      'soyad': 'DenemeSoyad',
                      'k_adi': '',
                      'yetkili_e_posta': '',
                      'faaliyet_belgesi_verilis_tarihi': "31.05.2017"}

        # UYARILAR

        # firma e-postası
        resp = self.client.post(wf='bap_firma_kayit', form=firma_form)
        assert resp.json['msgbox']['title'] == "Mevcut Bilgi Uyarısı"
        assert "firma e-postasına ait kayıt bulunmaktadır." in resp.json['msgbox']['msg']
        assert resp.json['forms']['schema']['title'] == 'Firma Bilgileri'

        # yetkili kullanıcı adı
        firma_form['e_posta'] = ''
        firma_form['k_adi'] = mevcut_firma.Yetkililer[0].yetkili.username
        resp = self.client.post(wf='bap_firma_kayit', form=firma_form)
        assert resp.json['msgbox']['title'] == "Mevcut Bilgi Uyarısı"
        assert "yetkili kullanıcı adına ait kayıt bulunmaktadır." in resp.json['msgbox']['msg']
        assert resp.json['forms']['schema']['title'] == 'Firma Bilgileri'

        # yetkili e-postası
        firma_form['k_adi'] = ''
        firma_form['yetkili_e_posta'] = mevcut_firma.Yetkililer[0].yetkili.e_mail
        resp = self.client.post(wf='bap_firma_kayit', form=firma_form)
        assert resp.json['msgbox']['title'] == "Mevcut Bilgi Uyarısı"
        assert "yetkili e-postasına ait kayıt bulunmaktadır." in resp.json['msgbox']['msg']
        assert resp.json['forms']['schema']['title'] == 'Firma Bilgileri'

        # vergi no ve vergi dairesi
        firma_form['yetkili_e_posta'] = ''
        firma_form['vergi_no'] = mevcut_firma.vergi_no
        firma_form['vergi_dairesi'] = mevcut_firma.vergi_dairesi
        resp = self.client.post(wf='bap_firma_kayit', form=firma_form)
        assert resp.json['forms']['schema']['title'] == 'Vergi Bilgileri Uyarısı'
        assert 'ait firma kaydı bulunmaktadır.' in resp.json['forms']['form'][0]['helpvalue']
        resp = self.client.post(wf='bap_firma_kayit',cmd = 'geri_don', form={'geri_don': 1})
        assert resp.json['forms']['schema']['title'] == 'Firma Bilgileri'
        self.client.post(wf='bap_firma_kayit', form=firma_form)
        resp = self.client.post(wf='bap_firma_kayit', cmd='hatirlat', form={'hatirlat': 1})
        assert resp.json['forms']['schema']['title'] == "Giriş Bilgileri Hatırlatma E-Postası Onayı"
        assert "hatırlatma e-postası yollanacaktır." in resp.json['forms']['form'][0]['helpvalue']
        resp = self.client.post(wf='bap_firma_kayit',cmd = 'geri_don', form={'geri_don': 1})
        assert resp.json['forms']['schema']['title'] == 'Firma Bilgileri'

        # e-posta gönderimi
        self.client.post(wf='bap_firma_kayit', form=firma_form)
        self.client.post(wf='bap_firma_kayit', cmd='hatirlat', form={'hatirlat': 1})
        resp = self.client.post(wf='bap_firma_kayit', cmd='onayla', form={'onayla': 1})
        assert resp.json['msgbox']['title'] == "Giriş Bilgileri Hatırlatma E-Posta Gönderimi"
        assert "yetkili giriş bilgileri başarıyla gönderilmiştir." in resp.json['msgbox']['msg']
        assert User.objects.count() == mevcut_kullanici_sayisi
        assert BAPFirma.objects.count() == mevcut_firma_sayisi

        # başarılı kayıt işlemi
        self.prepare_client('/bap_firma_kayit', username='ulakbus')
        resp = self.client.post()
        firma_form['kaydi_bitir'] = 1
        firma_form['vergi_no'] = '12345678'
        firma_form['vergi_dairesi'] = 98765
        firma_form['k_adi'] = 'deneme_k_adi'
        firma_form['yetkili_e_posta'] = 'bubir@deneme.mailidir'
        resp = self.client.post(wf='bap_firma_kayit', form=firma_form)
        assert resp.json['forms']['schema']['title'] == "Firma Kaydı İşlem Mesajı"
        assert 'DenemeFirma' in resp.json['forms']['form'][0]['helpvalue']

        time.sleep(1)
        assert BAPFirma.objects.count() == mevcut_firma_sayisi + 1
        assert User.objects.count() == mevcut_kullanici_sayisi + 1
        assert TaskInvitation.objects.count() == davet_sayisi + 1
        assert Message.objects.count() == mesaj_sayisi + 1
        assert 'DenemeFirma' in Message.objects.filter().order_by()[0].body

        user = User.objects.get(username='deneme_k_adi')
        assert user.name == 'DenemeKullanici'
        assert user.is_active == False
        firma = user.bap_firma_set[0].bap_firma
        assert firma.ad == 'DenemeFirma'
        assert firma.vergi_no == '12345678'
        assert firma.vergi_dairesi == 98765
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
        assert "DenemeFirma" in firma_adlari_list

        WFInstance.objects.filter(wf_object=firma.key).delete()
        TaskInvitation.objects.all().order_by()[0].delete()
        Message.objects.all().order_by()[0].delete()
        user.blocking_delete()
        firma.blocking_delete()
