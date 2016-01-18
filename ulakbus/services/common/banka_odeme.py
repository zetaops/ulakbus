# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.services.common.banka import BankaService
from ulakbus.models.ogrenci import OgrenciProgram, Borc, Odeme


class BankaOdemeService(BankaService):
    """
    Banka Odeme Zato Servisi
    """

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

        # birden fazla odeme varsa tahakkuka gore mi karar verilecek
        # toplu odeme sansi var mi?
        tahakkuk_referans_no = self.request.input.tahakkuk_referans_no
        borc = Borc.objects.filter(ogrenci=ogr, tahakkuk_referans_no=tahakkuk_referans_no)
        banka = Banka.object.get(kod=self.banka_kodu) # duplicate

        # eksikler: mesaj_no, donem?
        # borc modeline de kaydedilecek mi
        odeme = Odeme()
        odeme.miktar = self.request.input.odeme_tutari
        # odeme.para_birimi = self.request.input.para_birimi
        # odeme.aciklama =  self.request.input.aciklama
        # odeme.odeme_sekli = self.request.input.odeme_sekli
        odeme.odeme_tarihi = self.request.input.odeme_timestamp
        odeme.borc = borc
        odeme.ogrenci = ogr
        odeme.banka = banka
        odeme.banka_sube_kodu = self.request.input.sube_kodu
        odeme.banka_kanal_kodu = self.request.input.kanal_kodu
        odeme.tahsilat_referans_no = self.request.input.tahsilat_referans_no

        try:
            odeme.save()
            # mesaj_statusu =
            # hata_mesaj =
        except:
            # mesaj_statusu =
            # hata_mesaj =
            pass

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

        self.response.payload.append(odeme_response)
