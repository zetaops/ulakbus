# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Ali Riza Keles'

from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from ulakbus.models import Personel, HizmetKayitlari
from ulakbus.models import KurumDisiGorevlendirmeBilgileri, KurumIciGorevlendirmeBilgileri
from zengine.lib.translation import gettext_lazy as __
from ulakbus.lib.role import AbsRole


def listele():
    pass
