# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from .personel import Personel
from pyoko import Model, field, ListNode
from .auth import Role, User
from .auth import Unit
from .buildings_rooms import Room
import six


class HariciOkutman(Model):
    tckn = field.String("TC No", index=True)
    ad = field.String("Adı", index=True)
    soyad = field.String("Soyadı", index=True)
    cinsiyet = field.Integer("Cinsiyet", index=True, choices='cinsiyet')
    uyruk = field.String("Uyruk", index=True)
    medeni_hali = field.Integer("Medeni Hali", index=True, choices="medeni_hali", required=False)
    ikamet_adresi = field.String("İkamet Adresi", index=True, required=False)
    ikamet_il = field.String("İkamet Il", index=True, required=False)
    ikamet_ilce = field.String("İkamet Ilce", index=True, required=False)
    adres_2 = field.String("Adres 2", index=True, required=False)
    adres_2_posta_kodu = field.String("Adres 2 Posta Kodu", index=True, required=False)
    telefon_no = field.String("Telefon Numarası", index=True, required=True)
    oda_no = field.String("Oda Numarası", index=True, required=False)
    oda_tel_no = field.String("Oda Telefon Numarası", index=True, required=False)
    e_posta = field.String("E-Posta", index=True)
    e_posta_2 = field.String("E-Posta 2", index=True, required=False)
    e_posta_3 = field.String("E-Posta 3", index=True, required=False)
    web_sitesi = field.String("Web Sitesi", index=True, required=False)
    yayinlar = field.String("Yayınlar", index=True, required=False)
    projeler = field.String("Projeler", index=True, required=False)
    kan_grubu = field.String("Kan Grubu", index=True, required=False)
    ehliyet = field.String("Ehliyet", index=True, required=False)
    biyografi = field.Text("Biyografi")
    notlar = field.Text("Notlar")
    engelli_durumu = field.String("Engellilik", index=True)
    engel_grubu = field.String("Engel Grubu", index=True)
    engel_derecesi = field.String("Engel Derecesi")
    engel_orani = field.Integer("Engellilik Orani")
    cuzdan_seri = field.String("Seri", index=True)
    cuzdan_seri_no = field.String("Seri No", index=True)
    baba_adi = field.String("Ana Adi", index=True)
    ana_adi = field.String("Baba Adi", index=True)
    dogum_tarihi = field.Date("Doğum Tarihi", index=True, format="%d.%m.%Y")
    dogum_yeri = field.String("Doğum Yeri", index=True)
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
    akademik_yayinlari = field.String("Akademik Yayınları", index=True, required=False)
    verdigi_dersler = field.String("Verdiği Dersler", index=True, required=False)
    unvan = field.Integer("Unvan", index=True, choices="akademik_unvan", required=False)
    aktif = field.Boolean("Aktif", index=True, required=False)

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Harici Okutman"
        verbose_name_plural = "Harici Okutmanlar"
        search_fields = ['unvan', 'ad', 'soyad']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.soyad)

    def update_okutman(self):
        try:
            okutman = Okutman.objects.get(harici_okutman=self)
        except:
            okutman = Okutman()
        okutman.harici_okutman = self
        okutman.ad = self.ad
        okutman.soyad = self.soyad
        okutman.unvan = self.unvan
        okutman.save()

    def save(self):
        super(HariciOkutman, self).save()
        self.update_okutman()


class Okutman(Model):
    ad = field.String("Ad", index=True, required=False)
    soyad = field.String("Soyad", index=True, required=False)
    unvan = field.String("Unvan", index=True, required=False)
    birim_no = field.String("Birim ID", index=True, required=False)
    personel = Personel()
    harici_okutman = HariciOkutman()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Okutman"
        verbose_name_plural = "Okutmanlar"
        search_fields = ['unvan', 'personel']

    @property
    def okutman(self):
        # self.personel layz model dondurdugu icin self.personel.key seklinde kontrol etmeliyiz.
        return self.personel if self.personel.key else self.harici_okutman

    def __unicode__(self):
        return '%s %s' % (self.okutman.ad, self.okutman.soyad)

    def check_uniqueness(self):
        p = len(self.objects.filter(personel=self.personel)) if self.okutman.key else 0
        return False if p > 0 else True

    def save(self):
        self.ad = self.okutman.ad
        self.soyad = self.okutman.soyad
        self.unvan = self.okutman.unvan

        if self.is_in_db() or self.check_uniqueness():
            super(Okutman, self).save()
        else:
            raise Exception("Okutman must be unique %s")


