# -*- coding:utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from .personel import Personel
from pyoko import Model, field, Node
from .auth import Role
import datetime


class NufusKayitlari(Model):
    tckn = field.String("Sigortalının TC Kimlik No")
    ad = field.String("Adı")
    soyad = field.String("Soyadı")
    ilk_soy_ad = field.String("Memuriyete Girişteki İlk Soyadı")
    dogum_tarihi = field.Date("Doğum Tarihi", format="%d.%m.%Y")
    cinsiyet = field.String("Cinsiyet")
    emekli_sicil_no = field.Integer("Emekli Sicil No")
    memuriyet_baslama_tarihi = field.Date("Memuriyete İlk Başlama Tarihi",
                                          format="%d.%m.%Y")
    kurum_sicil = field.String("Kurum Sicili")
    maluliyet_kod = field.Integer("Malul Kod", choices="maluliyet_kod")
    yetki_seviyesi = field.String("Yetki Seviyesi")
    aciklama = field.String("Açıklama")
    kuruma_baslama_tarihi = field.Date("Kuruma Başlama Tarihi", format="%d.%m.%Y")
    gorev_tarihi_6495 = field.Date("Emeklilik Sonrası Göreve Başlama Tarihi",
                                   format="%d.%m.%Y")
    emekli_sicil_6495 = field.Integer("2. Emekli Sicil No")
    durum = field.Boolean("Durum")
    sebep = field.Integer("Sebep")
    sync = field.Integer("Senkronize")
    personel = Personel(one_to_one=True)

    # TODO: Personele gore unique olmali

    class Meta:
        app = 'Personel'
        verbose_name = "Nüfus Bilgisi"
        verbose_name_plural = "Nüfus Bilgileri"
        hitap_service_prefix = "HitapNufus"

    def __unicode__(self):
        return '%s %s %s' % (self.ad, self.soyad, self.emekli_sicil_no)


class HizmetKurs(Model):
    tckn = field.String("TC Kimlik No")
    kayit_no = field.String("Kursa Kayıt No")
    kurs_ogrenim_suresi = field.Integer("Kurs Öğrenim Süresi")
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", format="%d.%m.%Y")
    kurs_nevi = field.Integer("Kurs Nevi", choices="kurs_nevi")
    bolum_ad = field.Integer("Bölüm Adı", choices="bolum_adi")  # TODO: serviste karsiligi yok
    okul_ad = field.Integer("Okul Adı", choices="okul_adi")  # TODO: servisten gelen string
    ogrenim_yeri = field.String("Öğrenim Yeri")
    denklik_tarihi = field.Date("Denklik Tarihi", format="%d.%m.%Y")
    denklik_okulu = field.String("Denklik Okulu")
    denklik_bolum = field.String("Denklik Bölüm")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        list_fields = ['kayit_no', 'bolum_ad', 'okul_ad']
        search_fields = ['tckn', 'okul_ad', 'bolum_ad']
        hitap_service_prefix = "HitapKurs"

    def __unicode__(self):
        return '%s %s %s' % (self.kurs_nevi, self.bolum_ad, self.okul_ad)


class HizmetOkul(Model):
    kayit_no = field.String("Kayıt No")
    tckn = field.String("TC Kimlik No")
    ogrenim_durumu = field.Integer("Öğrenim Durumu", choices="ogrenim_durumu")
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", format="%d.%m.%Y")
    okul_ad = field.String("Okul Adı")
    bolum = field.String("Bölüm")
    ogrenim_yeri = field.Integer("Öğrenim Yeri", choices="ogrenim_yeri")
    denklik_tarihi = field.Date("Denklik Tarihi", format="%d.%m.%Y")
    denklik_okul = field.String("Denklik Okul")
    denklik_bolum = field.String("Denklik Bölüm")
    ogrenim_suresi = field.Integer("Öğrenim Süresi")
    hazirlik = field.Integer("Hazırlık", choices="hazirlik_bilgisi")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Okul"
        verbose_name_plural = "Okullar"
        list_fields = ['okul_ad', 'bolum', 'hazirlik', 'kayit_no']
        search_fields = ['okul_ad', 'bolum', 'tckn']
        hitap_service_prefix = "HitapOkul"

    def __unicode__(self):
        return '%s %s %s' % (self.kayit_no, self.bolum, self.okul_ad)


