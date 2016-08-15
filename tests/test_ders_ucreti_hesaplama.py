# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User, Okutman, Donem, Takvim, Unit
from zengine.lib.test_utils import BaseTestCase
from ulakbus.views.reports.ders_ucreti_hesaplama import donem_aralik_dondur
import calendar


class TestCase(BaseTestCase):
    def test_ders_ucreti_hesaplama(self):

        for loop in range(3):
            # mutemet kullanıcısıyla giriş yapılır.
            user = User.objects.get(username='mutemet_1')
            # testi yazılacak iş akışı seçilir.
            self.prepare_client('/ders_ucreti_hesaplama', user=user)
            self.client.post()

            if loop == 0:
                for i in range(2):

                    # 2016 yılı Aralık ayı seçilir. Veritabanında seçilen yıl ve


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


                        # Eğer iptal butonuna basılırsa, işlem iptali hakkında bilgilendirme
                        # mesajı çıkması beklenir.
                        resp = self.client.post(form={"iptal": 1, "geri_don": "null", "sec": 1},
                                                flow="islem_iptali_bilgilendir")
                        assert resp.json["msgbox"]["title"] == "Durum Mesajı" and "iptal" in resp.json["msgbox"]["msg"]

            if loop == 1:

                # Geçerli bir dönemin bulunduğu tarih seçildiğinde, mutemetin
                # işlem yaptığı birime ait öğretim görevlilerinin isimlerinin
                # olduğu bir form gelmesi beklenir.
                resp = self.client.post(form={"ay_sec": 11, "yil_sec": 0, "sec": 1})
                assert resp.json['forms']['schema']["title"] == "Okutman Seçiniz"

                # Ekrana gelen öğretim görevlisi sayısıyla veritabanındaki sayının
                # aynı olması beklenir.
                birim_no = self.client.current.role.unit.yoksis_no
                assert len(resp.json['forms']['model']["OkutmanListesi"]) == len(
                    Okutman.objects.filter(birim_no=birim_no))

                okutman_listesi = resp.json['forms']['model']["OkutmanListesi"]

                # Varsayılan olarak tüm öğretim görevlileri seçili halde gelir.
                # Seçimleri kaldırılır.
                for i in range(len(okutman_listesi)):
                    okutman_listesi[i]['secim'] = False

                for i in range(2):
                    # Hiçbir öğretim görevlisi seçmeden ilerlemeye çalışıldığında, işlem
                    # yapacak öğretim görevlisi olmadığından hata mesajı göstermesi beklenir.
                    resp = self.client.post(form={"OkutmanListesi": okutman_listesi, "sec": 1})
                    assert resp.json['forms']['schema']["title"] == "Öğretim Görevlisi Seçmelisiniz"

                    if i == 0:
                        # İlk döngüde hata mesajından sonra eğer geriye dönülmesi seçilirse,
                        # öğretim görevlisi seçme ekranına geri dönmesi beklenir.
                        resp = self.client.post(form={"iptal": "null", "geri_don": 1, "sec": 1}, flow="okutman_sec")
                        assert resp.json['forms']['schema']["title"] == \
                               "Okutman Seçiniz"
                    if i == 1:


                        # Eğer iptal butonuna basılırsa, işlem iptali hakkında bilgilendirme
                        # mesajı çıkması beklenir.
                        resp = self.client.post(form={"iptal": 1, "geri_don": "null", "sec": 1},
                                                flow="islem_iptali_bilgilendir")
                        assert resp.json["msgbox"]["title"] == "Durum Mesajı" and "iptal" in resp.json["msgbox"]["msg"]

            if loop == 2:
                # Geçerli bir tarih ve öğretim görevlisi seçilmesi senaryosu.
                resp = self.client.post(form={"ay_sec": 11, "yil_sec": 0, "sec": 1})
                okutman_listesi = resp.json['forms']['model']["OkutmanListesi"]

                for i in range(3):

                    birim_no = self.client.current.role.unit.yoksis_no
                    birim_unit = Unit.objects.get(yoksis_no=birim_no)


                    # 2016 yılı Şubat ayı verilir. Bahar dönemi ders başlangıcı 21 Şubat olduğu
                    # için tarih aralığının (21,29) olması kontrol edilir.
                    if i == 0:
                        takvim = calendar.monthrange(2016, 2)
                        donem_list = Donem.takvim_ayina_rastlayan_donemler(2016, 2, takvim)
                        assert len(donem_list) == 1

                        resmi_tatil_list, akademik_takvim_list = Takvim.resmi_tatil_gunleri_getir(donem_list,
                                                                                                  birim_unit, 2016, 2)

                        tarih_araligi = donem_aralik_dondur(donem_list, 2016, 2, takvim, akademik_takvim_list)

                        assert tarih_araligi == [(21, 29)]

                    # 2016 yılı Temmuz ayı verilir. Temmuz ayı Bahar dönemi bitişi ve Yaz dönemi başlangıcıdır.
                    # 2 döneme denk gelir. Ama Temmuz ayında sadece yaz döneminin ders etkinlikleri vardır.
                    # 2 döneme rastlayıp sadece 1 dönemin ders etkinliklerine rastladığı için, tarih aralığının
                    # 2 tuple dan oluşması ve bir tanesinin birbirine eşit olması beklenir.
                    if i == 1:
                        takvim = calendar.monthrange(2016, 7)
                        donem_list = Donem.takvim_ayina_rastlayan_donemler(2016, 7, takvim)
                        assert len(donem_list) == 2

                        resmi_tatil_list, akademik_takvim_list = Takvim.resmi_tatil_gunleri_getir(donem_list,
                                                                                                  birim_unit, 2016, 7)

                        tarih_araligi = donem_aralik_dondur(donem_list, 2016, 7, takvim, akademik_takvim_list)

                        assert tarih_araligi == [(1, 1), (15, 31)]


                    # 2016 yılı Mayıs ayı verilir. Mayıs ayı Bahar dönemine rastlar.
                    # 19 Mayıs ve 1 Mayıs'ın resmi tatil listesinde olması beklenir.
                    else:
                        takvim = calendar.monthrange(2016, 5)
                        donem_list = Donem.takvim_ayina_rastlayan_donemler(2016, 5, takvim)
                        assert len(donem_list) == 1
                        resmi_tatil_list, akademik_takvim_list = Takvim.resmi_tatil_gunleri_getir(donem_list,
                                                                                                  birim_unit, 2016, 5)

                        assert 19 and 1 in resmi_tatil_list[0]
                        tarih_araligi = donem_aralik_dondur(donem_list, 2016, 5, takvim, akademik_takvim_list)

                        assert tarih_araligi == [(1, 31)]

                # Varsayılan olarak tüm öğretim görevlileri seçili olarak
                # gelmesini kontrol eder.
                for i in range(len(okutman_listesi)):
                    assert okutman_listesi[i]['secim'] == True

                # Hepsi seçili olarak bir sonraki adıma ilerlenir.
                resp = self.client.post(form={"OkutmanListesi": okutman_listesi, "sec": 1})

                # Ders ücreti hesaplama türü seçim ekranına gelmesi beklenir.
                assert resp.json['forms']['schema'][
                           "title"] == "Öğretim Görevlileri Puantaj Tablosu Hesaplama Türü Seçiniz"

                # Tür seçildikten sonra ekrana Puantaj Tablosu çıkarılması beklenir.
                resp = self.client.post(form={"ek_ders": 'null', "ders": 1})
                assert "PUANTAJ TABLOSU" in resp.json['forms']['schema']["title"]
