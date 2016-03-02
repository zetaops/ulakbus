# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Istisnai Ilgi Sil

Hitap'da personelin Hizmet Istisnai Ilgi bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import HizmetIstisnaiIlgi


class HizmetIstisnaiIlgiSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Cetveli Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetIstisnaiIlgi'' modelinden gelen kayıtların alanları,
                    hizmetIstisnaiIlgiDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'hizmetIstisnaiIlgiDelete'
        hizmet_ilgi = HizmetIstisnaiIlgi.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_ilgi.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_ilgi.kayit_no

        super(HizmetIstisnaiIlgiSil, self).handle()
