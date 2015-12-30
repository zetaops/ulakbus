# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_service import HITAPService


class HizmetMahkemeGetir(HITAPService):
    """
    HITAP HizmetMahkemeGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetMahkemeSorgula'
        self.bean_name = 'HizmetMahkemeServisBean'
        self.service_dict = {
            'fields': {
                'kayit_no': 'kayitNo',
                'mahkeme_ad': 'mahkemeAd',
                'sebep': 'sebep',  # TODO: (bkz:Açıklamalar-9.madde)
                'karar_tarihi': 'kararTarihi',
                'karar_sayisi': 'kararSayisi',
                'kesinlesme_tarihi': 'kesinlesmeTarihi',
                'asil_dogum_tarihi': 'asilDogumTarihi',
                'tashih_dogum_tarihi': 'tashihDogumTarihi',
                'asil_ad': 'asilAd',
                'tashih_ad': 'tashihAd',
                'asil_soyad': 'asilSoyad',
                'tashih_soyad': 'tashihSoyad',
                'gecerli_dogum_tarihi': 'gecerliDogumTarihi',
                'aciklama': 'aciklama',
                'gun_sayisi': 'gunSayisi',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['karar_tarihi', 'kesinlesme_tarihi', 'asil_dogum_tarihi',
                           'tashih_dogum_tarihi', 'gecerli_dogum_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetMahkemeGetir, self).handle()
