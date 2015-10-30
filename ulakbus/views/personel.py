# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.model import field
from zengine.lib.forms import JsonForm
from zengine.views.base import SimpleView


class TCKNForm(JsonForm):
    class Meta:
        customize_types = {'cmd': 'submit'}
        title = 'Yeni Personel'

    tcno = field.String("TC No")
    cmd = field.String("Ekle", default='do')


class YeniPersonelEkle(SimpleView):
    def show_view(self):
        self.current.output['forms'] = TCKNForm().serialize()


def get_personel_from_hitap(tcno):
    pass
