# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from ulakbus import settings
from ulakbus.models import User, BAPTeklif, BAPButcePlani
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
        butce_kalemi = BAPButcePlani.objects.get('MpRqF2BZk6sMbi4QNkQvTNH1mVW')
        user = User.objects.get(username='bap_firma_yetkilisi_1')
        firma = user.bap_firma_set[0].bap_firma
        self.prepare_client('/bap_firma_teklif', user=user)
        resp = self.client.post()

        # listeleme ekranı
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemleri"
        assert resp.json['forms']['schema']['properties']['add']['title'] == "Mevcut Tekliflerim"
        assert resp.json['forms']['schema']['properties']['sonuclanan'][
                   'title'] == "Sonuçlanmış Tekliflerim"
        assert "Muhasebe Kod" in resp.json['objects'][0]
        assert "Kod Adı" in resp.json['objects'][0]
        assert resp.json['objects'][1]['actions'][0]['name'] == "Teklifte Bulun"

        # sonuçlanmış tekliflerim olumlu
        resp = self.client.post(wf='bap_firma_teklif', cmd="sonuclanan", form={"sonuclanan": 1})
        assert resp.json['forms']['schema']['title'] == "Firmanın Sonuçlanmış Teklifleri"
        assert "Bütçe Kalemi" in resp.json['objects'][0]
        assert "Durum" in resp.json['objects'][0]
        resp = self.client.post(wf='bap_firma_teklif', cmd="geri_don", form={'geri_don': 1})
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemleri"

        # sonuçlanmış tekliflerim olumsuz
        teklifler = []
        for teklif in BAPTeklif.objects.filter(firma=firma, durum__in=[2, 3]):
            teklif.deleted = True
            teklif.blocking_save()
            teklifler.append(teklif)
        time.sleep(1)

        resp = self.client.post(wf='bap_firma_teklif', cmd="sonuclanan", form={'sonuclanan': 1})
        assert resp.json['msgbox']['title'] == "Firma Teklifleri"
        assert 'sonuçlanmış' in resp.json['msgbox']['msg']

        # mevcut tekliflerim olumsuz
        BAPTeklif.objects.filter(firma=firma, durum=1).delete()
        time.sleep(1)
        resp = self.client.post(wf='bap_firma_teklif', cmd="mevcut", form={'add': 1})
        assert resp.json['msgbox']['title'] == "Firma Teklifleri"
        assert 'başvuru sürecinde bulunan' in resp.json['msgbox']['msg']

        # teklifte bulun
        resp = self.client.post(wf='bap_firma_teklif', cmd="teklif_ver",
                                object_id="MpRqF2BZk6sMbi4QNkQvTNH1mVW")
        assert resp.json['forms']['schema']['title'] == "Bütçe Kalemi Teklifi"
        assert 'Arduino' in resp.json['forms']['form'][0]['helpvalue']

        # geri dön
        resp = self.client.post(wf='bap_firma_teklif', cmd="geri_don", form={'geri': 1})
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemleri"

        # teklifte bulun
        resp = self.client.post(wf='bap_firma_teklif', cmd="teklif_ver",
                                object_id="MpRqF2BZk6sMbi4QNkQvTNH1mVW")
        assert resp.json['forms']['schema']['title'] == "Bütçe Kalemi Teklifi"
        assert 'Arduino' in resp.json['forms']['form'][0]['helpvalue']
        resp = self.client.post(wf='bap_firma_teklif', cmd="kaydet",
                                form={'Belgeler': [jpg_belge, png_belge], 'kaydet': 1})

        # teklif kaydedildi mesajı
        assert resp.json['msgbox']['title'] == "Firma Teklifleri"
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemleri"
        assert 'başarıyla yüklenmiştir' in resp.json['msgbox']['msg']

        # veritabanı kaydetme kontrol
        teklif = BAPTeklif.objects.get(firma=firma, butce=butce_kalemi)
        assert len(teklif.Belgeler) == 2
        belge_adlari = [png_belge['belge']['file_name'], jpg_belge['belge']['file_name']]
        for belge in teklif.Belgeler:
            assert belge.belge in belge_adlari

        # aynı bütçe kalemine teklif verme denemesi
        resp = self.client.post(wf='bap_firma_teklif', cmd="teklif_ver",
                                object_id="MpRqF2BZk6sMbi4QNkQvTNH1mVW")
        assert resp.json['msgbox']['title'] == "Mevcut Teklif Uyarısı"
        assert 'teklifiniz bulunmaktadır' in resp.json['msgbox']['msg']

        # mevcut tekliflerim olumlu, geri dön
        self.client.post(wf='bap_firma_teklif', cmd="mevcut", form={'add': 1})
        resp = self.client.post(wf='bap_firma_teklif', cmd="geri_don", form={'geri_don': 1})
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemleri"

        # mevcut tekliflerim olumlu, düzenle
        resp = self.client.post(wf='bap_firma_teklif', cmd='mevcut', form={'add': 1})
        assert resp.json['forms']['schema']['title'] == "Firmanın Mevcut Teklifleri"
        assert "Bütçe Kalemi" in resp.json['objects'][0]
        resp = self.client.post(wf='bap_firma_teklif', cmd="belge_duzenle", data_key=teklif.key)
        assert resp.json['forms']['schema']['title'] == "Teklif Belgeleri Düzenleme"
        belge_adlari = [png_belge['belge']['file_name'].replace(' ', ''),
                        jpg_belge['belge']['file_name'].replace(' ', '')]

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
        assert resp.json['forms']['schema']['title'] == "Teklife Açık Bütçe Kalemleri"
        assert 'başarıyla yüklenmiştir' in resp.json['msgbox']['msg']

        # düzenleme sonrası form data kontrol
        self.client.post(wf='bap_firma_teklif', cmd="mevcut", form={'add': 1})
        resp = self.client.post(wf='bap_firma_teklif', cmd="belge_duzenle", data_key=teklif.key)
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

        # belgeleri indir
        resp = self.client.post(wf='bap_firma_teklif', cmd="belge_indir", data_key=teklif.key)
        assert resp.json['download_url'] == "%s%s-teklif-belgeler.zip" % (
            settings.S3_PUBLIC_URL, teklif.__unicode__().replace(' ', ''))

        # belgelerin içeriği kontrol
        r = requests.get(resp.json['download_url'])
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall()
        file_names = [f for f in os.listdir(os.getcwd()) if
                      os.path.isfile(f) and (f.endswith('.png') or f.endswith('.pdf'))]

        for belge_ad in belge_aciklama.keys():
            assert belge_ad in file_names
            os.remove(belge_ad)

        for bap_teklif in teklifler:
            bap_teklif.deleted = False
            bap_teklif.blocking_save()
        time.sleep(1)

        teklif.blocking_delete()
