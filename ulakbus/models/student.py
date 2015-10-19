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
    tip = field.String("Tip", index=True)

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Okutman"
        verbose_name_plural = "Okutmanlar"
        search_fields = ['tip', 'personel']

    def __unicode__(self):
        return '%s %s %s' % (self.personel.ad, self.personel.soyad, self.tip)


class Program(Model):
    birim = Unit()
    ucret = field.Integer("Ücret", index=True)
    yil = field.String("Yıl", index=True)
    donem = field.Integer("Dönem", index=True)
    adi = field.String("Adı", index=True)
    tanim = field.String("Tanım", index=True)
    yeterlilik_kosullari_aciklamasi = field.String("Yeterlilik Koşulları Açıklaması", index=True)
    program_ciktilari = field.String("Program Çıktıları", index=True)
    mezuniyet_kosullari = field.String("Mezuniyet Koşulları", index=True)
    kabul_kosullari = field.String("Kabul Koşulları", index=True)
    bolum_baskani = Role()
    ects_bolum_kordinator = Role()
    akademik_kordinator = Role()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Program"
        verbose_name_plural = "Programlar"
        list_fields = ['adi', 'yil']
        search_fields = ['adi', 'yil', 'tanim']

    def __unicode__(self):
        return '%s %s' % (self.adi, self.yil)


class Donem(Model):
    baslangic_tarihi = field.Date("Başlangıç Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    ad = field.String("Ad", index=True)
    ucret = field.Integer("Ücret", index=True)
    program = Program()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Dönem"
        verbose_name_plural = "Dönemler"
        list_fields = ['ad', 'baslangic_tarihi']
        search_fields = ['ad']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.baslangic_tarihi)


class Ders(Model):
    ad = field.String("Ad", index=True)
    kod = field.String("Kod", index=True)
    kredi = field.String("Kredi", index=True)
    zorunlu = field.Boolean("Zorunlu", index=True)
    akts_teori = field.Float("AKTS Teori", index=True)
    akts_uygulama = field.Float("AKTS Uygulama", index=True)
    donem = Donem()
    ders_dili = field.String("Ders Dili", index=True)
    verilis_bicimi = field.Integer("Veriliş Biçimi", index=True)
    program = Program()

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
    kod = field.String("Kod", index=True)
    okutman = Okutman()
    ders = Ders()
    saat = field.Integer("Saat", index=True)
    gun = field.String("Gün", index=True)
    kredi = field.Integer("Kredi", index=True)
    donem = field.String("Dönem", index=True)
    kontenjan = field.Integer("Kontenjan", index=True)

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Sube"
        verbose_name_plural = "Subeler"
        list_fields = ['ad', 'kod']
        search_fields = ['ad', 'kod']

    def __unicode__(self):
        return '%s %s %s' % (self.kod, self.ders.ad, self.ders.donem)


class Ogrenci(Model):
    ad = field.String("Ad", index=True)
    soyad = field.String("Soyad", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    ikamet_adresi = field.String("İkamet Adresi", index=True)
    dogum_tarihi = field.Date("Doğum Tarihi", index=True, format="%d.%m.%Y")
    dogum_yeri = field.String("Doğum Yeri", index=True)
    uyruk = field.String("Uyruk", index=True)
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
    rol = Role()

    class Dersler(ListNode):
        saat = field.String("Saat", index=True)
        gun = field.String("Gün", index=True)
        kontenjan = field.Integer("Kontenjan", index=True)
        on_kosul = field.Boolean("Ön Koşul", index=True)
        gecme_notu = field.Integer("Geçme Notu", index=True)
        akademik_yil = field.String("Akademik Yıl", index=True)
        ders = Sube()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ogrenci"
        verbose_name_plural = "Ogrenci"
        list_fields = ['ad', 'soyad']
        search_fields = ['ad', 'soyad']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.soyad)


class DegerlendirmeTipi(Model):
    ad = field.String("Sinav Turu", index=True)

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Degerlendirme Tipi"
        verbose_name_plural = "Degerlendirme Tipleri"
        list_fields = ['ad']
        search_fields = ['ad']

    def __unicode__(self):
        return "%s" % self.ad


class Degerlendirme(Model):
    ders = Ders()
    tur = DegerlendirmeTipi()
    tarih = field.Date("Tarih", index=True, format="%d.%m.%Y")
    puan = field.Integer("Puan", index=True)

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Degerlendirme"
        verbose_name_plural = "Degerlendirmeler"

    def __unicode__(self):
        return '%s %s' % (self.ders.ad, self.tur.ad)


class DersDevamsizligi(Model):
    katilim_durumu = field.Float("Katılım Durumu", index=True)
    ders = Sube()
    ogrenci = Ogrenci()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ders Devamsizligi"
        verbose_name_plural = "Ders Devamsizliklari"

    def __unicode__(self):
        return '%s %s' % (self.katilim_durumu, self.ders.ad)


class Borc(Model):
    miktar = field.Float("Miktar", index=True)
    tur = field.Integer("Tür", index=True)
    ogrenci = Ogrenci()
    donem = Donem()
    son_odeme_tarihi = field.Date("Son Ödeme Tarihi", index=True, format="%d.%m.%Y")
    odeme_tarihi = field.Date("Ödeme Tarihi", index=True, format="%d.%m.%Y")

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Borc"
        verbose_name_plural = "Borclar"

    def __unicode__(self):
        return '%s %s %s %s' % (self.ogrenci.ad, self.ogrenci.soyad, self.donem.ad, self.miktar)


class Not(Model):
    degerlendirme = Degerlendirme()
    ogrenci = Ogrenci()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Not"
        verbose_name_plural = "Notlar"

    def __unicode__(self):
        return '%s %s' % (self.degerlendirme.ders.ad, self.ogrenci.ad)
