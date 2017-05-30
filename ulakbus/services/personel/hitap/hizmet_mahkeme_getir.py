# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Mahkeme Sorgula

Hitap üzerinden personelin mahkeme bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetMahkemeGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış Mahkeme Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetMahkemeSorgula',
        'bean_name': 'HizmetMahkemeServisBean',
        'fields': {
            'tckn': 'tckn',
            'kayit_no': 'kayitNo',
            'mahkeme_ad': 'mahkemeAd',
            'sebep': 'sebep',
            'karar_tarihi': 'kararTarihi',
            'karar_sayisi': 'kararSayisi',
            'kesinlesme_tarihi': 'kesinlesmeTarihi',
            'asil_dogum_tarihi': 'asilDogumTarihi',
            'tashih_dogum_tarihi': 'tashihDogumTarihi',
            'asil_ad': 'asilAd',
            'tashih_ad': 'tashihAd',
            'asil_soyad': 'asilSoyad',
            'tashih_soyad': 'tashihSoyad',
            'gecerli_dogum_tarihi': 'gecerliDogumTarihi',
            'aciklama': 'aciklama',
            'gun_sayisi': 'gunSayisi',
            'kurum_onay_tarihi': 'kurumOnayTarihi'
        },
        'date_filter': ['karar_tarihi', 'kesinlesme_tarihi', 'asil_dogum_tarihi',
                        'tashih_dogum_tarihi', 'gecerli_dogum_tarihi', 'kurum_onay_tarihi'],
        'required_fields': ['tckn']
    }
