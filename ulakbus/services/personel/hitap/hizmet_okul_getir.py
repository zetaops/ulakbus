# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Okul Sorgula

Hitap üzerinden personelin okul bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetOkulGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış Okul Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            bean_name (str): Hitap'tan gelen bean nesnesinin adı
            service_dict (dict): Hitap servisinden gelen kayıtların alanları,
                    ``HizmetOkul`` modelinin alanlarıyla eşlenmektedir.
                    Servis tarafında gerekli olan alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetOkulSorgula'
        self.bean_name = 'HizmetEgitimOkulServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'ogrenim_durumu': 'ogrenimDurumu',
                'mezuniyet_tarihi': 'mezuniyetTarihi',
                'okul_ad': 'okulAd',
                'bolum': 'bolum',
                'ogrenim_yeri': 'ogrenimYer',
                'denklik_tarihi': 'denklikTarihi',
                'denklik_okul': 'denklikOkul',
                'denklik_bolum': 'denklikBolum',
                'ogrenim_suresi': 'ogrenimSuresi',
                'hazirlik': 'hazirlik',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['mezuniyet_tarihi', 'denklik_tarihi', 'kurum_onay_tarihi'],
            'required_fields': ['tckn']
        }
        super(HizmetOkulGetir, self).handle()
