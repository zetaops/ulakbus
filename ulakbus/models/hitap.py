# -*- coding:utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from personel import Personel
from pyoko import Model, field, Node
from auth import Role


class HizmetKurs(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kursa Kayıt No", index=True)
    kurs_ogrenim_suresi = field.Integer("Kurs Öğrenim Süresi", index=True)
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True)
    kurs_nevi = field.String("Kurs Nevi", index=True)
    bolum_ad = field.String("Bölüm Adı", index=True)
    okul_ad = field.String("Okul Adı", index=True)
    ogrenim_yeri = field.String("Öğrenim Yeri", index=True)
    denklik_tarihi = field.Date("Denklik Tarihi", index=True)
    denklik_okulu = field.String("Denklik Okulu", index=True)
    denklik_bolum = field.String("Denklik Bölüm", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)


class HizmetOkul(Model):
    kayit_no = field.String("Kayıt No", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    ogrenim_durumu = field.Integer("Öğrenim Durumu", index=True)
    mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True)
    okul_ad = field.String("Okul Adı", index=True)
    bolum = field.String("Bölüm", index=True)
    ogrenim_yer = field.String("Öğrenim Yeri", index=True)
    denklik_tarihi = field.Date("Denklik Tarihi", index=True)
    denklik_okul = field.String("Denklik Okul", index=True)
    denklik_bolum = field.String("Denklik Bölüm", index=True)
    ogrenim_suresi = field.Integer("Öğrenim Süresi", index=True)
    hazirlik = field.Boolean("Hazırlık", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)


