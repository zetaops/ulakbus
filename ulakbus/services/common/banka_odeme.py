# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.services.common.banka import BankaService
from ulakbus.models.ogrenci import OgrenciProgram, Borc, Odeme
import json


class BankaOdemeService(BankaService):
    """
    Banka Odeme Zato Servisi
    """

    def __init__(self):
        super(BankaOdemeService, self).__init__()

    class SimpleIO:
        input_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                          'ogrenci_no', 'ucret_turu', 'tahakkuk_referans_no', 'tahsilat_referans_no', 'odeme_timestamp',
                          'odeme_tutari')
        output_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                           'mesaj_statusu', 'ogrenci_no', 'ucret_turu', 'tahakkuk_referans_no', 'tahsilat_referans_no',
                           'odeme_timestamp', 'odeme_tutari', 'hata_mesaj')

    def handle(self):
        super(BankaOdemeService, self).handle()

    def get_data(self):
        super(BankaOdemeService, self).get_data()

        ogrenci_no = self.request.input.ogrenci_no
        ogr = OgrenciProgram.objects.get(ogrenci_no=ogrenci_no).ogrenci

        # her borcun referans numarasi olarak 'tahakkuk_referans_no' kullanilir
        tahakkuk_referans_no = self.request.input.tahakkuk_referans_no
        borc = Borc.objects.filter(ogrenci=ogr, tahakkuk_referans_no=tahakkuk_referans_no)

        odeme = Odeme()
        odeme.miktar = self.request.input.odeme_tutari
        odeme.para_birimi = 1  # TL
        odeme.aciklama =  borc.aciklama
        odeme.odeme_sekli = 3  # Banka
        odeme.odeme_tarihi = self.request.input.odeme_timestamp
        odeme.borc = borc
        odeme.ogrenci = ogr
        odeme.banka = self.banka
        odeme.banka_sube_kodu = str(self.request.input.sube_kodu)
        odeme.banka_kanal_kodu = self.request.input.kanal_kodu
        odeme.tahsilat_referans_no = self.request.input.tahsilat_referans_no
        odeme.donem = borc.donem

        try:
            odeme.save()
            mesaj_statusu = "K"
            hata_mesaj = None
        except:
            mesaj_statusu = "R"
            hata_mesaj = "Odeme kaydedilirken hata olustu!"

        odeme_response = {
            'banka_kodu': self.request.input.banka_kodu,
            'sube_kodu': self.request.input.sube_kodu,
            'kanal_kodu': self.request.input.kanal_kodu,
            'mesaj_no': self.request.input.mesaj_no,
            'bank_username': self.request.input.bank_username,
            'bank_password': self.request.input.bank_password,
            'mesaj_statusu': mesaj_statusu,
            'ogrenci_no': self.request.input.ogrenci_no,
            'ucret_turu': self.request.input.sebep,
            'tahakkuk_referans_no': self.request.input.tahakkuk_referans_no,
            'tahsilat_referans_no': self.request.input.tahsilat_referans_no,
            'odeme_timestamp': self.request.input.odeme_timestamp,
            'odeme_tutari': self.request.input.odeme_tutari,
            'hata_mesaj': hata_mesaj
        }

        self.logger.info("Odeme bilgisi: %s" % json.dumps(odeme_response))
        self.response.payload.append(odeme_response)
