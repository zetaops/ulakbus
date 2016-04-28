# -*-  coding: utf-8 -*-
"""Roller ile ilgili yardımcı class ve fonksiyonların yer aldığı dosyadır.

"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = "H.İbrahim Yılmaz (drlinux)"


class RoleHelper():
    """RoleHelper Class

    """

    def get_abstract_role_name(self, role_key):
        """Verilen role keyine uygun değeri döndürür.

        :param role_key:
        :return: string

        """

        role_dict = {"yukselokul-kurulu-baskani": "Yükselokul Kurulu Başkanı",
                     "enstitu-muduru": "Enstitü Müdürü",
                     "yukselokul-yonetim-kurulu-baskani": "Yükselokul Yönetim Kurulu Başkanı",
                     "fakulte-yonetim-kurulu-uyesi": "Fakülte Yönetim Kurulu Üyesi",
                     "lisans-ogrencisi-kayit-silinmis": "Lisans Programı Öğrencisi - Kayıt Silinmiş",
                     "fakulte-yonetim-kurulu-baskani-dekan": "Fakülte Yönetim Kurulu Başkanı (Dekan)",
                     "fakulte-dekan-sekreteri": "Fakülte Dekan Sekreteri",
                     "fakulte-dekani": "Fakülte Dekanı",
                     "enstitu-ogrenci-isleri-sefi": "Enstitü Öğrenci İşleri Şefi",
                     "enstitu-mudur-yardimcisi": "Enstitü Müdür Yardımcısı",
                     "fakulte-ogrenci-isleri-sefi": "Fakülte Öğrenci İşleri Şefi",
                     "fakulte-kurulu-uyesi": "Fakülte Kurulu Üyesi",
                     "enstitu-muhasebe-isleri-personeli": "Enstitü Muhasebe İşleri Personeli",
                     "on-lisans-ogrencisi-kayit-silinmis": "Ön Lisans Programı Öğrencisi - Kayıt Silinmiş",
                     "yukselokul-birim-koordinatoru": "Yükselokul Birim Koordinatörü",
                     "yukselokul-yonetim-kurulu-uyesi": "Yükselokul Yönetim Kurulu Üyesi",
                     "tip-fakultesi-egitim-komisyonu-uyesi": "Tıp Fakültesi Eğitim Komisyonu Üyesi",
                     "yukselokul-muduru": "Yükselokul Müdürü",
                     "ana-bilim-dali-baskani": "Ana Bilim Dalı Başkanı",
                     "fakulte-sekreteri": "Fakülte Sekreteri",
                     "bolum-kurulu-uyesi": "Bölüm Kurulu Üyesi",
                     "tip-fakultesi-bas-koordinator-yardimcisi": "Tıp Fakültesi Baş Koordinatör Yardımcısı",
                     "fakulte-etik-kurulu-baskani": "Fakülte Etik Kurulu Başkanı",
                     "on-lisans-ogrencisi-kayit-dondurmus": "Ön Lisans Programı Öğrencisi - Kayıt Dondurmuş",
                     "yukselokul-sekreteri": "Yükselokul Sekreteri",
                     "yuksek-lisans-ogrencisi-aktif": "Yüksek Lisans Programı Öğrencisi - Aktif",
                     "fakulte-ogrenci-isleri-personeli": "Fakülte Öğrenci İşleri Personeli",
                     "yukselokul-muhasebe-isleri-sefi": "Yükselokul Muhasebe İşleri Şefi",
                     "ogretim-elemani": "Öğretim Elemanı",
                     "bolum-kurulu-baskani": "Bölüm Kurulu Başkanı",
                     "yuksek-lisans-ogrencisi-kayit-silinmis": "Yüksek Lisans Programı Öğrencisi - Kayıt Silinmiş",
                     "doktora-ogrencisi-kayit-dondurmus": "Doktora Programı Öğrencisi - Kayıt Dondurmuş",
                     "yukselokul-kurulu-uyesi": "Yükselokul Kurulu Üyesi",
                     "fakulte-etik-kurulu-uyesi": "Fakülte Etik Kurulu Üyesi",
                     "lisans-ogrencisi-aktif": "Lisans Programı Öğrencisi - Aktif",
                     "yuksek-lisans-ogrencisi-kayit-dondurmus": "Yüksek Lisans Programı Öğrencisi - Kayıt Dondurmuş",
                     "yukselokul-ogrenci-isleri-sefi": "Yükselokul Öğrenci İşleri Şefi",
                     "enstitu-kurulu-uyesi": "Enstitü Kurulu Üyesi",
                     "bilim-dali-uyesi": "Bilim Dalı Üyesi",
                     "enstitu-muhasebe-isleri-sefi": "Enstitü Muhasebe İşleri Şefi",
                     "lisans-ogrencisi-kayit-dondurmus": "Lisans Programı Öğrencisi - Kayıt Dondurmuş",
                     "enstitu-kurulu-baskani": "Enstitü Kurulu Başkanı",
                     "bolum-sekreteri": "Bölüm Sekreteri",
                     "fakulte-dekan-yardimcisi": "Fakülte Dekan Yardımcısı",
                     "daire-sube-muduru": "Daire Şube Müdürü",
                     "bilim-dali-baskani": "Bilim Dalı Başkanı",
                     "yukselokul-muhasebe-isleri-personeli": "Yükselokul Muhasebe İşleri Personeli",
                     "daire-baskani": "Daire Başkanı",
                     "enstitu-ogrenci-isleri-personeli": "Enstitü Öğrenci İşleri Personeli",
                     "doktora-ogrencisi-aktif": "Doktora Programı Öğrencisi - Aktif",
                     "fakulte-kurulu-baskani-dekan": "Fakülte Kurulu Başkanı (Dekan)",
                     "enstitu-sekreteri": "Enstitü Sekreteri",
                     "tip-fakultesi-egitim-komisyonu-baskani": "Tıp Fakültesi Eğitim Komisyonu Başkanı",
                     "yukselokul-mudur-yardimcisi": "Yükselokul Müdür Yardımcısı",
                     "ana-bilim-dali-uyesi": "Ana Bilim Dalı Üyesi",
                     "daire-personeli": "Daire Personeli",
                     "yukselokul-ogrenci-isleri-personeli": "Yükselokul Öğrenci İşleri Personeli",
                     "enstitu-yonetim-kurulu-baskani": "Enstitü Yönetim Kurulu Başkanı",
                     "tip-fakultesi-bas-koordinatoru": "Tıp Fakültesi Baş Koordinatörü",
                     "bolum-baskani": "Bölüm Başkanı",
                     "enstitu-yonetim-kurulu-uyesi": "Enstitü Yönetim Kurulu Üyesi",
                     "tip-fakultesi-donem-koordinatoru": "Tıp Fakültesi Dönem Koordinatörü",
                     "sube-sefi": "Şube Şefı",
                     "doktora-ogrencisi-kayit-silinmis": "Doktora Programı Öğrencisi - Kayıt Silinmiş",
                     "on-lisans-ogrencisi-aktif": "Ön Lisans Programı Öğrencisi - Aktif"}

        if role_key in role_dict:
            return role_dict[role_key]
