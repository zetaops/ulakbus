# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from dateutil.relativedelta import relativedelta
from pyoko.exceptions import ObjectDoesNotExist
import datetime

from ulakbus.lib.date_time_helper import zaman_araligi
from dateutil.relativedelta import relativedelta

__author__ = 'Ali Riza Keles'

# hitap_fixture ogrenim durumu
# ogrenim durumu 1 (okur yazar ise, maksimum
# 13. kademeye kadar yukselebilir.)
ogrenim_durumuna_gore_terfi = {
    1: {
        "derece": 7,
        "kademe": 31
    },
    2: {
        "derece": 7,
        "kademe": 31
    },
    3: {
        "derece": 5,
        "kademe": 25
    },
    4: {
        "derece": 5,
        "kademe": 25
    },
    5: {
        "derece": 4,
        "kademe": 22
    },
    6: {
        "derece": 3,
        "kademe": 19
    },
    7: {
        "derece": 1,
        "kademe": 13
    },
    8: {
        "derece": 1,
        "kademe": 13
    },
    9: {
        "derece": 1,
        "kademe": 13
    }
}

# derecede ilerlenebilecek maksimum kademe
derece_max_kademe = {
    1: 13,
    2: 16,
    3: 19,
    4: 22,
    5: 25,
    6: 28,
    7: 31,
    8: 34,
    9: 37,
    10: 40,
    11: 43,
    12: 46,
    13: 49
}


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
        return kademe_limitleri[derece] if kademe > kademe_limitleri[derece] else kademe
    except KeyError:
        return 0


def terfi_tikanma_kontrol(personel):
    """
    Terfi tıkanması kontrolü görev aylığı, kazanılmış hak ve emekli müktesebat
    içinde ayrı ayrı gerçekleştirilir.
    Args:
        personel: Personel class instance

    Returns:
        ga, kh, em : Terfi tıkanma durumları boolean türünden ifadeleri

    """
    ga = False
    kh = False
    em = False

    if personel.personel_turu == 1:
        if personel.kadro.derece >= personel.gorev_ayligi_derece:
            ga = True

        if personel.kadro.derece >= personel.kazanilmis_hak_derece:
            kh = True

        if personel.kadro.derece >= personel.emekli_muktesebat_derece:
            em = True

        return ga, kh, em
    else:
        from ulakbus.models import HizmetOkul
        personel_okul = HizmetOkul.objects.order_by('-mezuniyet_tarihi').filter(
            tckn=personel.tckn
        ).exclude(ogrenim_durumu=None)

        son_mezun_olunan_okul = personel_okul[0]

        derece_sinir = ogrenim_durumuna_gore_terfi[son_mezun_olunan_okul.ogrenim_durumu]['derece']
        #kademe_sinir = ogrenim_durumuna_gore_terfi[son_mezun_olunan_okul.ogrenim_durumu]['kademe']

        if personel.gorev_ayligi_derece <= derece_sinir:
            ga = True

        if personel.kazanilmis_hak_derece <= derece_sinir:
            kh = True

        if personel.emekli_muktesebat_derece <= derece_sinir:
            em = True

    return ga, kh, em


def torba_kadro_kontrol(personel):
    """
    İdari bir personel eğer torba kadro ile 1,2,3,4 derecelerinden birine sahip bir
    kadroya atanmışsa görev aylığı derecesi otomatik olarak kadro derecesiyle eşit
    olacağı için kazanılmış hak ve emekli müktesebat dereceleri kadro derecesiyle
    eşit olana kadar görev aylığı kademe ilerleyişi durdurulur.
    Args:
        personel: Personel class instance

    Returns:
        personel torba kadro ile atanmışsa True aksi halde False
    """
    return all(
        [
            personel.kadro.derece in [1, 2, 3, 4],
            personel.kadro.derece == personel.gorev_ayligi_derece,
            (personel.kazanilmis_hak_derece > personel.kadro.derece or
             personel.emekli_muktesebat_derece > personel.kadro.derece)
        ]
    )


def kademe_ilerlet(p, ga_kontrol, kh_kontrol, em_kontrol):
    """
    Personelin şartlara göre kademe derece ilerleyişini gerçekleştirir.
    ga_kontrol, kh_kontrol, em_kontrol parametreleriyle görev aylığı,
    kazanılmış hak ve emekli müktesebat bilgilerinden hangileri
    üzerinde terfi işlemi gerçekleştirileceği belirlenir.

    Args:
        p: Personel class instance
        ga_kontrol : Boolean
        kh_kontrol : Boolean
        em_kontrol : Boolean

    Returns:
        yeni kademeler (tuple)

    """

    ga = p.gorev_ayligi_kademe
    kh = p.kazanilmis_hak_kademe
    em = p.emekli_muktesebat_kademe

    if kh_kontrol and kh < derece_max_kademe[p.kazanilmis_hak_derece]:
        kh += 1

    if em_kontrol and em < derece_max_kademe[p.emekli_muktesebat_derece]:
        em += 1

    if ga_kontrol and ga < derece_max_kademe[p.gorev_ayligi_derece]:
        if (p.personel_turu == 2 and torba_kadro_kontrol(p) is False) or p.personel_turu == 1:
            ga += 1

    return ga, kh, em


