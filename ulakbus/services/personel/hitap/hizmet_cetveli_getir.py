# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Cetveli Sorgula

Hitap üzerinden personelin hizmet kaydı bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetCetveliGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış
    Hizmet Kaydı Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            bean_name (str): Hitap'tan gelen bean nesnesinin adı
            service_dict (dict): Hitap servisinden gelen kayıtların alanları,
                    ``HizmetKayitlari`` modelinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.

        """

        self.service_name = 'HizmetCetvelSorgula'
        self.bean_name = 'HizmetCetveliServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'baslama_tarihi': 'baslamaTarihi',
                'bitis_tarihi': 'bitisTarihi',
                'emekli_derece': 'emekliDerece',
                'emekli_kademe': 'emekliKademe',
                'gorev': 'gorev',
                'unvan_kod': 'unvanKod',
                'hizmet_sinifi': 'hizmetSinifi',
                'kayit_no': 'kayitNo',
                'kazanilmis_hak_ayligi_derece': 'kazanilmisHakAyligiDerece',
                'kazanilmis_hak_ayligi_kademe': 'kazanilmisHakAyligiKademe',
                'odeme_derece': 'odemeDerece',
                'odeme_kademe': 'odemeKademe',
                'emekli_ek_gosterge': 'emekliEkGosterge',
                'kadro_derece': 'kadroDerece',
                'kazanilmis_hak_ayligi_ekgosterge': 'kazanilmisHakAyligiEkGosterge',
                'odeme_ekgosterge': 'odemeEkGosterge',
                'sebep_kod': 'sebepKod',
                'ucret':'ucret',
                'yevmiye': 'yevmiye',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kurum_onay_tarihi'],
            'required_fields': ['tckn']
        }
        super(HizmetCetveliGetir, self).handle()

    def custom_filter(self, hitap_dict):
        """
        Hitap sözlüğüne uygulanacak ek filtreleri gerçekleştirir.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """

        for record in hitap_dict:
            record['hizmet_sinifi'] = self.hizmet_sinifi_int_kontrol(record['hizmet_sinifi'])

    def hizmet_sinifi_int_kontrol(self, hizmet_sinifi):
        """
        Hitap Hizmet Cetveli sorgulama servisinin,
        hem 1, 2, 3 ... 29 gibi tam sayı (servisten string olarak geliyor) değerleri
        hem de GİH, MİAH, ... SÖZ gibi string değerleri alabilen,
        hizmetSinifi alanının, her koşulda tam sayı olarak elde edilmesini sağlar.

        Args:
            hizmet_sinifi (str): Hizmet Cetveli hizmet sınıfı bilgisi

        Returns:
            int: Hizmet sınıfı tam sayı değeri.

        Raises:
            ValueError: Geçersiz hizmet sınıfı değeri.

        """

        hizmet_siniflari = {
            u"GİH": 1,
            u"MİAH": 2,
            u"SH": 3,
            u"TH": 4,
            u"EÖH": 5,
            u"AH": 6,
            u"EH": 7,
            u"DH": 8,
            u"YH": 9,
            u"MİT": 10,
            u"AHS": 11,
            u"BB": 12,
            u"CU": 13,
            u"CUM": 14,
            u"DE": 15,
            u"DVS": 16,
            u"HS": 17,
            u"MB": 18,
            u"MV": 19,
            u"ÖÜ": 20,
            u"SAY": 21,
            u"TBM": 22,
            u"TRT": 23,
            u"TSK": 24,
            u"YÖK": 25,
            u"YSH": 26,
            u"ÖGO": 27,
            u"ÖY": 28,
            u"SÖZ": 29
        }

        try:
            # return if it is int
            return int(hizmet_sinifi)

        except ValueError:
            # if not, find its value (int) in dict (key type is 'suds.sax.text.Text')
            try:
                return hizmet_siniflari[hizmet_sinifi.strip()]
            except KeyError:
                # TODO: admin'e bildirim gitmesi lazim
                self.logger.exception("Hizmet Sinifini (%s) Kontrol Edin!", hizmet_sinifi)
                return 0
