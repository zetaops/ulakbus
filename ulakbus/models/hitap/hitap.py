# -*- coding:utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ..personel import Personel
from pyoko import Model, field
import datetime
from .hitap_sebep import HitapSebep


class NufusKayitlari(Model):
    tckn = field.String("Sigortalının TC Kimlik No", index=True)
    ad = field.String("Adı", index=True)
    soyad = field.String("Soyadı", index=True)
    ilk_soy_ad = field.String("Memuriyete Girişteki İlk Soyadı", index=True)
    dogum_tarihi = field.Date("Doğum Tarihi", index=True, format="%d.%m.%Y")
    cinsiyet = field.String("Cinsiyet", index=True)
    emekli_sicil_no = field.Integer("Emekli Sicil No", index=True)
    memuriyet_baslama_tarihi = field.Date("Memuriyete İlk Başlama Tarihi", index=True,
                                          format="%d.%m.%Y")
    kurum_sicil = field.String("Kurum Sicili", index=True)
    maluliyet_kod = field.Integer("Malul Kod", index=True, choices="maluliyet_kod")
    yetki_seviyesi = field.String("Yetki Seviyesi", index=True)
    aciklama = field.String("Açıklama", index=True)
    kuruma_baslama_tarihi = field.Date("Kuruma Başlama Tarihi", index=True, format="%d.%m.%Y")
    gorev_tarihi_6495 = field.Date("Emeklilik Sonrası Göreve Başlama Tarihi", index=True,
                                   format="%d.%m.%Y")
    emekli_sicil_6495 = field.Integer("2. Emekli Sicil No", index=True)
    durum = field.Boolean("Durum", index=True)
    sebep = field.Integer("Sebep", index=True)
    sync = field.Integer("Senkronize", index=True)
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
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kursa Kayıt No", index=True)
    kurs_ogrenim_suresi = field.Integer("Kurs Öğrenim Süresi", index=True)
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True, format="%d.%m.%Y")
    kurs_nevi = field.Integer("Kurs Nevi", index=True, choices="kurs_nevi")
    bolum_ad = field.Integer("Bölüm Adı", index=True,
                             choices="bolum_adi")  # TODO: serviste karsiligi yok
    okul_ad = field.Integer("Okul Adı", index=True,
                            choices="okul_adi")  # TODO: servisten gelen string
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
        hitap_service_prefix = "HitapKurs"

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
        hitap_service_prefix = "HitapOkul"

    def __unicode__(self):
        return '%s %s %s' % (self.kayit_no, self.bolum, self.okul_ad)


class HizmetMahkeme(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
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
        hitap_service_prefix = "HitapMahkeme"

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
    kamu_isyeri_ad = field.String("Kamu İşyeri Adı", index=True)
    ozel_isyeri_ad = field.String("Özel İşyeri Adı", index=True)
    bag_kur_meslek = field.String("Bağ-Kur Meslek", index=True)
    ulke_kod = field.Integer("Ülke Kodu", index=True)
    banka_sandik_kod = field.Integer("Banka Sandık Kodu", index=True, choices="banka_kod")
    kidem_tazminat_odeme_durumu = field.String("Kıdem Tazminat Ödeme Durumu", index=True,
                                               choices="kidem_tazminat_odeme_durumu")
    ayrilma_nedeni = field.String("Ayrılma Nedeni", index=True)
    kha_durum = field.Integer("KHA Durum", index=True, choices="kha_durum")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
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
        hitap_service_prefix = "HitapTazminat"

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
        hitap_service_prefix = "HitapUnvan"

    def __unicode__(self):
        return '%s %s' % (self.unvan_kod, self.hizmet_sinifi)


class HizmetAcikSure(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    acik_sekil = field.Integer("Açığa Alınma Şekli", index=True, choices="acik_sekli")
    iade_sekil = field.Integer("İade Şekil", index=True)
    hizmet_durum = field.Integer("Hizmet Durumu", index=True, choices="hizmet_durumu")
    husus = field.Integer("Husus", index=True, choices="husus")
    husus_aciklama = field.String("Husus Açıklaması", index=True)
    aciga_alinma_tarih = field.Date("Açığa Alınma Tarihi", index=True, format="%d.%m.%Y")
    goreve_son_tarih = field.Date("Göreve Son Tarih", index=True, format="%d.%m.%Y")
    goreve_iade_istem_tarih = field.Date("Göreve İade İstem Tarihi", index=True, format="%d.%m.%Y")
    goreve_iade_tarih = field.Date("Göreve İade Tarihi", index=True, format="%d.%m.%Y")
    acik_aylik_bas_tarih = field.Date("Açık Aylık Başlama Tarihi", index=True, format="%d.%m.%Y")
    acik_aylik_bit_tarih = field.Date("Açık Aylık Bitiş Tarihi", index=True, format="%d.%m.%Y")
    goreve_son_aylik_bas_tarih = field.Date("Göreve Sonlandırma Aylık Başlangıç Tarihi", index=True,
                                            format="%d.%m.%Y")
    goreve_son_aylik_bit_tarih = field.Date("Göreve Sonlandırma Aylık Bitiş Tarihi", index=True,
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
        hitap_service_prefix = "HitapAcikSure"

    def __unicode__(self):
        return '%s %s %s' % (self.iade_sekil, self.kayit_no, self.aciga_alinma_tarih)


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
        hitap_service_prefix = "HitapBorclanma"

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
        hitap_service_prefix = "HitapIHS"

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
    sebep_kod = HitapSebep("Hitap Sebep Kodu")
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True, format="%d.%m.%Y")
    sync = field.Integer("Senkronize", index=True)
    personel = Personel()

    # hizmet cetveline birden cok modelden veri girilmektedir. bu alanda, hizmet
    # cetveli kaydini olusturan diger modeldeki kaydin key i saklanir.
    model_key = field.String()

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
            self.unvan_kod = self.personel.kadro.unvan
            self.hizmet_sinifi = self.personel.atama.hizmet_sinifi
            self.kadro_derece = self.personel.kadro_derece
            self.odeme_derece = self.personel.gorev_ayligi_derece
            self.odeme_kademe = self.personel.gorunen_gorev_ayligi_kademe
            self.odeme_ekgosterge = self.personel.gorev_ayligi_ekgosterge
            self.kazanilmis_hak_ayligi_derece = self.personel.kazanilmis_hak_derece
            self.kazanilmis_hak_ayligi_kademe = self.personel.gorunen_kazanilmis_hak_kademe
            self.kazanilmis_hak_ayligi_ekgosterge = self.personel.kazanilmis_hak_ekgosterge
            self.emekli_derece = self.personel.emekli_muktesebat_derece
            self.emekli_kademe = self.personel.gorunen_emekli_muktesebat_kademe
            self.emekli_ekgosterge = self.personel.emekli_muktesebat_ekgosterge
            self.save()

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
        hitap_service_prefix = "HitapAskerlik"

    def __unicode__(self):
        return '%s %s %s %s' % (
            self.askerlik_nevi, self.kayit_no, self.kita_baslama_tarihi, self.gorev_yeri)