class Donem(Model):
    ad = field.String("Ad", index=True)
    baslangic_tarihi = field.Date("Başlangıç Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    guncel = field.Boolean(index=True)

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
    bolum_baskani = Role(verbose_name='Bolum Başkanı', reverse_name='bolum_baskani_program')
    ects_bolum_kordinator = Role(verbose_name='ECTS Bölüm Koordinator',
                                 reverse_name='ects_koordinator_program')
    akademik_kordinator = Role(verbose_name='Akademik Koordinator',
                               reverse_name='akademik_koordinator_program')
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
        dersi_verenler = Okutman()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ders"
        verbose_name_plural = "Dersler"
        list_fields = ['ad', 'kod', 'ders_dili']
        search_fields = ['ad', 'kod']

    def __unicode__(self):
        return '%s %s %s' % (self.ad, self.kod, self.ders_dili)


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
    tur = field.Integer("Sınav Türü", index=True, choices="sinav_turleri")
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
    derslik = Room()

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
    cinsiyet = field.Integer("Cinsiyet", index=True, choices="cinsiyet")
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
    kimlik_cuzdani_verilis_tarihi = field.Date("Nüfus Cüzdanı Veriliş Tarihi", index=True, format="%d.%m.%Y")
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
    e_posta = field.String("E-Posta", index=True)
    tel_no = field.String("Telefon Numarası", index=True)
    kan_grubu = field.String("Kan Grubu", index=True)
    user = User(one_to_one=True)

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ogrenci"
        verbose_name_plural = "Ogrenciler"
        list_fields = ['ad', 'soyad']
        search_fields = ['ad', 'soyad']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.soyad)


class OncekiEgitimBilgisi(Model):
    okul_adi = field.String("Mezun Olduğu Okul", index=True)
    diploma_notu = field.Float("Diploma Notu", index=True)
    mezuniyet_yili = field.String("Mezuniyet Yılı", index=True)
    ogrenci = Ogrenci()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Önceki Eğitim Bilgisi"
        verbose_name_plural = "Önceki Eğitim Bilgileri"
        list_fields = ['okul_adi', 'diploma_notu', 'mezuniyet_yili']
        search_fields = ['okul_adi', 'diploma_notu', 'mezuniyet_yili']


class OgrenciProgram(Model):
    ogrenci_no = field.String("Öğrenci Numarası", index=True)
    giris_tarihi = field.Date("Giriş Tarihi", index=True, format="%d.%m.%Y")
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True, format="%d.%m.%Y")
    aktif_donem = field.String("Dönem", index=True)
    basari_durumu = field.String("Başarı Durumu", index=True)
    ders_programi = DersProgrami()
    danisman = Personel()
    program = Program()
    ogrenci = Ogrenci()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Öğrenci Program"
        verbose_name_plural = "Öğrenci Program"

    def __unicode__(self):
        return '%s %s - %s / %s' % (self.ogrenci.ad, self.ogrenci.soyad, self.program.adi, self.program.yil)


class OgrenciDersi(Model):
    alis_bicimi = field.Integer("Dersi Alış Biçimi", index=True)
    ders = Sube()
    ogrenci_program = OgrenciProgram()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ogrenci Dersi"
        verbose_name_plural = "Ogrenci Dersleri"
        list_fields = ['sube_dersi', 'alis_bicimi']
        search_fields = ['alis_bicimi', ]

    def sube_dersi(self):
        # return '%s - %s' % (self.ders.ders.kod, self.ders.ders)
        return six.text_type(self.ders)

    sube_dersi.title = 'Ders'

    def __unicode__(self):
        return '%s %s %s' % (self.ders.ders.kod, self.ders.ders.ad, self.alis_bicimi)


class DersKatilimi(Model):
    katilim_durumu = field.Float("Katılım Durumu", index=True)
    ders = Sube()
    ogrenci = Ogrenci()
    okutman = Okutman()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Ders Devamsizligi"
        verbose_name_plural = "Ders Devamsizliklari"
        list_fields = ['katilim_durumu', 'sube_dersi']
        search_fields = ['sube_dersi', 'katilim_durumu']

    def sube_dersi(self):
        # return '%s - %s' % (self.ders.ders.kod, self.ders.ders)
        return six.text_type(self.ders)

    sube_dersi.title = 'Ders'

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


