# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap import HizmetMahkeme


class HizmetMahkemeSync(HITAPSync):
    """
    HITAP HizmetMahkemeSync Zato Servisi
    """

    def handle(self):
        """
        :param sorgula_service: HITAP servisi adi
        :type sorgula_service: str

        :param model: HITAP verisinin model karsiligi
        :type model: Model
        """

        self.sorgula_service = 'hizmet-mahkeme-getir.hizmet-mahkeme-getir'
        self.model = HizmetMahkeme

        super(HizmetMahkemeSync, self).handle()
