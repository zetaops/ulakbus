# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User, Okutman, Personel, Izin
from zengine.lib.test_utils import BaseTestCase
import time


class TestCase(BaseTestCase):
    def test_okutman_ders_ucreti_goruntuleme(self):



        for loop in range(2):
            # ogretim_elemani_2 kullanıcısıyla giriş yapılır.
            user = User.objects.get(username='ogretim_elemani_2')
            # testi yazılacak iş akışı seçilir.
            self.prepare_client('/okutman_ders_ucreti_goruntuleme', user=user)
            self.client.post()

            if loop == 0:
                for i in range(2):


                    # 2016 yılı Mayıs ayı seçilir. Veritabanında seçilen yıl ve
                    #  ayı içeren dönem bulunmamaktadır. 'Dönem Bulunamadı' başlıklı
                    # hata mesajının çıkması beklenir.
                    resp = self.client.post(form={"ay_sec": 5, "yil_sec": 1, "sec": 1})
                    assert resp.json['forms']['schema']["title"] == "Dönem Bulunamadı"

                    if i == 0:
                        # İlk döngüde hata mesajından sonra eğer geriye dönülmesi seçilirse,
                        # tarih seçme ekranına geri dönmesi beklenir.
                        resp = self.client.post(form={"iptal": "null", "geri_don": 1, "sec": 1}, flow="tarih_sec")
                        assert resp.json['forms']['schema'][
                                   "title"] == "Puantaj Tablosu Hazırlamak İstediğiniz Yıl ve Ayı Seçiniz"

                    if i == 1:
                        # Eğer iptal butonuna basılırsa, işem iptali hakkında bilgilendirme
                        # mesajı çıkması beklenir.
                        resp = self.client.post(form={"iptal": 1, "geri_don": "null", "sec": 1},
                                                flow="islem_iptali_bilgilendir")
                        assert resp.json["msgbox"]["title"] == "Durum Mesajı" and "iptal" in resp.json["msgbox"]["msg"]

            if loop == 1:
                # Geçerli bir dönemin bulunduğu tarih seçilir.
                resp = self.client.post(form={"ay_sec": 11, "yil_sec": 0, "sec": 1})

                # Ders ücreti hesaplama türü seçim ekranına gelmesi beklenir.
                assert resp.json['forms']['schema'][
                           "title"] == "Öğretim Görevlileri Puantaj Tablosu Hesaplama Türü Seçiniz"

                # Tür seçildikten sonra ekrana Puantaj Tablosu çıkarılması beklenir.
                resp = self.client.post(form={"ek_ders": 'null', "ders": 1})
                assert "PUANTAJ TABLOSU" in resp.json['forms']['schema']["title"]

                # Kullanıcı adından öğretim görevlisinin adı soyadı bulunur.
                # Oluşturulan puantaj tablosunun doğru öğretim görevlisi adına
                # oluşturulup oluşturulmadığı kontrol edilir.
                okutman_personel = Personel.objects.get(user=self.client.current.user)
                okutman = Okutman.objects.get(personel=okutman_personel)
                okutman_adi = okutman.ad + ' ' + okutman.soyad

                # Personel izin listesi getirilir.
                personel_izin_list = Izin.personel_izin_gunlerini_getir(okutman, 2016, 11)

                # Personel'in izin günlerinin doğru olup olmadığı test edilir.
                assert personel_izin_list == [16, 17, 18, 19, 20, 21]

                # Puantaj tablosu'nda öğretim görevlisinin isminin olduğu test edilir.
                assert okutman_adi.upper() in resp.json['forms']['schema']["title"].upper()
