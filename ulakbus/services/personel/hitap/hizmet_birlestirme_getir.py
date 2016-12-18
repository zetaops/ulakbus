# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Birleştirme Sorgula

Hitap üzerinden personelin hizmet birleştirme bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetBirlestirmeGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış
    Hizmet Birleştirme Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            bean_name (str): Hitap'tan gelen bean nesnesinin adı
            service_dict (dict): Hitap servisinden gelen kayıtların alanları,
                    ``HizmetBirlestirme`` modelinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.

        """

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
            'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kurum_onay_tarihi'],
            'required_fields': ['tckn']
        }
        super(HizmetBirlestirmeGetir, self).handle()

    def custom_filter(self, hitap_dict):
        """
        Hitap sözlüğüne uygulanacak ek filtreleri gerçekleştirir.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """

        for record in hitap_dict:
            record['kidem_tazminat_odeme_durumu'] = \
                self.kidem_durum_kontrol(record['kidem_tazminat_odeme_durumu'])
            record['kha_durum'] = self.kha_durum_kontrol(record['kha_durum'])

    def kidem_durum_kontrol(self, kidem_durum):
        """
        Hitap Hizmet Birleştirme servisinin,
        "0" veya "1" olarak gelen Kıdem Tazminatı Ödeme Durumu değeri,
        tam sayı olarak elde edilmektedir.

        - "0": "HAYIR"
        - "1": "EVET"
        - "": "BELİRLENEMEDİ"

        Args:
            kidem_durum (str): Hizmet Birleştirme Kıdem Tazminatı Ödeme Durumu değeri.

        Returns:
            int: Kıdem Tazminatı Ödeme Durumu tam sayı değeri.

        Raises:
            ValueError: Geçersiz Kıdem Tazminatı Ödeme Durumu kodu.
                Varsayılan olarak 2 değeri verilmektedir.

        """

        try:
            return int(kidem_durum)
        except ValueError:
            return 2

    def kha_durum_kontrol(self, kha_durum):
        """
        Hitap Hizmet Birleştirme servisinin,
        "0", "1", "2", "3", "4", "5" olarak gelen Kazanılmış Hak Aylığı
        durum bilgisi değerleri, tam sayı olarak elde edilmektedir.

        - "0": "Değerlendirilmedi"
        - "1": "Prim gün sayısının 2/3 oranında değerlendirildi"
        - "2": "Prim gün sayısının 3/4 oranında değerlendirildi"
        - "3": "Prim gün sayısının 4/4 oranında değerlendirildi"
        - "4": "Belirlenemedi"
        - "5": "İki tarih arasının tamamı değerlendirildi"

        Args:
            kha_durum (str): Hizmet Birleştirme KHA durum değeri.

        Returns:
            int: KHA durum tam sayı değeri.

        Raises:
            ValueError: Geçersiz KHA durum kodu.

        """

        try:
            return int(kha_durum)
        except ValueError:
            self.logger.exception("KHA Durum kodu gecersiz: %s" % kha_durum)
            return 0
