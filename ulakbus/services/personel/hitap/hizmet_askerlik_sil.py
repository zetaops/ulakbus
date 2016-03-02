# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Askerlik Sil

Hitap'da personelin askerlik bilgilerinin silinmesi sağlayan class.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil
from ulakbus.models.hitap import AskerlikKayitlari


class HizmetAskerlikSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Askerlik Bilgisi Silme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''AskerlikKayitlari'' modelinden gelen kayıtların alanları,
                    HizmetAskerlikDelete servisinin alanlarıyla eşlenmektedir.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetAskerlikDelete'
        hizmet_askerlik = AskerlikKayitlari.objects.get(key)

        self.service_dict['fields']['tckn'] = hizmet_askerlik.tckn
        self.service_dict['fields']['kayitNo'] = hizmet_askerlik.kayit_no

        super(HizmetAskerlikSil, self).handle()
