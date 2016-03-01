# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Açık Süre Ekle

Hitap'a personelin açık süre bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle
from ulakbus.models.hitap import HizmetAcikSure


class HizmetAcikSureEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Açık Süre Bilgisi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetAcikSure'' modelinden gelen kayıtların alanları,
                    HizmetAcikSureInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetAcikSureInsert'
        hizmet_acik_sure = HizmetAcikSure.objects.get(key)
        self.service_dict = {
            'fields': {
                'tckn': hizmet_acik_sure.tckn,
                'acikSekil': hizmet_acik_sure.acik_sekil,
                'iadeSekil': hizmet_acik_sure.iade_sekil,
                'hizmetDurum': hizmet_acik_sure.hizmet_durum,
                'husus': hizmet_acik_sure.husus,
                'acigaAlinmaTarih': hizmet_acik_sure.aciga_alinma_tarih,
                'goreveSonTarih': hizmet_acik_sure.goreve_son_tarih,
                'goreveIadeIstemTarih': hizmet_acik_sure.goreve_iade_istem_tarih,
                'goreveIadeTarih': hizmet_acik_sure.goreve_iade_tarih,
                'acikAylikBasTarihi': hizmet_acik_sure.acik_aylik_bas_tarih,
                'acikAylikBitTarihi': hizmet_acik_sure.acik_aylik_bit_tarih,
                'gorevSonAylikBasTarihi': hizmet_acik_sure.goreve_son_aylik_bas_tarih,
                'gorevSonAylikBitTarihi': hizmet_acik_sure.goreve_son_aylik_bit_tarih,
                'SYonetimKaldTarih': hizmet_acik_sure.s_yonetim_kald_tarih,
                'aciktanAtanmaTarih': hizmet_acik_sure.aciktan_atanma_tarih,
                'kurumOnayTarihi': hizmet_acik_sure.kurum_onay_tarihi
            },
            'date_filter': ['acigaAlinmaTarih', 'goreveSonTarih', 'goreveIadeIstemTarih',
                            'goreveIadeTarih', 'acikAylikBasTarihi', 'acikAylikBitTarihi',
                            'gorevSonAylikBasTarihi', 'gorevSonAylikBitTarihi', 'SYonetimKaldTarih',
                            'aciktanAtanmaTarih', 'kurumOnayTarihi']
        }
        super(HizmetAcikSureEkle, self).handle()
