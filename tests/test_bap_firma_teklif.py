# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from ulakbus import settings
from ulakbus.models import User, BAPTeklif, BAPButcePlani, BAPSatinAlma
from zengine.lib.test_utils import BaseTestCase
import requests, zipfile, io, os

png_belge = {u'belge': {
    u'file_content': u"""data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BM
    VEX/TQBcNTh/AAAAAXRSTlPM0jRW/QAAAApJREFUeJxjYgAAAAYAAzY3fKgAAAAASUVORK5CYII=""",
    u'file_name': u'png_trial.png', u'isImage': True}, u'aciklama': u'png denemesi'}

pdf_belge = {u'belge': {
    u'file_content': u"""data:application/pdf;base64,JVBERi0xLjEKJcKlwrHDqwoKMSAwIG9iagogIDw8IC9UeX
    BlIC9DYXRhbG9nCiAgICAgL1BhZ2VzIDIgMCBSCiAgPj4KZW5kb2JqCgoyIDAgb2JqCiAgPDwgL1R5cGUgL1BhZ2VzCiAgI
    CAgL0tpZHMgWzMgMCBSXQogICAgIC9Db3VudCAxCiAgICAgL01lZGlhQm94IFswIDAgMzAwIDE0NF0KICAPgplbmRvYmoKC
    jMgMCBvYmoKICA8PCAgL1R5cGUgL1BhZ2UKICAgICAgL1BhcmVudCAyIDAgUgogICAgICAvUmVzb3VyY2VzCiAgICAgICA8
    PCAvRm9udAogICAgICAgICAgIDw8IC9GMQogICAgICAgICAgICAgICA8PCAvVHlwZSAvRm9udAogICAgICAgICAgICAgICA
    gICAvU3VidHlwZSAvVHlwZTEKICAgICAgICAgICAgICAgICAgL0Jhc2VGb250IC9UaW1lcy1Sb21hbgogICAgICAgICAgIC
    AgICAPgogICAgICAgICAgID4CiAgICAgICAPgogICAgICAvQ29udGVudHMgNCAwIFIKICAPgplbmRvYmoKCjQgMCBvYmoKI
    CA8PCAvTGVuZ3RoIDU1ID4CnN0cmVhbQogIEJUCiAgICAvRjEgMTggVGYKICAgIDAgMCBUZAogICAgKEhlbGxvIFdvcmxkK
    SBUagogIEVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxOCAwMDAw
    MCBuIAowMDAwMDAwMDc3IDAwMDAwIG4gCjAwMDAwMDAxNzggMDAwMDAgbiAKMDAwMDAwMDQ1NyAwMDAwMCBuIAp0cmFpbGV
    yCiAgPDwgIC9Sb290IDEgMCBSCiAgICAgIC9TaXplIDUKICAPgpzdGFydHhyZWYKNTY1CiUlRU9GCg==""",
    u'file_name': u'pdf_trial.pdf', u'isImage': False}, u'aciklama': u'pdf denemesi'}

jpg_belge = {u'belge': {
    u'file_content': u"""data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/4QAWRXhpZgAASUkqAAgAAAA
    AAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQ
    EBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBA
    QH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAr/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEB
    AAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AL+AAf/Z""",
    u'file_name': u'jpg_trial.jpg', u'isImage': True}, u'aciklama': u'jpg denemesi'}


