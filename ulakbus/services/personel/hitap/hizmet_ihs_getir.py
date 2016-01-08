# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_service import HITAPService


class HizmetIHSGetir(HITAPService):
    """
    HITAP HizmetIHSGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetIHSSorgula'
        self.bean_name = 'HizmetIHSServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',  # TODO: ihzID mi olacak?
                'baslama_tarihi': 'baslamaTarihi',
                'bitis_tarihi': 'bitisTarihi',
                'ihz_nevi': 'ihzNevi'
            },
            'date_filter': ['baslama_tarihi', 'bitis_tarihi']
        }
        super(HizmetIHSGetir, self).handle()
