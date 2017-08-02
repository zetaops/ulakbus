# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Okutman
from ulakbus.models.form import Form
from ulakbus.models import Room, Personel, Role, User
from ulakbus.models.demirbas import Demirbas
from pyoko.lib.utils import lazy_property

from zengine.lib.translation import gettext_lazy as __, gettext as _

from pyoko import Model, field, ListNode

talep_durum = [(1, 'Yeni'),
               (2, 'Silinecek'),
               (3, 'Düzenlendi'),
               (4, 'Düzenlenmedi')]


class BAPProjeTurleri(Model):
    kod = field.String(__(u"Proje tür kodu"))
    ad = field.String(__(u"Proje türünün Adı"))
    aciklama = field.Text(__(u"Proje türüne dair açıklama"))
    min_sure = field.Integer(__(u"Projenin minumum süreceği ay sayısı"))
    max_sure = field.Integer(__(u"Projenin maximum süreceği ay sayısı"))
    butce_ust_limit = field.Float(__(u"Projenin üst limiti"))
    gerceklestirme_gorevlisi_yurutucu_ayni_mi = field.Boolean(
        __(u"Projenin gerçekleştirme görevlisi ile yürütücüsü aynı kişi mi?"))

    class Meta:
        verbose_name = __(u"Proje Türü")
        verbose_name_plural = __(u"Proje Türleri")
        list_fields = ['kod', 'ad', 'min_sure', 'max_sure', 'butce_ust_limit']
        list_filters = ['kod', ]
        search_fields = ['kod', 'ad', 'min_sure', 'max_sure', 'butce_ust_limit']

    class Belgeler(ListNode):
        class Meta:
            title = __(u"Projede Kullanılacak Belgeler")

        ad = field.String(__(u"Belgenin İsmi"))
        gereklilik = field.Boolean(__(u"Belgenin Zorunluluğu"), required=False)

    class Formlar(ListNode):
        class Meta:
            title = __(u"Projede Kullanılacak Formlar")

        proje_formu = Form()
        gereklilik = field.Boolean(__(u"Formun Gerekliliği"), default=False)
        secili = field.Boolean(__(u"Projeye Dahil Et"), default=False)

    def __unicode__(self):
        return "%s: %s" % (self.kod, self.ad)


class BAPTakvim(Model):
    class Meta:
        search_fields = ['ProjeTuru', 'aciklama', ]
        list_fields = ['donem', '_takvim_turu', '_tarih', 'takvim_aciklama']

    class ProjeTuru(ListNode):
        class Meta:
            title = __(u"Proje Türü")

        proje_turu = BAPProjeTurleri()

    class OnemliTarihler(ListNode):
        class Meta:
            title = __(u"Önemli Tarihler")

        baslangic_tarihi = field.Date(__(u"Başlangıç Tarihi"))
        bitis_tarihi = field.Date(__(u"Bitiş Tarihi"))
        aciklama = field.Integer(__(u"Açıklama Seçiniz"), choices='onemli_tarih_aciklama',
                                 default=1)

    takvim_aciklama = field.Text(__(u"Takvim Açıklaması"))
    donem = field.Integer(__(u"Takvimin Yayınlanacağı Dönem"))

    def __unicode__(self):
        return "%s. Dönem: %s" % (self.donem, self.takvim_aciklama)

    def _takvim_turu(self):
        if self.ProjeTuru:
            return ''.join(["""
            %s\n""" % proje.proje_turu for proje in self.ProjeTuru])
        else:
            return """
            Genel Takvim"""

    def _tarih(self):
        return ''.join(["""
        %s / %s\n""" % (tarih.baslangic_tarihi.strftime("%d.%m.%Y"),
                        tarih.bitis_tarihi.strftime("%d.%m.%Y")) for tarih in
                        self.OnemliTarihler])

    _takvim_turu.title = __(u"Proje Türü")
    _tarih.title = __(u"Tarih")