class TestCase(BaseTestCase):
    """
    Firmaların, teklife açık bütçe kalemlerine 
    teklif vermesini sağlayan iş akışı testi.

    """

    def test_bap_firma_teklif(self):
        satin_alma = BAPSatinAlma.objects.get('EEEKHshgTCZXSl02obdeZckzut2')
        user = User.objects.get(username='bap_firma_yetkilisi_1')
        firma = user.bap_firma_set[0].bap_firma
        self.prepare_client('/bap_firma_teklif', user=user)
        resp = self.client.post()

        # listeleme ekranı

        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemi Satın Almaları"
        assert resp.json['forms']['schema']['properties']['add']['title'] == "Tekliflerimi Göster"
        assert "Satın Alma Duyuru Adı" in resp.json['objects'][0]
        assert "Teklife Açılma Tarihi" in resp.json['objects'][0]
        action_names = ["Teklifte Bulun", "Ayrıntı Gör", "Teklif Belgeleri Düzenle",
                        "Teklif Belgeleri İndir"]
        for action in resp.json['objects'][1]['actions']:
            assert action['name'] in action_names

        # tekliflerim olumlu
        resp = self.client.post(wf='bap_firma_teklif', cmd="tekliflerim", form={"add": 1})
        assert resp.json['forms']['schema']['title'] == "Firmanın Teklifleri"
        assert "Satın Alma Adı" in resp.json['objects'][0]
        assert "Durum" in resp.json['objects'][0]
        assert 'sonuçlanmış' in resp.json['forms']['form'][0]['helpvalue']
        action_names = ["Teklif Belgeleri İndir", "Ayrıntı Gör"]
        for action in resp.json['objects'][1]['actions']:
            assert action['name'] in action_names

        # sonuçlanmış teklif ayrıntı gör
        resp = self.client.post(wf='bap_firma_teklif', cmd="ayrinti",
                                data_key="GSX4LNZntJicEmD4k0DQ3u7M9ME")

        assert "4 Kalem Kırtasiye Malzemesi Alımı" in resp.json['forms']['schema']['title']

        assert "Bütçe Kalemi Adı" in resp.json['objects'][0]
        assert "Adet" in resp.json['objects'][0]

        self.client.post(wf='bap_firma_teklif', cmd="geri_don", form={'geri_don': 1})
        resp = self.client.post(wf='bap_firma_teklif', cmd="geri_don", form={'geri_don': 1})
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemi Satın Almaları"

        # tekliflerim olumsuz
        teklifler = []
        for teklif in BAPTeklif.objects.filter(firma=firma):
            teklif.deleted = True
            teklif.blocking_save()
            teklifler.append(teklif)
        time.sleep(1)

        resp = self.client.post(wf='bap_firma_teklif', cmd="tekliflerim", form={'add': 1})
        assert resp.json['msgbox']['title'] == "Firma Teklifleri"
        assert 'sonuçlanmış' in resp.json['msgbox']['msg']

        # bütçe kalemlerini ayrıntılı gör
        resp = self.client.post(wf='bap_firma_teklif', cmd="ayrinti",
                                object_id="EEEKHshgTCZXSl02obdeZckzut2")
        assert resp.json['forms']['schema'][
                   'title'] == "3 Kalem Büro Malzemesi Alımı Satın Alma Duyurusu Bütçe Kalemleri"

        assert "Bütçe Kalemi Adı" in resp.json['objects'][0]
        assert "Adet" in resp.json['objects'][0]

        self.client.post(wf='bap_firma_teklif', cmd="geri_don", form={'geri_don': 1})

        # teklifte bulun, geri dön
        resp = self.client.post(wf='bap_firma_teklif', cmd="teklif_ver",
                                object_id="EEEKHshgTCZXSl02obdeZckzut2")
        assert resp.json['forms']['schema']['title'] == "Bütçe Kalemi Teklifi"
        assert '3 Kalem Büro Malzemesi Alımı' in resp.json['forms']['form'][0]['helpvalue']
        resp = self.client.post(wf='bap_firma_teklif', cmd="geri_don", form={'geri': 1})
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemi Satın Almaları"

        # teklif belgeleri boş kontrol
        resp = self.client.post(wf='bap_firma_teklif', cmd="teklif_ver",
                                object_id="EEEKHshgTCZXSl02obdeZckzut2")
        resp = self.client.post(wf='bap_firma_teklif', cmd="kaydet",
                                form={'Belgeler': [], 'kaydet': 1})
        assert resp.json['forms']['schema']['title'] == "Bütçe Kalemi Teklifi"
        assert '3 Kalem Büro Malzemesi Alımı' in resp.json['forms']['form'][0]['helpvalue']
        assert resp.json['msgbox']['title'] == "Belge Eksikliği"

        # teklifte bulun
        resp = self.client.post(wf='bap_firma_teklif', cmd="kaydet",
                                form={'Belgeler': [jpg_belge, png_belge], 'kaydet': 1})

        # teklif kaydedildi mesajı
        assert resp.json['msgbox']['title'] == "Firma Teklifleri"
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemi Satın Almaları"
        assert 'başarıyla yüklenmiştir' in resp.json['msgbox']['msg']
        del resp.json['objects'][0]

        # teklif kaydından sonra buton değişikliği
        for obj in resp.json['objects']:
            if obj['key'] == "EEEKHshgTCZXSl02obdeZckzut2":
                break

        action_list = ['Teklif Belgeleri Düzenle', 'Teklif Belgeleri İndir', 'Ayrıntı Gör']
        for action in obj['actions']:
            assert action['name'] in action_list

        # veritabanı kaydetme kontrol
        teklif = BAPTeklif.objects.get(firma=firma, satin_alma=satin_alma)
        assert len(teklif.Belgeler) == 2
        belge_adlari = [png_belge['belge']['file_name'], jpg_belge['belge']['file_name']]
        for belge in teklif.Belgeler:
            assert belge.belge in belge_adlari

        # mevcut tekliflerim olumlu, düzenle
        resp = self.client.post(wf='bap_firma_teklif', cmd="duzenle",
                                object_id="EEEKHshgTCZXSl02obdeZckzut2")
        assert resp.json['forms']['schema']['title'] == "Teklif Belgeleri Düzenleme"
        belge_adlari = [png_belge['belge']['file_name'],
                        jpg_belge['belge']['file_name']]

        for belge in resp.json['forms']['model']['Belgeler']:
            assert belge['belge'] in belge_adlari

        assert len(resp.json['forms']['model']['Belgeler']) == 2

        # düzenleme yap, kaydet
        # jpg dosyası silinir, pdf dosyası eklenir, png dosyasının açıklaması değiştirilir
        resp = self.client.post(wf='bap_firma_teklif', cmd="kaydet", form=
        {'Belgeler': [pdf_belge,
                      {'belge': "png_trial.png", 'aciklama': "png değişmiş aciklama"}],
         'kaydet': 1, 'model_type': 'BAPTeklif', 'object_key': 'SPMUxcVSQCNzwhHQjC5d8MloC5j'})

        # işlem mesajı kontrolü
        assert resp.json['msgbox']['title'] == "Firma Teklifleri"
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemi Satın Almaları"
        assert 'başarıyla yüklenmiştir' in resp.json['msgbox']['msg']

        # düzenleme sonrası form data kontrol
        resp = self.client.post(wf='bap_firma_teklif', cmd="duzenle",
                                object_id="EEEKHshgTCZXSl02obdeZckzut2")
        belge_aciklama = {"png_trial.png": "png değişmiş aciklama",
                          "pdf_trial.pdf": "pdf denemesi"}
        assert len(resp.json['forms']['model']['Belgeler']) == 2
        for belge in resp.json['forms']['model']['Belgeler']:
            assert belge['belge'] in belge_aciklama
            assert belge['aciklama'] == belge_aciklama[belge['belge']]

        # düzenleme sonrası veritabanı kontrol
        teklif.reload()
        assert len(teklif.Belgeler) == 2
        for belge in teklif.Belgeler:
            assert belge.belge in belge_aciklama
            assert belge.aciklama == belge_aciklama[belge.belge]

        # geri dön
        self.client.post(wf='bap_firma_teklif', cmd="geri_don", form={'geri': 1})

        # silinen teklifler eski haline döndürülür
        for tek in teklifler:
            tek.deleted = False
            tek.blocking_save()
        time.sleep(1)

        # belgeleri indirme
        for i in range(2):
            # güncel tekliflerden indir
            if i == 0:
                resp = self.client.post(wf='bap_firma_teklif', cmd="indir",
                                        object_id="EEEKHshgTCZXSl02obdeZckzut2")
                assert resp.json['download_url'] == "%s%s-teklif-belgeler.zip" % (
                    settings.S3_PUBLIC_URL, teklif.__unicode__().replace(' ', ''))

            # sonuçlanmış tekliflerden indir
            else:
                user = User.objects.get(username='bap_firma_yetkilisi_1')
                self.prepare_client('/bap_firma_teklif', user=user)
                self.client.post()
                ikinci_teklif = BAPTeklif.objects.get('GSX4LNZntJicEmD4k0DQ3u7M9ME')
                self.client.post(wf='bap_firma_teklif', cmd="tekliflerim", form={"add": 1})
                resp = self.client.post(wf='bap_firma_teklif', cmd="belge_indir",
                                        data_key=ikinci_teklif.key)
                assert resp.json['download_url'] == "%s%s-teklif-belgeler.zip" % (
                    settings.S3_PUBLIC_URL, ikinci_teklif.__unicode__().replace(' ', ''))
                belge_aciklama = {'png_trial.png': 'Başvuru belgesi'}

            # belgelerin içeriği kontrol
            r = requests.get(resp.json['download_url'])
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall()
            file_names = [f for f in os.listdir(os.getcwd()) if
                          os.path.isfile(f) and (f.endswith('.png') or f.endswith('.pdf'))]

            for belge_ad in belge_aciklama.keys():
                assert belge_ad in file_names
                os.remove(belge_ad)

            teklif.blocking_delete()
