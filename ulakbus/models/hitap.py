# -*- coding:utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from .personel import Personel
from pyoko import Model, field, Node
from .auth import Role


class NufusKayitlari(Model):
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
    maluliyet_kod = field.Integer("Malul Kod", index=True, choices="maluliyet_kod")
    yetki_seviyesi = field.String("Yetki Seviyesi", index=True)
    aciklama = field.String("Aciklama", index=True)
    kuruma_baslama_tarihi = field.Date("Kuruma Baslama Tarihi", index=True, format="%d.%m.%Y")
    gorev_tarihi_6495 = field.Date("Emeklilik Sonrası Göreve Başlama Tarihi", index=True,
                                   format="%d.%m.%Y")
    emekli_sicil_6495 = field.Integer("2. Emekli Sicil No", index=True)
    durum = field.Boolean("Durum", index=True)
    sebep = field.Integer("Sebep", index=True)
    sync = field.Integer("Senkronize", index=True)
    personel = Personel(one_to_one=True)

    # personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Nüfus Bilgileri"
        verbose_name_plural = "Nüfus Bilgileri"


class HizmetKurs(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kursa Kayıt No", index=True)
    kurs_ogrenim_suresi = field.Integer("Kurs Öğrenim Süresi", index=True)
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True, format="%d.%m.%Y")
    kurs_nevi = field.Integer("Kurs Nevi", index=True, choices="kurs_nevi")
    bolum_ad = field.Integer("Bölüm Adı", index=True, choices="bolum_ad")
    okul_ad = field.Integer("Okul Adı", index=True, choices="okul_ad")
    ogrenim_yeri = field.String("Öğrenim Yeri", index=True)
    denklik_tarihi = field.Date("Denklik Tarihi", index=True, format="%d.%m.%Y")
    denklik_okulu = field.String("Denklik Okulu", index=True)
    denklik_bolum = field.String("Denklik Bölüm", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        list_fields = ['kayit_no', 'bolum_ad', 'okul_ad']
        search_fields = ['tckn', 'okul_ad', 'bolum_ad']

    def __unicode__(self):
        return '%s %s %s' % (self.kurs_nevi, self.bolum_ad, self.okul_ad)


class HizmetOkul(Model):
    kayit_no = field.String("Kayıt No", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    ogrenim_durumu = field.Integer("Öğrenim Durumu", index=True, choices="ogrenim_durumu")
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True, format="%d.%m.%Y")
    okul_ad = field.String("Okul Adı", index=True)
    bolum = field.String("Bölüm", index=True)
    ogrenim_yeri = field.Integer("Öğrenim Yeri", index=True, choices="ogrenim_yeri")
    denklik_tarihi = field.Date("Denklik Tarihi", index=True, format="%d.%m.%Y")
    denklik_okul = field.String("Denklik Okul", index=True)
    denklik_bolum = field.String("Denklik Bölüm", index=True)
    ogrenim_suresi = field.Integer("Öğrenim Süresi", index=True)
    hazirlik = field.Integer("Hazırlık", index=True, choices="hazirlik_bilgisi")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Okul"
        verbose_name_plural = "Okullar"
        list_fields = ['okul_ad', 'bolum', 'hazirlik', 'kayit_no']
        search_fields = ['okul_ad', 'bolum', 'tckn']

    def __unicode__(self):
        return '%s %s %s' % (self.kayit_no, self.bolum, self.okul_ad)


class HizmetMahkeme(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("kayıt No", index=True)
    mahkeme_ad = field.String("Mahkeme Adı", index=True)
    sebep = field.Integer("Mahkeme Sebebi", index=True, choices="mahkeme_sebep")
    karar_tarihi = field.Date("Mahkeme Karar Tarihi", index=True, format="%d.%m.%Y")
    karar_sayisi = field.Integer("Karar Sayısı", index=True)
    kesinlesme_tarihi = field.Date("Kesinleşme Tarihi", index=True, format="%d.%m.%Y")
    asil_dogum_tarihi = field.Date("Asıl Doğum Tarihi", index=True, format="%d.%m.%Y")
    tashih_dogum_tarihi = field.Date("Tashih Doğum Tarihi", index=True, format="%d.%m.%Y")
    asil_ad = field.String("Asıl Ad", index=True)
    tashih_ad = field.String("Tashih Ad", index=True)
    asil_soyad = field.String("Asıl Soyad", index=True)
    tashih_soyad = field.String("Tashih Soyad", index=True)
    gecerli_dogum_tarihi = field.Date("Geçerli Doğum Tarihi", index=True, format="%d.%m.%Y")
    aciklama = field.String("Açıklama", index=True)
    gun_sayisi = field.Integer("Gün Sayısı", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Mahkeme"
        verbose_name_plural = "Mahkemeler"
        list_fields = ['mahkeme_ad', 'karar_sayisi', 'aciklama', 'kurum_onay_tarihi']
        search_fields = ['kayit_no', 'mahkeme_ad', 'karar_sayisi']

    def __unicode__(self):
        return '%s %s %s' % (self.mahkeme_ad, self.karar_tarihi, self.aciklama)


class HizmetBirlestirme(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    sgk_nevi = field.Integer("SGK Nevi", index=True, choices="sgk_nevi")
    sgk_sicil_no = field.String("SGK Sicil No", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    sure = field.Integer("Süre", index=True)
    kamuIsyeri_ad = field.String("Kamu İşyeri Adı", index=True)
    ozel_isyeri_ad = field.String("Özel İşyeri Adı", index=True)
    bag_kur_meslek = field.String("Bağ-Kur Meslek", index=True)
    ulke_kod = field.Integer("Ülke Kodu", index=True)
    banka_sandik_kod = field.Integer("Banka Sandık Kodu", index=True, choices="banka_kod")
    kidem_tazminat_odeme_durumu = field.String("Kıdem Tazminat Ödeme Durumu", index=True)
    ayrilma_nedeni = field.Integer("Ayrılma Nedeni", index=True)
    kha_durum = field.Integer("KHA Durum", index=True, choices="kha_durum")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Birleştirme"
        verbose_name_plural = "Birleştirmeler"
        list_fields = ['sgk_sicil_no', 'baslama_tarihi', 'bitis_tarihi', 'kamuIsyeri_ad']
        search_fields = ['kayit_no', 'sgk_sicil_no', 'kamuIsyeri_ad']

    def __unicode__(self):
        return '%s %s' % (self.kayit_no, self.sgk_nevi)


class HizmetTazminat(Model):
    kayit_no = field.String("Kayıt No", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    unvan_kod = field.Integer("Ünvan Kodu", index=True)
    makam = field.Integer("Makam", index=True)
    gorev = field.Integer("Görev", index=True)
    temsil = field.Integer("Temsil", index=True)
    tazminat_tarihi = field.Date("Tazminat Tarihi", index=True, format="%d.%m.%Y")
    tazminat_bitis_tarihi = field.Date("Tazminat Bitiş Tarihi", index=True, format="%d.%m.%Y")
    kadrosuzluk = field.Integer("Kadrosuzluk", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Tazminat"
        verbose_name_plural = "Tazminatlar"
        list_fields = ['unvan_kod', 'makam', 'gorev']
        search_fields = ['makam', 'gorev', 'temsil']

    def __unicode__(self):
        return '%s %s' % (self.gorev, self.tazminat_tarihi)


class HizmetUnvan(Model):
    kayit_no = field.String("Hizmet Kayıt No", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    unvan_kod = field.Integer("Ünvan Kodu", index=True)
    unvan_tarihi = field.Date("Ünvan Tarihi", index=True, format="%d.%m.%Y")
    unvan_bitis_tarihi = field.Date("Ünvan Bitiş Tarihi", index=True, format="%d.%m.%Y")
    hizmet_sinifi = field.String("Hizmet Sınıfı", index=True)
    asil_vekil = field.String("Asıl Vekil", index=True)
    atama_sekli = field.String("Atama Sekli", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    fhz_orani = field.Float("FHZ Oranı", index=True)
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Ünvan"
        verbose_name_plural = "Ünvanlar"
        list_fields = ['unvan_kod', 'hizmet_sinifi', 'kurum_onay_tarihi']
        search_fields = ['unvan_kod', 'hizmet_sinifi']

    def __unicode__(self):
        return '%s %s' % (self.unvan_kod, self.hizmet_sinifi)


class HizmetAcikSure(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    acik_sekil = field.Integer("Açığa Alınma Şekli", index=True, choices="acik_sekli")
    durum = field.Integer("Durum", index=True)
    hizmet_durum = field.Integer("Hizmet Durumu", index=True, choices="hizmet_durumu")
    husus = field.Integer("Husus", index=True, choices="husus")
    aciga_alinma_tarih = field.Date("Açığa Alınma Tarihi", index=True, format="%d.%m.%Y")
    goreve_son_tarih = field.Date("Göreve Son Tarih", index=True, format="%d.%m.%Y")
    goreve_iade_istem_tarih = field.Date("Göreve İade İstem Tarihi", index=True, format="%d.%m.%Y")
    goreve_iade_tarih = field.Date("Göreve İade Tarihi", index=True, format="%d.%m.%Y")
    acik_aylik_bas_tarih = field.Date("Açık Aylık Başlama Tarihi", index=True, format="%d.%m.%Y")
    acik_aylik_bit_tarih = field.Date("Açık Aylık Bitiş Tarihi", index=True, format="%d.%m.%Y")
    goreve_son_aylik_bas_tarih = field.Date("Göreve sonlandırma aylık başlangıç tarihi", index=True,
                                            format="%d.%m.%Y")
    goreve_son_aylik_bit_tarih = field.Date("Göreve sonlandırma aylık bitiş tarihi", index=True,
                                            format="%d.%m.%Y")
    s_yonetim_kald_tarih = field.Date("Sıkı Yönetim Kaldırıldığı Tarih", index=True,
                                      format="%d.%m.%Y")
    aciktan_atanma_tarih = field.Date("Açıktan Atanma Tarihi", index=True, format="%d.%m.%Y")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Açığa Alınma"
        verbose_name_plural = "Açığa Alınmalar"
        list_fields = ['acik_sekil', 'aciga_alinma_tarih', 'kurum_onay_tarihi']
        search_fields = ['hizmet_durum', 'acik_sekil', 'aciga_alinma_tarih']

    def __unicode__(self):
        return '%s %s %s' % (self.durum, self.kayit_no, self.aciga_alinma_tarih)


class HizmetBorclanma(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    ad = field.String("Ad", index=True)
    soyad = field.String("Soyad", index=True)
    emekli_sicil = field.String("Emekli Sicili", index=True)
    derece = field.Integer("Derece", index=True)
    kademe = field.Integer("Kademe", index=True)
    ekgosterge = field.Integer("Ek Gösterge", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    gun_sayisi = field.Integer("Gün Sayısı", index=True)
    kanun_kod = field.Integer("Kanun Kodu", index=True, choices="kanun_kod")
    borc_nevi = field.Integer("Borç Nevi", index=True, choices="borc_nevi")
    toplam_tutar = field.Float("Toplam Tutar", index=True)
    odenen_miktar = field.Float("Ödenen Miktar", index=True)
    calistigi_kurum = field.String("çalıştığı Kurum", index=True)
    isyeri_il = field.String("İşyeri İli", index=True)
    isyeri_ilce = field.String("İşyeri İlçesi", index=True)

    borclanma_tarihi = field.Date("Borçlanma Tarihi", index=True, format="%d.%m.%Y")
    odeme_tarihi = field.Date("Ödeme Tarihi", index=True, format="%d.%m.%Y")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Borçlanma"
        verbose_name_plural = "Borçlanmalar"
        list_fields = ['ad', 'soyad', 'toplam_tutar', 'odenen_miktar', 'borclanma_tarihi']
        search_fields = ['tckn', 'ad', 'soyad']

    def __unicode__(self):
        return '%s %s %s' % (self.borc_nevi, self.calistigi_kurum, self.gun_sayisi)


class HizmetIHS(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    ihz_nevi = field.Integer("İHZ Nevi", index=True)
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "İtibari Hizmet Süresi"
        verbose_name_plural = "İtibari Hizmet Süreleri"
        list_fields = ['kayit_no', 'ihz_nevi']
        search_fields = ['tckn', 'ihz_nevi']

    def __unicode__(self):
        return '%s %s' % (self.baslama_tarihi, self.ihz_nevi)


class HizmetIstisnaiIlgi(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    gun_sayisi = field.Integer("Gün Sayısı", index=True)
    istisnai_ilgi_nevi = field.Integer("İstisnai İlgi Nevi", index=True)
    kha_durum = field.Integer("KHA Durum", index=True, choices="kha_durum")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "İstisnai İlgi"
        verbose_name_plural = "İstisnai İlgiler"
        list_fields = ['baslama_tarihi', 'bitis_tarihi', 'istisnai_ilgi_nevi', 'kha_durum']
        search_fields = ['istisnai_ilgi_nevi', 'kha_durum']

    def __unicode__(self):
        return '%s %s %s' % (self.kayit_no, self.istisnai_nevi_ilgi, self.kha_durum)


class HizmetKayitlari(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    gorev = field.String("Görev", index=True)
    unvan_kod = field.Integer("Unvan Kod", index=True)
    yevmiye = field.String("Yevmiye", index=True)
    ucret = field.String("Ücret", index=True)
    hizmet_sinifi = field.Integer("Hizmet Sınıfı", index=True, choices="hizmet_sinifi")
    kadro_derece = field.Integer("Kadro Derecesi", index=True)
    odeme_derece = field.Integer("Ödeme Derecesi", index=True)
    odeme_kademe = field.Integer("Ödeme Kademesi", index=True)
    odeme_ekgosterge = field.Integer("Ödeme Ek Göstergesi", index=True)
    kazanilmis_hak_ayligi_derece = field.Integer("Kazanılmış Hak Aylığı Derecesi", index=True)
    kazanilmis_hak_ayligi_kademe = field.Integer("Kazanılmış Hak Aylığı Kademesi", index=True)
    kazanilmis_hak_ayligi_ekgosterge = field.Integer("Kazanılmış Hak Aylığı Ek Göstergesi",
                                                     index=True)
    emekli_derece = field.Integer("Emekli Derecesi", index=True)
    emekli_kademe = field.Integer("Emekli Kademe", index=True)
    emekli_ekgosterge = field.Integer("Emekli Ek Göstergesi", index=True)
    sebep_kod = field.Integer("Sebep Kodu", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Kayıt"
        verbose_name_plural = "Kayıtlar"
        list_fields = ['unvan_kod', 'gorev', 'yevmiye', 'ucret', 'hizmet_sinifi']
        search_fields = ['unvan_kod', 'gorev', 'yevmiye']

    def __unicode__(self):
        return '%s %s %s' % (self.unvan_kod, self.hizmet_sinifi, self.gorev)


class AskerlikKayitlari(Model):
    askerlik_nevi = field.Integer("Askerlik Nevi", index=True, choices="askerlik_nevi")
    baslama_tarihi = field.Date("Başlama Tarihi", index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
    kayit_no = field.String("Kayıt No", index=True)
    kita_baslama_tarihi = field.Date("Kıta Başlama Tarihi", index=True, format="%d.%m.%Y")
    kita_bitis_tarihi = field.Date("Kıta Bitiş Tarihi", index=True, format="%d.%m.%Y")
    muafiyet_neden = field.String("Muafiyet Neden", index=True)
    sayilmayan_gun_sayisi = field.Integer("Sayılmayan Gün Sayısı", index=True)
    sinif_okulu_sicil = field.String("Sınıf Okulu Sicil", index=True)
    subayliktan_erlige_gecis_tarihi = field.Date("Subaylıktan Erliğe Geçiş Tarihi", index=True,
                                                 format="%d.%m.%Y")
    subay_okulu_giris_tarihi = field.Date("Subay Okulu Giriş Tarihi", index=True, format="%d.%m.%Y")
    tckn = field.String("TC Kimlik No", index=True)
    tegmen_nasp_tarihi = field.Date("Teğmen Nasp Tarihi", index=True, format="%d.%m.%Y")
    gorev_yeri = field.String("Görev Yeri", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    astegmen_nasp_tarihi = field.Date("Asteğmen Nasp Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Kayıt"
        verbose_name_plural = "Kayıtlar"
        list_fields = ['askerlik_nevi', 'kita_baslama_tarihi', 'gorev_yeri']
        search_fields = ['askerlik_nevi', 'gorev_yeri', 'tckn']

    def __unicode__(self):
        return '%s %s %s %s' % (
            self.askerlik_nevi, self.kayit_no, self.kita_baslama_tarihi, self.gorev_yeri)


class HitapSebep(Model):
    sebep_no = field.Integer("Sebep No", index=True)
    ad = field.String("Sebep Adı", index=True)
    nevi = field.Integer("Sebep Nevi", index=True)
    zorunlu_alan = field.String("Zorunlu ALan")

    class Meta:
        app = 'Personel'
        verbose_name = "Hitap Sebep Kodu"
        verbose_name_plural = "Hitap Sebep Kodları"
        list_fields = ['sebep_no', 'ad', 'nevi', 'zorunlu_alan']
        search_fields = ['sebep_no', 'ad']

    def __unicode__(self):
        return '%s - %s' % (self.sebep_no, self.ad)