class HizmetMahkeme(Model):
    tckn = field.String("TC Kimlik No")
    kayit_no = field.String("Kayıt No")
    mahkeme_ad = field.String("Mahkeme Adı")
    sebep = field.Integer("Mahkeme Sebebi", choices="mahkeme_sebep")
    karar_tarihi = field.Date("Mahkeme Karar Tarihi", format="%d.%m.%Y")
    karar_sayisi = field.Integer("Karar Sayısı")
    kesinlesme_tarihi = field.Date("Kesinleşme Tarihi", format="%d.%m.%Y")
    asil_dogum_tarihi = field.Date("Asıl Doğum Tarihi", format="%d.%m.%Y")
    tashih_dogum_tarihi = field.Date("Tashih Doğum Tarihi", format="%d.%m.%Y")
    asil_ad = field.String("Asıl Ad")
    tashih_ad = field.String("Tashih Ad")
    asil_soyad = field.String("Asıl Soyad")
    tashih_soyad = field.String("Tashih Soyad")
    gecerli_dogum_tarihi = field.Date("Geçerli Doğum Tarihi", format="%d.%m.%Y")
    aciklama = field.String("Açıklama")
    gun_sayisi = field.Integer("Gün Sayısı")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Mahkeme"
        verbose_name_plural = "Mahkemeler"
        list_fields = ['mahkeme_ad', 'karar_sayisi', 'aciklama', 'kurum_onay_tarihi']
        search_fields = ['kayit_no', 'mahkeme_ad', 'karar_sayisi']
        hitap_service_prefix = "HitapMahkeme"

    def __unicode__(self):
        return '%s %s %s' % (self.mahkeme_ad, self.karar_tarihi, self.aciklama)