class BAPIs(Model):
    class Meta:
        verbose_name = __(u"Bap İş Türü")
        verbose_name_plural = __(u"Bap İş Türleri")

    ad = field.String(__(u"Bap İş"))
    baslama_tarihi = field.Date(__(u"Başlama Tarihi"))
    bitis_tarihi = field.Date(__(u"Bitiş Tarihi"))

    def __unicode__(self):
        return "%s" % self.ad


class BAPProje(Model):
    durum = field.Integer(_(u"Durum"), choices='bap_proje_durum')
    basvuru_rolu = Role()

    # Komisyon kararıyla doldurulacak alanlar
    proje_no = field.Integer(_(u"Proje No"))
    kabul_edilen_baslama_tarihi = field.Date(_(u"Kabul Edilen Başlama Tarihi"))
    kabul_edilen_butce = field.Float(_(u"Kabul Edilen Bütçe"))

    # Başvuruda doldurulacak alanlar
    yurutucu = Okutman()
    gerceklestirme_gorevlisi = Personel()
    harcama_yetkilisi = Personel()
    muhasebe_yetkilisi = Personel()

    tur = BAPProjeTurleri()

    ad = field.String(_(u"Proje Adı"))
    sure = field.Integer(_(u"Süre(Ay Cinsinden Olmalıdır)"))
    anahtar_kelimeler = field.String(_(u"Anahtar Kelimeler(Virgülle Ayrılmış Şekilde Olmalıdır)"))
    teklif_edilen_baslama_tarihi = field.Date(_(u"Teklif Edilen Başlama Tarihi"))
    teklif_edilen_butce = field.Float(_(u"Teklif Edilen Bütçe"))

    konu_ve_kapsam = field.Text(_(u"Konu ve Kapsam"), min_length=650, max_length=1000)
    literatur_ozeti = field.Text(_(u"Literatür Özeti"), min_length=650, max_length=1000)
    ozgun_deger = field.Text(_(u"Özgün Değer"), min_length=650, max_length=1000)
    hedef_ve_amac = field.Text(_(u"Hedef ve Amaç"), min_length=650, max_length=1000)
    yontem = field.Text(_(u"Yöntem"), min_length=650, max_length=1000)
    basari_olcutleri = field.Text(_(u"Başarı Ölçütleri"), min_length=650, max_length=1000)
    b_plani = field.Text(_(u"B Planı"), min_length=650, max_length=1000)

    bitis_tarihi = field.Date(_(u"Tamamlanma Tarihi"))

    class ProjeBelgeleri(ListNode):
        class Meta:
            verbose_name = __(u"Proje Belgesi")
            verbose_name_plural = __(u"Proje Belgeleri")

        belge = field.File(_(u"Belge"), random_name=True)
        belge_aciklamasi = field.String(_(u"Belge Açıklaması"), required=False)

    class ArastirmaOlanaklari(ListNode):
        class Meta:
            verbose_name = __(u"Araştırma Olanağı")
            verbose_name_plural = __(u"Araştırma Olanakları")

        lab = Room()
        demirbas = Demirbas()
        personel = Personel()

    class ProjeCalisanlari(ListNode):
        class Meta:
            verbose_name = __(u"Proje Çalışanı")
            verbose_name_plural = __(u"Proje Çalışanları")

        ad = field.String(_(u"Ad"))
        soyad = field.String(_(u"Soyad"))
        nitelik = field.String(_(u"Nitelik"))
        calismaya_katkisi = field.String(_(u"Çalışmaya Katkısı"))
        kurum = field.String(_(u"Kurum"))

    class UniversiteDisiUzmanlar(ListNode):
        class Meta:
            verbose_name = __(u"Üniversite Dışı Uzman")
            verbose_name_plural = __(u"Üniversite Dışı Uzmanlar")

        ad = field.String(_(u"Ad"))
        soyad = field.String(_(u"Soyad"))
        unvan = field.String(_(u"Unvan"))
        kurum = field.String(_(u"Kurum"))
        tel = field.String(_(u"Telefon"))
        faks = field.String(_(u"Faks"))
        eposta = field.String(_(u"E-posta"))

    class UniversiteDisiDestek(ListNode):
        class Meta:
            verbose_name = __(u"Üniversite Dışı Destek")
            verbose_name_plural = __(u"Üniversite Dışı Destekler")

        kurulus = field.String(_(u"Destekleyen Kurulus"))
        tur = field.String(_(u"Destek Türü"))
        destek_miktari = field.Float(_(u"Destek Miktarı"))
        verildigi_tarih = field.Date(_(u"Verildiği Tarih"))
        sure = field.Integer(_(u"Süresi(Ay CinsindenBA)"))
        destek_belgesi = field.File(_(u"Destek Belgesi"), random_name=True)
        destek_belgesi_aciklamasi = field.String(_(u"Belge Açıklaması"), required=False)

    # Koordinatörlük tarafından atanacak
    class BAPHakem(ListNode):
        class Meta:
            verbose_name = __(u"Hakem")
            verbose_name_plural = __(u"Hakemler")

        ad = field.String(_(u"Ad"))
        soyad = field.String(_(u"Soyad"))
        # todo hakemler sorulacak
        birim = field.String(_(u"Birim"))

    class ProjeIslemGecmisi(ListNode):
        class Meta:
            verbose_name = __(u"İşlem Geçmişi")
            verbose_name_plural = __(u"İşlem Geçmişi")

        eylem = field.String(_(u"Eylem"))
        aciklama = field.String(_(u"Açıklama"))
        tarih = field.DateTime(_(u"Tarih"))

    class ProjeDegerlendirmeleri(ListNode):
        class Meta:
            verbose_name = __(u"Proje Değerlendirmesi")
            verbose_name_plural = __(u"Proje Değerlendirmeleri")

        hakem = Okutman()
        form_data = field.Text(_(u"Form Data"))
        hakem_degerlendirme_durumu = field.Integer(_(u"Hakem/Değerlendirme Durumu"),
                                                   choices='bap_proje_hakem_degerlendirme_durum')
        degerlendirme_sonucu = field.Integer(_(u"Değerlendirme Sonucu"),
                                             choices="bap_proje_degerlendirme_sonuc")

    @lazy_property
    def yurutucu_diger_projeler(self):
        return self.objects.filter(yurutucu=self.yurutucu)

    @lazy_property
    def proje_kodu(self):
        return "%s%s" % (self.tur.kod, self.proje_no)

    class Meta:
        app = 'BAP'
        verbose_name = _(u"BAP Proje")
        verbose_name_plural = _(u"BAP Projeler")
        list_fields = ['ad', 'yurutucu']
        search_fields = ['ad']
        list_filters = ['durum']
        unique_together = [('tur', 'proje_no')]

    def __unicode__(self):
        return "%s: %s" % (self.ad, self.yurutucu.__unicode__())


