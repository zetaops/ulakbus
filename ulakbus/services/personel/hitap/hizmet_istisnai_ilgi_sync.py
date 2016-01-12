# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap import HizmetIstisnaiIlgi


class HizmetIstisnaiIlgiSync(HITAPSync):
    """
    HITAP HizmetIstisnaiIlgiSync Zato Servisi
    """

    def handle(self):
        """
        :param sorgula_service: HITAP servisi adi
        :type sorgula_service: str

        :param model: HITAP verisinin model karsiligi
        :type model: Model
        """

        self.sorgula_service = 'hizmet-istisnai-ilgi-getir.hizmet-istisnai-ilgi-getir'
        self.model = HizmetIstisnaiIlgi

        super(HizmetIstisnaiIlgiSync, self).handle()
