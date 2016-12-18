# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Borclanma Ekle

Hitap'a personelin açık süre bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetBorclanmaEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Borçlanma Bilgisi Ekleme servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetBorclanmaInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.

        """

        self.service_name = 'HizmetBorclanmaInsert'

        self.service_dict = {
            'fields': {
                'tckn': self.request.payload.get('tckn', ''),
                'ad': self.request.payload.get('ad', ''),
                'soyad': self.request.payload.get('soyad', ''),
                'baslamaTarihi': self.request.payload.get('baslama_tarihi', ''),
                'bitisTarihi': self.request.payload.get('bitis_tarihi', ''),
                'gunSayisi': self.request.payload.get('gun_sayisi', ''),
                'odenenMiktar': self.request.payload.get('odenen_miktar', ''),
                'toplamTutar': self.request.payload.get('toplam_tutar', ''),
                'kanunKod': self.request.payload.get('kanun_kod', ''),
                'borcNevi': self.request.payload.get('borc_nevi', ''),
                'borclanmaTarihi': self.request.payload.get('borclanma_tarihi', ''),
                'odemeTarihi': self.request.payload.get('odeme_tarihi', ''),
                'derece': self.request.payload.get('derece', ''),
                'kademe': self.request.payload.get('kademe', ''),
                'ekgosterge': self.request.payload.get('ekgosterge', ''),
                'emekliSicil': self.request.payload.get('emekli_sicil', ''),
                'calistigiKurum': self.request.payload.get('calistigi_kurum', ''),
                'isyeriIl': self.request.payload.get('isyeri_il', ''),
                'isyeriIlce': self.request.payload.get('isyeri_ilce', ''),
                'kurumOnayTarihi': self.request.payload.get('kurum_onay_tarihi', '')
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'borclanmaTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'ad', 'soyad', 'emekliSicil', 'derece', 'kademe',
                                'ekgosterge', 'baslamaTarihi', 'bitisTarihi', 'gunSayisi',
                                'kanunKod', 'borcNevi', 'toplamTutar', 'calistigiKurum', 'isyeriIl',
                                'isyeriIlce', 'kurumOnayTarihi']
        }
        super(HizmetBorclanmaEkle, self).handle()
