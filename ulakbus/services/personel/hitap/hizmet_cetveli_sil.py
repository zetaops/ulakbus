# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Cetveli Sil

Hitap'da personelin Hizmet Cetveli bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import HizmetKayitlari


class HizmetCetvelSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Cetveli Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetBorclanma'' modelinden gelen kayıtların alanları,
                    HizmetBorclanmaDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetCetvelDelete'
        hizmet_kayit = HizmetKayitlari.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_kayit.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_kayit.kayit_no

        super(HizmetCetvelSil, self).handle()
