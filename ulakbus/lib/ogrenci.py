# -*-  coding: utf-8 -*-
"""Öğrenci ile ilgili yardımcı class ve fonksiyonların yer aldığı dosyadır.
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Ogrenci, SinavEtkinligi, AbstractRole

ABSTRACT_ROLE_LIST_DONDURULMUS = [
    "Doktora Programı Öğrencisi - Kayıt Dondurmuş",
    "Yüksek Lisans Programı Öğrencisi - Kayıt Dondurmuş",
    "Ön Lisans Programı Öğrencisi - Kayıt Dondurmuş",
    "Lisans Programı Öğrencisi - Kayıt Dondurmuş"
]


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


def dondurulacak_kayitin_abstract_rolu(unit):
    abstract_role = None
    if unit.unit_type == "Program" and unit.learning_duration == 4:
        abstract_role = AbstractRole.objects.get(name=ABSTRACT_ROLE_LIST_DONDURULMUS[3])
    elif unit.unit_type == "Program" and unit.learning_duration == 2:
        abstract_role = AbstractRole.objects.get(name=ABSTRACT_ROLE_LIST_DONDURULMUS[2])
    elif unit.unit_type == "Yüksek Lisans Programı":
        abstract_role = AbstractRole.objects.get(name=ABSTRACT_ROLE_LIST_DONDURULMUS[1])
    elif unit.unit_type == "Doktora Programı":
        abstract_role = AbstractRole.objects.get(name=ABSTRACT_ROLE_LIST_DONDURULMUS[0])
    else:
        pass
    return abstract_role