class BAPIsPaketi(Model):
    class Meta:
        verbose_name = __(u"Bap İş Paketi")
        verbose_name_plural = __(u"Bap İş Paketleri")
        unique_together = [('ad', 'proje')]

    ad = field.String(__(u"İş Paketinin Adı"))
    baslama_tarihi = field.Date(__(u"Başlama Tarihi"))
    bitis_tarihi = field.Date(__(u"Bitiş Tarihi"))
    proje = BAPProje()

    class Isler(ListNode):
        isler = BAPIs()

    def __unicode__(self):
        return "%s" % self.ad


class BAPFirma(Model):
    class Meta:
        verbose_name = __(u"Firma")
        verbose_name_plural = __(u"Firmalar")
        list_fields = ['ad', 'vergi_no']
        unique_together = [('vergi_no', 'vergi_dairesi')]

    ad = field.String(__(u"Firma Adı"), required=True)
    telefon = field.String(__(u"Telefon"), required=True)
    adres = field.String(__(u"Adres"), required=True)
    e_posta = field.String(__(u"E-posta Adresi"), required=True, unique=True)
    vergi_no = field.String(__(u"Vergi Kimlik Numarası"), required=True)
    vergi_dairesi = field.Integer(__(u"Vergi Dairesi"), choices='vergi_daireleri', required=True)
    faaliyet_belgesi = field.File(_(u"Firma Faaliyet Belgesi"), random_name=False, required=True)
    faaliyet_belgesi_verilis_tarihi = field.Date(__(u"Faaliyet Belgesi Veriliş Tarihi"),
                                                 required=True)
    durum = field.Integer(__(u"Durum"), choices='bap_firma_durum')

    class Yetkililer(ListNode):
        yetkili = User()

    def __unicode__(self):
        return "%s" % self.ad


