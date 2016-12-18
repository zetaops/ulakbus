# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Tazminat Sorgula

Hitap üzerinden personelin tazminat bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetTazminatGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış Tazminat Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            bean_name (str): Hitap'tan gelen bean nesnesinin adı
            service_dict (dict): Hitap servisinden gelen kayıtların alanları,
                    ``HizmetTazminat`` modelinin alanlarıyla eşlenmektedir.
                    Servis tarafında gerekli olan alanlar listede tutulmaktadır.

        """

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
            'date_filter': ['tazminat_tarihi', 'tazminat_bitis_tarihi', 'kurum_onay_tarihi'],
            'required_fields': ['tckn']
        }
        super(HizmetTazminatGetir, self).handle()
