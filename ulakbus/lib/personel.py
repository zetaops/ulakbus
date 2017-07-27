# -*-  coding: utf-8 -*-
"""
"""
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import datetime
from ulakbus.lib.date_time_helper import zaman_araligi

__author__ = 'Ali Riza Keles'


def personel_izin_gunlerini_getir(okutman, yil, ay):
    """
    Args:
        okutman: okutman object
        yil: 2016
        ay: 7

    Returns: Seçilen yıl ve ay içinde
    okutmanın izin ve ücretsiz izinlerini
    gün şeklinde döndüren liste.

    """
    from ulakbus.models.personel import Izin, UcretsizIzin
    from ulakbus.lib.date_time_helper import yil_ve_aya_gore_ilk_ve_son_gun

    baslangic, bitis = yil_ve_aya_gore_ilk_ve_son_gun(yil, ay)
    personel_izin_list = []
    for i in range(2):
        model = Izin if i == 0 else UcretsizIzin

        for personel_izin in model.objects.filter(personel=okutman.personel,
                                                  baslangic__gte=baslangic,
                                                  bitis__lte=bitis):
            for gun in zaman_araligi(personel_izin.baslangic, personel_izin.bitis):
                    personel_izin_list.append(gun.day)

    return personel_izin_list


def gorunen_kademe_hesapla(derece, kademe):
    """
    Args:
        derece (int): personel derece
        kademe (int): personel kademe

    Returns:
        kademe (int): limite gore hesaplanmis kademe degeri
    """
    kademe_limitleri = {1: 4, 2: 6, 3: 8, 4: 9, 5: 9, 6: 9, 7: 9, 8: 9, 9: 9, 10: 9, 11: 9,
                        12: 9, 13: 9, 14: 9, 15: 9}
    try:
        kademe = kademe_limitleri[derece] if kademe > kademe_limitleri[derece] else kademe
        return kademe
    except KeyError:
        return 0


def derece_ilerlet(pkd, der, kad):
    """
    Derece 3 kademede bir artar. Eger kademe 4 gelmise, derece 1 arttirilir
    Args:
        pkd (int): personel kadro derecesi
        der (int): derece
        kad (int): kademe

    Returns:
        der, kad: ilerletilmis derece ve kademe

    """
    if pkd < der:
        if kad == 4:
            kad = 1
            der -= 1
    return der, kad


def suren_terfi_var_mi(p):
    """
    Mevcut wfler icinde arama yaparak personel hakkinda, devam eden terfi isleminin
    olup olmadigi kontrol edilir.

    Args:
        p (str): personel key

    Returns:
        Devam eden islem varsa True, yoksa False

    """

    # TODO: wf ler icinde arama yap
    return False