class BAPTeknikSartname(Model):
    class Meta:
        verbose_name = __(u"Teknik Şartname")
        verbose_name_plural = __(u"Teknik Şartnameler")

    sartname_dosyasi = field.File(__(u"Şartname Dosyası"), random_name=True)
    aciklama = field.String(__(u"Açıklama"))
    ilgili_proje = BAPProje()

    def __unicode__(self):
        return "%s" % self.aciklama


class BAPButcePlani(Model):
    class Meta:
        verbose_name = __(u"Bap Bütçe Planı")
        verbose_name_plural = __(u"Bap Bütçe Planları")
        list_fields = ['_muhasebe_kod', 'kod_adi', 'ad', 'birim_fiyat', 'adet',
                       'toplam_fiyat', 'teknik_sartname']

    # Öğretim üyesinin seçeceği muhasebe kodları
    muhasebe_kod_genel = field.Integer(__(u"Muhasebe Kod"),
                                       choices='bap_ogretim_uyesi_gider_kodlari', default=1)


    muhasebe_kod = field.String(__(u"Muhasebe Kod"),
                                choices='analitik_butce_dorduncu_duzey_gider_kodlari',
                                default="03.2.6.90")
    kod_adi = field.String(__(u"Kod Adı"))
    ad = field.String(__(u"Alınacak Malzemenin Adı"))
    birim_fiyat = field.Float(__(u"Birim Fiyat"),
                              help_text=__(u"Birim fiyatlar KDV dahil fiyatlar olmalıdır!"))
    adet = field.Integer(__(u"Adet"))
    toplam_fiyat = field.Float(__(u"Toplam Fiyat"))
    gerekce = field.Text(__(u"Gerekçe"))
    ilgili_proje = BAPProje()
    onay_tarihi = field.Date(__(u"Onay Tarihi"))
    durum = field.Integer(__(u"Durum"), choices=talep_durum, default=1)
    ozellik = field.Text(__(u"Özellik(Şartname Özeti)"), required=True)
    kazanan_firma = BAPFirma()

    teknik_sartname = BAPTeknikSartname()

    def __unicode__(self):
        return "%s / %s / %s" % (self.muhasebe_kod or self.muhasebe_kod_genel, self.kod_adi,
                                 self.ad)

    def _muhasebe_kod(self):
        return self.muhasebe_kod or self.muhasebe_kod_genel

    _muhasebe_kod.title = __(u"Muhasebe Kodu")


