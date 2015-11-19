# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from .personel import Personel
from pyoko import Model, field, ListNode
from .auth import Role
from .auth import Unit


class Okutman(Model):
    personel = Personel()
    harici_okutman_ad = field.String("Harici Okutman Ad", index=True)
    harici_okutman_soyad = field.String("Harici Okutman Soyad", index=True)
    tckn = field.String("Okutmanın TC Kimlik Numarası", index=True)
    dogum_tarihi = field.Date("Okutmanın Doğum Tarihi", index=True)
    dogum_yeri = field.String("Okutmanın Doğum Yeri", index=True)
    uyruk = field.String("Uyruk", index=True)
    medeni_hali = field.String("Medeni Hali", index=True, choices="medeni_hali")
    ikamet_adresi = field.String("İkamet Adresi", index=True)
    telefon_no = field.String("Telefon Numarası", index=True)
    oda_no = field.String("Oda Numarası", index=True)
    oda_tel_no = field.String("Oda Telefon Numarası", index=True)
    e_posta = field.String("E-posta Adresi", index=True)
    web_sitesi = field.String("Web Sitesi", index=True)
    yayinlar = field.String("Yayınlar", index=True)
    projeler = field.String("Projeler", index=True)
    kan_grubu = field.String("Kan Grubu", index=True)
    ehliyet = field.String("Ehliyet", index=True)
    akademik_yayinlari = field.String("Akademik Yayınları", index=True)
    verdigi_dersler = field.String("Verdiği Dersler", index=True)
    unvan = field.String("Unvan", index=True, choices="akademik_unvan")

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Okutman"
        verbose_name_plural = "Okutmanlar"
        search_fields = ['unvan', 'personel']

    def __unicode__(self):
        return '%s %s %s' % (self.personel_ad, self.personel_soyad, self.unvan)


class Donem(Model):
    ad = field.String("Ad", index=True)
    baslangic_tarihi = field.Date("Başlangıç Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    guncel = field.Boolean()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Dönem"
        verbose_name_plural = "Dönemler"
        list_fields = ['ad', 'baslangic_tarihi']
        search_fields = ['ad']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.baslangic_tarihi)


class Program(Model):
    yoksis_id = field.String("YOKSIS ID", index=True)
    bolum = field.String("Bölüm", index=True)
    ucret = field.Integer("Ücret", index=True)
    yil = field.String("Yıl", index=True)
    adi = field.String("Adı", index=True)
    tanim = field.String("Tanım", index=True)
    yeterlilik_kosullari_aciklamasi = field.String("Yeterlilik Koşulları Açıklaması", index=True)
    program_ciktilari = field.String("Program Çıktıları", index=True)
    mezuniyet_kosullari = field.String("Mezuniyet Koşulları", index=True)
    kabul_kosullari = field.String("Kabul Koşulları", index=True)
    bolum_baskani = Role()
    ects_bolum_kordinator = Role()
    akademik_kordinator = Role()
    birim = Unit()

    class Donemler(ListNode):
        donem = Donem()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Program"
        verbose_name_plural = "Programlar"
        list_fields = ['adi', 'yil']
        search_fields = ['adi', 'yil', 'tanim']

    def __unicode__(self):
        return '%s %s' % (self.adi, self.yil)


