# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko.model import Model, Node
from pyoko import field
from .auth import Unit


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
        maluliyet_kod = field.Integer("Malul Kod", index=True)
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


class AdresBilgileri(Model):
    ad = field.String("Adres Adı", index=True)
    adres = field.String("Adres", index=True)
    ilce = field.String("İlçe", index=True)
    il = field.String("İl", index=True)
    personel = Personel()

    class Meta:
        verbose_name = "Adres Bilgisi"
        verbose_name_plural = "Adres Bilgileri"


class KurumIciGorevlendirmeBilgileri(Model):
    gorev_tipi = field.String("Görev Tipi", index=True)
    kurum_ici_gorev_baslama_tarihi = field.Date("Baslama Tarihi", index=True, format="%d.%m.%Y")
    kurum_ici_gorev_bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    birim = Unit()
    aciklama = field.String("Aciklama")
    resmi_yazi_sayi = field.String("Resmi Yazi Sayi")
    resmi_yazi_tarih = field.Date("Resmi Yazi Tarihi", index=True, format="%d.%m.%Y")
    personel = Personel()

    class Meta:
        verbose_name = "Kurum Ici Gorevlendirme"
        verbose_name_plural = "Kurum Ici Gorevlendirmeler"
        form_grouping = [
            {
                "group_title": "Gorev",
                "items": ["gorev_tipi", "kurum_ici_gorev_baslama_tarihi", "kurum_ici_gorev_bitis_tarihi", "birim",
                          "aciklama"],
                "layout": "4",
                "collapse": False
            },
            {
                "group_title": "Resmi Yazi",
                "items": ["resmi_yazi_sayi", "resmi_yazi_tarih"],
                "layout": "2",
                "collapse": False
            }
        ]


class KurumDisiGorevlendirmeBilgileri(Model):
    gorev_tipi = field.Integer("Görev Tipi", index=True)
    kurum_disi_gorev_baslama_tarihi = field.Date("Baslama Tarihi", index=True, format="%d.%m.%Y")
    kurum_disi_gorev_bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    aciklama = field.Text("Aciklama")
    resmi_yazi_sayi = field.String("Resmi Yazi Sayi")
    resmi_yazi_tarih = field.Date("Resmi Yazi Tarihi", index=True, format="%d.%m.%Y")
    maas = field.Boolean("Maas")
    yevmiye = field.Boolean("Yevmiye", default=False)
    yolluk = field.Boolean("Yolluk", default=False)
    ulke = field.Integer("Ulke", default="90")
    personel = Personel()

    class Meta:
        verbose_name = "Kurum Disi Gorevlendirme"
        verbose_name_plural = "Kurum Disi Gorevlendirmeler"
        form_grouping = [
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": "Gorev",
                        "items": ["gorev_tipi", "kurum_disi_gorev_baslama_tarihi", "kurum_disi_gorev_bitis_tarihi",
                                  "ulke",
                                  "aciklama"],
                        "collapse": False
                    }
                ]

            },
            {
                "layout": "2",
                "groups": [
                    {
                        "group_title": "Resmi Yazi",
                        "items": ["resmi_yazi_sayi", "resmi_yazi_tarih"],
                        "collapse": False
                    },
                    {
                        "items": ["maas", "yevmiye", "yolluk"],
                        "collapse": False
                    }
                ]

            },
        ]
