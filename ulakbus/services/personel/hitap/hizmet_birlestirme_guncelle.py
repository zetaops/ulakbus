# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Birlestirme Guncelle

Hitap'a personelin hizmet birlestirme bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle
from ulakbus.models.hitap import HizmetBirlestirme


class HizmetBirlestirmeGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Birlestirme Bilgisi Guncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetBirlestirme'' modelinden gelen kayıtların alanları,
                    HizmetBirlestirmeUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetBirlestirmeUpdate'
        hizmet_birlestirme = HizmetBirlestirme.objects.get(key)
        self.service_dict = {
            'fields': {
                'kayitNo': hizmet_birlestirme.kayit_no,
                'tckn': hizmet_birlestirme.tckn,
                'sgkNevi': hizmet_birlestirme.sgk_nevi,
                'sgkSicilNo': hizmet_birlestirme.sgk_sicil_no,
                'baslamaTarihi': hizmet_birlestirme.baslama_tarihi,
                'bitisTarihi': hizmet_birlestirme.bitis_tarihi,
                'kamuIsyeriAd': hizmet_birlestirme.kamu_isyeri_ad,
                'ozelIsyeriAd': hizmet_birlestirme.ozel_isyeri_ad,
                'bagKurMeslek': hizmet_birlestirme.bag_kur_meslek,
                'ulkeKod': hizmet_birlestirme.ulke_kod,
                'bankaSandikKod': hizmet_birlestirme.banka_sandik_kod,
                'kidemTazminatOdemeDurumu': hizmet_birlestirme.kidem_tazminat_odeme_durumu,
                'ayrilmaNedeni': hizmet_birlestirme.ayrilma_nedeni,
                'sure': hizmet_birlestirme.sure,
                'khaDurum': hizmet_birlestirme.kha_durum,
                'kurumOnayTarihi': hizmet_birlestirme.kurum_onay_tarihi
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kurumOnayTarihi']
        }
        super(HizmetBirlestirmeGuncelle, self).handle()
