# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Sil

Hitap'da personelin IHS bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import HizmetIHS


class HizmetIHSSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet IHS Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetIHS'' modelinden gelen kayıtların alanları,
                    HizmetIHSDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetIHSDelete'
        hizmet_ihs = HizmetIHS.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_ihs.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_ihs.kayit_no

        super(HizmetIHSSil, self).handle()