class Ders(Model):
    ad = field.String("Ad", index=True)
    kod = field.String("Kod", index=True)
    tanim = field.String("Tanım", index=True)
    aciklama = field.String("Açıklama", index=True)
    onkosul = field.String("Önkoşul", index=True)
    uygulama_saati = field.Integer("Uygulama Saati", index=True)
    teori_saati = field.Integer("Teori Saati", index=True)
    ects_kredisi = field.Integer("ECTS Kredisi", index=True)
    yerel_kredisi = field.Integer("Yerel Kredisi", index=True)
    zorunlu = field.Boolean("Zorunlu", index=True)
    ders_dili = field.String("Ders Dili", index=True)
    ders_turu = field.Integer("Ders Türü", index=True, choices="ders_turleri")
    ders_amaci = field.String("Ders Amacı", index=True)
    ogrenme_ciktilari = field.String("Öğrenme Çıktıları", index=True)
    ders_icerigi = field.String("Ders İçeriği", index=True)
    ders_kategorisi = field.Integer("Ders Kategorisi", index=True, choices="ders_kategorileri")
    ders_kaynaklari = field.String("Ders kaynakları", index=True)
    ders_mufredati = field.String("Ders Müfredatı", index=True)
    verilis_bicimi = field.Integer("Veriliş Biçimi", index=True, choices="ders_verilis_bicimleri")
    program = Program()
    donem = Donem()
    ders_koordinatoru = Personel()

    class Degerlendirme(ListNode):
        tur = field.String("Değerlendirme Türü", index=True)
        toplam_puana_etki_yuzdesi = field.Integer("Toplam Puana Etki Yüzdesi", index=True)

    class DersYardimcilari(ListNode):
        ders_yardimcilari = Personel()

    class DersVerenler(ListNode):
        dersi_verenler = Personel()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ders"
        verbose_name_plural = "Dersler"
        list_fields = ['ad', 'kod', 'ders_dili']
        search_fields = ['ad', 'kod']

    def __unicode__(self):
        return '%s %s %s' % (self.ad, self.kod, self.ders_dili)


class Derslik(Model):
    kod = field.String("Kod", index=True)
    # TODO: Bina ve diger fiziki varkliklar map edilecek.
    bina = field.String("Bina", index=True)
    tur = field.Integer("Derslik Türü", index=True, choices="derslik_turleri")
    kapasite = field.String("Kapasite", index=True)

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Derslik"
        verbose_name_plural = "Derslikler"
        list_fields = ['kod', 'bina']
        search_fields = ['bina', 'kod']

    def __unicode__(self):
        return '%s %s' % (self.bina, self.kod)


class Sube(Model):
    ad = field.String("Ad", index=True)
    kontenjan = field.Integer("Kontenjan", index=True)
    dis_kontenjan = field.Integer("Dis Kontenjan", index=True)
    okutman = Okutman()
    ders = Ders()
    donem = Donem()

    class Programlar(ListNode):
        programlar = Program()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Sube"
        verbose_name_plural = "Subeler"
        list_fields = ['ad', 'kontenjan']
        search_fields = ['ad', 'kontenjan']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.kontenjan)


class Sinav(Model):
    tarih = field.Date("Sınav Tarihi", index=True)
    yapilacagi_yer = field.String("Yapılacağı Yer", index=True)
    tur = field.String("Sınav Türü", index=True, choices="sinav_turleri")
    aciklama = field.String("Açıklama", index=True)
    sube = Sube()
    ders = Ders()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Sinav"
        verbose_name_plural = "Sinavlar"
        list_fields = ['tarih', 'yapilacagi_yer']
        search_fields = ['aciklama', 'tarih']

    def __unicode__(self):
        return '%s %s' % (self.tarih, self.yapilacagi_yer)


class DersProgrami(Model):
    gun = field.String("Ders Günü", index=True)
    saat = field.Integer("Ders Saati", index=True)
    sube = Sube()
    derslik = Derslik()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ders Programi"
        verbose_name_plural = "Ders Programlari"
        list_fields = ['gun', 'saat']
        search_fields = ['gun', 'saat']

    def __unicode__(self):
        return '%s %s' % (self.gun, self.saat)


