# -*-  coding: utf-8 -*-
"""Öğrenci ile ilgili yardımcı class ve fonksiyonların yer aldığı dosyadır.
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from enum import Enum

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.models import Ogrenci, OgrenciProgram, OgrenciDersi
from pyoko.exceptions import ObjectDoesNotExist


class OgrenciHelper():
    """OgrenciHelper Class

    """

    def diploma_notu_uret(self, ogrenci_no):
        try:
            ogrenci_program = OgrenciProgram.objects.get(ogrenci_no=ogrenci_no)
            return "%s-%s-%s" % (ogrenci_program.giris_tarihi,
                                 ogrenci_program.program.yoksis_no, ogrenci_program.ogrenci_no)
        except ObjectDoesNotExist:
            return "Öğrenci Bulunamadı"


class HarfNotu(Enum):
    """
    HarfNotu.AA._4()

    """

    AA = {
        "name": "AA",
        "bas": 90,
        "bit": 100,
        "dort": 4.00
    }

    BA = {
        "name": "BA",
        "bas": 85,
        "bit": 89,
        "dort": 3.50
    }

    BB = {
        "name": "BB",
        "bas": 75,
        "bit": 84,
        "dort": 3.00
    }
    CB = {
        "name": "CB",
        "bas": 70,
        "bit": 74,
        "dort": 2.50
    }
    CC = {
        "name": "CC",
        "bas": 60,
        "bit": 69,
        "dort": 2.00
    }
    DC = {
        "name": "DC",
        "bas": 55,
        "bit": 59,
        "dort": 1.50
    }
    DD = {
        "name": "DD",
        "bas": 50,
        "bit": 54,
        "dort": 1.00
    }
    FD = {
        "name": "FD",
        "bas": 40,
        "bit": 49,
        "dort": 0.50
    }
    FF = {
        "name": "FF",
        "bas": 0,
        "bit": 39,
        "dort": 0.00
    }

    def get_4(self):
        return self.value.get('dort', None)

    def get_100(self):
        return self.value.get('bas', None), self.value.get('bit', None)

    @classmethod
    def puan_harf_notu(cls, puan):
        for name, obj in cls.__members__.items():
            bas, bit = obj.get_100()
            if puan in range(bas, bit + 1):
                return name


class AkademikTakvimEtkinlikleri(Enum):
    YENI_OGRENCI_ON_KAYIT = "Yeni Öğrenci Ön Kayıt"
    GUZ_BASLANGICI = "Güz Dönem Başlangıcı"
    GUZ_DERSLERIN_ACILMASI = "Derslerin Acılması"
    GUZ_SUBELENDIRME_DERS_PROGRAMI_ILANI = "Subelendirme ve Ders Programının Ilan Edilmesi"
    GUZ_OGRENCI_HARC = "Öğrenci Harç"
    GUZ_OGRENCI_EK_HARC = "Oğrenci Ek Harç"
    GUZ_MAZERETLI_OGRENCI_HARC = "Mazeretli Öğrenci Harç"
    YENI_OGRENCI_DERS_KAYIT = "Yeni Öğrenci Ders Kayıt"
    YENI_OGRENCI_DANISMAN_ONAY = "Yeni Öğrenci Danışman Onay"
    GUZ_DERS_KAYIT = "Ders Kayıt"
    GUZ_DANISMAN_ONAY = "Danışman Onay"
    GUZ_MAZERETLI_DERS_KAYIT = "Mazeretli Ders Kayıt"
    GUZ_MAZERETLI_DANISMAN_ONAY = "Mazeretli Danışman Onay"
    GUZ_DERSLERIN_BASLANGICI = "Derslerin Başlangıcı"
    GUZ_DERS_EKLE_BIRAK = "Ders Ekle/Bırak"
    GUZ_DERS_EKLE_BIRAK_DANISMAN_ONAY = "Ders Ekle/Bırak Danışman Onay"
    GUZ_DANISMAN_DERSTEN_CEKILME_ISLEMLERI = "Danışman Dersten Çekilme İşlemleri"
    GUZ_ARA_SINAV = "Ara Sinav"
    GUZ_ARA_SINAV_NOT_GIRIS = "Ara Sınav Not Giriş"
    GUZ_ARA_SINAV_NOT_YAYINLAMA = "Ara Sınav Notlarının Öğrenciye Yayınlanması"
    GUZ_ARA_SINAV_MAZERETLI = "Ara Sinav Mazeretli"
    GUZ_ARA_SINAV_MAZERET_NOT_GIRIS = "Ara Sınav Mazeret Not Giriş"
    GUZ_ARA_SINAV_MAZERET_NOT_YAYINLAMA = "Ara Sınav Mazeret Notlarının Yayınlanması"
    GUZ_SINAV_MADDI_HATA_DUZELTME = "Sınav Maddi Hata Düzeltme"
    GUZ_DERSLERIN_BITISI = "Derslerin Bitişi"
    GUZ_YARIYIL_SINAV = "Yariyil Sinav"
    GUZ_YARIYIL_SINAVI_NOT_GIRIS = "Yarıyıl Sınavı Not Giriş"
    GUZ_YARIYIL_SINAVI_NO_YAYINLAMA = "Yarıyıl Sınavı Notlarının Öğrenciye Yayınlanmasi"
    GUZ_BUT_VE_YARIYIL_SONU_MAZERET_SINAVI = "Bütünleme ve Yarı Yıl Sonu Mazeret Sınavı"
    GUZ_BUT_VE_YARIYIL_SONU_MAZERET_SINAVI_NOT_GIRIS = "Bütünleme ve Yarı Yıl Sonu Mazeret Sınavı Not Giriş"
    GUZ_BUT_VE_YARIYIL_SONU_MAZERET_SINAVI_NOT_YAYINLAMA = "Bütünleme ve Yarı Yıl Sonu Mazeret Sınavı Notlarının Öğrenciye Yayınlanması"
    GUZ_HARF_NOT_YAYINLAMA = "Harf Notlarının Öğrenciye Yayınlanması"
    GUZ_BUT_HARF_NOT_YAYINLAMA = "Bütünleme Harf Notlarının Öğrenciye Yayınlanması"
    GUZ_OGRETIM_ELEMANI_YOKLAMA_GIRISI = "Öğretim Elemanı Yoklama Girişi"
    GUZ_DONEMI_BITIS = "Güz Dönemi Bitiş"
    BAHAR_BASLANGICI = "Bahar Dönemi Başlangıcı"
    BAHAR_DERSLERIN_ACILMASI = "Bahar Donemi Derslerin Acilmasi"
    BAHAR_SUBELENDIRME_DERS_PROGRAMI_ILANI = "Subelendirme ve Ders Programının Ilan Edilmesi"
    BAHAR_OGRENCI_HARC = "Öğrenci Harç"
    BAHAR_OGRENCI_EK_HARC = "Öğrenci Ek Harç"
    BAHAR_MAZERETLI_OGRENCI_HARC = "Mazeretli Öğrenci Harç"
    BAHAR_DERS_KAYIT = "Ders Kayıt"
    BAHAR_DANISMAN_ONAY = "Danışman Onay"
    BAHAR_MAZERETLI_DERS_KAYIT = "Mazeretli Ders Kayıt"
    BAHAR_MAZERETLI_DANISMAN_ONAY = "Mazeretli Danışman Onay"
    BAHAR_DERSLERIN_BASLANGICI = "Derslerin Başlangıcı"
    BAHAR_DERS_EKLE_BIRAK = "Ders Ekle / Bırak"
    BAHAR_DERS_EKLE_BIRAK_ONAY = "Ders Ekle / Bırak Onay"
    BAHAR_ARA_SINAV = "Ara Sinav"
    BAHAR_ARA_SINAV_NOT_GIRIS = "Ara Sınav Not Giriş"
    BAHAR_ARA_SINAV_NOTLARININ_OGRENCIYE_YAYINLANMASI = "Ara Sınav Notlarının Yayınlanması"
    BAHAR_ARA_SINAV_MAZERETLI = "Ara Sinav Mazeretli"
    BAHAR_ARA_SINAV_MAZERET_NOT_GIRIS = "Ara Sınav Mazeret Not Giriş"
    BAHAR_ARA_SINAV_MAZERET_NOT_YAYINLAMA = "Ara Sınav Mazeret Notlarının Öğrenciye Yayınlanması"
    BAHAR_SINAV_MADDI_HATA_DUZELTME = "Sınav Maddi Hata Düzeltme"
    BAHAR_DERSLERIN_BITISI = "Derslerin Bitişi"
    BAHAR_YARIYIL_SINAV_BASLANGIC = "Yariyil Sinav baslangic"
    BAHAR_YARIYIL_SINAVI_NOT_GIRIS = "Yarıyıl Sınavı Not Giriş"
    BAHAR_YARIYIL_SINAVI_NOT_YAYINLAMA = "Yarıyıl Sınavı Notlarının Öğrenciye Yayınlanmasi"
    BAHAR_OGRETIM_ELEMANI_YOKLAMA_GIRISI = "Öğretim Elemanı Yoklama Girişi"
    BAHAR_BITISI = "Bahar Dönem Bitişi"
    YAZ_DONEMI_BASLANGICI = "Yaz Dönemi Başlangıcı"
    YAZ_DONEMI_DERSLERIN_BITISI = "Yaz Dönemi Derslerin Bitişi"
    YAZ_DONEMI_SINAVLARIN_BASLANGICI = "Yaz Dönemi Sınavların Başlangıcı"
    YAZ_DONEMI_BITISI = "Yaz Dönemi Bitişi"
    GUZ_DONEMI_DERSLER = "Güz Dönemi Dersler"
    BAHAR_DONEMI_DERSLER = "Bahar Dönemi Dersler"
    YAZ_DONEMI_DERSLER = "Yaz Dönemi Dersler"
    ISCI_BAYRAMI = "1 Mayıs İşçi Bayrami"
    ULUSAL_EGEMENLIK_VE_COCUK_BAYRAMI = "23 Nisan Ulusal Egemenlik ve Çocuk Bayramı"
    GENCLIK_VE_SPOR_BAYRAMI = "19 Mayıs Genclik ve Spor Bayramı"
