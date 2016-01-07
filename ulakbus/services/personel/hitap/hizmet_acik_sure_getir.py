# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_service import HITAPService


class HizmetAcikSureGetir(HITAPService):
    """
    HITAP HizmetAcikSureGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetAcikSureSorgula'
        self.bean_name = 'HizmetAcikSureServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'acik_sekil': 'acikSekil',
                'durum': 'durum',
                'hizmet_durum': 'hizmetDurum',
                'husus': 'Husus',
                'aciga_alinma_tarih': 'acigaAlinmaTarih',
                'goreve_son_tarih': 'goreveSonTarih',
                'goreve_iade_istem_tarih': 'goreveIadeIstemTarih',
                'goreve_iade_tarih': 'goreveIadeTarih',
                'acik_aylik_bas_tarih': 'acikAylikBasTarih',
                'acik_aylik_bit_tarih': 'acikAylikBitTarih',
                'goreve_son_aylik_bas_tarih': 'goreveSonAylikBasTarih',
                'goreve_son_aylik_bit_tarih': 'goreveSonAylikBitTarih',
                's_yonetim_kald_tarih': 'sYonetimKaldTarih',
                'aciktan_atanma_tarih': 'aciktanAtanmaTarih',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['aciga_alinma_tarih', 'goreve_son_tarih', 'goreve_iade_istem_tarih',
                           'goreve_iade_tarih', 'acik_aylik_bas_tarih', 'acik_aylik_bit_tarih',
                           'goreve_son_aylik_bas_tarih', 'goreve_son_aylik_bit_tarih',
                           's_yonetim_kald_tarih', 'aciktan_atanma_tarih', 'kurum_onay_tarihi'],
        }
        super(HizmetAcikSureGetir, self).handle()

    def custom_filter(self, hitap_dict):
        for record in hitap_dict:
            husus = record['husus']
            record['husus'], record['husus_aciklama'] = self.husus_aciklama_kontrol(husus)

    def husus_aciklama_kontrol(self, husus):
        """
        Acik Sure HITAP servisinin husus alaninin, husus kodu ve
        husus aciklamasi (tarih, mahkeme detayi vb.) seklinde elde edilmesi.

        :param husus: hitaptan donen husus bilgisi
        :type husus: str
        :return tuple: husus kodu (int) ve aciklamasi (string)
        """

        husus = husus.split(' ', 1)
        try:
            husus_kodu = int(husus[0])
        except ValueError:
            self.logger.info("Husus Kodu tam sayi olmali.")
            return 0, ""

        # sadece husus kodu icerenler
        if husus_kodu in [1, 2, 3, 4, 5, 6, 7, 10, 11, 14]:
            return husus_kodu, ""
        # husus kodu ve aciklamasini icerenler
        elif husus_kodu in [8, 9, 12, 13, 15, 16, 17, 18]:
            try:
                aciklama = husus[1]
                return husus_kodu, aciklama
            except IndexError:
                self.logger.info("Husus aciklamasi yok.")
                return husus_kodu, ""
        else:
            self.logger.info('Husus Kodu gecersiz.')
            return 0, ""
