# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
#
from collections import OrderedDict

from ulakbus.models import Unit
from zengine.views.crud import CrudView
from ulakbus.models.ogrenci import AKADEMIK_TAKVIM_ETKINLIKLERI
from ulakbus.models.ogrenci import AkademikTakvim
from ulakbus.settings import UID

__author__ = 'Ali Riza Keles'


class AkademikTakvimView(CrudView):
    class Meta:
        model = "AkademikTakvim"

    def goster(self):
        # role = self.current.role
        # unit = role.unit
        # akademik_takvim = AkademikTakvim.objects.filter(birim=unit)[0]
        self.current.output['client_cmd'] = ['show', ]
        unit = Unit.objects.get(yoksis_no=UID)
        akademik_takvim = AkademikTakvim.objects.filter(birim=unit)[0]
        etkinlikler = []
        for e in akademik_takvim.Takvim:
            etkinlik = OrderedDict({})
            etkinlik['Etkinlik'] = dict(AKADEMIK_TAKVIM_ETKINLIKLERI).get(str(e.etkinlik), '')
            etkinlik['Başlangıç'] = '{:%d.%m.%Y}'.format(e.baslangic)
            etkinlik['Bitiş'] = '{:%d.%m.%Y}'.format(e.bitis)
            etkinlikler.append(etkinlik)

        # self.current.output['msgbox'] = {'type': 'info', "title": 'Nerdeyiz?',
        #                                  "msg": 'Akademik Takvim WF deyiz.'}

        self.output['object'] = {
            "type": "table-multiRow",
            "fields": etkinlikler
        }