def derece_ilerlet(**kwargs):
    """
        kademe durumuna göre derece ilerleten metod.
    Args:
        **kwargs:

    Returns:

    """
    ga_derece = kwargs.pop('ga_derece')
    ga_kademe = kwargs.pop('ga_kademe')
    kh_derece = kwargs.pop('kh_derece')
    kh_kademe = kwargs.pop('kh_kademe')
    em_derece = kwargs.pop('em_derece')
    em_kademe = kwargs.pop('em_kademe')
    personel = kwargs.pop('personel')

    ga_tikanma, kh_tikanma, em_tikanma = terfi_tikanma_kontrol(personel)

    if all([not ga_tikanma, ga_derece > 1, ga_kademe >= 4]):
        ga_kademe = 1
        ga_derece -= 1

    if all([not kh_tikanma, kh_derece > 1, kh_kademe >= 4]):
        kh_kademe = 1
        kh_derece -= 1

    if all([not em_tikanma, em_derece > 1, em_kademe >= 4]):
        em_kademe = 1
        em_derece -= 1

    return {
        "ga": {
            "derece": ga_derece,
            "kademe": ga_kademe
        },
        "kh": {
            "derece": kh_derece,
            "kademe": kh_kademe
        },
        "em": {
            "derece": em_derece,
            "kademe": em_kademe
        }
    }


def terfi(personel, baslangic_tarihi, bitis_tarihi):
    ga_tarih = personel.ga_sonraki_terfi_tarihi
    kh_tarih = personel.kh_sonraki_terfi_tarihi
    em_tarih = personel.em_sonraki_terfi_tarihi

    ga_kademe, kh_kademe, em_kademe = kademe_ilerlet(personel, baslangic_tarihi <= ga_tarih <= bitis_tarihi,
                                                     baslangic_tarihi <= kh_tarih <= bitis_tarihi,
                                                     baslangic_tarihi <= em_tarih <= bitis_tarihi)

    sonuc = derece_ilerlet(ga_derece=personel.gorev_ayligi_derece,
                           ga_kademe=ga_kademe,
                           kh_derece=personel.kazanilmis_hak_derece,
                           kh_kademe=kh_kademe,
                           em_derece=personel.emekli_muktesebat_derece,
                           em_kademe=em_kademe,
                           personel=personel)

    return sonuc

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


def terfi_tarhine_gore_personel_listesi(baslangic_tarihi=None,
                                        bitis_tarihi=None,
                                        personel_turu=None):
    """
    Args:
        baslangic_tarihi (date): baslangic_tarihi
        bitis_tarihi (date): bitis_tarihi
        personel_turu (str): personel turu, 1 akademik, 2 idari

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

        # personel temel bilgileri
        p_data = {"key": personel.key, "tckn": personel.tckn, "ad": personel.ad,
                  "soyad": personel.soyad, "kadro_derece": personel.kadro.derece}

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

        personel_terfi = terfi(personel, baslangic_tarihi, bitis_tarihi)

        # terfi sonrasi derece ve kademeler
        p_data["terfi_sonrasi_gorev_ayligi_derece"] = personel_terfi['ga']['derece']
        p_data["terfi_sonrasi_gorev_ayligi_kademe"] = personel_terfi['ga']['kademe']

        p_data["terfi_sonrasi_kazanilmis_hak_derece"] = personel_terfi['kh']['derece']
        p_data["terfi_sonrasi_kazanilmis_hak_kademe"] = personel_terfi['kh']['kademe']

        p_data["terfi_sonrasi_emekli_muktesebat_derece"] = personel_terfi['em']['derece']
        p_data["terfi_sonrasi_emekli_muktesebat_kademe"] = personel_terfi['em']['kademe']

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

def nonetype_kontrol(data):
    """
        Değeri 0 olan integer bir field veritabanından none olarak döndüğü için
        none değeri 0 olarak return edecek bir metoda itiyaç duyuldu.
    """
    if data == None:
        return 0
    else:
        return data


def terfi_durum_kontrol(personel_id):
    """
    :param personel_id:
    :return: terfi_kontrol (bool) : İlgili personelin terfisinin durup durmadığını belirtir.
    """

    from ulakbus.models import Personel, AskerlikKayitlari, UcretsizIzin

    personel = Personel.objects.get(personel_id)
    baslangic_tarih = datetime.date.today() - datetime.timedelta(days=1)
    bitis_tarih = datetime.date.today() + datetime.timedelta(days=1)
    askerlik_kontrol = False
    ucretsiz_izin_kontrol = False
    aday_memur_kontrol = False
    try:
        askerlik_kayit = AskerlikKayitlari.objects.get(
            personel_id = personel_id,
            baslama_tarihi__gte = baslangic_tarih,
            bitis_tarihi__lte = bitis_tarih
        )
    except ObjectDoesNotExist:
        askerlik_kontrol = True

    try:
        ucretsiz_izin = UcretsizIzin.objects.get(
            personel_id = personel_id,
            baslangic_tarih__gte = baslangic_tarih,
            bitis_tarihi__lte = bitis_tarih
        )
    except ObjectDoesNotExist:
        ucretsiz_izin_kontrol = True

    if not personel.aday_memur:
        aday_memur_kontrol = True

    # TODO : Personelin ceza durumu kontrol edilecek

    return (askerlik_kontrol and ucretsiz_izin_kontrol and aday_memur_kontrol)

def terfi_tikanma_kontrol(personel_id):

    from ulakbus.models import Personel

    personel = Personel.objects.get(personel_id)
    if personel.gorev_ayligi_derece == personel.kadro_derece:
        return True
    else:
        return False

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