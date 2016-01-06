## -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_service import HITAPService


class HizmetBirlestirmeGetir(HITAPService):
    """
    HITAP HizmetBirlestirmeGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetBirlestirmeSorgula'
        self.bean_name = 'HizmetBirlestirmeServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'Tckn',
                'kayit_no': 'kayitNo',
                'sgk_nevi': 'sgkNevi',
                'sgk_sicil_no': 'sgkSicilNo',
                'baslama_tarihi': 'baslamaTarihi',
                'bitis_tarihi': 'bitisTarihi',
                'sure': 'sure',
                'kamu_isyeri_ad': 'kamuIsyeriAd',
                'ozel_isyeri_ad': 'ozelIsyeriAdl',
                'bag_kur_meslek': 'bagKurMeslek',
                'ulke_kod': 'ulkeKod',
                'banka_sandik_kod': 'bankaSandikKod',
                'kidem_tazminat_odeme_durumu': 'kidemTazminatOdemeDurumu',
                'ayrilma_nedeni': 'ayrilmaNedeni',
                'kha_durum': 'khaDurum',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetBirlestirmeGetir, self).handle()

    def custom_filter(self, hitap_dict):
        for record in hitap_dict:
            record['kidem_tazminat_odeme_durumu'] = self.kidem_durum_kontrol(record['kidem_tazminat_odeme_durumu'])

    def kidem_durum_kontrol(self, kidem_durum):
        """
        Kıdem Tazminat ödeme durumu hitap servisinden aşağıdaki gibi gelmektedir.
        0: HAYIR
        1: EVET
        “”(BOŞ KARAKTER): BELİRLENEMEDİ

        Ulakbus kaydederken BELİRLENEMEDİ = 2 yapılacaktır

        :param hs: hitaptan donen kıdem durumu
        :type hs: str
        :return int: kıdem durumu
        """

        try:
            return int(kidem_durum)
        except ValueError:
            return 2
