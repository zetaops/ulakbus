# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Açık Süre Sorgula

Hitap üzerinden personelin
açık süre hizmet bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetAcikSureGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış
    Açık Süre Hizmet Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            bean_name (str): Hitap'tan gelen bean nesnesinin adı
            service_dict (dict): Hitap servisinden gelen kayıtların alanları,
                    ``HizmetAcikSure`` modelinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.

        """

        self.service_name = 'HizmetAcikSureSorgula'
        self.bean_name = 'HizmetAcikSureServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'acik_sekil': 'acikSekil',
                'iade_sekil': 'iadeSekil',
                'hizmet_durum': 'hizmetDurum',
                'husus': 'husus',
                'aciga_alinma_tarih': 'acigaAlinmaTarih',
                'goreve_son_tarih': 'goreveSonTarih',
                'goreve_iade_istem_tarih': 'goreveIadeIstemTarih',
                'goreve_iade_tarih': 'goreveIadeTarih',
                'acik_aylik_bas_tarih': 'acikAylikBasTarih',
                'acik_aylik_bit_tarih': 'acikAylikBitTarih',
                'goreve_son_aylik_bas_tarih': 'goreveSonAylikBasTarih',
                'goreve_son_aylik_bit_tarih': 'goreveSonAylikBitTarih',
                's_yonetim_kald_tarih': 'SYonetimKaldTarih',
                'aciktan_atanma_tarih': 'aciktanAtanmaTarih',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['aciga_alinma_tarih', 'goreve_son_tarih', 'goreve_iade_istem_tarih',
                            'goreve_iade_tarih', 'acik_aylik_bas_tarih', 'acik_aylik_bit_tarih',
                            'goreve_son_aylik_bas_tarih', 'goreve_son_aylik_bit_tarih',
                            's_yonetim_kald_tarih', 'aciktan_atanma_tarih', 'kurum_onay_tarihi'],
            'required_fields': ['tckn']
        }
        super(HizmetAcikSureGetir, self).handle()

    def custom_filter(self, hitap_dict):
        """
        Hitap sözlüğüne uygulanacak ek filtreleri gerçekleştirir.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """

        for record in hitap_dict:
            husus = record['husus']
            record['husus'], record['husus_aciklama'] = self.husus_aciklama_kontrol(husus)

    def husus_aciklama_kontrol(self, husus):
        """
        Hitap Açık Süre servisinin,
        husus bilgisi tek başına husus kodunu veya
        husus kodu ve açıklamasını veya
        husus kodu ve birkaç tarih bilgisini birlikte içerebilmektedir.

        Bu amaçla husus kodu ve açıklama (mahkeme detayı, tarih bilgileri vs.)
        kısımları ayrı ayrı elde edilmektedir.

        Args:
            husus (str): Açık Süre husus bilgisi.
                Gelen veri 1, 2, 3, 4, 5, 6, 7, 10, 11, 14 değerlerinden biriyse,
                sadece husus kodunu içermektedir. Doğrudan husus kodu olarak elde edilir.
                Gelen veri 8, 9, 12, 13, 15, 16, 17, 18 değerleriyle birlikte
                açıklama (mahkeme detayı, tarih bilgileri vs.) kısmını da içeriyorsa,
                husus kodu ve açıklama olacak şekilde iki parçalı olarak elde edilir.

        Returns:
            (int, str): Husus kodu ve açıklaması.

        Raises:
            IndexError: Husus açıklaması eksik.

        """

        husus = husus.split(' ', 1)
        try:
            husus_kodu = int(husus[0])
        except ValueError:
            self.logger.exception("Husus Kodu tam sayi olmali.")
            return 0, ""

        # only code
        if husus_kodu in [1, 2, 3, 4, 5, 6, 7, 10, 11, 14]:
            return husus_kodu, ""
        # code and explanation
        elif husus_kodu in [8, 9, 12, 13, 15, 16, 17, 18]:
            try:
                aciklama = husus[1]
                return husus_kodu, aciklama
            except IndexError:
                self.logger.exception("Husus aciklamasi yok.")
                return husus_kodu, ""
        else:
            self.logger.info('Husus Kodu gecersiz.')
            return 0, ""
