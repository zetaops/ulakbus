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
    harici_okutman_ad = field.String("Harici Okutman Ad", index=True, required=False)
    harici_okutman_soyad = field.String("Harici Okutman Soyad", index=True, required=False)
    tckn = field.String("Okutmanın TC Kimlik Numarası", index=True, required=False)
    dogum_tarihi = field.Date("Okutmanın Doğum Tarihi", index=True, required=False)
    dogum_yeri = field.String("Okutmanın Doğum Yeri", index=True, required=False)
    uyruk = field.String("Uyruk", index=True, required=False)
    medeni_hali = field.String("Medeni Hali", index=True, choices="medeni_hali", required=False)
    ikamet_adresi = field.String("İkamet Adresi", index=True, required=False)
    telefon_no = field.String("Telefon Numarası", index=True, required=False)
    oda_no = field.String("Oda Numarası", index=True, required=False)
    oda_tel_no = field.String("Oda Telefon Numarası", index=True, required=False)
    e_posta = field.String("E-posta Adresi", index=True, required=False)
    web_sitesi = field.String("Web Sitesi", index=True, required=False)
    yayinlar = field.String("Yayınlar", index=True, required=False)
    projeler = field.String("Projeler", index=True, required=False)
    kan_grubu = field.String("Kan Grubu", index=True, required=False)
    ehliyet = field.String("Ehliyet", index=True, required=False)
    akademik_yayinlari = field.String("Akademik Yayınları", index=True, required=False)
    verdigi_dersler = field.String("Verdiği Dersler", index=True, required=False)
    unvan = field.String("Unvan", index=True, choices="akademik_unvan", required=False)

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Okutman"
        verbose_name_plural = "Okutmanlar"
        search_fields = ['unvan', 'personel']

    def __unicode__(self):
        return '%s %s' % (self.personel.key, self.harici_okutman_ad)


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
    yoksis_no = field.String("YOKSIS ID", index=True)
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
    cinsiyet = field.Integer("Cinsiyet", index = True, choices = "cinsiyet")
    tckn = field.String("TC Kimlik No", index=True)
    cuzdan_seri = field.String("Seri", index=True)
    cuzdan_seri_no = field.String("Seri No", index=True)
    kayitli_oldugu_il = field.String("İl", index=True)
    kayitli_oldugu_ilce = field.String("İlçe", index=True)
    kayitli_oldugu_mahalle_koy = field.String("Mahalle/Koy")
    kayitli_oldugu_cilt_no = field.String("Cilt No")
    kayitli_oldugu_aile_sira_no = field.String("Aile Sıra No")
    kayitli_oldugu_sira_no = field.String("Sıra No")
    kimlik_cuzdani_verildigi_yer = field.String("Nüfus Cuzdanı Verildigi Yer")
    kimlik_cuzdani_verilis_nedeni = field.String("Nufus Cuzdanı Verilis Nedeni")
    kimlik_cuzdani_kayit_no = field.String("Nüfus Cuzdanı Kayit No")
    kimlik_cuzdani_verilis_tarihi = field.Date("Nüfus Cüzdanı Veriliş Tarihi", index = True, format = "%d.%m.%Y")
    baba_adi = field.String("Ana Adı", index=True)
    ana_adi = field.String("Baba Adı", index=True)
    ikamet_il = field.String("İkamet İl", index=True)
    ikamet_ilce = field.String("İkamet İlçe", index=True)
    ikamet_adresi = field.String("İkametgah Adresi", index=True)
    posta_kodu = field.String("Posta Kodu", index=True)
    dogum_tarihi = field.Date("Doğum Tarihi", index=True, format="%d.%m.%Y")
    dogum_yeri = field.String("Doğum Yeri", index=True)
    uyruk = field.String("Uyruk", index=True)
    medeni_hali = field.Integer("Medeni Hali", index=True, choices="medeni_hali")
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
