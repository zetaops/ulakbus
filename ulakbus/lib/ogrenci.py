# -*-  coding: utf-8 -*-
"""Öğrenci ile ilgili yardımcı class ve fonksiyonların yer aldığı dosyadır.
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from operator import attrgetter
from ulakbus.lib.role import AbsRole
from ulakbus.models import Ogrenci, AbstractRole


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


def kayidin_abstract_rolu(role, sil=None, dondur=None):
    """
    Sil True kaydı silinecek kaydın abstract rolünü getirir, Dondur True ise
    dondurulacak kaydın abstract rolünü getirir.
    Args:
     sil(Bool) Kaydı silinecek kaydın abstract rolü
     dondur(Bool) Kaydı dondurulacak kaydın abstract rolü
    """
    func = attrgetter("unit.unit_type", "unit.learning_duration")
    unit_type, learning_duration = func(role)
    if unit_type == "Program" and learning_duration == 4:
        if dondur:
            AbstractRole.objects.get(AbsRole.LISANS_OGRENCISI_KAYIT_DONDURMUS.name)
            return
        if sil:
            return AbstractRole.objects.get(AbsRole.LISANS_OGRENCISI_KAYIT_SILINMIS.name)
    elif unit_type == "Program" and learning_duration == 2:
        if dondur:
            return AbstractRole.objects.get(AbsRole.ON_LISANS_OGRENCISI_KAYIT_DONDURMUS.name)
        if sil:
            return AbstractRole.objects.get(AbsRole.ON_LISANS_OGRENCISI_KAYIT_SILINMIS.name)

    elif unit_type == "Yüksek Lisans Programı":
        if dondur:
            return AbstractRole.objects.get(AbsRole.YUKSEK_LISANS_OGRENCISI_KAYIT_DONDURMUS.name)
        if sil:
            return AbstractRole.objects.get(AbsRole.YUKSEK_LISANS_OGRENCISI_KAYIT_SILINMIS.name)
    elif unit_type == "Doktora Programı":
        if dondur:
            return AbstractRole.objects.get(AbsRole.DOKTORA_OGRENCISI_KAYIT_DONDURMUS.name)
        if sil:
            AbstractRole.objects.get(AbsRole.DOKTORA_OGRENCISI_KAYIT_SILINMIS.name)
    else:
        return AbstractRole()
