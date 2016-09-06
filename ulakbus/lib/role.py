# -*-  coding: utf-8 -*-
"""Roller ile ilgili yardımcı class ve fonksiyonların yer aldığı dosyadır.

"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from enum import Enum
from gettext import gettext as _


class AbsRole(Enum):
    """
    Abstract roller icin enumerated data. Veritabani keyleri ozellik adi ile eslesir.
    Kod icinde su sekilde kullanilabilir:

    ... code-block:: python
        hitap_kaydi = form_data["soyut_rol_id"] in [AbsRole.FAKULTE_DEKANI, AbsRole.REKTOR]

    kod icinde translation ile birlikte kullanilabilir.

    .. code-block:: python
        _("%s degistirildi..") % AbsRole.FAKULTE_YONETIM_KURULU_UYESI

    """

    FAKULTE_YONETIM_KURULU_UYESI = _(u"Fakülte Yönetim Kurulu Üyesi")
    FAKULTE_YONETIM_KURULU_BASKANI_DEKAN = _(u"Fakülte Yönetim Kurulu Başkanı (Dekan)")
    FAKULTE_DEKAN_SEKRETERI = _(u"Fakülte Dekan Sekreteri")
    FAKULTE_DEKANI = _(u"Fakülte Dekanı")
    FAKULTE_OGRENCI_ISLERI_SEFI = _(u"Fakülte Öğrenci İşleri Şefi")
    FAKULTE_KURULU_UYESI = _(u"Fakülte Kurulu Üyesi")
    FAKULTE_SEKRETERI = _(u"Fakülte Sekreteri")
    FAKULTE_ETIK_KURULU_BASKANI = _(u"Fakülte Etik Kurulu Başkanı")
    FAKULTE_ETIK_KURULU_UYESI = _(u"Fakülte Etik Kurulu Üyesi")
    FAKULTE_OGRENCI_ISLERI_PERSONELI = _(u"Fakülte Öğrenci İşleri Personeli")
    FAKULTE_DEKAN_YARDIMCISI = _(u"Fakülte Dekan Yardımcısı")
    FAKULTE_KURULU_BASKANI = _(u"Fakülte Kurulu Başkanı (Dekan)")
    ENSTITU_MUDURU = _(u"Enstitü Müdürü")
    ENSTITU_YONETIM_KURULU_BASKANI = _(u"Enstitü Yönetim Kurulu Başkanı")
    ENSTITU_OGRENCI_ISLERI_PERSONELI = _(u"Enstitü Öğrenci İşleri Personeli")
    ENSTITU_YONETIM_KURULU_UYESI = _(u"Enstitü Yönetim Kurulu Üyesi")
    ENSTITU_SEKRETERI = _(u"Enstitü Sekreteri")
    ENSTITU_OGRENCI_ISLERI_SEFI = _(u"Enstitü Öğrenci İşleri Şefi")
    ENSTITU_MUDUR_YARDIMCISI = _(u"Enstitü Müdür Yardımcısı")
    ENSTITU_MUHASEBE_ISLERI_PERSONELI = _(u"Enstitü Muhasebe İşleri Personeli")
    ENSTITU_KURULU_UYESI = _(u"Enstitü Kurulu Üyesi")
    ENSTITU_MUHASEBE_ISLERI_SEFI = _(u"Enstitü Muhasebe İşleri Şefi")
    ENSTITU_KURULU_BASKANI = _(u"Enstitü Kurulu Başkanı")
    YUKSELOKUL_KURULU_BASKANI = _(u"Yükselokul Kurulu Başkanı")
    YUKSELOKUL_YONETIM_KURULU_BASKANI = _(u"Yükselokul Yönetim Kurulu Başkanı")
    YUKSELOKUL_BIRIM_KOORDINATORU = _(u"Yükselokul Birim Koordinatörü")
    YUKSELOKUL_YONETIM_KURULU_UYESI = _(u"Yükselokul Yönetim Kurulu Üyesi")
    YUKSELOKUL_MUDURU = _(u"Yükselokul Müdürü")
    YUKSELOKUL_MUDUR_YARDIMCISI = _(u"Yükselokul Müdür Yardımcısı")
    YUKSELOKUL_SEKRETERI = _(u"Yükselokul Sekreteri")
    YUKSELOKUL_OGRENCI_ISLERI_SEFI = _(u"Yükselokul Öğrenci İşleri Şefi")
    YUKSELOKUL_KURULU_UYESI = _(u"Yükselokul Kurulu Üyesi")
    YUKSELOKUL_MUHASEBE_ISLERI_SEFI = _(u"Yükselokul Muhasebe İşleri Şefi")
    YUKSELOKUL_MUHASEBE_ISLERI_PERSONELI = _(u"Yükselokul Muhasebe İşleri Personeli")
    YUKSELOKUL_OGRENCI_ISLERI_PERSONELI = _(u"Yükselokul Öğrenci İşleri Personeli")
    TIP_FAKULTESI_EGITIM_KOMISYONU_UYESI = _(u"Tıp Fakültesi Eğitim Komisyonu Üyesi")
    TIP_FAKULTESI_BAS_KOORDINATOR_YARDIMCISI = _(u"Tıp Fakültesi Baş Koordinatör Yardımcısı")
    TIP_FAKULTESI_EGITIM_KOMISYONU_BASKANI = _(u"Tıp Fakültesi Eğitim Komisyonu Başkanı")
    TIP_FAKULTESI_DONEM_KOORDINATORU = _(u"Tıp Fakültesi Dönem Koordinatörü")
    TIP_FAKULTESI_BAS_KOORDINATORU = _(u"Tıp Fakültesi Baş Koordinatörü")
    ON_LISANS_OGRENCISI_AKTIF = _(u"Ön Lisans Programı Öğrencisi - Aktif")
    ON_LISANS_OGRENCISI_KAYIT_SILINMIS = _(u"Ön Lisans Programı Öğrencisi - Kayıt Silinmiş")
    ON_LISANS_OGRENCISI_KAYIT_DONDURMUS = _(u"Ön Lisans Programı Öğrencisi - Kayıt Dondurmuş")
    LISANS_OGRENCISI_AKTIF = _(u"Lisans Programı Öğrencisi - Aktif")
    LISANS_OGRENCISI_KAYIT_SILINMIS = _(u"Lisans Programı Öğrencisi - Kayıt Silinmiş")
    LISANS_OGRENCISI_KAYIT_DONDURMUS = _(u"Lisans Programı Öğrencisi - Kayıt Dondurmuş")
    YUKSEK_LISANS_OGRENCISI_AKTIF = _(u"Yüksek Lisans Programı Öğrencisi - Aktif")
    YUKSEK_LISANS_OGRENCISI_KAYIT_SILINMIS = _(u"Yüksek Lisans Programı Öğrencisi - Kayıt Silinmiş")
    YUKSEK_LISANS_OGRENCISI_KAYIT_DONDURMUS = _(
        u"Yüksek Lisans Programı Öğrencisi - Kayıt Dondurmuş")
    DOKTORA_OGRENCISI_AKTIF = _(u"Doktora Programı Öğrencisi - Aktif")
    DOKTORA_OGRENCISI_KAYIT_SILINMIS = _(u"Doktora Programı Öğrencisi - Kayıt Silinmiş")
    DOKTORA_OGRENCISI_KAYIT_DONDURMUS = _(u"Doktora Programı Öğrencisi - Kayıt Dondurmuş")
    OGRETIM_ELEMANI = _(u"Öğretim Elemanı")
    ANA_BILIM_DALI_UYESI = _(u"Ana Bilim Dalı Üyesi")
    ANA_BILIM_DALI_BASKANI = _(u"Ana Bilim Dalı Başkanı")
    BILIM_DALI_UYESI = _(u"Bilim Dalı Üyesi")
    BILIM_DALI_BASKANI = _(u"Bilim Dalı Başkanı")
    BOLUM_BASKANI = _(u"Bölüm Başkanı")
    BOLUM_KURULU_BASKANI = _(u"Bölüm Kurulu Başkanı")
    BOLUM_KURULU_UYESI = _(u"Bölüm Kurulu Üyesi")
    BOLUM_SEKRETERI = _(u"Bölüm Sekreteri")
    DAIRE_BASKANI = _(u"Daire Başkanı")
    DAIRE_SUBE_SEFI = _(u"Şube Şefi")
    DAIRE_SUBE_MUDURU = _(u"Daire Şube Müdürü")
    DAIRE_PERSONELI = _(u"Daire Personeli")
    REKTOR = _(u"Rektör")
