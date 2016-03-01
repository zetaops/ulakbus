# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Askerlik Ekle

Hitap'a personelin askerlik bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle
from ulakbus.models.hitap import AskerlikKayitlari


class HizmetAskerlikEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Askerlik Bilgisi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''AskerlikKayitlari'' modelinden gelen kayıtların alanları,
                    HizmetAskerlikInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetAskerlikInsert'
        hizmet_acik_sure = AskerlikKayitlari.objects.get(key)
        self.service_dict = {
            'fields': {
                'askerlikNevi': hizmet_askerlik.askerlik_nevi,
                'baslamaTarihi': hizmet_askerlik.baslama_tarihi,
                'bitisTarihi': hizmet_askerlik.bitis_tarihi,
                'kitaBaslamaTarihi': hizmet_askerlik.kita_baslama_tarihi,
                'kitaBitisTarihi': hizmet_askerlik.kita_bitis_tarihi,
                'muafiyetNeden': hizmet_askerlik.muafiyet_neden,
                'sayilmayanGunSayisi': hizmet_askerlik.sayilmayan_gun_sayisi,
                'sinifOkuluSicil': hizmet_askerlik.sinif_okulu_sicil,
                'subayliktanErligeGecisTarihi': hizmet_askerlik.subayliktan_erlige_gecis_tarihi,
                'subayOkuluGirisTarihi': hizmet_askerlik.subay_okulu_giris_tarihi,
                'tckn': hizmet_askerlik.tckn,
                'tegmenNaspTarihi': hizmet_askerlik.tegmen_nasp_tarihi,
                'gorevYeri': hizmet_askerlik.gorev_yeri,
                'kurumOnayTarihi': hizmet_askerlik.kurum_onay_tarihi,
                'astegmenNaspTarihi': hizmet_askerlik.astegmen_nasp_tarihi
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kitaBaslamaTarihi','kitaBitisTarihi',
                            'subayliktanErligeGecisTarihi', 'subayOkuluGirisTarihi',
                            'tegmenNaspTarihi', 'kurumOnayTarihi', 'astegmenNaspTarihi']
        }
        super(HizmetAskerlikEkle, self).handle()