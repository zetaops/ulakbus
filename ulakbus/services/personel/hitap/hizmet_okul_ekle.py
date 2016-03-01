# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Okul Ekle

Hitap'a personelin Okul bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle
from ulakbus.models.hitap import HizmetOkul


class HizmetOkulEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Okul Bilgi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetOkul'' modelinden gelen kayıtların alanları,
                    HizmetOkulInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetOkulInsert'
        hizmet_okul = HizmetOkul.objects.get(key)
        self.service_dict = {
            'fields': {
                'bolum': hizmet_okul.bolum,
                'kayitNo': hizmet_okul.kayit_no,
                'mezuniyetTarihi': hizmet_okul.mezuniyet_tarihi,
                'ogrenimDurumu': hizmet_okul.ogrenim_durumu,
                'ogrenimSuresi': hizmet_okul.ogrenim_suresi,
                'okulAd': hizmet_okul.okul_ad,
                'tckn': hizmet_okul.tckn,
                'denklikTarihi': hizmet_okul.denklik_tarihi,
                'ogrenimYer': hizmet_okul.ogrenim_yeri,
                'denklikBolum': hizmet_okul.denklik_bolum,
                'denklikOkul': hizmet_okul.denklik_okul,
                'hazirlik': hizmet_okul.hazirlik,
                'kurumOnayTarihi': hizmet_okul.kurum_onay_tarihi
            },
            'date_filter': ['mezuniyetTarihi', 'denklikTarihi', 'kurumOnayTarihi']
        }
        super(HizmetOkulEkle, self).handle()
