# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetBirlestirmeGetir(HITAPSorgula):
    """
    HITAP HizmetBirlestirmeGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetBirlestirmeSorgula'
        self.bean_name = 'HizmetBirlestirmeServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'sgk_nevi': 'sgkNevi',
                'sgk_sicil_no': 'sgkSicilNo',
                'baslama_tarihi': 'baslamaTarihi',
                'bitis_tarihi': 'bitisTarihi',
                'sure': 'sure',
                'kamu_isyeri_ad': 'kamuIsyeriAd',
                'ozel_isyeri_ad': 'ozelIsyeriAd',
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
        """
        Sozluge (hitap_dict) uygulanacak ek filtrelerin gerceklestirimi

        :param hitap_dict: HITAP verisini modeldeki alanlara uygun bicimde tutan sozluk
        :type hitap_dict: List[dict]
        """

        for record in hitap_dict:
            record['kidem_tazminat_odeme_durumu'] = self.kidem_durum_kontrol(record['kidem_tazminat_odeme_durumu'])
            record['kha_durum'] = self.kha_durum_kontrol(record['kha_durum'])

    def kidem_durum_kontrol(self, kidem_durum):
        """
        Kıdem Tazminat ödeme durumu hitap servisinden aşağıdaki gibi gelmektedir.
        0: HAYIR
        1: EVET
        “”(BOŞ KARAKTER): BELİRLENEMEDİ

        Ulakbus kaydederken BELİRLENEMEDİ = 2 yapılacaktır

        :param kidem_durum: hitaptan donen kıdem durumu
        :type kidem_durum: str

        :return int: kıdem durumu
        """

        try:
            return int(kidem_durum)
        except ValueError:
            return 2

    def kha_durum_kontrol(self, kha_durum):
        """
        KHA Durum hitap servisinden aşağıdaki gibi gelmektedir.

        0: Değerlendirilmedi
        1: Prim gün sayısının 2/3 oranında değerlendirildi
        2: Prim gün sayısının 3/4 oranında değerlendirildi
        3: Prim gün sayısının 4/4 oranında değerlendirildi
        4: Belirlenemedi
        5: İki tarih arasının tamamı değerlendirildi

        :param kha_durum: hitaptan donen kha durum
        :type kha_durum: str

        :return int: kha durum
        """

        try:
            return int(kha_durum)
        except ValueError:
            self.logger.info("KHA Durum kodu gecersiz: %s" % kha_durum)
            return 0
