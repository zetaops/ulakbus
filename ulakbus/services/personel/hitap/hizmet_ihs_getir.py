# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Sorgula

Hitap üzerinden personelin itibari hizmet süresi zammı bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetIHSGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış IHS Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            bean_name (str): Hitap'tan gelen bean nesnesinin adı
            service_dict (dict): Hitap servisinden gelen kayıtların alanları,
                    ``HizmetIHS`` modelinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.

        """

        self.service_name = 'HizmetIHSSorgula'
        self.bean_name = 'HizmetIHSServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'ihzID',  # TODO: ihzID mi olacak?
                'baslama_tarihi': 'baslamaTarihi',
                'bitis_tarihi': 'bitisTarihi',
                'ihz_nevi': 'ihzNevi'
            },
            'date_filter': ['baslama_tarihi', 'bitis_tarihi'],
            'required_fields': ['tckn']
        }
        super(HizmetIHSGetir, self).handle()
