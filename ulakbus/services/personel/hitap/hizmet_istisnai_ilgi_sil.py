# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Istisnai Ilgi Sil

Hitap'da personelin Hizmet Istisnai Ilgi bilgilerinin silinmesi sağlayan class.

"""

from .hitap_sil import HITAPSil


class HizmetIstisnaiIlgiSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Cetveli Bilgisi Silme servisi

    """

    CONNECTION = "channel"
    DATA_FORMAT = "json"
    NAME = "hizmet.istisnai.ilgi.sil"
    URL_PATH = '/personel/hitap/hizmet-istisnai-ilgi-sil'
    TRANSPORT = "plain_http"
    IS_ACTIVE = True
    IS_INTERNAL = False

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yolula gelen kayıtlar,
                    hizmetIstisnaiIlgiDelete servisinin alanlarıyla eşlenmektedir.
                    Servis tarafında gerekli olan alanlar listede tutulmaktadır.
        """

        self.service_name = 'hizmetIstisnaiIlgiDelete'

        self.service_dict['fields']['tckn'] = self.request.payload.get('tckn', '')
        self.service_dict['fields']['kayitNo'] = self.request.payload.get('kayit_no', '')
        self.service_dict['required_fields'] = ['tckn', 'kayitNo']

        super(HizmetIstisnaiIlgiSil, self).handle()
