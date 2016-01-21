# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP İstisnai İlgi Sorgula

Hitap üzerinden personelin istisnai ilgi bilgilerinin sorgulamasını yapar.

Note:
    Bu servis, service ve bean isimlerindeki hatadan dolayı çalışmamaktadır.
    Açıklama için ilgili birimlere basvuruldu, yanıt bekleniyor.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetIstisnaiIlgiGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış İstisnai İlgi Bilgisi Sorgulama servisi

    """

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            bean_name (str): Hitap'tan gelen bean nesnesinin adı
            service_dict (dict): Hitap servisinden gelen kayıtların alanları,
                    ``HizmetIstisnaiIlgi`` modelinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.

        """

        self.service_name = 'hizmetIstisnaiIlgiSorgu'
        self.bean_name = 'HizmetIstisnaiIlgiServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'baslama_tarihi': 'baslamaTarihi',
                'bitis_tarihi': 'bitisTarihi',
                'gun_sayisi': 'gunSayisi',
                'istisnai_ilgi_nevi': 'istisnaiIlgiNevi',
                'kha_durum': 'khaDurum',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetIstisnaiIlgiGetir, self).handle()

    def custom_filter(self, hitap_dict):
        """
        Sozluge (hitap_dict) uygulanacak ek filtrelerin gerceklestirimi

        :param hitap_dict: HITAP verisini modeldeki alanlara uygun bicimde tutan sozluk
        :type hitap_dict: List[dict]
        """

        for record in hitap_dict:
            record['kha_durum'] = self.kha_durum_kontrol(record['kha_durum'])

    def kha_durum_kontrol(self, kha_durum):
        """
        KHA Durum hitap servisinden aşağıdaki gibi gelmektedir.

        "0" : "Değerlendirilmedi"
        "1" : "Değerlendirildi"

        :param kha_durum: hitaptan donen kha durum
        :type kha_durum: str
        :return int: kha durum
        """

        try:
            return int(kha_durum)
        except ValueError:
            self.logger.info("KHA Durum kodu gecersiz: %s" % kha_durum)
            return 0