AKADEMIK_TAKVIM_ETKINLIKLERI = [
    ('1', 'Yeni Öğrenci Ön Kayıt'),
    ('2', 'Güz Dönem Başlangıcı'),
    ('3', 'Derslerin Acılması'),
    ('4', 'Subelendirme ve Ders Programının Ilan Edilmesi'),
    ('5', 'Öğrenci Harç'),
    ('6', 'Öğrenci Ek Harç'),
    ('7', 'Mazeretli Öğrenci Harç'),
    ('8', 'Yeni Öğrenci Ders Kayıt'),
    ('9', 'Yeni Öğrenci Danışman Onay'),
    ('10', 'Ders Kayıt'),
    ('11', 'Danışman Onay'),
    ('12', 'Mazeretli Ders Kayıt'),
    ('13', 'Mazeretli Danışman Onay'),
    ('14', 'Ders Ekle/Bırak'),
    ('15', 'Ders Ekle/Bırak Danışman Onay'),
    ('16', 'Danışman Dersten Çekilme İşlemleri'),
    ('17', 'Ara Sinav'),
    ('18', 'Ara Sınav Not Giriş'),
    ('19', 'Ara Sınav Notlarının Öğrenciye Yayınlanması'),
    ('20', 'Ara Sinav Mazeretli'),
    ('21', 'Ara Sınav Mazeret Not Giriş'),
    ('22', 'Ara Sınav Mazeret Notlarının Öğrenciye Yayınlanması'),
    ('23', 'Sınav Maddi Hata Düzeltme'),
    ('24', 'Yariyil Sinav'),
    ('25', 'Yarıyıl Sınavı Not Giriş'),
    ('26', 'Yarıyıl Sınavı Notlarının Öğrenciye Yayınlanmasi'),
    ('27', 'Bütünleme ve Yarı Yıl Sonu Mazeret Sınavı'),
    ('28', 'Bütünleme ve Yarı Yıl Sonu Mazeret Sınavı Not Giriş'),
    ('29', 'Bütünleme ve Yarı Yıl Sonu Mazeret Sınavı Notlarının Öğrenciye Yayınlanması'),
    ('30', 'Harf Notlarının Öğrenciye Yayınlanması'),
    ('31', 'Bütünleme Harf Notlarının Öğrenciye Yayınlanması'),
    ('32', 'Öğretim Elemanı Yoklama Girişi'),
    ('33', 'Bahar Donemi Derslerin Acilmasi'),
    ('34', 'Bahar Donemi Subelendirme ve Ders Programının Ilan Edilmesi'),
    ('35', 'Bahar Dönem Başlangıcı'),
    ('36', 'Öğrenci Harç'),
    ('37', 'Öğrenci Ek Harç'),
    ('38', 'Mazeretli Öğrenci Harç'),
    ('39', 'Ders Kayıt'),
    ('40', 'Danışman Onay'),
    ('41', 'Mazeretli Ders Kayıt'),
    ('42', 'Mazeretli Danışman Onay'),
    ('43', 'Ders Ekle / Bırak'),
    ('44', 'Ders Ekle / Bırak Onay'),
    ('45', 'Ara Sinav'),
    ('46', 'Ara Sınav Not Giriş'),
    ('47', 'Ara Sınav Notlarının Öğrenciye Yayınlanması'),
    ('48', 'Ara Sinav Mazeretli'),
    ('49', 'Ara Sınav Mazeret Not Giriş'),
    ('50', 'Ara Sınav Mazeret Notlarının Öğrenciye Yayınlanması'),
    ('51', 'Sınav Maddi Hata Düzeltme'),
    ('52', 'Yariyil Sinav'),
    ('53', 'Yarıyıl Sınavı Not Giriş'),
    ('54', 'Yarıyıl Sınavı Notlarının Öğrenciye Yayınlanmasi'),
    ('55', 'Öğretim Elemanı Yoklama Girişi'),
]


class AkademikTakvim(Model):
    birim = Unit("Birim", index=True)
    yil = field.Date("Yil", index=True)

    class Takvim(ListNode):
        etkinlik = field.Integer("Etkinlik", index=True, choices=AKADEMIK_TAKVIM_ETKINLIKLERI)
        baslangic = field.Date("Başlangıç", index=True)
        bitis = field.Date("Bitiş", index=True, required=False)

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Akademik Takvim"
        verbose_name_plural = "Akademik Takvim"
        list_fields = ['_birim', 'yil']
        # search_fields = ['yil']

    def _birim(self):
        return "%s" % self.birim
    _birim.title = 'Birim'

    def __unicode__(self):
        return '%s %s' % (self.birim, self.yil)
