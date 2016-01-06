# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_service import HITAPService


class HizmetOkulGetir(HITAPService):
    """
    HITAP HizmetOkulGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetOkulSorgula'
        self.bean_name = 'HizmetEgitimOkulServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'Tckn',
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
            'date_filter': ['mezuniyet_tarihi', 'denklik_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetOkulGetir, self).handle()