class BAPEtkinlikProje(Model):
    class Meta:
        verbose_name = __(u"Bilimsel Etkinliklere Katılım Desteği")
        verbose_name_plural = __(u"Bilimsel Etkinliklere Katılım Destekleri")
        list_filters = ['durum']

    ulke = field.String(__(u"Ülke"), required=True)
    sehir = field.String(__(u"Şehir"), required=True)
    bildiri_basligi = field.String(__(u"Etkinlik Başlığı"), required=True)
    baslangic = field.Date(__(u"Başlangıç Tarihi"), required=True)
    bitis = field.Date(__(u"Bitiş Tarihi"), required=True)
    katilim_turu = field.Integer(__(u"Katılım Turu"), required=True,
                                 choices='bap_bilimsel_etkinlik_katilim_turu')
    etkinlik_lokasyon = field.Integer(__(u"Etkinlik Türü"), required=True,
                                      choices="arastirma_hedef_lokasyon")
    basvuru_yapan = Okutman()
    durum = field.Integer(__(u"Durum"), choices='bap_bilimsel_etkinlik_butce_talep_durum')
    onay_tarihi = field.Date(__(u"Onay Tarihi"))

    class EtkinlikButce(ListNode):
        class Meta:
            verbose_name = __(u"Bilimsel Etkinliklere Katılım Desteği Bütçe Planı")
            verbose_name_plural = __(u"Bilimsel Etkinliklere Katılım Desteği Bütçe Planları")

        talep_turu = field.Integer(__(u"Talep Türü"), required=True,
                                   choices='bap_bilimseL_etkinlik_butce_talep_turleri')
        muhasebe_kod = field.String(__(u"Muhasebe Kod"),
                                    choices='analitik_butce_dorduncu_duzey_gider_kodlari',
                                    default="03.2.6.90")
        istenen_tutar = field.Float(__(u"Talep Edilen Tutar"), required=True)

    class Degerlendirmeler(ListNode):
        class Meta:
            verbose_name = __(u"Bilimsel Etkinliklere Katılım Desteği Değerlendirmesi")
            verbose_name_plural = __(u"Bilimsel Etkinliklere Katılım Desteği Değerlendirmeleri")

        aciklama = field.Text(_(u"Açıklama"), required=False)
        degerlendirme_sonuc = field.Integer(_(u"Değerlendirme Sonucu"),
                                            choices='bap_proje_degerlendirme_sonuc')

    def __unicode__(self):
        return "%s | %s" % (self.bildiri_basligi, self.basvuru_yapan.__unicode__())

    def _teknik_sartname(self):
        return "Var" if self.teknik_sartname.aciklama else "Yok"

    _teknik_sartname.title = __(u"Teknik Şartname")


class BAPGundem(Model):
    class Meta:
        verbose_name = __(u"Gündem")
        verbose_name_plural = __(u"Gündemler")
        list_fields = ['_proje_adi', '_proje_yurutucusu', 'gundem_tipi', 'oturum_numarasi',
                       'oturum_tarihi', 'karar_no', 'karar_tarihi']

    proje = BAPProje()
    etkinlik = BAPEtkinlikProje()
    gundem_tipi = field.String(__(u"Gündem Tipi"), choices='bap_komisyon_gundemleri', default=1)
    gundem_aciklama = field.Text(__(u"Gündem Açıklaması"))
    oturum_numarasi = field.Integer(__(u"Oturum Numarası"), default=0)
    oturum_tarihi = field.Date(__(u"Oturum Tarihi"))
    karar_no = field.Integer(__(u"Karar No"), default=0)
    karar = field.Text(__(u"Karar"))
    karar_tarihi = field.Date(__(u"Karar Tarihi"))
    sonuclandi = field.Boolean(__(u"Kararın Sonuçlandırılması"), default=False)

    def _proje_adi(self):
        return "%s" % self.proje.ad if self.proje.key else self.etkinlik.bildiri_basligi

    _proje_adi.title = __(u"Projenin Adı")

    def _proje_yurutucusu(self):
        return "%s %s" % (
            (self.proje.yurutucu.ad, self.proje.yurutucu.soyad) if self.proje.key else (
                self.etkinlik.basvuru_yapan.ad, self.etkinlik.basvuru_yapan.soyad))

    _proje_yurutucusu.title = __(u"Proje Yürütücüsü")

    def __unicode__(self):
        return "Bap Gündem"


class BAPSSS(Model):
    class Meta:
        verbose_name = __(u"Sıkça Sorulan Soru")
        verbose_name_plural = __(u"Sıkça Sorulan Sorular")
        list_fields = ['soru', 'cevap']

    soru = field.Text(__(u"Sıkça Sorulan Soru"))
    cevap = field.Text(__(u"Cevap"))
    yayinlanmis_mi = field.Boolean(__(u"Yayınlanmış mı?"), default=False)

    def __unicode__(self):
        return "%s" % self.soru


