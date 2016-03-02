# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Kurs Sil

Hitap'da personelin Hizmet Kurs bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import HizmetKurs


class HizmetKursSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Kurs Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetKurs'' modelinden gelen kayıtların alanları,
                    HizmetKursDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetKursDelete'
        hizmet_kurs = HizmetKurs.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_kurs.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_kurs.kayit_no

        super(HizmetKursSil, self).handle()
