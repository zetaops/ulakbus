# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Unvan Sil

Hitap'da personelin Hizmet Unvan bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import HizmetUnvan


class HizmetUnvanSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Mahkeme Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetUnvan'' modelinden gelen kayıtların alanları,
                    HizmetUnvanDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetUnvanDelete'
        hizmet_unvan = HizmetUnvan.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_unvan.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_unvan.kayit_no

        super(HizmetUnvanSil, self).handle()
