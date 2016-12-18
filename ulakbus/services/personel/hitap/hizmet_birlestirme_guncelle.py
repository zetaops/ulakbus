# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Birlestirme Guncelle

Hitap'a personelin hizmet birlestirme bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle


class HizmetBirlestirmeGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Birlestirme Bilgisi Guncelleme servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetBirlestirmeUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """

        self.service_name = 'HizmetBirlestirmeUpdate'

        self.service_dict = {
            'fields': {
                'kayitNo': self.request.payload.get('kayit_no', ''),
                'tckn': self.request.payload.get('tckn', ''),
                'sgkNevi': self.request.payload.get('sgk_nevi', ''),
                'sgkSicilNo': self.request.payload.get('sgk_sicil_no', ''),
                'baslamaTarihi': self.request.payload.get('baslama_tarihi', ''),
                'bitisTarihi': self.request.payload.get('bitis_tarihi', ''),
                'kamuIsyeriAd': self.request.payload.get('kamu_isyeri_ad', ''),
                'ozelIsyeriAd': self.request.payload.get('ozel_isyeri_ad', ''),
                'bagKurMeslek': self.request.payload.get('bag_kur_meslek', ''),
                'ulkeKod': self.request.payload.get('ulke_kod', ''),
                'bankaSandikKod': self.request.payload.get('banka_sandik_kod', ''),
                'kidemTazminatOdemeDurumu': self.request.payload.get('kidem_tazminat_odeme_durumu', ''),
                'ayrilmaNedeni': self.request.payload.get('ayrilma_nedeni', ''),
                'sure': self.request.payload.get('sure', ''),
                'khaDurum': self.request.payload.get('kha_durum', ''),
                'kurumOnayTarihi': self.request.payload.get('kurum_onay_tarihi', '')
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'kayitNo', 'sgkNevi', 'sgkSicilNo', 'baslamaTarihi',
                                'bitisTarihi', 'kurumOnayTarihi']
        }
        super(HizmetBirlestirmeGuncelle, self).handle()
