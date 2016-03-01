# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Kurs Ekle

Hitap'a personelin kurs bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle
from ulakbus.models.hitap import HizmetKurs


class HizmetKursEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Kurs Bilgisi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetKurs'' servisinden gelen kayıtların alanları,
                    HizmetKursInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetKursInsert'
        hizmet_kurs = HizmetKurs.objects.get(key)
        self.service_dict = {
            'fields': {
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
        super(HizmetKursEkle, self).handle()