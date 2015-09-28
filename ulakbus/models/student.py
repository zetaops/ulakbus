# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from personel import Personel
from pyoko import Model, field
from auth import Role


class Okutman(Model):
    calisan = Personel()
    ad = field.String("Ad", index=True)
    tip = field.String("Tip", index=True)

class Program(Model):
    birim = Birim()
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

class Derslik(Model):
    kod = field.String("Kod", index=True)
    bina = field.String("Bina", index=True)
    dersler = Sube()

class Sube(Model):
    ad = field.String("Ad", index=True)
    kod = field.String("Kod", index=True)
    okutman = Okutman()
    ana_ders = Ders()
    derslik = Derslik()
    saat = field.Integer("Saat", index=True)
    gun = field.String("Gün", index=True)
    kredi = field.Integer("Kredi", index=True)
    donem = field.String("Dönem", index=True)
    kontenjan = field.Integer("Kontenjan", index=True)

class Ders(Model):
    ad = field.String("Ad", index=True)
    kod = field.String("Kod", index=True)
    kredi = field.String("Kredi", index=True)
    zorunlu = field.Boolean("Zorunlu", index=True)
    akts_teori = field.Float("AKTS Teori", index=True)
    akts_uygulama = field.Float("AKTS Uygulama", index=True)
    donem = field.Integer("Dönem", index=True)
    ders_dili = field.String("Ders Dili", index=True)
    verilis_bicimi = field.Integer("Veriliş Biçimi", index=True)

class Sinav(Model):
    ders = Ders()


class Ogrenci(Model):
    ad = field.String("Ad", index=True)
    soyad = field.String("Soyad", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    ikamet_adresi = field.String("İkamet Adresi", index=True)
    dogum_tarihi = field.Date("Doğum Tarihi", index=True)
    dogum_yeri = field.String("Doğum Yeri", index=True)
    uyruk = field.String("Uyruk", index=True)
    giris_tarihi = field.Date("Giriş Tarihi", index=True)
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True)
    bolum = field.String("Bölüm", index=True)
    fakulte = field.String("Fakülte", index=True)
    e_posta = field.String("E-Posta", index=True)
    ogrenci_no = field.Integer("Öğrenci Numarası", index=True)
    tel_no = field.Integer("Telefon Numarası", index=True)
    akademik_yil = field.String("Akademik Yıl", index=True)
    donem = field.String("Dönem", index=True)
    kan_grubu = field.String("Kan Grubu", index=True)
    ders_programi = DersProgrami()
    rol = Role()

    class Dersler(ListNode):
        saat = field.String("Saat", index=True)
        gun = field.String("Gün", index=True)
        kontenjan = field.Integer("Kontenjan", index=True)
        on_kosul = field.Boolean("Ön Koşul", index=True)
        gecme_notu = field.Integer("Geçme Notu", index=True)
        akademik_yil = field.String("Akademik Yıl", index=True)
        donem = field.String("Dönem", index=True)
        ders = Sube()


class Degerlendirme(Model):
    ogrenci = Ogrenci()
    ders = Ders()
    tur = field.String("Tür", index=True)
    tarih = field.Date("Tarih", index=True)
    puan = field.Integer("Puan", index=True)

class DersDevamsizligi(Model):
    katilim_durumu = field.Integer("Katılım Durumu", index=True)
    ders = Sube()
    ogrenci = Ogrenci()

class Borc(Model):
    miktar = field.Float("Miktar", index=True)
    tur = field.Integer("Tür", index=True)
    ogrenci = Ogrenci()
    donem = Donem()
    son_odeme_tarihi = field.Date("Son Ödeme Tarihi", index=True)
    odeme_tarihi = field.Date("Ödeme Tarihi", index=True)

class Not(Model):
    sinav = Sinav()
    ogrenci = Ogrenci()

class Donem(Model):
    baslangic_tarihi = field.Date("Başlangıç Tarihi", index=True)
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True)
    ad = field.String("Ad", index=True)
    ucret = field.Integer("Ücret", index=True)
    program = Program()
