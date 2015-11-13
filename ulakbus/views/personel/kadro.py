# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Yeni Personel Ekle WF adimlarini icerir.

from zengine.lib.forms import JsonForm
from zengine.views.base import SimpleView
from ulakbus.models.personel import Kadro


class SakliKadroEkle(SimpleView):
    def show_view(self):
        form = JsonForm(model=Kadro)
        self.current.output['forms'] = form.serialize()
