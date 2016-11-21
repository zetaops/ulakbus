# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Istisnai Ilgi Guncelle

Hitap'a personelin Istisnai Ilgi bilgilerinin guncellemesini yapar.

"""

from .hitap_guncelle import HITAPGuncelle


class HizmetIstisnaiIlgiGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Istisnai Bilgi Guncelleme servisi

    """

    CONNECTION = "channel"
    DATA_FORMAT = "json"
    NAME = "hizmet.istisnai.ilgi.guncelle"
    URL_PATH = '/personel/hitap/hizmet-istisnai-ilgi-guncelle'
    TRANSPORT = "plain_http"
    IS_ACTIVE = True
    IS_INTERNAL = False

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    hizmetIstisnaiIlgiUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'hizmetIstisnaiIlgiUpdate'
        self.service_dict = {
            'fields': {
                'kayitNo': self.request.payload.get('kayit_no', ''),
                'tckn': self.request.payload.get('tckn', ''),
                'istisnaiIlgiNevi': self.request.payload.get('istisnai_ilgi_nevi', ''),
                'baslamaTarihi': self.request.payload.get('baslama_tarihi', ''),
                'bitisTarihi': self.request.payload.get('bitis_tarihi', ''),
                'gunSayisi': self.request.payload.get('gun_sayisi', ''),
                'khaDurum': self.request.payload.get('kha_durum', ''),
                'kurumOnayTarihi': self.request.payload.get('kurum_onay_tarihi', '')
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kurumOnayTarihi'],
            'required_fields': ['kayitNo', 'tckn', 'istisnaiIlgiNevi', 'baslamaTarihi',
                                'bitisTarihi', 'gunSayisi', 'khaDurum', 'kurumOnayTarihi']
        }
        super(HizmetIstisnaiIlgiGuncelle, self).handle()
