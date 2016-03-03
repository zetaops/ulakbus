# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Kurs Guncelle

Hitap'a personelin Kurs bilgilerinin guncellemesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle
from ulakbus.models.hitap import HizmetKurs


class HizmetKursGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Kurs Bilgi Guncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetKurs'' modelinden gelen kayıtların alanları,
                    hizmetKursUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetKursUpdate'
        hizmet_kurs = HizmetKurs.objects.get(key)
        self.service_dict = {
            'fields': {
                'kayitNo': hizmet_kurs.kayit_no,
                'tckn': hizmet_kurs.tckn,
                'kursOgrenimSuresi': hizmet_kurs.kurs_ogrenim_suresi,
                'mezuniyetTarihi': hizmet_kurs.mezuniyet_tarihi,
                'kursNevi': hizmet_kurs.kurs_nevi,
                'bolumAd': hizmet_kurs.bolum_ad,
                'okulAd': hizmet_kurs.okul_ad,
                'ogrenimYeri': hizmet_kurs.ogrenim_yeri,
                'denklikTarihi': hizmet_kurs.denklik_tarihi,
                'denklikOkul': hizmet_kurs.denklik_okulu,
                'denklikBolum': hizmet_kurs.denklik_bolum,
                'kurumOnayTarihi': hizmet_kurs.kurum_onay_tarihi
            },
            'date_filter': ['mezuniyetTarihi', 'denklikTarihi', 'kurumOnayTarihi']
        }
        super(HizmetKursGuncelle, self).handle()
