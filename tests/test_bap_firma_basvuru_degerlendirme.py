# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus import settings
from ulakbus.models import BAPFirma, User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Firmaların, teklife açık bütçe kalemlerine 
    teklif vermesini sağlayan iş akışı testi.

    """

    def test_bap_firma_basvuru_degerlendirme(self):
        firma = BAPFirma.objects.get("5uGjOb0fj9rzGwfIwYoSIN2pNRH")
        self.prepare_client('/bap_firma_basvuru_degerlendirme',
                            username='bap_koordinasyon_birimi_1')
        resp = self.client.post()

        # listeleme ekranı
        assert resp.json['forms']['schema']['title'] == "Firma Başvuru Değerlendirmeleri"
        assert "Firma Adı" in resp.json['objects'][0]
        assert "Vergi Kimlik Numarası" in resp.json['objects'][0]
        action_names = ["Karar Ver", "İncele"]
        for action in resp.json['objects'][1]['actions']:
            assert action['name'] in action_names

        # incele
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="incele",
                                object_id="5uGjOb0fj9rzGwfIwYoSIN2pNRH")
        assert "Firması Kayıt Başvurusu Değerlendirme" in resp.json['forms']['schema']['title']
        assert resp.json['object']['Firma Adı'] == 'Veli Usta Dondurma'
        assert resp.json['object']['Vergi No'] == '8402384024802'

        # geri don
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="geri_don")
        assert resp.json['forms']['schema']['title'] == "Firma Başvuru Değerlendirmeleri"

        # karar, geri don
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="karar_ver",
                                object_id="5uGjOb0fj9rzGwfIwYoSIN2pNRH")
        assert "Firması Başvuru Değerlendirme Kararı" in resp.json['forms']['schema']['title']
        assert "değerlendirme kararınızı veriniz" in resp.json['forms']['form'][0]['helpvalue']
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="red", form={'red': 1})
        assert "Firması Başvuru Reddi Gerekçesi" in resp.json['forms']['schema']['title']
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="gonder",
                                form={'gerekce': "Belgeler eksik"})
        assert "Firması Başvuru Reddi" in resp.json['forms']['schema']['title']
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="geri_don",
                                form={'geri': 1})
        assert "Firması Başvuru Değerlendirme Kararı" in resp.json['forms']['schema']['title']
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="geri_don",
                                form={'geri': 1})
        assert resp.json['forms']['schema']['title'] == "Firma Başvuru Değerlendirmeleri"

        # karar, red
        self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="karar_ver",
                         object_id="5uGjOb0fj9rzGwfIwYoSIN2pNRH")
        self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="red", form={'red': 1})
        self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="gonder",
                         form={'gerekce': "Belgeler eksik"})
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="onayla",
                                form={'onayla': 1})
        assert resp.json['msgbox']['title'] == "Firma Başvuru Kaydı Değerlendirme"
        assert 'firma yetkilisine başarıyla iletilmiştir' in resp.json['msgbox']['msg']

        del resp.json['objects'][0]
        firma_adlari_list = [obj['fields'][0] for obj in resp.json['objects']]
        assert "Veli Usta Dondurma" not in firma_adlari_list
        kullanici = firma.Yetkililer[0].yetkili
        assert User.objects.filter(key=kullanici.key).count() == 0
        assert BAPFirma.objects.filter(key="5uGjOb0fj9rzGwfIwYoSIN2pNRH").count() == 0
        firma = BAPFirma.objects.filter(key="5uGjOb0fj9rzGwfIwYoSIN2pNRH", deleted=True)[0]
        kullanici = User.objects.filter(key=kullanici.key, deleted=True)[0]
        firma.deleted = False
        firma.save()
        kullanici.deleted = False
        kullanici.save()

        # karar, onayla
        assert resp.json['forms']['schema']['title'] == "Firma Başvuru Değerlendirmeleri"
        self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="karar_ver",
                         object_id="OzRUS2vPOp12ju4Oj47CwaeRvV6")
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="onayla",
                                form={'onayla': 1})
        assert "Firması Başvuru Kabulü" in resp.json['forms']['schema']['title']
        assert "onaylıyor musunuz" in resp.json['forms']['form'][0]['helpvalue']
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="onayla",
                                form={'onayla': 1})

        firma = BAPFirma.objects.get("OzRUS2vPOp12ju4Oj47CwaeRvV6")
        assert firma.durum == 2

        assert resp.json['msgbox']['title'] == "Firma Başvuru Kaydı Değerlendirme"
        assert firma.ad in resp.json['msgbox']['msg']

        del resp.json['objects'][0]
        firma_adlari_list = [obj['fields'][0] for obj in resp.json['objects']]
        assert firma.ad not in firma_adlari_list

        kullanici = firma.Yetkililer[0].yetkili
        assert kullanici.is_active == True
        role = kullanici.role_set[0].role
        assert 'bap_firma_teklif' in role.get_permissions()

        firma.durum = 1
        firma.blocking_save()
        kullanici.is_active = False
        kullanici.blocking_save()

        # belge indir
        firma = BAPFirma.objects.get("5uGjOb0fj9rzGwfIwYoSIN2pNRH")
        self.prepare_client('/bap_firma_basvuru_degerlendirme',
                            username='bap_koordinasyon_birimi_1')
        self.client.post()

        self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="incele",
                         object_id="5uGjOb0fj9rzGwfIwYoSIN2pNRH")
        resp = self.client.post(wf='bap_firma_basvuru_degerlendirme', cmd="indir",
                                form={"belge_indir": 1})
        assert resp.json['download_url'] == "%s%s" % (
            settings.S3_PUBLIC_URL, firma.faaliyet_belgesi)
