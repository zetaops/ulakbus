# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Ekle

Hitap'a personelin IHS bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle
from ulakbus.models.hitap import HizmetIHS


class HizmetIhsEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet IHS Bilgisi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetIHS'' modelinden gelen kayıtların alanları,
                    HizmetIHSInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetIHSInsert'
        hizmet_ihs = HizmetIHS.objects.get(key)
        self.service_dict = {
            'fields': {
                'tckn': hizmet_ihs.tckn,
                'baslamaTarihi': hizmet_ihs.baslama_tarihi,
                'bitisTarihi': hizmet_ihs.bitis_tarihi,
                'ihzNevi': hizmet_ihs.ihz_nevi,
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi']
        }
        super(HizmetIhsEkle, self).handle()