class HizmetMahkeme(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("kayıt No", index=True)
    mahkeme_ad = field.String("Mahkeme Adı", index=True)
    sebep = field.Integer("Mahkeme Sebebi", index=True)
    karar_tarihi = field.Date("Mahkeme Karar Tarihi", index=True)
    karar_sayisi = field.Integer("Karar Sayısı", index=True)
    kesinlesme_tarihi = field.Date("Kesinleşme Tarihi", index=True)
    asil_dogum_tarihi = field.Date("Asıl Doğum Tarihi", index=True)
    tashih_dogum_tarihi = field.Date("Tashih Doğum Tarihi", index=True)
    asil_ad = field.String("Asıl Ad", index=True)
    tashih_ad = field.String("Tashih Ad", index=True)
    asil_soyad = field.String("Asıl Soyad", index=True)
    tashih_soyad = field.String("Tashih Soyad", index=True)
    gecerli_dogum_tarihi = field.Date("Geçerli Doğum Tarihi", index=True)
    aciklama = field.String("Açıklama", index=True)
    gun_sayisi = field.Integer("Gün Sayısı", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)


class HizmetBirlestirme(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    sgk_nevi = field.Integer("SGK Nevi", index=True)
    sgk_sicil_no = field.String("SGK Sicil No", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True)
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True)
    sure = field.Integer("Süre", index=True)
    kamuIsyeri_ad = field.String("Kamu İşyeri Adı", index=True)
    ozel_isyeri_ad = field.String("Özel İşyeri Adı", index=True)
    bag_kur_meslek = field.String("Bağ-Kur Meslek", index=True)
    ulke_kod = field.Integer("Ülke Kodu", index=True)
    banka_sandik_kod = field.Integer("Banka Sandık Kodu", index=True)
    kidem_tazminat_odeme_durumu = field.String("Kıdem Tazminat Ödeme Durumu", index=True)
    ayrilma_nedeni = field.String("Ayrılma Nedeni", index=True)
    kha_durum = field.String("KHA Durum", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)


class HizmetTazminat(Model):
    kayit_no = field.String("Kayıt No", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    unvan_kod = field.Integer("Ünvan Kodu", index=True)
    makam = field.Integer("Makam", index=True)
    gorev = field.Integer("Görev", index=True)
    temsil = field.Integer("Temsil", index=True)
    tazminat_tarihi = field.Date("Tazminat Tarihi", index=True)
    tazminat_bitis_tarihi = field.Date("Tazminat Bitiş Tarihi", index=True)
    kadrosuzluk = field.Integer("Kadrosuzluk", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)


class HizmetUnvan(Model):
    kayit_no = field.String("Hizmet Kayıt No", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    unvan_kod = field.Integer("Ünvan Kodu", index=True)
    unvan_tarihi = field.Date("Ünvan Tarihi", index=True)
    unvan_bitis_tarihi = field.Date("Ünvan Bitiş Tarihi", index=True)
    hizmet_sinifi = field.String("Hizmet Sınıfı", index=True)
    asil_vekil = field.String("Asıl Vekil", index=True)
    atama_sekli = field.String("Atama Sekli", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)
    fhz_orani = field.Float("FHZ Oranı", index=True)


class HizmetAcikSure(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    acik_sekil = field.Integer("Açığa Alınma Şekli", index=True)
    durum = field.Integer("Durum", index=True)
    hizmet_durum = field.Integer("Hizmet Durumu", index=True)
    husus = field.String("Husus", index=True)
    aciga_alinma_tarih = field.Date("Açığa Alınma Tarihi", index=True)
    goreve_son_tarih = field.Date("Göreve Son Tarih", index=True)
    goreve_iade_istem_tarih = field.Date("Göreve İade İstem Tarihi", index=True)
    goreve_iade_tarih = field.Date("Göreve İade Tarihi", index=True)
    acik_aylik_bas_tarih = field.Date("Açık Aylık Başlama Tarihi", index=True)
    acik_aylik_bit_tarih = field.Date("Açık Aylık Bitiş Tarihi", index=True)
    goreve_son_aylik_bas_tarih = field.Date("Göreve sonlandırma aylık başlangıç tarihi", index=True)
    goreve_son_aylik_bit_tarih = field.Date("Göreve sonlandırma aylık bitiş tarihi", index=True)
    s_yonetim_kald_tarih = field.Date("Sıkı Yönetim Kaldırıldığı Tarih", index=True)
    aciktan_atanma_tarih = field.Date("Açıktan Atanma Tarihi", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)


class HizmetBorclanma(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    ad = field.String("Ad", index=True)
    soyad = field.String("Soyad", index=True)
    emekli_sicil = field.String("Emekli Sicili", index=True)
    derece = field.Integer("Derece", index=True)
    kademe = field.Integer("Kademe", index=True)
    ekgosterge = field.Integer("Ek Gösterge", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True)
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True)
    gun_sayisi = field.Integer("Gün Sayısı", index=True)
    kanun_kod = field.Integer("Kanun Kodu", index=True)
    borc_nevi = field.String("Borç Nevi", index=True)
    toplam_tutar = field.Float("Toplam Tutar", index=True)
    odenen_miktar = field.Float("Ödenen Miktar", index=True)
    calistigi_kurum = field.String("çalıştığı Kurum", index=True)
    isyeri_il = field.String("İşyeri İli", index=True)
    isyeri_ilce = field.String("İşyeri İlçesi", index=True)
    borclanma_tarihi = field.Date("Borçlanma Tarihi", index=True)
    odeme_tarihi = field.Date("Ödeme Tarihi", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)


class HizmetIHS(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True)
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True)
    ihz_nevi = field.Integer("İHZ Nevi", index=True)


class HizmetIstisnaiIlgi(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True)
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True)
    gun_sayisi = field.Integer("Gün Sayısı", index=True)
    istisnai_ilgi_nevi = field.Integer("İstisnai İlgi Nevi", index=True)
    kha_durum = field.String("KHA Durum", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)


class HizmetKayitlari(Model):
    tckn = field.String("TC Kimlik No", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True)
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True)
    gorev = field.String("Görev", index=True)
    unvan_kod = field.Integer("Unvan Kod", index=True)
    yevmiye = field.String("Yevmiye", index=True)
    ucret = field.String("Ücret", index=True)
    hizmet_sinifi = field.String("Hizmet Sınıfı", index=True)
    kadro_derece = field.Integer("Kadro Derecesi", index=True)
    odeme_derece = field.Integer("Ödeme Derecesi", index=True)
    odeme_kademe = field.Integer("Ödeme Kademesi", index=True)
    odeme_ekgosterge = field.Integer("Ödeme Ek Göstergesi", index=True)
    kazanilmis_hak_ayligi_derece = field.Integer("Kazanılmış Hak Aylığı Derecesi", index=True)
    kazanilmis_hak_ayligi_kademe = field.Integer("Kazanılmış Hak Aylığı Kademesi", index=True)
    kazanilmis_hak_ayligi_ekgosterge = field.Integer("Kazanılmış Hak Aylığı Ek Göstergesi", index=True)
    emekli_derece = field.Integer("Emekli Derecesi", index=True)
    emekli_kademe = field.Integer("Emekli Kademe", index=True)
    emekli_ekgosterge = field.Integer("Emekli Ek Göstergesi", index=True)
    sebep_kod = field.Integer("Sebep Kodu", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)


class AskerlikKayitlari(Model):
    askerlik_nevi = field.Integer("Askerlik Nevi", index=True)
    baslama_tarihi = field.Date("Başlama Tarihi", index=True)
    bitis_tarihi = field.Date("Bitiş Tarihi", index=True)
    kayit_no = field.String("Kayıt No", index=True)
    kita_baslama_tarihi = field.Date("Kıta Başlama Tarihi", index=True)
    kita_bitis_tarihi = field.Date("Kıta Bitiş Tarihi", index=True)
    muafiyet_neden = field.String("Muafiyet Neden", index=True)
    sayilmayan_gun_sayisi = field.Integer("Sayılmayan Gün Sayısı", index=True)
    sinif_okulu_sicil = field.String("Sınıf Okulu Sicil", index=True)
    subayliktan_erlige_gecis_tarihi = field.Date("Subaylıktan Erliğe Geçiş Tarihi", index=True)
    subay_okulu_giris_tarihi = field.Date("Subay Okulu Giriş Tarihi", index=True)
    tckn = field.String("TC Kimlik No", index=True)
    tegmen_nasp_tarihi = field.Date("Teğmen Nasp Tarihi", index=True)
    gorev_yeri = field.String("Görev Yeri", index=True)
    kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)
    astegmen_nasp_tarihi = field.Date("Asteğmen Nasp Tarihi", index=True)


