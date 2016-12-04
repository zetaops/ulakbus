# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Askerlik Ekle

Hitap'a personelin askerlik bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetAskerlikEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Askerlik Bilgisi Ekleme servisi

    """

    @staticmethod
    def get_name():
        # Zato service ismi
        return "hizmet_askerlik_ekle"

    DEPLOY = True
    CONNECTION = "channel"
    DATA_FORMAT = "json"
    CHANNEL_NAME = "hizmet.askerlik.ekle.channel"
    URL_PATH = '/personel/hitap/hizmet-askerlik-ekle'
    TRANSPORT = "plain_http"
    IS_ACTIVE = True
    IS_INTERNAL = False

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetAskerlikInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve gerekli alanlar listede tutulmaktadır.
        """

        self.service_dict = {
            'fields': {
                'askerlikNevi': self.request.payload.get('askerlik_nevi', ''),
                'baslamaTarihi': self.request.payload.get('baslama_tarihi', ''),
                'bitisTarihi': self.request.payload.get('bitis_tarihi', ''),
                'kitaBaslamaTarihi': self.request.payload.get('kita_baslama_tarihi', ''),
                'kitaBitisTarihi': self.request.payload.get('kita_bitis_tarihi', ''),
                'muafiyetNeden': self.request.payload.get('muafiyet_neden', ''),
                'sayilmayanGunSayisi': self.request.payload.get('sayilmayan_gun_sayisi', ''),
                'sinifOkuluSicil': self.request.payload.get('sinif_okulu_sicil', ''),
                'subayliktanErligeGecisTarihi': self.request.payload.get(
                    'subayliktan_erlige_gecis_tarihi', ''),
                'subayOkuluGirisTarihi': self.request.payload.get('subay_okulu_giris_tarihi', ''),
                'tckn': self.request.payload.get('tckn', ''),
                'tegmenNaspTarihi': self.request.payload.get('tegmen_nasp_tarihi', ''),
                'gorevYeri': self.request.payload.get('gorev_yeri', ''),
                'kurumOnayTarihi': self.request.payload.get('kurum_onay_tarihi', ''),
                'astegmenNaspTarihi': self.request.payload.get('astegmen_nasp_tarihi', '')
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kitaBaslamaTarihi', 'kitaBitisTarihi',
                            'subayliktanErligeGecisTarihi', 'subayOkuluGirisTarihi',
                            'tegmenNaspTarihi', 'kurumOnayTarihi', 'astegmenNaspTarihi'],
            'required_fields': ['tckn', 'askerlikNevi', 'kurumOnayTarihi']
        }
        super(HizmetAskerlikEkle, self).handle()
