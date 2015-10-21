# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko.model import Model, ListNode, Node
from pyoko import field


class Personel(Model):
    tckn = field.String("TC No", index=True)
    ad = field.String("Adı", index=True)
    soyad = field.String("Soyadı", index=True)
    dogum_tarihi = field.Date("Doğum Tarihi", index=True, format="%d.%m.%Y")
    dogum_yeri = field.String("Doğum Yeri", index=True)
    uyruk = field.String("Uyruk", index=True)
    medeni_hali = field.String("Medeni Hali", index=True)
    ikamet_adresi = field.String("İkamet Adresi", index=True)
    oda_no = field.Integer("Oda Numarası", index=True)
    oda_tel_no = field.String("Oda Telefon Numarası", index=True)
    cep_telefonu = field.String("Cep Telefonu", index=True)
    e_posta = field.String("E-Posta", index=True)
    web_sitesi = field.String("Web Sitesi", index=True)
    yayinlar = field.String("Yayınlar", index=True)
    projeler = field.String("Projeler", index=True)
    kan_grubu = field.String("Kan Grubu", index=True)
    ehliyet = field.String("Ehliyet", index=True)
    verdigi_dersler = field.String("Verdiği Dersler", index=True)
    unvan = field.String("Unvan", index=True)

    class Meta:
        app = 'Personel'
        verbose_name = "Personel"
        verbose_name_plural = "Personeller"
        list_fields = ['ad', 'soyad', 'tckn', 'durum']
        search_fields = ['ad', 'soyad', 'cep_telefonu', 'tckn']

    def durum(self):
        return self.NufusKayitlari.durum

    durum.title = "Durum"

    def __unicode__(self):
        return "%s %s (%s | %s)" % (self.ad, self.soyad, self.tckn,
                                    self.NufusKayitlari.emekli_sicil_no)

    class NufusKayitlari(Node):
        tckn = field.String("Sigortalının TC Kimlik No", index=True)
        ad = field.String("Adi", index=True)
        soyad = field.String("Soyadi", index=True)
        ilk_soy_ad = field.String("Memuriyete Girişteki İlk Soyadı", index=True)
        dogum_tarihi = field.Date("Dogum Tarihi", index=True, format="%d.%m.%Y")
        cinsiyet = field.String("Cinsiyet", index=True)
        emekli_sicil_no = field.Integer("Emekli Sicil No", index=True)
        memuriyet_baslama_tarihi = field.Date("Memuriyete Ilk Baslama Tarihi", index=True,
                                              format="%d.%m.%Y")
        kurum_sicil = field.String("Kurum Sicili", index=True)
        maluliyet_kod = field.String("Malul Kod", index=True)
        yetki_seviyesi = field.String("Yetki Seviyesi", index=True)
        aciklama = field.String("Aciklama", index=True)
        kuruma_baslama_tarihi = field.Date("Kuruma Baslama Tarihi", index=True, format="%d.%m.%Y")
        gorev_tarihi_6495 = field.Date("Emeklilik Sonrası Göreve Başlama Tarihi", index=True,
                                       format="%d.%m.%Y")
        emekli_sicil_6495 = field.Integer("2. Emekli Sicil No", index=True)
        durum = field.Boolean("Durum", index=True)
        sebep = field.Integer("Sebep", index=True)

        class Meta:
            verbose_name = "Nüfus Bilgileri"

    class AdresBilgileri(ListNode):
        ad = field.String("Adres Adı", index=True)
        adres = field.String("Adres", index=True)
        ilce = field.String("İlçe", index=True)
        il = field.String("İl", index=True)

        class Meta:
            verbose_name = "Adres Bilgisi"
            verbose_name_plural = "Adres Bilgileri"
