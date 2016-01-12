# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetKursGetir(HITAPSorgula):
    """
    HITAP HizmetKursGetir Zato Servisi
    """

    def handle(self):
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
            'date_filter': ['mezuniyet_tarihi', 'denklik_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetKursGetir, self).handle()