class Ogrenci(Model):
    ad = field.String("Ad", index=True)
    soyad = field.String("Soyad", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    ikamet_adresi = field.String("İkamet Adresi", index=True)
    dogum_tarihi = field.Date("Doğum Tarihi", index=True, format="%d.%m.%Y")
    dogum_yeri = field.String("Doğum Yeri", index=True)
    uyruk = field.String("Uyruk", index=True)
    medeni_hali = field.String("Medeni Hali", index=True)
    ehliyet = field.String("Ehliyet", index=True)
    giris_tarihi = field.Date("Giriş Tarihi", index=True, format="%d.%m.%Y")
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True, format="%d.%m.%Y")
    bolum = field.String("Bölüm", index=True)
    fakulte = field.String("Fakülte", index=True)
    e_posta = field.String("E-Posta", index=True)
    ogrenci_no = field.Integer("Öğrenci Numarası", index=True)
    tel_no = field.Integer("Telefon Numarası", index=True)
    akademik_yil = field.String("Akademik Yıl", index=True)
    aktif_donem = field.String("Dönem", index=True)
    kan_grubu = field.String("Kan Grubu", index=True)
    basari_durumu = field.String("Başarı Durumu", index=True)
    rol = Role(one_to_one=True)
    ders_programi = DersProgrami()
    danisman = Personel()

    class KayitliOluduguProgramlar(ListNode):
        program = Program()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ogrenci"
        verbose_name_plural = "Ogrenciler"
        list_fields = ['ad', 'soyad']
        search_fields = ['ad', 'soyad']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.soyad)


class OgrenciDersi(Model):
    alis_bicimi = field.Integer("Dersi Alış Biçimi", index=True)
    ders = Sube()
    ogrenci = Ogrenci()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ogrenci Dersi"
        verbose_name_plural = "Ogrenci Dersleri"
        list_fields = ['ders', 'alis_bicimi']
        search_fields = ['alis_bicimi', ]

    def __unicode__(self):
        return '%s %s' % (self.ad, self.soyad)


class DersKatilimi(Model):
    katilim_durumu = field.Float("Katılım Durumu", index=True)
    ders = Sube()
    ogrenci = Ogrenci()
    okutman = Okutman()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ders Devamsizligi"
        verbose_name_plural = "Ders Devamsizliklari"
        list_fields = ['katilim_durumu', 'ders']
        search_fields = ['ders', 'katilim_durumu']

    def __unicode__(self):
        return '%s %s' % (self.katilim_durumu, self.ogrenci)


class Borc(Model):
    miktar = field.Float("Borç Miktarı", index=True)
    para_birimi = field.Integer("Para Birimi", index=True, choices="para_birimleri")
    sebep = field.Integer("Borç Sebebi", index=True, choices="ogrenci_borc_sebepleri")
    son_odeme_tarihi = field.Date("Son Ödeme Tarihi", index=True)
    aciklama = field.String("Borç Açıklaması", index=True)
    odeme_sekli = field.Integer("Ödeme Şekli", index=True, choices="odeme_sekli")
    odeme_tarihi = field.Date("Ödeme Tarihi", index=True)
    odenen_miktar = field.String("Ödenen Miktar", index=True)
    ogrenci = Ogrenci()
    donem = Donem()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Borc"
        verbose_name_plural = "Borclar"
        list_fields = ['miktar', 'son_odeme_tarihi']
        search_fields = ['miktar', 'odeme_tarihi']

    def __unicode__(self):
        return '%s %s %s %s' % (self.miktar, self.para_birimi, self.sebep, self.son_odeme_tarihi)


class DegerlendirmeNot(Model):
    puan = field.Integer("Puan", index=True)
    aciklama = field.String("Puan Açıklaması", index=True)
    yil = field.String("Yıl", index=True)
    donem = field.String("Dönem", index=True)
    ogretim_elemani = field.String("Öğretim Elemanı", index=True)
    sinav = Sinav()
    ogrenci = Ogrenci()
    ders = Ders()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Not"
        verbose_name_plural = "Notlar"
        list_fields = ['puan', 'ders']
        search_fields = ['aciklama', 'puan']

    def __unicode__(self):
        return '%s %s' % (self.puan, self.sinav)
