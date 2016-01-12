# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap import NufusKayitlari


class HizmetNufusSync(HITAPSync):
    """
    HITAP HizmetNufusSync Zato Servisi
    """

    def handle(self):
        """
        :param sorgula_service: HITAP servisi adi
        :type sorgula_service: str

        :param model: HITAP verisinin model karsiligi
        :type model: Model
        """

        self.sorgula_service = 'hizmet-nufus-getir.hizmet-nufus-getir'
        self.model = NufusKayitlari

        super(HizmetNufusSync, self).handle()
