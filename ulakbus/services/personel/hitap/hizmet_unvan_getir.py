# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetUnvanGetir(HITAPSorgula):
    """
    HITAP HizmetUnvanGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetUnvanSorgula'
        self.bean_name = 'HizmetUnvanServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'unvan_kod': 'unvanKod',
                'unvan_tarihi': 'unvanTarihi',
                'unvan_bitis_tarihi': 'unvanBitisTarihi',
                'hizmet_sinifi': 'hizmetSinifi',
                'asil_vekil': 'asilVekil',
                'atama_sekli': 'atamaSekli',
                'fhz_orani': 'fhzOrani',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['unvan_tarihi', 'unvan_bitis_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetUnvanGetir, self).handle()