class BAPDuyuru(Model):
    class Meta:
        verbose_name = __(u"BAP Duyuru")
        verbose_name_plural = __(u"BAP Duyurular")
        list_fields = ['duyuru_baslik', 'eklenme_tarihi', 'son_gecerlilik_tarihi']

    ekleyen = User()
    eklenme_tarihi = field.Date(__(u"Eklenme Tarihi"))
    son_gecerlilik_tarihi = field.Date(__(u"Son Geçerlilik Tarihi"))
    duyuru_baslik = field.String(__(u"Duyuru Başlığı"))
    duyuru_icerik = field.Text(__(u"Duyuru İçeriği"))
    yayinlanmis_mi = field.Boolean(__(u"Yayınlanmış mı?"), default=False)

    class EkDosyalar(ListNode):
        class Meta:
            verbose_name = __(u"Ek Dosya")
            verbose_name_plural = __(u"Ek Dosyalar")
            list_fields = ['dosya_aciklamasi']

        ek_dosya = field.File(__(u"Ek Dosya Seç"), random_name=True)
        dosya_aciklamasi = field.String(__(u"Dosya Açıklaması"))

    def __unicode__(self):
        return "%s" % self.duyuru_baslik


class BAPSatinAlma(Model):
    class Meta:
        verbose_name = __(u"Bütçe Kalemi Satın Alma")
        verbose_name_plural = __(u"Bütçe Kalemi Satın Almaları")
        list_fields = ['ad', 'teklife_acilma_tarihi', 'teklife_kapanma_tarihi']

    ad = field.String(__(u"Satın Alma Duyuru Adı"))
    teklife_acilma_tarihi = field.DateTime(__(u"Teklife Açılma Tarihi"))
    teklife_kapanma_tarihi = field.DateTime(__(u"Teklife Kapanma Tarihi"))
    sonuclanma_tarihi = field.Date(__(u"Teklifin Sonuçlanma Tarihi"))
    teklif_durum = field.Integer(__(u"Teklif Durum"), choices='bap_satin_alma_durum')
    sorumlu = Role()

    class ButceKalemleri(ListNode):
        butce = BAPButcePlani()

    def __unicode__(self):
        return "%s" % self.ad


class BAPTeklif(Model):
    class Meta:
        verbose_name = __(u"Firma Teklif")
        verbose_name_plural = __(u"Firma Teklifleri")

    firma = BAPFirma()
    satin_alma = BAPSatinAlma()
    durum = field.Integer(__(u"Durum"), choices='bap_teklif_durum')
    ilk_teklif_tarihi = field.DateTime(_(u"İlk Teklif Tarihi"))
    son_degisiklik_tarihi = field.DateTime(_(u"Son Değişiklik Tarihi"))
    sonuclanma_tarihi = field.Date(__(u"Firma Teklifinin Sonuçlanma Tarihi"))
    fiyat_islemesi = field.Boolean(__(u"Fiyat İşlemesi Yapıldı mı?"), default=False)

    class Belgeler(ListNode):
        belge = field.File(_(u"Firma Teklif Belgesi"), random_name=False, required=True)
        aciklama = field.String(__(u"Belge Açıklaması"), required=True)

    def __unicode__(self):
        return "%s-%s" % (self.firma.ad, self.satin_alma.ad)


class BAPTeklifFiyatIsleme(Model):
    class Meta:
        verbose_name = __(u"Teklif Fiyat İşleme")
        verbose_name_plural = __(u"Teklif Fiyat İşlemeleri")

    firma = BAPFirma()
    kalem = BAPButcePlani()
    satin_alma = BAPSatinAlma()
    birim_fiyat = field.Float(__(u"Birim Fiyat"))
    toplam_fiyat = field.Float(__(u"Toplam Fiyat"))

    def __unicode__(self):
        return "%s-%s" % (self.firma.ad, self.kalem.ad)

    @classmethod
    def en_iyi_teklif_veren_ikinci_ve_ucuncu_firmayi_getir(cls, butce):
        firmalar = cls.objects.filter(kalem=butce).exclude(firma=butce.kazanan_firma).order_by(
            '-toplam_fiyat')

        return firmalar[0], firmalar[1]


