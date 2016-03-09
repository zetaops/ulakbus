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

class HizmetKursSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Kurs Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetKursDelete servisinin alanlarıyla eşlenmektedir.
                    Servis tarafında gerekli olan alanlar listede tutulmaktadır.
        """

        self.service_name = 'HizmetKursDelete'

        self.service_dict['fields']['tckn'] = self.request.payload['tckn']
        self.service_dict['fields']['kayitNo'] = self.request.payload['kayit_no']
        self.service_dict['required_fields'] = ['tckn', 'kayitNo']

        super(HizmetKursSil, self).handle()
