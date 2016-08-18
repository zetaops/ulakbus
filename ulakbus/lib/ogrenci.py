# -*-  coding: utf-8 -*-
"""Öğrenci ile ilgili yardımcı class ve fonksiyonların yer aldığı dosyadır.
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Ogrenci, SinavEtkinligi


def diploma_no_uret(ogrenci_program):
    """
    Öğrenci programı için diploma no üretir.

    Args:
        ogrenci_program (): öğrenci program nesnesi

    Returns:
        diploama no (string)

    """
    return "%s-%s-%s" % (ogrenci_program.giris_tarihi,
                         ogrenci_program.program.yoksis_no, ogrenci_program.ogrenci_no)


def aktif_sinav_listesi(obj):
    """
    obj (öğrenci veya okutman) için aktif sınavlarının listesini üretir.

    Args:
        obj (Ogrenci): öğrenci veya okutman nesnesi

    Returns:
        sinav listesi (list)

    """

    from ulakbus.models.ders_sinav_programi import SinavEtkinligi
    sinavlar = []
    for sube in obj.donem_subeleri():
        sinavlar.extend(SinavEtkinligi.sube_sinav_listesi(sube=sube))
    return sinavlar