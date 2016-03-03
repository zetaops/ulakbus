# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Istisnai Ilgi Guncelle

Hitap'a personelin Istisnai Ilgi bilgilerinin guncellemesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle
from ulakbus.models.hitap import HizmetIstisnaiIlgi


class HizmetIstisnaiIlgiGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Istisnai Bilgi Guncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetIstisnaiIlgi'' modelinden gelen kayıtların alanları,
                    hizmetIstisnaiIlgiUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'hizmetIstisnaiIlgiUpdate'
        hizmet_is_ilgi = HizmetIstisnaiIlgi.objects.get(key)
        self.service_dict = {
            'fields': {
                'kayitNo': hizmet_is_ilgi.kayit_no,
                'tckn': hizmet_is_ilgi.tckn,
                'istisnaiIlgiNevi': hizmet_is_ilgi.istisnai_ilgi_nevi,
                'baslamaTarihi': hizmet_is_ilgi.baslama_tarihi,
                'bitisTarihi': hizmet_is_ilgi.bitis_tarihi,
                'gunSayisi': hizmet_is_ilgi.gun_sayisi,
                'khaDurum': hizmet_is_ilgi.kha_durum,
                'kurumOnayTarihi': hizmet_is_ilgi.kurum_onay_tarihi
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kurumOnayTarihi']
        }
        super(HizmetIstisnaiIlgiGuncelle, self).handle()
