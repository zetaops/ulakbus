# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje, User, BAPRapor, BAPGundem
from zengine.lib.test_utils import BaseTestCase
from time import sleep
from ulakbus import settings

dosya = {u'belge': {
    u'file_content': u"""data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEX/TQBcNTh/AAAAAXRSTlPM0jRW/QAAAApJREFUeJxjYgAAAAYAAzY3fKgAAAAASUVORK5CYII=""",
    u'file_name': u'a.png', u'isImage': True}, "gonder": 1}


class TestCase(BaseTestCase):
    def test_ogretim_uyesi_basvuru_listele(self):
        # Öğretim üyesi kullanıcısı alınır.
        user_ou = User.objects.get(username='ogretim_uyesi_1')

        okutman = user_ou.personel.okutman
        proje_sayisi = BAPProje.objects.filter(yurutucu=okutman).count()

        # Ogretim uyesi başvuru listeleme iş akışını başlatır.
        self.prepare_client('/bap_ogretim_uyesi_basvuru_listeleme', user=user_ou)
        resp = self.client.post()

        # Kullanıcının proje sayısı kontrol edilir
        assert proje_sayisi + 1 == len(resp.json['objects'])

        # Durumu onaylanmış olan projelerde görüntüle dışındaki action butonlarının olduğu kontrol
        # edilir.
        for i in range(1, len(resp.json['objects'])):
            obj = resp.json['objects'][i]
            if BAPProje.objects.get(obj['key']).durum == 5:
                assert len(obj['actions']) > 1
            else:
                assert len(obj['actions']) == 1

        # Talep seçme adımına gidilir.
        self.client.post(cmd='talepler', object_id='b5avq6Tc6jHuKf9z2kizPFK3nc')

        # Ek bütçe talebine gidilir.
        resp = self.client.post(form={'sec': 1, 'talepler': 1})

        # Ek bütçe adımına gelindiği kontrol edilir.
        assert resp.json['wf_meta']['name'] == 'bap_ek_butce_talep'

        # Ek bütçe adımı iptal edilerek listeleme adımına dönülür.
        self.client.post(cmd='iptal')

        # Talep seçme adımına gidilir.
        self.client.post(cmd='talepler', object_id='b5avq6Tc6jHuKf9z2kizPFK3nc')

        # Ek süre adımına gidilir.
        resp = self.client.post(form={'sec': 1, 'talepler': 3})

        # Ek süre adımına gidildiği kontrol edilir.
        assert resp.json['wf_meta']['name'] == 'bap_ek_sure_talep'

        # Ek süre adımı kontrol edilir.
        self.client.post(cmd='iptal')

        # Talep seçme adımına gidilir.
        self.client.post(cmd='talepler', object_id='b5avq6Tc6jHuKf9z2kizPFK3nc')

        # Fasıl aktarımı adımına gidilir.
        resp = self.client.post(form={'sec': 1, 'talepler': 2})

        # Fasıl aktarımı adımına gidildiği kontrol edilir.
        assert resp.json['wf_meta']['name'] == 'bap_fasil_aktarim_talep'

        # vazgeç butonuna basılarak listeleme ekranına gidilir.
        self.client.post(form={'bitir': 1}, cmd='bitir')

        # bap proje raporu tür seçme ekranı
        resp = self.client.post(cmd='bap_proje_raporu')

        # dönem ve sonuç raporu türlerinin seçilme ekranı
        assert resp.json['forms']['schema']['title'] == "Lütfen Rapor Türü Seçiniz."
        resp = self.client.post(form={'sec': 1, 'tur': 1})

        # rapor yükleme ekranı
        assert resp.json['forms']['schema']['title'] == "Rapor Yükleme Formu"
        rapor_sayisi = BAPRapor.objects.filter().count()
        resp = self.client.post(form=dosya)

        # rapor oluşturuldu mu kontrol edildi. Geri dön butonuna basıldı.
        assert rapor_sayisi + 1 == BAPRapor.objects.filter().count()
        assert resp.json['forms']['schema']['title'] == "Rapor Gönderme Form"
        resp = self.client.post(form={'geri_don': 1})

        # dönem ve sonuç raporu türlerinin seçilme ekranı
        assert resp.json['forms']['schema']['title'] == "Lütfen Rapor Türü Seçiniz."
        resp = self.client.post(form={'sec':1, 'tur':1})

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
