# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model,  field
from .auth import Unit, User

PERSONEL_TURU = [
    (1, 'Akademik'),
    (2, 'İdari')
]


class Personel(Model):
    tckn = field.String("TC No", index=True)
    ad = field.String("Adı", index=True)
    soyad = field.String("Soyadı", index=True)
    cinsiyet = field.Integer("Cinsiyet", index=True, choices='cinsiyet')
    uyruk = field.String("Uyruk", index=True)
    ikamet_adresi = field.String("İkamet Adresi", index=True)
    ikamet_il = field.String("İkamet Il", index=True)
    ikamet_ilce = field.String("İkamet Ilce", index=True)
    adres_2 = field.String("Adres 2", index=True)
    adres_2_posta_kodu = field.String("Adres 2 Posta Kodu", index=True)
    oda_no = field.String("Oda Numarası", index=True)
    oda_tel_no = field.String("Oda Telefon Numarası", index=True)
    cep_telefonu = field.String("Cep Telefonu", index=True)
    e_posta = field.String("E-Posta", index=True)
    e_posta_2 = field.String("E-Posta 2", index=True)
    e_posta_3 = field.String("E-Posta 3", index=True)
    web_sitesi = field.String("Web Sitesi", index=True)
    yayinlar = field.String("Yayınlar", index=True)
    projeler = field.String("Projeler", index=True)
    kan_grubu = field.String("Kan Grubu", index=True)
    ehliyet = field.String("Ehliyet", index=True)
    verdigi_dersler = field.String("Verdiği Dersler", index=True)
    unvan = field.Integer("Unvan", index=True, choices="akademik_unvan")
    biyografi = field.Text("Biyografi")
    notlar = field.Text("Notlar")
    engelli_durumu = field.String("Engellilik", index=True)
    engel_grubu = field.String("Engel Grubu", index=True)
    engel_derecesi = field.String("Engel Derecesi")
    engel_orani = field.Integer("Engellilik Orani")
    personel_turu = field.Integer("Personel Türü", choices=PERSONEL_TURU, index=True)
    cuzdan_seri = field.String("Seri", index=True)
    cuzdan_seri_no = field.String("Seri No", index=True)
    baba_adi = field.String("Ana Adi", index=True)
    ana_adi = field.String("Baba Adi", index=True)
    dogum_tarihi = field.Date("Doğum Tarihi", index=True, format="%d.%m.%Y")
    dogum_yeri = field.String("Doğum Yeri", index=True)
    medeni_hali = field.Integer("Medeni Hali", index=True, choices="medeni_hali")
    kayitli_oldugu_il = field.String("Il", index=True)
    kayitli_oldugu_ilce = field.String("Ilce", index=True)
    kayitli_oldugu_mahalle_koy = field.String("Mahalle/Koy")
    kayitli_oldugu_cilt_no = field.String("Cilt No")
    kayitli_oldugu_aile_sira_no = field.String("Aile Sira No")
    kayitli_oldugu_sira_no = field.String("Sira No")
    kimlik_cuzdani_verildigi_yer = field.String("Cuzdanin Verildigi Yer")
    kimlik_cuzdani_verilis_nedeni = field.String("Cuzdanin Verilis Nedeni")
    kimlik_cuzdani_kayit_no = field.String("Cuzdan Kayit No")
    kimlik_cuzdani_verilis_tarihi = field.String("Cuzdan Kayit Tarihi")
    birim = Unit("Birim")
    hizmet_sinifi = field.Integer("Hizmet Sınıfı", index=True, choices="hizmet_sinifi")
    user = User(one_to_one=True)

    class Meta:
        app = 'Personel'
        verbose_name = "Personel"
        verbose_name_plural = "Personeller"
        list_fields = ['ad', 'soyad', 'tckn', 'durum']
        search_fields = ['ad', 'soyad', 'cep_telefonu', 'tckn']

    def durum(self):
        return self.nufus_kayitlari.durum if self.nufus_kayitlari.key else None

    durum.title = "Durum"

    def kadro(self):
        atama = Atama.objects.get(personel=self)
        return atama.kadro

    def __unicode__(self):
        return "%s %s" % (self.ad, self.soyad)


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
    gorev_tipi = field.String("Görev Tipi", index=True, choices="gorev_tipi")
    kurum_ici_gorev_baslama_tarihi = field.Date("Baslama Tarihi", index=True, format="%d.%m.%Y")
    kurum_ici_gorev_bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    birim = Unit()
    aciklama = field.String("Aciklama")
    resmi_yazi_sayi = field.String("Resmi Yazi Sayi")
    resmi_yazi_tarih = field.Date("Resmi Yazi Tarihi", index=True, format="%d.%m.%Y")
    personel = Personel()

    def __unicode__(self):
        return "%s %s" % (self.gorev_tipi, self.aciklama)

    class Meta:
        verbose_name = "Kurum İçi Görevlendirme"
        verbose_name_plural = "Kurum İçi Görevlendirmeler"
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
    aciklama = field.Text("Aciklama", index=True)
    resmi_yazi_sayi = field.String("Resmi Yazi Sayi")
    resmi_yazi_tarih = field.Date("Resmi Yazi Tarihi", index=True, format="%d.%m.%Y")
    maas = field.Boolean("Maas")
    yevmiye = field.Boolean("Yevmiye", default=False)
    yolluk = field.Boolean("Yolluk", default=False)
    ulke = field.Integer("Ulke", default="90", choices="ulke", index=True)
    personel = Personel()

    def __unicode__(self):
        return "%s %s %s" % (self.gorev_tipi, self.aciklama, self.ulke)

    class Meta:
        verbose_name = "Kurum Disi Gorevlendirme"
        verbose_name_plural = "Kurum Disi Gorevlendirmeler"
        list_search = ["aciklama"]
        list_fields = ["ulke", "gorev_tipi", "kurum_disi_gorev_baslama_tarihi"]
        list_filters = ["ulke", "gorev_tipi", "kurum_disi_gorev_baslama_tarihi"]
        search_fields = ["aciklama", ]
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


