# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import datetime

from ulakbus.lib.date_time_helper import zaman_araligi

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
    9: 37
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
        personel_okul = HizmetOkul.objects.set_params(
            sort='mezuniyet_tarihi desc').filter(tckn=personel.tckn).exclude(ogrenim_durumu=None)

        son_mezun_olunan_okul = personel_okul[0]

        derece_sinir = ogrenim_durumuna_gore_terfi[son_mezun_olunan_okul.ogrenim_durumu]['derece']
        kademe_sinir = ogrenim_durumuna_gore_terfi[son_mezun_olunan_okul.ogrenim_durumu]['kademe']

        if (personel.gorev_ayligi_derece == derece_sinir and
                personel.gorev_ayligi_kademe == kademe_sinir):
            ga = True

        if (personel.kazanilmis_hak_derece == derece_sinir and
                personel.kazanilmis_hak_kademe == kademe_sinir):
            kh = True

        if (personel.emekli_muktesebat_derece == derece_sinir and
                personel.emekli_muktesebat_kademe == kademe_sinir):
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


def terfi(personel):
    ga_tarih = personel.ga_sonraki_terfi_tarihi
    kh_tarih = personel.kh_sonraki_terfi_tarihi
    em_tarih = personel.em_sonraki_terfi_tarihi
    
    bugun = datetime.date.today()

    ga_kademe, kh_kademe, em_kademe = kademe_ilerlet(personel, ga_tarih <= bugun, kh_tarih <= bugun,
                                                     em_tarih <= bugun)

    sonuc = derece_ilerlet(ga_derece=personel.gorev_ayligi_derece,
                           ga_kademe=ga_kademe,
                           kh_derece=personel.kazanilmis_hak_derece,
                           kh_kademe=kh_kademe,
                           em_derece=personel.emekli_muktesebat_derece,
                           em_kademe=em_kademe,
                           personel=personel)

    return sonuc


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

    qs = Personel.objects.filter(personel_turu=personel_turu)

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

        personel_terfi = terfi(personel)

        # terfi sonrasi derece ve kademeler
        p_data["terfi_sonrasi_gorev_ayligi_derece"] = personel_terfi['ga']['derece']
        p_data["terfi_sonrasi_gorev_ayligi_kademe"] = personel_terfi['ga']['kademe']

        p_data["terfi_sonrasi_kazanilmis_hak_derece"] = personel_terfi['ga']['derece']
        p_data["terfi_sonrasi_kazanilmis_hak_kademe"] = personel_terfi['ga']['kademe']

        p_data["terfi_sonrasi_emekli_muktesebat_derece"] = personel_terfi['ga']['derece']
        p_data["terfi_sonrasi_emekli_muktesebat_kademe"] = personel_terfi['ga']['kademe']

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
