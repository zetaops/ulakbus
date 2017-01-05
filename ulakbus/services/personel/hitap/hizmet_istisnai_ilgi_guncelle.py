# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Istisnai Ilgi Guncelle

Hitap'a personelin Istisnai Ilgi bilgilerinin guncellemesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle


class HizmetIstisnaiIlgiGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Istisnai Bilgi Guncelleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'hizmetIstisnaiIlgiUpdate',
        'fields': {
            'kayitNo': 'kayit_no',
            'tckn': 'tckn',
            'istisnaiIlgiNevi': 'istisnai_ilgi_nevi',
            'baslamaTarihi': 'baslama_tarihi',
            'bitisTarihi': 'bitis_tarihi',
            'gunSayisi': 'gun_sayisi',
            'khaDurum': 'kha_durum',
            'kurumOnayTarihi': 'kurum_onay_tarihi'
        },
        'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kurumOnayTarihi'],
        'required_fields': ['kayitNo', 'tckn', 'istisnaiIlgiNevi', 'baslamaTarihi',
                            'bitisTarihi', 'gunSayisi', 'khaDurum', 'kurumOnayTarihi']
    }
