# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.services.common.banka import BankaService
from ulakbus.models.ogrenci import OgrenciProgram, Borc, Odeme
from pyoko.exceptions import ObjectDoesNotExist
import json


class BankaBorcOdeme(BankaService):
    """
    Banka Borc Odeme Zato Servisi

    :param banka_kodu: Universite tarafindan bankaya verilen kod
    :type banka_kodu: int -> str

    :param bank_username: Universite tarafindan bankaya verilen kullanici kodu
    :type bank_username: str

    :param bank_password: Universite tarafindan bankaya verilen kullanici sifresi
    :type bank_username: str

    :param ogrenci_no: Borclari sorgulanan ogrencinin kayitli oldugu programa ait ogrenci numarasi
    :type sube_kodu: str

    :param sube_kodu: Bankalarin subeleri icin hali hazirda kullandiklari kodlar
    :type sube_kodu: int -> str

    :param kanal_kodu: G: Gise, I: Internet, A: ATM, T: AloBanka vb.
    :type kanal_kodu: str

    :param tahakkuk_referans_no: Universite tarafindan her tahakkuka verilen referans numarasi
    :type tahakkuk_referans_no: str

    :param tahsilat_referans_no: Banka tarafindan verilen tahsilata ait referans no (makbuz no olabilir)
    :type tahsilat_referans_no: str

    :param odeme_timestamp: DDMMYYYYHHMMSS formatinda odeme tarihidir
    :type odeme_timestamp: str

    :param odeme_tutari: Banka tarafindan tahsil edilen miktar
    :type odeme_tutari: float

    :return Odeme bilgisini iceren JSON nesnesi
    """

    def __init__(self):
        super(BankaBorcOdeme, self).__init__()

    class SimpleIO():
        input_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                          'ogrenci_no', 'ucret_turu', 'tahakkuk_referans_no', 'tahsilat_referans_no', 'odeme_timestamp',
                          'odeme_tutari')
        output_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                           'mesaj_statusu', 'ogrenci_no', 'ucret_turu', 'tahakkuk_referans_no', 'tahsilat_referans_no',
                           'odeme_timestamp', 'odeme_tutari', 'hata_mesaj')

    def handle(self):
        super(BankaBorcOdeme, self).handle()

    def get_data(self):
        """
        Ogrencinin borc odeme bilgilerinin kaydedilmesi

        :return: Odeme bilgisini iceren JSON nesnesi
        """

        super(BankaBorcOdeme, self).get_data()

        try:
            ogrenci_no = self.request.input.ogrenci_no
            ogrenci = OgrenciProgram.objects.get(ogrenci_no=ogrenci_no).ogrenci

            # her borcun referans numarasi olarak 'tahakkuk_referans_no' kullanilir
            tahakkuk_referans_no = self.request.input.tahakkuk_referans_no
            borc = Borc.objects.filter(ogrenci=ogrenci, tahakkuk_referans_no=tahakkuk_referans_no)[0]

            odeme = Odeme()
            odeme.miktar = self.request.input.odeme_tutari
            odeme.para_birimi = 1  # TL
            odeme.aciklama =  borc.aciklama
            odeme.odeme_sekli = 3  # Banka
            odeme.odeme_tarihi = self.request.input.odeme_timestamp
            odeme.borc = borc
            odeme.ogrenci = ogrenci
            odeme.banka = self.banka
            odeme.banka_sube_kodu = str(self.request.input.sube_kodu)
            odeme.banka_kanal_kodu = self.request.input.kanal_kodu
            odeme.banka_kanal_kodu = self.request.input.kanal_kodu
            odeme.tahsilat_referans_no = self.request.input.tahsilat_referans_no
            odeme.donem = borc.donem

            odeme.save()
            mesaj_statusu = "K"
            hata_mesaj = None

        except ObjectDoesNotExist:
            self.logger.info('Ogrenci numarasi bulunamadi.')
            mesaj_statusu = "R"
            hata_mesaj = "Ogrenci numarasi bulunamadi!"

        except Exception as e:
            self.logger.info("Odeme kaydedilirken hata olustu: %s" % e)
            mesaj_statusu = "R"
            hata_mesaj = "Odeme kaydedilirken hata olustu!"

        finally:
            odeme_response = {
                'banka_kodu': self.request.input.banka_kodu,
                'sube_kodu': self.request.input.sube_kodu,
                'kanal_kodu': self.request.input.kanal_kodu,
                'mesaj_no': self.request.input.mesaj_no,
                'bank_username': self.request.input.bank_username,
                'bank_password': self.request.input.bank_password,
                'mesaj_statusu': mesaj_statusu,
                'ogrenci_no': self.request.input.ogrenci_no,
                'ucret_turu': self.request.input.ucret_turu,
                'tahakkuk_referans_no': self.request.input.tahakkuk_referans_no,
                'tahsilat_referans_no': self.request.input.tahsilat_referans_no,
                'odeme_timestamp': self.request.input.odeme_timestamp,
                'odeme_tutari': self.request.input.odeme_tutari,
                'hata_mesaj': hata_mesaj
            }

            self.logger.info("Odeme bilgisi: %s" % json.dumps(odeme_response))
            self.response.payload.append(odeme_response)
