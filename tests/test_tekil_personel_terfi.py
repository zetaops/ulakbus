# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Mithat Raşit Özçıkrıkcı'

from ulakbus.models import User, Personel, AskerlikKayitlari, UcretsizIzin
from zengine.lib.test_utils import *
from zengine.notifications.model import NotificationMessage
from dateutil.relativedelta import relativedelta
from pyoko.exceptions import ObjectDoesNotExist
import datetime

class TestCase(BaseTestCase):
    def test_tekil_personel(self):
        """
            Tekil personel terfi (Kanunla verilen terfi) için hazırlanmış test metodudur.
        """

        # Notification kontrolü yapabilmek için öncelikle tüm notificationlar temizlenir.
        NotificationMessage.objects.delete()

        # Askerlik durumu sorgusu için kullanılacak olan tarih aralığı
        baslangic_tarih = datetime.date.today() - datetime.timedelta(days=1)
        bitis_tarih = datetime.date.today() + datetime.timedelta(days=1)

        # Personel İşleri Dairesi kullanıcı girişi
        personel_isleri_usr = User.objects.get(username='personel_isleri_1')
        self.prepare_client('/tekil_personel_terfi', user=personel_isleri_usr)

        akademik_personel_id = 'XFLlsTdqyOV07kgQCbJiIGIvC0v'
        idari_personel_id = 'UIq8We6bYsj0zXHmnwkLDUDgWWt'

        akademik_personel = Personel.objects.get("XFLlsTdqyOV07kgQCbJiIGIvC0v")
        # Akademik personel görev aylığı yeni kademe ve derece durumu
        akademik_personel_ga_kademe = akademik_personel.gorev_ayligi_kademe + 1
        akademik_personel_ga_derece = akademik_personel.gorev_ayligi_derece
        akademik_personel_ga_gorunen = akademik_personel.gorev_ayligi_kademe
        if (akademik_personel_ga_kademe == 4) & (akademik_personel.gorev_ayligi_derece != akademik_personel.kadro_derece):
            akademik_personel_ga_kademe = 1
            akademik_personel_ga_derece -= 1

        # Akademik personel kazanılmış hak yeni kademe ve derece durumu
        akademik_personel_kh_kademe = akademik_personel.kazanilmis_hak_kademe + 1
        akademik_personel_kh_derece = akademik_personel.kazanilmis_hak_derece
        akademik_personel_kh_gorunen = akademik_personel.kazanilmis_hak_kademe
        if akademik_personel_kh_kademe == 4:
            akademik_personel_kh_kademe = 1
            akademik_personel_kh_derece -= 1

        # Akademik personel emekli muktesebat yeni kademe ve derece durumu
        akademik_personel_em_kademe = akademik_personel.emekli_muktesebat_kademe + 1
        akademik_personel_em_derece = akademik_personel.emekli_muktesebat_derece
        akademik_personel_em_gorunen = akademik_personel.emekli_muktesebat_kademe
        if akademik_personel_em_kademe == 4:
            akademik_personel_em_kademe = 1
            akademik_personel_em_derece -= 1

        idari_personel = Personel.objects.get("UIq8We6bYsj0zXHmnwkLDUDgWWt")

        # İdari personel görev aylığı yeni kademe ve derece durumu
        idari_personel_ga_kademe = idari_personel.gorev_ayligi_kademe + 1
        idari_personel_ga_derece = idari_personel.gorev_ayligi_derece
        idari_personel_ga_gorunen = idari_personel.gorev_ayligi_kademe
        if (idari_personel_ga_kademe == 4) & (idari_personel.gorev_ayligi_derece != idari_personel.kadro_derece):
            idari_personel_ga_kademe = 1
            idari_personel_ga_derece -= 1

        # İdari personel kazanılmış hak yeni kademe ve derece durumu
        idari_personel_kh_kademe = idari_personel.kazanilmis_hak_kademe + 1
        idari_personel_kh_derece = idari_personel.kazanilmis_hak_derece
        idari_personel_kh_gorunen = idari_personel.kazanilmis_hak_kademe
        if idari_personel_kh_kademe == 4:
            idari_personel_kh_kademe = 1
            idari_personel_kh_derece -= 1

        # İdari personel emekli müktesebat yeni kademe ve drece durumu
        idari_personel_em_kademe = idari_personel.emekli_muktesebat_kademe + 1
        idari_personel_em_derece = idari_personel.emekli_muktesebat_derece
        idari_personel_em_gorunen = idari_personel.emekli_muktesebat_kademe
        if idari_personel_em_kademe == 4:
            idari_personel_em_kademe = 1
            idari_personel_em_derece -= 1

        self.client.post(id=akademik_personel_id, model="Personel", param="personel_id",
                         wf="tekil_personel_terfi")
        akademik_personel_terfi_form = {
            "yeni_gorev_ayligi_derece" : akademik_personel_ga_derece,
            "yeni_gorev_ayligi_kademe" : akademik_personel_ga_kademe,
            "yeni_gorev_ayligi_gorunen" : akademik_personel_ga_gorunen,
            "yeni_kazanilmis_hak_derece" : akademik_personel_kh_derece,
            "yeni kazanilmis_hak_kademe" : akademik_personel_kh_kademe,
            "yeni_kazanilmis_hak_gorunen" : akademik_personel_kh_gorunen,
            "yeni_emekli_muktesebat_derece" : akademik_personel_em_derece,
            "yeni_emekli_muktesebat_kademe" : akademik_personel_em_kademe,
            "yeni_emekli_muktesebat_gorunen" : akademik_personel_em_gorunen

        }

        idari_personel_terfi_form = {
            "yeni_gorev_ayligi_derece" : idari_personel_ga_derece,
            "yeni_gorev_ayligi_kademe" : idari_personel_ga_kademe,
            "yeni_gorev_ayligi_gorunen" : idari_personel_ga_gorunen,
            "yeni_kazanilmis_hak_derece" : idari_personel_kh_derece,
            "yeni_kazanilmis_hak_kademe" : idari_personel_kh_kademe,
            "yeni_kazanilmis_hak_gorunen" : idari_personel_kh_gorunen,
            "yeni_emekli_muktesebat_derece" : idari_personel_em_derece,
            "yeni_emekli_muktesebat_kademe" : idari_personel_em_kademe,
            "yeni_emekli_muktesebat_gorunen" : idari_personel_em_gorunen
        }

        resp = self.client.post(model="Personel", wf="tekil_personel_terfi", form=akademik_personel_terfi_form)


        # Akademik personelin terfisinin durma durumunda görüntülenecek mesaj
        akademik_personel_terfi_durma_hata_mesaj = "%s %s isim soyisimli personelin terfisi durdurulmuştur"%(
            akademik_personel.ad, akademik_personel.soyad)

        # İdari personelin terfisinin durma durumunda görüntülenecek mesaj
        idari_personel_terfi_durma_hata_mesaj = "%s %s isim soyisimli personelin terfisi durdurulmuştur"%(
            idari_personel.ad, idari_personel.soyad
        )

        # Personelin terfisinin Personel İşleri tarafından yapılıp onaya gönderilmesi durumunda görüntülenecek mesaj
        personel_terfi_mesaj = "Terfi işlemi, onay sürecine girmiştir."


        # Bir personel askere gittiğinde yada ücretsiz izne ayrıldığında terfisi durdurulur

        # Akademik personel askerlik ve ücretsiz izin kontrolü
        try:
            akademik_personel_askerlik = AskerlikKayitlari.objects.get(
                personel_id = akademik_personel.key,
                baslama_tarihi__gte = baslangic_tarih,
                bitis_tarihi__lte = bitis_tarih
            )
            assert resp.json["msgbox"]["msg"] == akademik_personel_terfi_durma_hata_mesaj
        except ObjectDoesNotExist:
            pass

        try:
            akademik_personel_ucretsiz_izin = UcretsizIzin.objects.get(
                personel_id = akademik_personel.key,
                baslangic_tarih__gte = baslangic_tarih,
                bitis_tarihi__lte = bitis_tarih
            )
            assert resp.json["msgbox"]["msg"] == akademik_personel_terfi_durma_hata_mesaj
        except ObjectDoesNotExist:
            pass

        # Terfisi yapılan personel eğer akademik personel ise notification rektöre
        # İdari personel ise genel sekretere gitmelidir.
        # Aşağıda bunun kontrolü yapılmaktadır.
        assert NotificationMessage.objects.filter().count() == 1

        # Rektör kullanıcı girişi
        rektor_usr = User.objects.get(username='rektor')
        msg = NotificationMessage.objects.filter(receiver=rektor_usr)[0]
        token = msg.url.split('/')[-1]
        self.prepare_client('/tekil_personel_terfi', user=rektor_usr, token=token)

        # Lane değişimi olduğu ve tekrar notification gideceği için önceki notificationlar temizlenir
        NotificationMessage.objects.delete()

        resp = self.client.post(cmd="onayla_kaydet", form=akademik_personel_terfi_form)
        assert resp.json["msgbox"]["title"] == "TERFİ İŞLEMİ SONUÇ BİLGİSİ"

        # personel_isleri_1 kullanıcısına gelen notification bulunur.
        msg = NotificationMessage.objects.filter(receiver=personel_isleri_usr)[0]
        token = msg.url.split("/")[-1]
        # personel_isleri_1 kullanıcısı ve notification üzerinden wf ye ulaşılır.
        self.prepare_client("/tekil_personel_terfi", user=personel_isleri_usr, token=token)

        #ilgili wf adımına gidilir.
        resp = self.client.post(cmd="sonuc_bilgisi")

        # Ulaşılan wf adımından dönen terfi işlemi sonuç mesajı kontrol edilir.
        assert  resp.json["msgbox"]["title"] == "TERFİ İŞLEMİ SONUÇ BİLGİSİ"

