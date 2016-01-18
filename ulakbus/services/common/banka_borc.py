# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.services.common.banka import BankaService
from ulakbus.models.ogrenci import OgrenciProgram, Borc


class BankaBorcService(BankaService):
    """
    Banka Borc Sorgulama Zato Servisi
    """

    class SimpleIO:
        input_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                          'ogrenci_no')
        output_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                           'ogrenci_no', 'ad_soyad', 'ucret_turu', 'tahakkuk_referans_no', 'son_odeme_tarihi',
                           'borc', 'borc_ack')

    def handle(self):
        super(BankaBorcService, self).handle()

    def get_data(self):
        super(BankaBorcService, self).get_data()

        ogrenci_no = self.request.input.ogrenci_no
        ogr = OgrenciProgram.objects.get(ogrenci_no=ogrenci_no).ogrenci

        borclar = Borc.objects.filter(ogrenci=ogr)
        for borc in borclar:
            borc_sorgu = {
                'banka_kodu': self.request.input.banka_kodu,
                'sube_kodu': self.request.input.sube_kodu,
                'kanal_kodu': self.request.input.kanal_kodu,
                'mesaj_no': self.request.input.mesaj_no,
                'bank_username': self.request.input.bank_username,
                'bank_password': self.request.input.bank_password,
                'ogrenci_no': self.request.input.ogrenci_no,
                'ad_soyad': ogr.ad + ogr.soyad,
                'ucret_turu': borc.sebep,
                'tahakkuk_referans_no': borc.tahakkuk_referans_no,
                'son_odeme_tarihi': borc.son_odeme_tarihi,
                'borc': borc.miktar,
                'borc_ack': borc.aciklama
            }
            self.response.payload.append(borc_sorgu)
