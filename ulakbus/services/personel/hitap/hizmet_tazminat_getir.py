# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetTazminatGetir(HITAPSorgula):
    """
    HITAP HizmetTazminatGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetTazminatSorgula'
        self.bean_name = 'HizmetTazminatServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'unvan_kod': 'unvanKod',
                'makam': 'makam',
                'gorev': 'gorev',
                'temsil': 'temsil',
                'tazminat_tarihi': 'tazminatTarihi',
                'tazminat_bitis_tarihi': 'tazminatBitisTarihi',
                'kadrosuzluk': 'kadrosuzluk',
                'kurum_onay_tarihi': 'kurumOnayTarihi',
            },
            'date_filter': ['tazminat_tarihi', 'tazminat_bitis_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetTazminatGetir, self).handle()
