# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Guncelle

Hitap'a personelin IHS bilgilerinin guncellemesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle
# todo: from ulakbus.models.hitap.hitap import HizmetIHS


class HizmetIhsGuncelle(HITAPGuncelle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet IHS Bilgisi Guncelleme servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetIHS'' modelinden gelen kayıtların alanları,
                    HizmetIHSUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.

        """

        self.service_name = 'HizmetIHSUpdate'
        self.service_dict = {
            'fields': {
                'ihzID': self.request.payload.get('kayit_no', ''),
                'tckn': self.request.payload.get('tckn', ''),
                'baslamaTarihi': self.request.payload.get('baslama_tarihi', ''),
                'bitisTarihi': self.request.payload.get('bitis_tarihi', ''),
                'ihzNevi': self.request.payload.get('ihz_nevi', '')
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi'],
            'required_fields': ['tckn', 'ihzID', 'baslamaTarihi', 'bitisTarihi', 'ihzNevi']
        }
        super(HizmetIhsGuncelle, self).handle()
