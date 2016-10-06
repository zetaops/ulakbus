# -*-  coding: utf-8 -*-
"""Roller ile ilgili yardımcı class ve fonksiyonların yer aldığı dosyadır.

"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from enum import Enum
from zengine.lib.translation import gettext_lazy as __


class AbsRole(Enum):
    """
    Abstract roller icin enumerated data. Veritabani keyleri ozellik adi ile eslesir.
    Kod icinde su sekilde kullanilabilir:

    ... code-block:: python
        hitap_kaydi = form_data["soyut_rol_id"] in [AbsRole.FAKULTE_DEKANI, AbsRole.REKTOR]

    kod icinde translation ile birlikte kullanilabilir.

    .. code-block:: python
        __("%s degistirildi..") % AbsRole.FAKULTE_YONETIM_KURULU_UYESI

    """

    FAKULTE_YONETIM_KURULU_UYESI = __(u"Fakülte Yönetim Kurulu Üyesi")
    FAKULTE_YONETIM_KURULU_BASKANI_DEKAN = __(u"Fakülte Yönetim Kurulu Başkanı (Dekan)")
    FAKULTE_DEKAN_SEKRETERI = __(u"Fakülte Dekan Sekreteri")
    FAKULTE_DEKANI = __(u"Fakülte Dekanı")
    FAKULTE_OGRENCI_ISLERI_SEFI = __(u"Fakülte Öğrenci İşleri Şefi")
    FAKULTE_KURULU_UYESI = __(u"Fakülte Kurulu Üyesi")
    FAKULTE_SEKRETERI = __(u"Fakülte Sekreteri")
    FAKULTE_ETIK_KURULU_BASKANI = __(u"Fakülte Etik Kurulu Başkanı")
    FAKULTE_ETIK_KURULU_UYESI = __(u"Fakülte Etik Kurulu Üyesi")
    FAKULTE_OGRENCI_ISLERI_PERSONELI = __(u"Fakülte Öğrenci İşleri Personeli")
    FAKULTE_DEKAN_YARDIMCISI = __(u"Fakülte Dekan Yardımcısı")
    FAKULTE_KURULU_BASKANI = __(u"Fakülte Kurulu Başkanı (Dekan)")
    ENSTITU_MUDURU = __(u"Enstitü Müdürü")
    ENSTITU_YONETIM_KURULU_BASKANI = __(u"Enstitü Yönetim Kurulu Başkanı")
    ENSTITU_OGRENCI_ISLERI_PERSONELI = __(u"Enstitü Öğrenci İşleri Personeli")
    ENSTITU_YONETIM_KURULU_UYESI = __(u"Enstitü Yönetim Kurulu Üyesi")
    ENSTITU_SEKRETERI = __(u"Enstitü Sekreteri")
    ENSTITU_OGRENCI_ISLERI_SEFI = __(u"Enstitü Öğrenci İşleri Şefi")
    ENSTITU_MUDUR_YARDIMCISI = __(u"Enstitü Müdür Yardımcısı")
    ENSTITU_MUHASEBE_ISLERI_PERSONELI = __(u"Enstitü Muhasebe İşleri Personeli")
    ENSTITU_KURULU_UYESI = __(u"Enstitü Kurulu Üyesi")
    ENSTITU_MUHASEBE_ISLERI_SEFI = __(u"Enstitü Muhasebe İşleri Şefi")
    ENSTITU_KURULU_BASKANI = __(u"Enstitü Kurulu Başkanı")
    YUKSELOKUL_KURULU_BASKANI = __(u"Yükselokul Kurulu Başkanı")
    YUKSELOKUL_YONETIM_KURULU_BASKANI = __(u"Yükselokul Yönetim Kurulu Başkanı")
    YUKSELOKUL_BIRIM_KOORDINATORU = __(u"Yükselokul Birim Koordinatörü")
    YUKSELOKUL_YONETIM_KURULU_UYESI = __(u"Yükselokul Yönetim Kurulu Üyesi")
    YUKSELOKUL_MUDURU = __(u"Yükselokul Müdürü")
    YUKSELOKUL_MUDUR_YARDIMCISI = __(u"Yükselokul Müdür Yardımcısı")
    YUKSELOKUL_SEKRETERI = __(u"Yükselokul Sekreteri")
    YUKSELOKUL_OGRENCI_ISLERI_SEFI = __(u"Yükselokul Öğrenci İşleri Şefi")
    YUKSELOKUL_KURULU_UYESI = __(u"Yükselokul Kurulu Üyesi")
    YUKSELOKUL_MUHASEBE_ISLERI_SEFI = __(u"Yükselokul Muhasebe İşleri Şefi")
    YUKSELOKUL_MUHASEBE_ISLERI_PERSONELI = __(u"Yükselokul Muhasebe İşleri Personeli")
    YUKSELOKUL_OGRENCI_ISLERI_PERSONELI = __(u"Yükselokul Öğrenci İşleri Personeli")
    TIP_FAKULTESI_EGITIM_KOMISYONU_UYESI = __(u"Tıp Fakültesi Eğitim Komisyonu Üyesi")
    TIP_FAKULTESI_BAS_KOORDINATOR_YARDIMCISI = __(u"Tıp Fakültesi Baş Koordinatör Yardımcısı")
    TIP_FAKULTESI_EGITIM_KOMISYONU_BASKANI = __(u"Tıp Fakültesi Eğitim Komisyonu Başkanı")
    TIP_FAKULTESI_DONEM_KOORDINATORU = __(u"Tıp Fakültesi Dönem Koordinatörü")
    TIP_FAKULTESI_BAS_KOORDINATORU = __(u"Tıp Fakültesi Baş Koordinatörü")
    ON_LISANS_OGRENCISI_AKTIF = __(u"Ön Lisans Programı Öğrencisi - Aktif")
    ON_LISANS_OGRENCISI_KAYIT_SILINMIS = __(u"Ön Lisans Programı Öğrencisi - Kayıt Silinmiş")
    ON_LISANS_OGRENCISI_KAYIT_DONDURMUS = __(u"Ön Lisans Programı Öğrencisi - Kayıt Dondurmuş")
    LISANS_OGRENCISI_AKTIF = __(u"Lisans Programı Öğrencisi - Aktif")
    LISANS_OGRENCISI_KAYIT_SILINMIS = __(u"Lisans Programı Öğrencisi - Kayıt Silinmiş")
    LISANS_OGRENCISI_KAYIT_DONDURMUS = __(u"Lisans Programı Öğrencisi - Kayıt Dondurmuş")
    YUKSEK_LISANS_OGRENCISI_AKTIF = __(u"Yüksek Lisans Programı Öğrencisi - Aktif")
    YUKSEK_LISANS_OGRENCISI_KAYIT_SILINMIS = __(u"Yüksek Lisans Programı Öğrencisi - Kayıt Silinmiş")
    YUKSEK_LISANS_OGRENCISI_KAYIT_DONDURMUS = __(u"Yüksek Lisans Programı Öğrencisi - Kayıt Dondurmuş")
    DOKTORA_OGRENCISI_AKTIF = __(u"Doktora Programı Öğrencisi - Aktif")
    DOKTORA_OGRENCISI_KAYIT_SILINMIS = __(u"Doktora Programı Öğrencisi - Kayıt Silinmiş")
    DOKTORA_OGRENCISI_KAYIT_DONDURMUS = __(u"Doktora Programı Öğrencisi - Kayıt Dondurmuş")
    OGRETIM_ELEMANI = __(u"Öğretim Elemanı")
    ANA_BILIM_DALI_UYESI = __(u"Ana Bilim Dalı Üyesi")
    ANA_BILIM_DALI_BASKANI = __(u"Ana Bilim Dalı Başkanı")
    BILIM_DALI_UYESI = __(u"Bilim Dalı Üyesi")
    BILIM_DALI_BASKANI = __(u"Bilim Dalı Başkanı")
    BOLUM_BASKANI = __(u"Bölüm Başkanı")
    BOLUM_KURULU_BASKANI = __(u"Bölüm Kurulu Başkanı")
    BOLUM_KURULU_UYESI = __(u"Bölüm Kurulu Üyesi")
    BOLUM_SEKRETERI = __(u"Bölüm Sekreteri")
    DAIRE_BASKANI = __(u"Daire Başkanı")
    DAIRE_SUBE_SEFI = __(u"Şube Şefi")
    DAIRE_SUBE_MUDURU = __(u"Daire Şube Müdürü")
    DAIRE_PERSONELI = __(u"Daire Personeli")
    REKTOR = __(u"Rektör")
    DANISMAN = __(u"Danışman")
    DERS_PROGRAMI_KOORDINATORU = __(u"Ders Programı Koordinatörü")
    BASEABSROLE = __(u"BaseAbsRole")
    GENEL_SEKRETER = __(u"Genel Sekreter")
    MUTEMET = __(u"Mutemet")