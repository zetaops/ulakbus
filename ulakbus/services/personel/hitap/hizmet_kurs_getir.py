# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Kurs Sorgula

Hitap üzerinden personelin kurs bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetKursGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış Kurs Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            bean_name (str): Hitap'tan gelen bean nesnesinin adı
            service_dict (dict): Hitap servisinden gelen kayıtların alanları,
                    ``HizmetKurs`` modelinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
                    Servis tarafında gerekli olan alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetKursSorgula'
        self.bean_name = 'HizmetEgitimKursServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'kurs_ogrenim_suresi': 'kursOgrenimSuresi',
                'mezuniyet_tarihi': 'mezuniyetTarihi',
                'kurs_nevi': 'kursNevi',
                'bolum_ad': 'bolumAd',
                'okul_ad': 'okulAd',
                'ogrenim_yeri': 'ogrenimYeri',
                'denklik_tarihi': 'denklikTarihi',
                'denklik_okulu': 'denklikOkul',
                'denklik_bolum': 'denklikBolum',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['mezuniyet_tarihi', 'denklik_tarihi', 'kurum_onay_tarihi'],
            'required_fields': ['tckn']
        }
        super(HizmetKursGetir, self).handle()
