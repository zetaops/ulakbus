# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_service import HITAPService


class HizmetBorclanmaGetir(HITAPService):
    """
    HITAP HizmetBorclanmaGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetBorclanmaSorgula'
        self.bean_name = 'HizmetBorclanmaServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'ad': 'ad',
                'soyad': 'soyad',
                'emekli_sicil': 'emekliSicil',
                'derece': 'derece',
                'kademe': 'kademe',
                'ekgosterge': 'ekgosterge',
                'baslama_tarihi': 'baslamaTarihi',
                'bitis_tarihi': 'bitisTarihi',
                'gun_sayisi': 'gunSayisi',
                'kanun_kod': 'kanunKod',
                'borc_nevi': 'borcNevi',
                'toplam_tutar': 'toplamTutar',
                'odenen_miktar': 'odenenMiktar',
                'calistigi_kurum': 'calistigiKurum',
                'isyeri_il': 'isyeriIl',
                'isyeri_ilce': 'isyeriIlce',
                'borclanma_tarihi': 'borclanmaTarihi',
                'odeme_tarihi': 'odemeTarihi',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'borclanma_tarihi', 'odeme_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetBorclanmaGetir, self).handle()
