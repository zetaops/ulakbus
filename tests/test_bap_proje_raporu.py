# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import User, BAPRapor, BAPGundem
from time import sleep
from ulakbus import settings

dosya = {u'belge': {
    u'file_content': u"""data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEX/TQBcNTh/AAAAAXRSTlPM0jRW/QAAAApJREFUeJxjYgAAAAYAAzY3fKgAAAAASUVORK5CYII=""",
    u'file_name': u'a.png', u'isImage': True}, "gonder": 1}


class TestCase(BaseTestCase):
    """
    BAP proje raporunun öğretim üyesi tarafından yüklenmesi ve koordinasyon birimi tarafından
    rapora ait kararın verilmesi işlemlerini gerçekleştiren iş akışı testi.

    """

    def test_bap_proje_raporu(self):
        user = User.objects.get(username="ogretim_uyesi_1")
        self.prepare_client('/bap_proje_raporu', user=user)
        resp = self.client.post()

        # dönem ve sonuç raporu türlerinin seçilme ekranı
        assert resp.json['forms']['schema']['title'] == "Lütfen Rapor Türü Seçiniz."
        resp = self.client.post(form={'sec': 1})

        # rapor yükleme ekranı
        assert resp.json['forms']['schema']['title'] == "Rapor Yükleme Formu"
        rapor_sayisi = BAPRapor.objects.filter().count()
        resp = self.client.post(form=dosya)

        # rapor oluşturuldu mu kontrol edildi. Geri dön butonuna basıldı.
        assert rapor_sayisi + 1 == BAPRapor.objects.filter().count()
        assert resp.json['forms']['schema']['title'] == "Rapor Gönderme Form"
        resp = self.client.post(form={'geri_don': 1})

        #dönem ve sonuç raporu türlerinin seçilme ekranı
        assert resp.json['forms']['schema']['title'] == "Lütfen Rapor Türü Seçiniz."
        resp = self.client.post(form={'sec': 1})

        # rapor yükleme ekranı
        assert resp.json['forms']['schema']['title'] == "Rapor Yükleme Formu"
        rapor_sayisi = BAPRapor.objects.filter().count()
        resp = self.client.post(form=dosya)

        # rapor oluşturuldu mu kontrol edildi.
        assert rapor_sayisi + 1 == BAPRapor.objects.filter().count()
        assert resp.json['forms']['schema']['title'] == "Rapor Gönderme Form"

        # rapor koordinasyon birimine gönderildi.
        resp = self.client.post(form={'gonder': 1}, cmd="gonder")
        assert resp.json['msgbox']['title'] == "Proje Raporu Gönderildi!"

        # rapor koordinasyon birimine gönderildi.
        sleep(1)
        token, user = self.get_user_token('bap_koordinasyon_birimi_1')
        self.prepare_client('/bap_proje_raporu', user=user, token=token)
        resp = self.client.post()

        # raporun koordinasyon birimi tarafından görüntülenme ekranı
        assert resp.json['forms']['schema']['title'] == "Proje Rapor Görüntüleme"
        rapor = BAPRapor.objects.all()[0]
        resp = self.client.post(cmd="rapor_indir")

        # doğru rapor indirildi mi kontrol yapıldı.
        assert resp.json['download_url'] == "%s%s" % (
            settings.S3_PUBLIC_URL, rapor.belge)
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == "Proje Rapor Görüntüleme"
        resp = self.client.post(cmd="karar")
        assert resp.json['forms']['schema']['title'] == "Proje Raporu Karar Formu"
        resp = self.client.post(cmd="revizyon")

        # koordinasyon birimi raporu revizyona aldı. Revizyon mesajı giriş ekranı
        assert resp.json['forms']['schema']['title'] == "Revizyon Mesajı Giriş"
        self.client.post(wf='bap_proje_raporu')
        token, user = self.get_user_token('ogretim_uyesi_1')
        self.prepare_client('/bap_proje_raporu', user=user, token=token)
        resp = self.client.post()

        # koordinasyon birimi tarafından girilen revizyon mesajının öğretim üyesi tarafından
        # görüntülenme ekranı
        assert resp.json['forms']['schema']['title'] == "Rapor Revizyon Bilgi Mesajı"
        resp = self.client.post(form={'tamam': 1})
        assert resp.json['forms']['schema']['title'] == "Lütfen Rapor Türü Seçiniz."
        resp = self.client.post(form={'sec': 1})
        assert resp.json['forms']['schema']['title'] == "Rapor Yükleme Formu"
        rapor_sayisi = BAPRapor.objects.filter().count()
        resp = self.client.post(form=dosya)

        # rapor oluşturuldu mu kontrol edildi.
        assert rapor_sayisi + 1 == BAPRapor.objects.filter().count()
        assert resp.json['forms']['schema']['title'] == "Rapor Gönderme Form"
        resp = self.client.post(form={'gonder': 1}, cmd="gonder")
        assert resp.json['msgbox']['title'] == "Proje Raporu Gönderildi!"
        sleep(1)
        token, user = self.get_user_token('bap_koordinasyon_birimi_1')
        self.prepare_client('/bap_proje_raporu', user=user, token=token)
        resp = self.client.post()

        # raporun koordinasyon birimi tarafından görüntülenme ekranı
        assert resp.json['forms']['schema']['title'] == "Proje Rapor Görüntüleme"
        resp = self.client.post(cmd="karar")
        assert resp.json['forms']['schema']['title'] == "Proje Raporu Karar Formu"
        bap_gundem_sayisi = BAPGundem.objects.filter().count()
        resp = self.client.post(cmd="onayla")

        # koordinasyon birimi rapor onaylandı ve rapora ait BAPGundem nesnesi oluşturuldu.
        assert bap_gundem_sayisi + 1 == BAPGundem.objects.filter().count()
        assert resp.json['forms']['schema']['title'] == "Rapor Gündem Bilgi Mesajı"