class Birim(Model):
    type = field.String("Tip", index=True)
    name = field.String("Ad", index=True)
    # parent = Birim()


class Atama(Model):
    kurum_sicil_no = field.String("Kurum Sicil No", index=True)
    personel_tip = field.Integer("Personel Tipi", index=True)
    hizmet_sinif = field.Integer("Hizmet Sınıfı", index=True)
    statu = field.Integer("Statü", index=True)
    gorev_suresi_baslama = field.Date("Görev Süresi Başlama", index=True)
    gorev_suresi_bitis = field.Date("Görev Süresi Bitiş", index=True)
    goreve_baslama_tarihi = field.Date("Göreve Başlama Tarihi", index=True)
    ibraz_tarihi = field.Date("İbraz Tarihi", index=True)
    durum = field.Integer("Durum", index=True)
    mecburi_hizmet_suresi = field.Date("Mecburi Hizmet Süresi", index=True)
    nereden = field.Integer("Nereden", index=True)
    atama_aciklama = field.String("Atama Açıklama", index=True)
    goreve_baslama_aciklama = field.String("Göreve Başlama Açıklama", index=True)
    kadro_unvan = field.Integer("Kadro Unvan", index=True)
    kadro_derece = field.Integer("Kadro Derece", index=True)


class Kadro(Model):
    durum = field.Integer("Durum", index=True)
    unvan = field.Integer("Unvan", index=True)
    derece = field.Integer("Derece", index=True)
    rol = Role()
    aciklama = field.String("Açıklama", index=True)


class Izin(Model):
    tip = field.Integer("Tip", index=True)
    baslangic = field.Date("Başlangıç", index=True)
    bitis = field.Date("Bitiş", index=True)
    onay = field.Date("Onay", index=True)
    adres = field.String("Adres", index=True)
    telefon = field.String("Telefon", index=True)
    personel = Personel()
    vekil = Personel()


class UcretsizIzin(Model):
    tip = field.Integer("Tip", index=True)
    baslangic = field.Date("Başlangıç", index=True)
    bitis = field.Date("Bitiş", index=True)
    onay = field.Date("Onay", index=True)

    class Donus(Node):
        donus_sebep = field.Integer("Dönüş Sebebi", index=True)
        ise_baslama = field.Date("İşe Başlama", index=True)
