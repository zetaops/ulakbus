# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Açık Süre Sil

Hitap'da personelin açık süre bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import HizmetAcikSure


class HizmetAcikSureSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Açık Süre Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetAcikSure'' modelinden gelen kayıtların alanları,
                    HizmetAcikSureDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetAcikSureDelete'
        hizmet_acik_sure = HizmetAcikSure.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_acik_sure.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_acik_sure.kayit_no

        super(HizmetAcikSureSil, self).handle()