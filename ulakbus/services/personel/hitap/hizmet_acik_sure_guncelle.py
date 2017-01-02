# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Açık Süre Güncelle

Hitap'a personelin açık süre bilgilerinin güncellemesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle


class HizmetAcikSureGuncelle(HITAPGuncelle):
    """
    HITAP Güncelleme servisinden kalıtılmış Hizmet Açık Süre Bilgisi Güncelleme servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request ile gelen kayıtlar,
                    HizmetAcikSureUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve gerekli alanlar listede tutulmaktadır.
        """

        self.service_name = 'HizmetAcikSureUpdate'
        hizmet_acik_sure = HizmetAcikSure.objects.get(key)
        self.service_dict = {
            'fields': {
                'kayitNo': self.request.payload.get('kayit_no', ''),
                'tckn': self.request.payload.get('tckn', ''),
                'acikSekil': self.request.payload.get('acik_sekil', ''),
                'iadeSekil': self.request.payload.get('iade_sekil', ''),
                'hizmetDurum': self.request.payload.get('hizmet_durum', ''),
                'husus': self.request.payload.get('husus', ''),
                'acigaAlinmaTarih': self.request.payload.get('aciga_alinma_tarih', ''),
                'goreveSonTarih': self.request.payload.get('goreve_son_tarih', ''),
                'goreveIadeIstemTarih': self.request.payload.get('goreve_iade_istem_tarih', ''),
                'goreveIadeTarih': self.request.payload.get('goreve_iade_tarih', ''),
                'acikAylikBasTarihi': self.request.payload.get('acik_aylik_bas_tarih', ''),
                'acikAylikBitTarihi': self.request.payload.get('acik_aylik_bit_tarih', ''),
                'gorevSonAylikBasTarihi': self.request.payload.get('goreve_son_aylik_bas_tarih',
                                                                   ''),
                'gorevSonAylikBitTarihi': self.request.payload.get('goreve_son_aylik_bit_tarih',
                                                                   ''),
                'SYonetimKaldTarih': self.request.payload.get('s_yonetim_kald_tarih', ''),
                'aciktanAtanmaTarih': self.request.payload.get('aciktan_atanma_tarih', ''),
                'kurumOnayTarihi': self.request.payload.get('kurum_onay_tarihi', '')
            },
            'date_filter': ['acigaAlinmaTarih', 'goreveSonTarih', 'goreveIadeIstemTarih',
                            'goreveIadeTarih', 'acikAylikBasTarihi', 'acikAylikBitTarihi',
                            'gorevSonAylikBasTarihi', 'gorevSonAylikBitTarihi', 'SYonetimKaldTarih',
                            'aciktanAtanmaTarih', 'kurumOnayTarihi'],
            'required_fields': ['kayitNo', 'tckn', 'acikSekil', 'durum', 'hizmetDurum', 'husus',
                                'kurumOnayTarihi']
        }
        super(HizmetAcikSureGuncelle, self).handle()
