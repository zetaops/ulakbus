# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Mahkeme Sil

Hitap'da personelin Hizmet Mahkeme bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import HizmetMahkeme


class HizmetMahkemeSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Mahkeme Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetMahkeme'' modelinden gelen kayıtların alanları,
                    HizmetMahkemeDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetMahkemeDelete'
        hizmet_mahkeme = HizmetMahkeme.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_mahkeme.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_mahkeme.kayit_no

        super(HizmetMahkemeSil, self).handle()
