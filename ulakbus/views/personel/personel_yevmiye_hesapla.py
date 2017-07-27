# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView

# 2017 derece ve ekgostergeye baglı olarak gundelik yevmiye ücretleri
EK_GOSTERGE_8K = 48.25
EK_GOSTERGE_5800_8K = 45
EK_GOSTERGE_3K_5800 = 42.25
DERECE_1_4 = 37.25
DERECE_5_15 = 36.25

# Km hesabı için
KM_KATSAYISI = 5 / 100.0


class PersonelYevmiyeHesapla(CrudView):
    def personel_yevmiye_yol_hesapla(self, konaklama_gun_sayisi, derece, ek_gosterge, km,
                                     tasit_ucreti,
                                     yolculuk_gun_sayisi,
                                     birey_sayisi):

        """
        Bu metot yevmiye ve yol_masrafi hesapla metotlarının sonuclarını alır

        Args:
            konaklama_gun_sayisi (int): konaklama gun sayisi yevmiye hesabı için
            derece (int): yevmiye için personel derecesi
            ek_gosterge (int): yevmiye için personel ek_gostergesi
            km (int): yolculuk hesabı için gidilecek olan km
            tasit_ucreti (int): en uygun yol ve tasıta gore verilir
            yolculuk_gun_sayisi (int): yolculugun kac gun sureceği
            birey_sayisi (int): kişinin bakmakla yükümlü olduğu kişi sayısı

        Returns:

        """

        yevmiye = self.yevmiye_hesapla(konaklama_gun_sayisi, derece, ek_gosterge)
        yol_masrafi = self.yol_masrafi_hesapla(derece, ek_gosterge, km, tasit_ucreti,
                                               yolculuk_gun_sayisi, birey_sayisi)
        print yevmiye, yol_masrafi

    def yevmiye_hesapla(self, konaklama_gun_sayisi, derece, ek_gosterge):

        """
        Bu Metot gelen parametrelere baglı olarak bize kişinin konaklama ücreti için
        verilecek yevmiyeyi hesaplar

        Hesaplama Şekli:
        6245 sayılı Harcırah Kanununun 33 üncü maddesinin
        (b) fıkrasına göre yatacak yer temini için ödenecek ücretlerin
        hesabında gündeliklerinin %50 artırımlı miktarı,
        (d) fıkrasına göre yapılacak ödemelerde ise görevlendirmenin
        ilk 10 günü için gündeliklerinin %50 artırımlı miktarı,
        takip eden 80 günü için gündeliklerinin %50’si

        Args:
            konaklama_gun_sayisi (int): konaklama gun sayisi yevmiye hesabı için
            derece (int): yevmiye için personel derecesi
            ek_gosterge (int): yevmiye için personel ek_gostergesi

        Returns:
            toplam (float) : toplam yevmiyeyi dondurur

        """

        yevmiye = self.yevmiye_ucreti(derece, ek_gosterge)
        toplam = 0.0
        if konaklama_gun_sayisi > 10:
            if konaklama_gun_sayisi > 90:
                toplam = (1.5 * 10 * yevmiye)
                konaklama_gun_sayisi = konaklama_gun_sayisi - 10
                toplam += (0.5 * 80 * yevmiye)
                konaklama_gun_sayisi = konaklama_gun_sayisi - 80
                toplam += ((2 / 3.0) * 0.4 * yevmiye * konaklama_gun_sayisi)
            else:
                toplam += (1.5 * 10 * yevmiye)
                konaklama_gun_sayisi = konaklama_gun_sayisi - 10
                toplam += (0.5 * yevmiye * konaklama_gun_sayisi)
        else:
            toplam += (1.5 * konaklama_gun_sayisi * yevmiye)
        return toplam

    def yevmiye_ucreti(self, derece, ek_gosterge):

        """
        Ek göstergesi 8000 ve daha yüksek olan kadrolarda bulunanlar 48,28
        Ek göstergesi 5800(dahil)-8000 (hariç) olan kadrolarda bulunanlar 45
        Ek göstergesi 3000(dahil)-5800(hariç) olan kadrolarda bulunanlar 42,25
        Aylık/kadro derecesi 1-4 olanlar 37,25
        Aylık/kadro derecesi 5-15 olanlar

        Args:
            derece (int): yevmiye için personel derecesi
            ek_gosterge (int): yevmiye için personel ek_gostergesi

        Returns:
            personelin derecesine yada ek gostergesine baglı olarak gunluk yevmiye

        """

        if ek_gosterge >= 8000:
            return EK_GOSTERGE_8K
        elif ek_gosterge >= 5800 and ek_gosterge < 8000:
            return EK_GOSTERGE_5800_8K
        elif ek_gosterge >= 3000 and ek_gosterge < 5800:
            return EK_GOSTERGE_3K_5800
        elif derece > 0 and derece < 5:
            return DERECE_1_4
        elif derece > 4 and derece < 15:
            return DERECE_5_15

    def yol_masrafi_hesapla(self, derece, ek_gosterge, km, tasit_ucreti, yolculuk_gun_sayisi,
                            birey_sayisi):
        """

        Bu metot toplam yol masraflarını hesaplar

        Yevmiye-Yol mesafe ücreti-Taşıt ücreti-Seyahat günlerine ait yevmiyeler
        Kendisi için yurtiçi gündeliğinin 20 (yirmi) katı
        Aile fertleri için 10 kati
        Yol mesafe ücreti: Her kilometre basına (gundelik_yevmiye*5)/100
        Taşıt ücreti: en uygun yol ve tasıta gore verilir
        seyahat suresi 24 saatlik dilimde birey sayısına gore yevmiye eklenir

        Args:
            derece (int): yevmiye için personel derecesi
            ek_gosterge (int): yevmiye için personel ek_gostergesi
            km (int): yolculuk hesabı için gidilecek olan km
            tasit_ucreti (int): en uygun yol ve tasıta gore verilir
            yolculuk_gun_sayisi (int): yolculugun kac gun sureceği
            birey_sayisi (int): kişinin bakmakla yukumlu oldugu kisi sayısı

        Returns:
            toplam_yol _masrafi (float) : birey sayısına gore toplam yol masrafı dondurulur

        """
        yevmiye = self.yevmiye_ucreti(derece, ek_gosterge)
        mesafe_ucreti = yevmiye * KM_KATSAYISI
        tasit_ucreti = (birey_sayisi + 1) * tasit_ucreti
        seyahat_suresi = (birey_sayisi + 1) * yevmiye * yolculuk_gun_sayisi

        toplam_yol_masrafi = 20 * yevmiye + mesafe_ucreti * km + tasit_ucreti + seyahat_suresi

        if birey_sayisi == 0:
            return toplam_yol_masrafi
        else:
            #diger bireyler için yevmiyenin 10 katı
            return toplam_yol_masrafi + 10 * (birey_sayisi) * yevmiye
