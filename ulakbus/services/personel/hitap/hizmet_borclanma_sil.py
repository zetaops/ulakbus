# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Borçlanma Sil

Hitap'da personelin Hizmet Borçlanma bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import HizmetBorclanma


class HizmetBorclanmaSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Borçlanma Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetBorclanma'' modelinden gelen kayıtların alanları,
                    HizmetBorclanmaDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetBorclanmaDelete'
        hizmet_borclanma = HizmetBorclanma.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_borclanma.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_borclanma.kayit_no

        super(HizmetBorclanmaSil, self).handle()
