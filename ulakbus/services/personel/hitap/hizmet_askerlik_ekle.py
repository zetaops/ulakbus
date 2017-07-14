# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Askerlik Ekle

Hitap'a personelin askerlik bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetAskerlikEkle(ZatoHitapService):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Askerlik Bilgisi Ekleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetAskerlikInsert',
        'service_mapper': 'ns1:HizmetAskerlikServisBean',
        'fields': {
            'askerlikNevi': 'askerlik_nevi',
            'baslamaTarihi': 'baslama_tarihi',
            'bitisTarihi': 'bitis_tarihi',
            'kitaBaslamaTarihi': 'kita_baslama_tarihi',
            'kitaBitisTarihi': 'kita_bitis_tarihi',
            'muafiyetNeden': 'muafiyet_neden',
            'sayilmayanGunSayisi': 'sayilmayan_gun_sayisi',
            'sinifOkuluSicil': 'sinif_okulu_sicil',
            'subayliktanErligeGecisTarihi':
                'subayliktan_erlige_gecis_tarihi',
            'subayOkuluGirisTarihi': 'subay_okulu_giris_tarihi',
            'tckn': 'tckn',
            'tegmenNaspTarihi': 'tegmen_nasp_tarihi',
            'gorevYeri': 'gorev_yeri',
            'kurumOnayTarihi': 'kurum_onay_tarihi',
            'astegmenNaspTarihi': 'astegmen_nasp_tarihi',
        },
        'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kita_baslama_tarihi',
                        'kita_bitis_tarihi', 'subayliktan_erlige_gecis_tarihi',
                        'subay_okulu_giris_tarihi', 'tegmen_nasp_tarihi', 'kurum_onay_tarihi',
                        'astegmen_nasp_tarihi'],
        'long_to_string': ['kayit_no'],
        'required_fields': ['tckn', 'askerlikNevi', 'kurumOnayTarihi']
    }
