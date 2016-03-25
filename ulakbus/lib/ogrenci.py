# -*-  coding: utf-8 -*-
"""Öğrenci ile ilgili yardımcı class ve fonksiyonların yer aldığı dosyadır.
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.models import Ogrenci, OgrenciProgram, OgrenciDersi
from pyoko.exceptions import ObjectDoesNotExist


class OgrenciHelper():
    """OgrenciHelper Class

    """

    def diploma_notu_uret(self, ogrenci_no):
        try:
            ogrenci_program = OgrenciProgram.objects.get(ogrenci_no=ogrenci_no)
            return "%s-%s-%s" % (ogrenci_program.giris_tarihi,
                                  ogrenci_program.program.yoksis_no, ogrenci_program.ogrenci_no)
        except ObjectDoesNotExist:
            return "Öğrenci Bulunamadı"
