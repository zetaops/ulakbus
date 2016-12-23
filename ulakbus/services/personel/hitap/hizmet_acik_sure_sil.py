# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Açık Süre Sil

Hitap'da personelin açık süre bilgilerinin silinmesi sağlayan class.

"""

from ulakbus.services.personel.hitap.hitap_sil import HITAPSil


class HizmetAcikSureSil(HITAPSil):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Açık Süre Bilgisi Silme servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yolula gelen kayıtlar,
                    HizmetAcikSureDelete servisinin alanlarıyla eşlenmektedir.
                    Servis tarafında gerekli olan alanlar listede tutulmaktadır.

        """
        self.service_name = 'HizmetAcikSureDelete'

        self.service_dict['fields']['tckn'] = self.request.payload.get('tckn', '')
        self.service_dict['fields']['kayitNo'] = self.request.payload.get('kayit_no', '')
        self.service_dict['required_fields'] = ['tckn', 'kayit_no']
        super(HizmetAcikSureSil, self).handle()
