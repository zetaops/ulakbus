# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Mahkeme Guncelle

Hitap'a personelin Mahkeme bilgilerinin guncellemesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle
from ulakbus.models.hitap import HizmetMahkeme


class HizmetMahkemeGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Mahkeme Bilgi Guncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetMahkeme'' modelinden gelen kayıtların alanları,
                    HizmetMahkemeUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetMahkemeUpdate'
        hizmet_mahkeme = HizmetMahkeme.objects.get(key)
        self.service_dict = {
            'fields': {
                'kayitNo': hizmet_mahkeme.kayit_no,
                'tckn': hizmet_mahkeme.tckn,
                'mahkemeAd': hizmet_mahkeme.mahkeme_ad,
                'sebep': hizmet_mahkeme.sebep,
                'kararTarihi': hizmet_mahkeme.karar_tarihi,
                'kararSayisi': hizmet_mahkeme.karar_sayisi,
                'kesinlesmeTarihi': hizmet_mahkeme.kesinlesme_tarihi,
                'asilDogumTarihi': hizmet_mahkeme.asil_dogum_tarihi,
                'tashihDogumTarihi': hizmet_mahkeme.tashih_dogum_tarihi,
                'gecerliDogumTarihi': hizmet_mahkeme.gecerli_dogum_tarihi,
                'asilAd': hizmet_mahkeme.asil_ad,
                'tashihAd': hizmet_mahkeme.tashih_ad,
                'asilSoyad': hizmet_mahkeme.asil_soyad,
                'tashihSoyad': hizmet_mahkeme.tashih_soyad,
                'aciklama': hizmet_mahkeme.aciklama,
                'gunSayisi': hizmet_mahkeme.gun_sayisi,
                'kurumOnayTarihi': hizmet_mahkeme.kurum_onay_tarihi
            },
            'date_filter': ['kesinlesmeTarihi', 'asilDogumTarihi', 'tashihDogumTarihi',
                            'gecerliDogumTarihi', 'kurumOnayTarihi']
        }
        super(HizmetMahkemeGuncelle, self).handle()
