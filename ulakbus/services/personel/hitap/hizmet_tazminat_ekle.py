# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Tazminat Ekle

Hitap'a personelin Tazminat bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle
from ulakbus.models.hitap import HizmetTazminat


class HizmetTazminatEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Tazminat Bilgi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetTazminat'' modelinden gelen kayıtların alanları,
                    HizmetTazminatInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetTazminatInsert'
        hizmet_tazminat = HizmetTazminat.objects.get(key)
        self.service_dict = {
            'fields': {
                'gorev': hizmet_tazminat.gorev,
                'kadrosuzluk': hizmet_tazminat.kadrosuzluk,
                'makam': hizmet_tazminat.makam,
                'tckn': hizmet_tazminat.tckn,
                'temsil': hizmet_tazminat.temsil,
                'unvanKod': hizmet_tazminat.unvan_kod,
                'tazminatTarihi': hizmet_tazminat.tazminat_tarihi,
                'tazminatBitisTarihi': hizmet_tazminat.tazminat_bitis_tarihi,
                'kurumOnayTarihi': hizmet_tazminat.kurum_onay_tarihi
            },
            'date_filter': ['tazminatTarihi', 'tazminatBitisTarihi', 'kurumOnayTarihi']
        }
        super(HizmetTazminatEkle, self).handle()