def terfi_tarhine_gore_personel_listesi(baslangic_tarihi=None, bitis_tarihi=None,
                                        personel_turu=None, suren_terfi_kontrol=True):
    """
    Args:
        baslangic_tarihi (date): baslangic_tarihi
        bitis_tarihi (date): bitis_tarihi
        personel_turu (str): personel turu, 1 akademik, 2 idari
        suren_terfi_kontrol (bool): personel listesi hazirlanirken suren baska terfi islemi varmi
                                    kontrolunun yapilip yapilmayacagini kontrol eder.

    Returns:
        personeller (dict): personel kademe derece bilgileri iceren sozluk

    """

    from ulakbus.models.personel import Personel

    simdi = datetime.date.today()
    baslangic_tarihi = baslangic_tarihi or simdi
    bitis_tarihi = bitis_tarihi or simdi + datetime.timedelta(days=90)

    personeller = {}

    qs = Personel.objects.all(personel_turu=personel_turu)

    terfisi_gelen_personeller = qs.or_filter(
        ga_sonraki_terfi_tarihi__range=[baslangic_tarihi, bitis_tarihi],
        kh_sonraki_terfi_tarihi__range=[baslangic_tarihi, bitis_tarihi],
        em_sonraki_terfi_tarihi__range=[baslangic_tarihi, bitis_tarihi]
    )

    for personel in terfisi_gelen_personeller:

        suren_terfi = False
        if suren_terfi_kontrol:
            suren_terfi = suren_terfi_var_mi(personel.key)

        if not suren_terfi_kontrol or not suren_terfi:
            # personel temel bilgileri
            p_data = {"key": personel.key, "tckn": personel.tckn, "ad": personel.ad,
                      "soyad": personel.soyad, "kadro_derece": personel.kadro.derece,
                      "suren_terfi": suren_terfi}

            # personel guncel derece ve kademeleri
            p_data.update(
                {
                    "guncel_gorev_ayligi_derece": personel.gorev_ayligi_derece,
                    "guncel_gorev_ayligi_kademe": personel.gorev_ayligi_kademe,
                    "guncel_kazanilmis_hak_derece": personel.kazanilmis_hak_derece,
                    "guncel_kazanilmis_hak_kademe": personel.kazanilmis_hak_kademe,
                    "guncel_emekli_muktesebat_derece": personel.emekli_muktesebat_derece,
                    "guncel_emekli_muktesebat_kademe": personel.emekli_muktesebat_kademe
                }
            )

            # personel guncel gorunen kademeleri
            p_data.update(
                {
                    "gorunen_gorev_ayligi_kademe": personel.gorunen_gorev_ayligi_kademe,
                    "gorunen_kazanilmis_hak_kademe": personel.gorunen_kazanilmis_hak_kademe,
                    "gorunen_emekli_muktesebat_kademe": personel.gorunen_emekli_muktesebat_kademe
                }
            )

            pkd = personel.kadro.derece

            # terfi sonrasi derece ve kademeler
            p_data["terfi_sonrasi_gorev_ayligi_derece"], p_data[
                "terfi_sonrasi_gorev_ayligi_kademe"] = derece_ilerlet(
                pkd,
                personel.gorev_ayligi_derece,
                personel.gorev_ayligi_kademe + 1)

            p_data["terfi_sonrasi_kazanilmis_hak_derece"], p_data[
                "terfi_sonrasi_kazanilmis_hak_kademe"] = derece_ilerlet(
                pkd,
                personel.kazanilmis_hak_derece,
                personel.kazanilmis_hak_kademe + 1)

            p_data["terfi_sonrasi_emekli_muktesebat_derece"], p_data[
                "terfi_sonrasi_emekli_muktesebat_kademe"] = derece_ilerlet(
                pkd,
                personel.gorev_ayligi_derece,
                personel.gorev_ayligi_kademe + 1)

            # terfi sonrasi gorunen kademeler
            p_data["terfi_sonrasi_gorunen_gorev_ayligi_kademe"] = gorunen_kademe_hesapla(
                p_data["terfi_sonrasi_gorev_ayligi_derece"],
                p_data["terfi_sonrasi_gorev_ayligi_kademe"])
            p_data["terfi_sonrasi_gorunen_kazanilmis_hak_kademe"] = gorunen_kademe_hesapla(
                p_data["terfi_sonrasi_kazanilmis_hak_derece"],
                p_data["terfi_sonrasi_kazanilmis_hak_kademe"])
            p_data["terfi_sonrasi_gorunen_emekli_muktesebat_kademe"] = gorunen_kademe_hesapla(
                p_data["terfi_sonrasi_emekli_muktesebat_derece"],
                p_data["terfi_sonrasi_emekli_muktesebat_kademe"])

            personeller[personel.key] = p_data

    return personeller


def yevmiye_ucreti(derece, ek_gosterge):

    """
    Ek göstergesi 8000 ve daha yüksek olan kadrolarda bulunanlar 48,28
    Ek göstergesi 5800(dahil)-8000 (hariç) olan kadrolarda bulunanlar 45
    Ek göstergesi 3000(dahil)-5800(hariç) olan kadrolarda bulunanlar 42,25
    Aylık/kadro derecesi 1-4 olanlar 37,25
    Aylık/kadro derecesi 5-15 olanlar, 36,25

    Args:
        derece (int): yevmiye için personel derecesi
        ek_gosterge (int): yevmiye için personel ek_gostergesi

    Returns:
        personelin derecesine yada ek gostergesine baglı olarak gunluk yevmiye

    """
    from ulakbus.settings import EK_GOSTERGE_8K,EK_GOSTERGE_5800_8K,EK_GOSTERGE_3K_5800
    from ulakbus.settings import DERECE_1_4,DERECE_5_15

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


def yevmiye_hesapla(konaklama_gun_sayisi, derece, ek_gosterge):

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

    yevmiye = yevmiye_ucreti(derece, ek_gosterge)
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


def yol_masrafi_hesapla(derece, ek_gosterge, km, tasit_ucreti, yolculuk_gun_sayisi,
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

    from ulakbus.settings import KM_KATSAYISI

    yevmiye = yevmiye_ucreti(derece, ek_gosterge)
    mesafe_ucreti = yevmiye * KM_KATSAYISI
    tasit_ucreti = (birey_sayisi + 1) * tasit_ucreti
    seyahat_suresi = (birey_sayisi + 1) * yevmiye * yolculuk_gun_sayisi

    toplam_yol_masrafi = 20 * yevmiye + mesafe_ucreti * km + tasit_ucreti + seyahat_suresi

    if birey_sayisi == 0:
        return toplam_yol_masrafi
    else:
        #diger bireyler için yevmiyenin 10 katı
        return toplam_yol_masrafi + 10 * (birey_sayisi) * yevmiye