class Kadro(Model):
    kadro_no = field.Integer("Kadro No", required=False)
    unvan = field.Integer("Akademik Unvan", index=True, choices="akademik_unvan", required=False)
    derece = field.Integer("Derece", index=True, required=False)
    durum = field.Integer("Durum", index=True, choices="kadro_durumlari", required=False)
    birim = Unit("Birim", required=False)
    aciklama = field.String("Açıklama", index=True, required=False)
    unvan_kod = field.Integer("Unvan", index=True, choices="unvan_kod", required=False)

    class Meta:
        app = 'Personel'
        verbose_name = "Kadro"
        verbose_name_plural = "Kadrolar"
        list_fields = ['durum', 'unvan', 'aciklama']
        search_fields = ['unvan', 'derece']
        list_filters = ['durum']

    def __unicode__(self):
        return "%s %s %s" % (self.unvan, self.derece, self.durum)


# class Atama(Model):
#     personel = Personel("Personel")
#     kadro = Kadro("Kadro")
#     notlar = field.String("Aciklama", index=True)
#
#     class Meta:
#         verbose_name = "Atama"
#         verbose_name_plural = "Atamalar"
#
#     def __unicode__(self):
#         return "%s %s" % (self.personel, self.kadro)

class Izin(Model):
    tip = field.Integer("Tip", index=True, choices="izin")
    baslangic = field.Date("Başlangıç", index=True, format="%d.%m.%Y")
    bitis = field.Date("Bitiş", index=True, format="%d.%m.%Y")
    onay = field.Date("Onay", index=True, format="%d.%m.%Y")
    adres = field.String("Geçireği Adres", index=True)
    telefon = field.String("Telefon", index=True)
    personel = Personel()
    vekil = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "İzin"
        verbose_name_plural = "İzinler"
        list_fields = ['tip', 'baslangic', 'bitis', 'onay', 'telefon']
        search_fields = ['tip', 'baslangic', 'onay']

    def __unicode__(self):
        return '%s %s' % (self.tip, self.onay)


class UcretsizIzin(Model):
    tip = field.Integer("Tip", index=True, choices="ucretsiz_izin")
    baslangic_tarihi = field.Date("İzin Başlangıç Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("İzin Bitiş Tarihi", index=True, format="%d.%m.%Y")
    donus_tarihi = field.Date("Dönüş Tarihi", index=True, format="%d.%m.%Y")
    donus_tip = field.Integer("Dönüş Tip", index=True)
    onay_tarihi = field.Date("Onay Tarihi", index=True, format="%d.%m.%Y")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Ücretsiz İzin"
        verbose_name_plural = "Ücretsiz İzinler"
        list_fields = ['tip', 'baslangic_tarihi', 'bitis_tarihi', 'donus_tarihi']
        search_fields = ['tip', 'onay_tarihi']

    def __unicode__(self):
        return '%s %s' % (self.tip, self.onay_tarihi)


class Atama(Model):
    kurum_sicil_no = field.String("Kurum Sicil No", index=True)
    personel_tip = field.Integer("Personel Tipi", index=True)
    hizmet_sinif = field.Integer("Hizmet Sınıfı", index=True, choices="hizmet_sinifi")
    statu = field.Integer("Statü", index=True)
    gorev_suresi_baslama = field.Date("Görev Süresi Başlama", index=True, format="%d.%m.%Y")
    gorev_suresi_bitis = field.Date("Görev Süresi Bitiş", index=True, format="%d.%m.%Y")
    goreve_baslama_tarihi = field.Date("Göreve Başlama Tarihi", index=True, format="%d.%m.%Y")
    ibraz_tarihi = field.Date("İbraz Tarihi", index=True, format="%d.%m.%Y")
    durum = field.Integer("Durum", index=True)
    mecburi_hizmet_suresi = field.Date("Mecburi Hizmet Süresi", index=True, format="%d.%m.%Y")
    nereden = field.Integer("Nereden", index=True)
    atama_aciklama = field.String("Atama Açıklama", index=True)
    goreve_baslama_aciklama = field.String("Göreve Başlama Açıklama", index=True)
    kadro_unvan = field.Integer("Kadro Unvan", index=True)
    kadro_derece = field.Integer("Kadro Derece", index=True)
    kadro = Kadro()
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Atama"
        verbose_name_plural = "Atamalar"
        list_fields = ['personel_tip', 'hizmet_sinif', 'gorev_suresi_baslama', 'ibraz_tarihi', 'durum']
        search_fields = ['personel_tip', 'hizmet_sinif', 'statu']

    def __unicode__(self):
        return '%s %s %s' % (self.kurum_sicil_no, self.gorev_suresi_baslama, self.ibraz_tarihi)
