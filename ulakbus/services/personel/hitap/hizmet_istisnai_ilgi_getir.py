# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP İstisnai İlgi Sorgula

Hitap üzerinden personelin istisnai ilgi bilgilerinin sorgulamasını yapar.

Note:
    Bu servis, service ve bean isimlerindeki hatadan dolayı çalışmamaktadır.
    Açıklama için ilgili birimlere başvuruldu, yanıt bekleniyor.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetIstisnaiIlgiGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış
    İstisnai İlgi Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'hizmetIstisnaiIlgiSorgu',
        'bean_name': 'HizmetIstisnaiIlgiServisBean',
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
        'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kurum_onay_tarihi'],
        'required_fields': ['tckn']
    }

    def custom_filter(self, hitap_dict):
        """
        Hitap sözlüğüne uygulanacak ek filtreleri gerçekleştirir.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """

        for record in hitap_dict:
            record['kha_durum'] = self.kha_durum_kontrol(record['kha_durum'])

    def kha_durum_kontrol(self, kha_durum):
        """
        Hitap İstisnai İlgi servisinin,
        "0" veya "1" olarak gelen Kazanılmış Hak Aylığı durum bilgisi değeri,
        tam sayı olarak elde edilmektedir.

        - "0" : "Değerlendirilmedi"
        - "1" : "Değerlendirildi"

        Args:
            kha_durum (str): İstisnai İlgi KHA durum değeri.

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
