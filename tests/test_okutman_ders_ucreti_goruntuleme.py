# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User,Donem, DersEtkinligi, Unit
from zengine.lib.test_utils import BaseTestCase
from ulakbus.lib.personel import personel_izin_gunlerini_getir
from ulakbus.views.reports.ders_ucreti_hesaplama import \
    doneme_gore_okutman_etkinlikleri,okutman_aylik_plani,\
    ders_etkinligine_gore_tarih_araligi
from ulakbus.lib.date_time_helper import resmi_tatil_gunleri_getir,\
    yil_ve_aya_gore_ilk_son_gun
from datetime import date

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
                resp = self.client.post(form={"ay_sec": 11 , "yil_sec": 0, "sec": 1})

                # Ders ücreti hesaplama türü seçim ekranına gelmesi beklenir.
                assert resp.json['forms']['schema'][
                           "title"] == "Öğretim Görevlileri Puantaj Tablosu Hesaplama Türü Seçiniz"

                # Tür seçildikten sonra ekrana Puantaj Tablosu çıkarılması beklenir.
                resp = self.client.post(form={"ek_ders": 'null', "ders": 1})
                assert "PUANTAJ TABLOSU" in resp.json['forms']['schema']["title"]

                # Kullanıcı adından öğretim görevlisinin adı soyadı bulunur.
                # Oluşturulan puantaj tablosunun doğru öğretim görevlisi adına
                # oluşturulup oluşturulmadığı kontrol edilir.
                okutman = user.personel.okutman
                okutman_adi = okutman.__unicode__()

                # Bir döneme denk geldiği kontrol edilir.
                donem_list = Donem.takvim_ayina_rastlayan_donemler(2016, 11)
                assert len(donem_list) == 1

                ders_etkinlik_list = doneme_gore_okutman_etkinlikleri(donem_list, okutman, True)

                # Etkinlik olan günlerin etkinlik listede olduğu kontrol edilir.
                for etkinlik in DersEtkinligi.objects.filter(donem=donem_list[0], okutman=okutman, ek_ders=False):
                    assert etkinlik.gun in ders_etkinlik_list[0]

                # Personel izin listesi getirilir.
                personel_izin_list = personel_izin_gunlerini_getir(okutman, 2016, 11)

                birim_unit = Unit.objects.get(yoksis_no = okutman.birim_no)
                resmi_tatil_list = resmi_tatil_gunleri_getir(birim_unit,2016,5)
                assert 19 and 1 in resmi_tatil_list[0]

                tarih_araligi = ders_etkinligine_gore_tarih_araligi(donem_list, 2016, 11, birim_unit)
                resmi_tatil_list = resmi_tatil_gunleri_getir(birim_unit, 2016, 11)

                aylik_plan = okutman_aylik_plani(donem_list, ders_etkinlik_list,
                                    resmi_tatil_list, personel_izin_list,
                                    tarih_araligi,2016, 11)

                son_gun = yil_ve_aya_gore_ilk_son_gun(2016,11)[1].day

                for i in range(son_gun):
                    if resp.json['objects'][1]['fields'][" %i"%(i+1)]== ' ':
                        assert i+1 not in aylik_plan[0]
                    elif resp.json['objects'][1]['fields'][" %i"%(i+1)]== 'İ':
                        assert aylik_plan[0][i+1] == 'İ'
                    elif resp.json['objects'][1]['fields'][" %i"%(i+1)]== 'R':
                        assert aylik_plan[0][i+1] == 'R'
                    else:
                        hafta_gun = date(2016,11,i+1).isoweekday()

                        assert resp.json['objects'][1]['fields'][" %i"%(i+1)] == str(ders_etkinlik_list[0][hafta_gun])
                        assert resp.json['objects'][1]['fields'][" %i"%(i+1)] == str(aylik_plan[0][i+1])

                # Personel'in izin günlerinin doğru olup olmadığı test edilir.
                assert personel_izin_list == [16, 17, 18, 19, 20, 21]

                # Puantaj tablosu'nda öğretim görevlisinin isminin olduğu test edilir.
                assert okutman_adi.upper() in resp.json['forms']['schema']["title"].upper()