class HizmetBirlestirme(Model):
    tckn = field.String("TC Kimlik No")
    kayit_no = field.String("Kayıt No")
    sgk_nevi = field.Integer("SGK Nevi", choices="sgk_nevi")
    sgk_sicil_no = field.String("SGK Sicil No")
    baslama_tarihi = field.Date("Başlama Tarihi", format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", format="%d.%m.%Y")
    sure = field.Integer("Süre")
    kamu_isyeri_ad = field.String("Kamu İşyeri Adı")
    ozel_isyeri_ad = field.String("Özel İşyeri Adı")
    bag_kur_meslek = field.String("Bağ-Kur Meslek")
    ulke_kod = field.Integer("Ülke Kodu")
    banka_sandik_kod = field.Integer("Banka Sandık Kodu", choices="banka_kod")
    kidem_tazminat_odeme_durumu = field.String("Kıdem Tazminat Ödeme Durumu",
                                               choices="kidem_tazminat_odeme_durumu")
    ayrilma_nedeni = field.String("Ayrılma Nedeni")
    kha_durum = field.Integer("KHA Durum", choices="kha_durum")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Birleştirme"
        verbose_name_plural = "Birleştirmeler"
        list_fields = ['sgk_sicil_no', 'baslama_tarihi', 'bitis_tarihi', 'kamu_isyeri_ad']
        search_fields = ['kayit_no', 'sgk_sicil_no', 'kamu_isyeri_ad']
        hitap_service_prefix = "HitapBirlestirme"

    def __unicode__(self):
        return '%s %s' % (self.kayit_no, self.sgk_nevi)


class HizmetTazminat(Model):
    kayit_no = field.String("Kayıt No")
    tckn = field.String("TC Kimlik No")
    unvan_kod = field.Integer("Ünvan Kodu")
    makam = field.Integer("Makam")
    gorev = field.Integer("Görev")
    temsil = field.Integer("Temsil")
    tazminat_tarihi = field.Date("Tazminat Tarihi", format="%d.%m.%Y")
    tazminat_bitis_tarihi = field.Date("Tazminat Bitiş Tarihi", format="%d.%m.%Y")
    kadrosuzluk = field.Integer("Kadrosuzluk")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Tazminat"
        verbose_name_plural = "Tazminatlar"
        list_fields = ['unvan_kod', 'makam', 'gorev']
        search_fields = ['makam', 'gorev', 'temsil']
        hitap_service_prefix = "HitapTazminat"

    def __unicode__(self):
        return '%s %s' % (self.gorev, self.tazminat_tarihi)


class HizmetUnvan(Model):
    kayit_no = field.String("Hizmet Kayıt No")
    tckn = field.String("TC Kimlik No")
    unvan_kod = field.Integer("Ünvan Kodu")
    unvan_tarihi = field.Date("Ünvan Tarihi", format="%d.%m.%Y")
    unvan_bitis_tarihi = field.Date("Ünvan Bitiş Tarihi", format="%d.%m.%Y")
    hizmet_sinifi = field.String("Hizmet Sınıfı")
    asil_vekil = field.String("Asıl Vekil")
    atama_sekli = field.String("Atama Sekli")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    fhz_orani = field.Float("FHZ Oranı")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Ünvan"
        verbose_name_plural = "Ünvanlar"
        list_fields = ['unvan_kod', 'hizmet_sinifi', 'kurum_onay_tarihi']
        search_fields = ['unvan_kod', 'hizmet_sinifi']
        hitap_service_prefix = "HitapUnvan"

    def __unicode__(self):
        return '%s %s' % (self.unvan_kod, self.hizmet_sinifi)


class HizmetAcikSure(Model):
    tckn = field.String("TC Kimlik No")
    kayit_no = field.String("Kayıt No")
    acik_sekil = field.Integer("Açığa Alınma Şekli", choices="acik_sekli")
    iade_sekil = field.Integer("İade Şekil")
    hizmet_durum = field.Integer("Hizmet Durumu", choices="hizmet_durumu")
    husus = field.Integer("Husus", choices="husus")
    husus_aciklama = field.String("Husus Açıklaması")
    aciga_alinma_tarih = field.Date("Açığa Alınma Tarihi", format="%d.%m.%Y")
    goreve_son_tarih = field.Date("Göreve Son Tarih", format="%d.%m.%Y")
    goreve_iade_istem_tarih = field.Date("Göreve İade İstem Tarihi", format="%d.%m.%Y")
    goreve_iade_tarih = field.Date("Göreve İade Tarihi", format="%d.%m.%Y")
    acik_aylik_bas_tarih = field.Date("Açık Aylık Başlama Tarihi", format="%d.%m.%Y")
    acik_aylik_bit_tarih = field.Date("Açık Aylık Bitiş Tarihi", format="%d.%m.%Y")
    goreve_son_aylik_bas_tarih = field.Date("Göreve Sonlandırma Aylık Başlangıç Tarihi",
                                            format="%d.%m.%Y")
    goreve_son_aylik_bit_tarih = field.Date("Göreve Sonlandırma Aylık Bitiş Tarihi",
                                            format="%d.%m.%Y")
    s_yonetim_kald_tarih = field.Date("Sıkı Yönetim Kaldırıldığı Tarih",
                                      format="%d.%m.%Y")
    aciktan_atanma_tarih = field.Date("Açıktan Atanma Tarihi", format="%d.%m.%Y")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Açığa Alınma"
        verbose_name_plural = "Açığa Alınmalar"
        list_fields = ['acik_sekil', 'aciga_alinma_tarih', 'kurum_onay_tarihi']
        search_fields = ['hizmet_durum', 'acik_sekil', 'aciga_alinma_tarih']
        hitap_service_prefix = "HitapAcikSure"

    def __unicode__(self):
        return '%s %s %s' % (self.iade_sekil, self.kayit_no, self.aciga_alinma_tarih)


class HizmetBorclanma(Model):
    tckn = field.String("TC Kimlik No")
    kayit_no = field.String("Kayıt No")
    ad = field.String("Ad")
    soyad = field.String("Soyad")
    emekli_sicil = field.String("Emekli Sicili")
    derece = field.Integer("Derece")
    kademe = field.Integer("Kademe")
    ekgosterge = field.Integer("Ek Gösterge")
    baslama_tarihi = field.Date("Başlama Tarihi", format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", format="%d.%m.%Y")
    gun_sayisi = field.Integer("Gün Sayısı")
    kanun_kod = field.Integer("Kanun Kodu", choices="kanun_kod")
    borc_nevi = field.Integer("Borç Nevi", choices="borc_nevi")
    toplam_tutar = field.Float("Toplam Tutar")
    odenen_miktar = field.Float("Ödenen Miktar")
    calistigi_kurum = field.String("çalıştığı Kurum")
    isyeri_il = field.String("İşyeri İli")
    isyeri_ilce = field.String("İşyeri İlçesi")

    borclanma_tarihi = field.Date("Borçlanma Tarihi", format="%d.%m.%Y")
    odeme_tarihi = field.Date("Ödeme Tarihi", format="%d.%m.%Y")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Borçlanma"
        verbose_name_plural = "Borçlanmalar"
        list_fields = ['ad', 'soyad', 'toplam_tutar', 'odenen_miktar', 'borclanma_tarihi']
        search_fields = ['tckn', 'ad', 'soyad']
        hitap_service_prefix = "HitapBorclanma"

    def __unicode__(self):
        return '%s %s %s' % (self.borc_nevi, self.calistigi_kurum, self.gun_sayisi)


class HizmetIHS(Model):
    tckn = field.String("TC Kimlik No")
    kayit_no = field.String("Kayıt No")
    baslama_tarihi = field.Date("Başlama Tarihi", format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", format="%d.%m.%Y")
    ihz_nevi = field.Integer("İHZ Nevi")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "İtibari Hizmet Süresi"
        verbose_name_plural = "İtibari Hizmet Süreleri"
        list_fields = ['kayit_no', 'ihz_nevi']
        search_fields = ['tckn', 'ihz_nevi']
        hitap_service_prefix = "HitapIHS"

    def __unicode__(self):
        return '%s %s' % (self.baslama_tarihi, self.ihz_nevi)


class HizmetIstisnaiIlgi(Model):
    tckn = field.String("TC Kimlik No")
    kayit_no = field.String("Kayıt No")
    baslama_tarihi = field.Date("Başlama Tarihi", format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", format="%d.%m.%Y")
    gun_sayisi = field.Integer("Gün Sayısı")
    istisnai_ilgi_nevi = field.Integer("İstisnai İlgi Nevi")
    kha_durum = field.Integer("KHA Durum", choices="kha_durum")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "İstisnai İlgi"
        verbose_name_plural = "İstisnai İlgiler"
        list_fields = ['baslama_tarihi', 'bitis_tarihi', 'istisnai_ilgi_nevi', 'kha_durum']
        search_fields = ['istisnai_ilgi_nevi', 'kha_durum']
        hitap_service_prefix = "HitapIstisnaiIlgi"

    def __unicode__(self):
        return '%s %s %s' % (self.kayit_no, self.istisnai_ilgi_nevi, self.kha_durum)


class HizmetKayitlari(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    gorev = field.String("Görev", index=True)  # birim + kadro unvanı
    unvan_kod = field.Integer("Unvan Kod", index=True)  # kadro unvan kodu
    yevmiye = field.String("Yevmiye", index=True)
    ucret = field.String("Ücret", index=True)
    hizmet_sinifi = field.Integer("Hizmet Sınıfı", index=True,
                                  choices="hizmet_sinifi")  # atama modelinden gelecek
    kadro_derece = field.Integer("Kadro Derecesi", index=True)  # personelden gelecek
    odeme_derece = field.Integer("Ödeme Derecesi", index=True)  # personelden gelecek
    odeme_kademe = field.Integer("Ödeme Kademesi", index=True)  # personelden gelecek (gorunen)
    odeme_ekgosterge = field.Integer("Ödeme Ek Göstergesi", index=True)  # personelden gelecek
    kazanilmis_hak_ayligi_derece = field.Integer("Kazanılmış Hak Aylığı Derecesi",
                                                 index=True)  # personelden gelecek
    kazanilmis_hak_ayligi_kademe = field.Integer("Kazanılmış Hak Aylığı Kademesi",
                                                 index=True)  # personelden gelecek (gorunen)
    kazanilmis_hak_ayligi_ekgosterge = field.Integer("Kazanılmış Hak Aylığı Ek Göstergesi",
                                                     index=True)  # personelden gelecek
    emekli_derece = field.Integer("Emekli Derecesi", index=True)  # personelden gelecek
    emekli_kademe = field.Integer("Emekli Kademe", index=True)  # personelden gelecek (gorunen)
    emekli_ekgosterge = field.Integer("Emekli Ek Göstergesi", index=True)  # personelden gelecek
    sebep_kod = field.Integer("Sebep Kodu", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    # post save metodunda baslangic ya da bitis tarihinden set edilir.
    order_date = field.DateTime()

    class Meta:
        app = 'Personel'
        verbose_name = "Kayıt"
        verbose_name_plural = "Kayıtlar"
        list_fields = ['unvan_kod', 'gorev', 'yevmiye', 'ucret', 'hizmet_sinifi']
        search_fields = ['unvan_kod', 'gorev', 'yevmiye']
        hitap_service_prefix = "HitapHizmetCetveli"

    def post_save(self):
        """
        Hizmet cetvelindeki kayıtların başlama veya bitiş tarihleri
        geliyor. Her kaydın başlama ve bitiş tarihi beraber gelmiyor.
        Bu yüzden kayıtların sıralanabilmesi için order_date alanı
        eklendi. Bitiş tarihi başka bir kaydın başlangıç tarihi ise
        önce bitiş tarihi olan kayıt gürüntülenmelidir. Bu yüzden
        başlangıç tarihine +1 saat eklendi.
        """
        if self.baslama_tarihi != datetime.date(1900, 1, 1):
            self.order_date = datetime.datetime.combine(self.baslama_tarihi, datetime.time(1))
        else:
            self.order_date = self.bitis_tarihi
        self.save()

    def post_creation(self):
        if self.personel:
            self.tckn = self.personel.tckn
            self.gorev = "%s %s" % (self.personel.birim.name, self.personel.kadro.unvan)
            self.unvan_kod = self.personel.kadro.unvan_kod
            self.hizmet_sinifi = self.personel.atama.hizmet_sinif
            self.kadro_derece = self.personel.kadro_derece
            self.odeme_derece = self.personel.gorev_ayligi_derece
            self.odeme_kademe = self.gorunen_gorev_ayligi_kademe
            self.odeme_ekgosterge = self.personel.gorev_ayligi_ekgosterge
            self.kazanilmis_hak_ayligi_derece = self.personel.kazanilmis_hak_derece
            self.kazanilmis_hak_ayligi_kademe = self.personel.gorunen_kazanilmis_hak_kademe
            self.kazanilmis_hak_ayligi_ekgosterge = self.personel.kazanilmis_hak_ekgosterge
            self.emekli_derece = self.personel.emekli_muktesebat_derece
            self.emekli_kademe = self.personel.gorunen_emekli_muktesebat_kademe
            self.emekli_ekgosterge = self.personel.emekli_muktesebat_ekgosterge

    def __unicode__(self):
        return '%s %s %s' % (self.unvan_kod, self.hizmet_sinifi, self.gorev)


class AskerlikKayitlari(Model):
    askerlik_nevi = field.Integer("Askerlik Nevi", choices="askerlik_nevi")
    baslama_tarihi = field.Date("Başlama Tarihi", format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", format="%d.%m.%Y")
    kayit_no = field.String("Kayıt No")
    kita_baslama_tarihi = field.Date("Kıta Başlama Tarihi", format="%d.%m.%Y")
    kita_bitis_tarihi = field.Date("Kıta Bitiş Tarihi", format="%d.%m.%Y")
    muafiyet_neden = field.String("Muafiyet Neden")
    sayilmayan_gun_sayisi = field.Integer("Sayılmayan Gün Sayısı")
    sinif_okulu_sicil = field.String("Sınıf Okulu Sicil")
    subayliktan_erlige_gecis_tarihi = field.Date("Subaylıktan Erliğe Geçiş Tarihi",
                                                 format="%d.%m.%Y")
    subay_okulu_giris_tarihi = field.Date("Subay Okulu Giriş Tarihi", format="%d.%m.%Y")
    tckn = field.String("TC Kimlik No")
    tegmen_nasp_tarihi = field.Date("Teğmen Nasp Tarihi", format="%d.%m.%Y")
    gorev_yeri = field.String("Görev Yeri")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", format="%d.%m.%Y")
    astegmen_nasp_tarihi = field.Date("Asteğmen Nasp Tarihi", format="%d.%m.%Y")
    sync = field.Integer("Senkronize")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Kayıt"
        verbose_name_plural = "Kayıtlar"
        list_fields = ['askerlik_nevi', 'kita_baslama_tarihi', 'gorev_yeri']
        search_fields = ['askerlik_nevi', 'gorev_yeri', 'tckn']
        hitap_service_prefix = "HitapAskerlik"

    def __unicode__(self):
        return '%s %s %s %s' % (
            self.askerlik_nevi, self.kayit_no, self.kita_baslama_tarihi, self.gorev_yeri)


## TODO : Sebep kodları fixture altına taşınacak, bkz; sepeb_kod_ayrilma, sebep_kod_baslama
class HitapSebep(Model):
    sebep_no = field.Integer("Sebep No")
    ad = field.String("Sebep Adı")
    nevi = field.Integer("Sebep Nevi")
    zorunlu_alan = field.String("Zorunlu ALan")

    class Meta:
        app = 'Personel'
        verbose_name = "Hitap Sebep Kodu"
        verbose_name_plural = "Hitap Sebep Kodları"
        list_fields = ['sebep_no', 'ad', 'nevi', 'zorunlu_alan']
        search_fields = ['sebep_no', 'ad']

    def __unicode__(self):
        return '%s - %s' % (self.sebep_no, self.ad)
