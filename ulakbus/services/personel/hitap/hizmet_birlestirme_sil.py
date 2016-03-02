# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Birleştirme Sil

Hitap'da personelin Hizmet Birleştirme bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import HizmetBirlestirme


class HizmetBirlestirmeSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Birleştirme Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetBirlestirme'' modelinden gelen kayıtların alanları,
                    HizmetBirlestirmeDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetBirlestirmeDelete'
        hizmet_birlestirme = HizmetBirlestirme.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_birlestirme.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_birlestirme.kayit_no

        super(HizmetBirlestirmeSil, self).handle()
