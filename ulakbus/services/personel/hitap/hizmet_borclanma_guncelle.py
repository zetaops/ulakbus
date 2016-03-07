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

class HizmetBorclanmaGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Borclanma Bilgisi Guncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): 'Request yoluyla kayıtlar,
                    HizmetBorclanmaUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """

        self.service_name = 'HizmetBorclanmaUpdate'
        hizmet_borclanma = HizmetBorclanma.objects.get(key)
        self.service_dict = {
            'fields': {
                'kayitNo': self.request.payload['kayit_no'],
                'tckn': self.request.payload['tckn'],
                'ad': self.request.payload['ad'],
                'soyad': self.request.payload['soyad'],
                'baslamaTarihi': self.request.payload['baslama_tarihi'],
                'bitisTarihi': self.request.payload['bitis_tarihi'],
                'gunSayisi': self.request.payload['gun_sayisi'],
                'odenenMiktar': self.request.payload['odenen_miktar'],
                'toplamTutar': self.request.payload['toplam_tutar'],
                'kanunKod': self.request.payload['kanun_kod'],
                'borcNevi': self.request.payload['borc_nevi'],
                'borclanmaTarihi': self.request.payload['borclanma_tarihi'],
                'odemeTarihi': self.request.payload['odeme_tarihi'],
                'derece': self.request.payload['derece'],
                'kademe': self.request.payload['kademe'],
                'ekgosterge': self.request.payload['ekgosterge'],
                'emekliSicil': self.request.payload['emekli_sicil'],
                'calistigiKurum': self.request.payload['calistigi_kurum'],
                'isyeriIl': self.request.payload['isyeri_il'],
                'isyeriIlce': self.request.payload['isyeri_ilce'],
                'kurumOnayTarihi': self.request.payload['kurum_onay_tarihi']
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'borclanmaTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'kayitNo', 'ad', 'soyad', 'emekliSicil', 'derece', 'kademe',
                                'ekgosterge', 'baslamaTarihi', 'bitisTarihi', 'gunSayisi',
                                'kanunKod', 'borcNevi', 'toplamTutar', 'calistigiKurum', 'isyeriIl',
                                'isyeriIlce', 'kurumOnayTarihi']
        }
        super(HizmetBorclanmaGuncelle, self).handle()
