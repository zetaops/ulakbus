# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Borclanma Guncelle

Hitap'a personelin hizmet borclanma bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle
from ulakbus.models.hitap import HizmetBorclanma


class HizmetBorclanmaGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Borclanma Bilgisi Guncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetBorclanma'' modelinden gelen kayıtların alanları,
                    HizmetBorclanmaUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetBorclanmaUpdate'
        hizmet_borclanma = HizmetBorclanma.objects.get(key)
        self.service_dict = {
            'fields': {
                'kayitNo': hizmet_borclanma.kayit_no,
                'tckn': hizmet_borclanma.tckn,
                'ad': hizmet_borclanma.ad,
                'soyad': hizmet_borclanma.soyad,
                'baslamaTarihi': hizmet_borclanma.baslama_tarihi,
                'bitisTarihi': hizmet_borclanma.bitis_tarihi,
                'gunSayisi': hizmet_borclanma.gun_sayisi,
                'odenenMiktar': hizmet_borclanma.odenen_miktar,
                'toplamTutar': hizmet_borclanma.toplam_tutar,
                'kanunKod': hizmet_borclanma.kanun_kod,
                'borcNevi': hizmet_borclanma.borc_nevi,
                'borclanmaTarihi': hizmet_borclanma.borclanma_tarihi,
                'odemeTarihi': hizmet_borclanma.odeme_tarihi,
                'derece': hizmet_borclanma.derece,
                'kademe': hizmet_borclanma.kademe,
                'ekgosterge': hizmet_borclanma.ekgosterge,
                'emekliSicil': hizmet_borclanma.emekli_sicil,
                'calistigiKurum': hizmet_borclanma.calistigi_kurum,
                'isyeriIl': hizmet_borclanma.isyeri_il,
                'isyeriIlce': hizmet_borclanma.isyeri_ilce,
                'kurumOnayTarihi': hizmet_borclanma.kurum_onay_tarihi
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'borclanmaTarihi', 'kurumOnayTarihi']
        }
        super(HizmetBorclanmaGuncelle, self).handle()
