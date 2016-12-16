# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
""" Personel Modülü

Bu modül Ulakbüs uygulaması için personel modelini ve  personel ile ilişkili modelleri içerir.

"""
from .hitap.hitap_sebep import HitapSebep
from pyoko.lib.utils import lazy_property

from pyoko import Model, field
from zengine.lib.translation import gettext_lazy as _, gettext
from ulakbus.lib.personel import gorunen_kademe_hesapla
from .auth import Unit, User
from ulakbus.settings import SICIL_PREFIX
from .auth import AbstractRole


class Personel(Model):
    """Personel Modeli

    Personelin özlük ve iletişim bilgilerini içerir.

    """

    tckn = field.String(_(u"TC No"))
    kurum_sicil_no_int = field.Integer(_(u"Kurum Sicil No"))
    ad = field.String(_(u"Adı"))
    soyad = field.String(_(u"Soyadı"))
    cinsiyet = field.Integer(_(u"Cinsiyet"), choices='cinsiyet')
    uyruk = field.String(_(u"Uyruk"))
    ikamet_adresi = field.String(_(u"İkamet Adresi"))
    ikamet_il = field.String(_(u"İkamet İl"))
    ikamet_ilce = field.String(_(u"İkamet İlçe"))
    adres_2 = field.String(_(u"Adres 2"))
    oda_no = field.String(_(u"Oda Numarası"))
    oda_tel_no = field.String(_(u"Oda Telefon Numarası"))
    cep_telefonu = field.String(_(u"Cep Telefonu"))
    e_posta = field.String(_(u"E-Posta"))
    e_posta_2 = field.String(_(u"E-Posta 2"))
    e_posta_3 = field.String(_(u"E-Posta 3"))
    web_sitesi = field.String(_(u"Web Sitesi"))
    yayinlar = field.String(_(u"Yayınlar"))
    projeler = field.String(_(u"Projeler"))
    kan_grubu = field.String(_(u"Kan Grubu"))
    ehliyet = field.String(_(u"Ehliyet"))
    verdigi_dersler = field.String(_(u"Verdiği Dersler"))
    biyografi = field.Text(_(u"Biyografi"))
    notlar = field.Text(_(u"Notlar"), required=False)
    engelli_durumu = field.String(_(u"Engellilik"))
    engel_grubu = field.String(_(u"Engel Grubu"))
    engel_derecesi = field.String(_(u"Engel Derecesi"))
    engel_orani = field.Integer(_(u"Engellilik Oranı"))
    cuzdan_seri = field.String(_(u"Seri"))
    cuzdan_seri_no = field.String(_(u"Seri No"))
    baba_adi = field.String(_(u"Ana Adı"))
    ana_adi = field.String(_(u"Baba Adı"))
    dogum_tarihi = field.Date(_(u"Doğum Tarihi"), format="%d.%m.%Y")
    dogum_yeri = field.String(_(u"Doğum Yeri"))
    medeni_hali = field.Integer(_(u"Medeni Hali"), choices="medeni_hali")
    kayitli_oldugu_il = field.String(_(u"İl"))
    kayitli_oldugu_ilce = field.String(_(u"İlçe"))
    kayitli_oldugu_mahalle_koy = field.String(_(u"Mahalle/Köy"))
    kayitli_oldugu_cilt_no = field.String(_(u"Cilt No"))
    kayitli_oldugu_aile_sira_no = field.String(_(u"Aile Sıra No"))
    kayitli_oldugu_sira_no = field.String(_(u"Sıra No"))
    kimlik_cuzdani_verildigi_yer = field.String(_(u"Cüzdanın Verildiği Yer"))
    kimlik_cuzdani_verilis_nedeni = field.String(_(u"Cüzdanın Veriliş Nedeni"))
    kimlik_cuzdani_kayit_no = field.String(_(u"Cüzdan Kayıt No"))
    kimlik_cuzdani_verilis_tarihi = field.String(_(u"Cüzdan Kayıt Tarihi"))

    kazanilmis_hak_derece = field.Integer(_(u"Güncel Kazanılmış Hak Derece"), index=True)
    kazanilmis_hak_kademe = field.Integer(_(u"Güncel Kazanılmış Hak Kademe"), index=True)
    kazanilmis_hak_ekgosterge = field.Integer(_(u"Kazanılmış Hak Ek Gösterge"), index=True)

    gorev_ayligi_derece = field.Integer(_(u"Güncel Görev Aylığı Derece"), index=True)
    gorev_ayligi_kademe = field.Integer(_(u"Güncel Görev Aylığı Kademe"), index=True)
    gorev_ayligi_ekgosterge = field.Integer(_(u"Görev Aylığı Ek Gösterge"), index=True)

    emekli_muktesebat_derece = field.Integer(_(u"Güncel Emekli Müktesebat Derece"), index=True)
    emekli_muktesebat_kademe = field.Integer(_(u"Güncel Emekli Müktesebat Kademe"), index=True)
    emekli_muktesebat_ekgosterge = field.Integer(_(u"Emekli Müktesebat Ek Gösterge"), index=True)

    kh_sonraki_terfi_tarihi = field.Date(_(u"Kazanılmış Hak Sonraki Terfi Tarihi"), index=True,
                                         format="%d.%m.%Y")
    ga_sonraki_terfi_tarihi = field.Date(_(u"Görev Aylığı Sonraki Terfi Tarihi"), index=True,
                                         format="%d.%m.%Y")
    em_sonraki_terfi_tarihi = field.Date(_(u"Emekli Müktesebat Sonraki Terfi Tarihi"), index=True,
                                         format="%d.%m.%Y")

    birim = Unit(_(u"Birim"))

    # Personelin Kendi Ünvanı
    unvan = field.Integer(_(u"Personel Unvan"), index=True, choices="unvan_kod", required=False)

    # Aşağıdaki bilgiler atama öncesi kontrol edilecek, Doldurulması istenecek
    emekli_sicil_no = field.String(_(u"Emekli Sicil No"), index=True)
    emekli_giris_tarihi = field.Date(_(u"Emekliliğe Giriş Tarihi"), index=True, format="%d.%m.%Y")

    personel_turu = field.Integer(_(u"Personel Türü"), choices="personel_turu")
    hizmet_sinifi = field.Integer(_(u"Hizmet Sınıfı"), choices="hizmet_sinifi")
    statu = field.Integer(_(u"Statü"), choices="personel_statu")
    brans = field.String(_(u"Branş"), index=True)

    # akademik personeller icin sozlesme sureleri
    gorev_suresi_baslama = field.Date(_(u"Görev Süresi Başlama"), index=True, format="%d.%m.%Y")
    gorev_suresi_bitis = field.Date(_(u"Görev Süresi Bitiş"), index=True, format="%d.%m.%Y")

    # todo: durum_degisikligi yonetimi
    # kurumda ilk goreve baslama bilgileri, atama modelinden elde edilip
    # edilemeyecegini soracagiz. mevcut otomasyonda ayrilmalar da burada tutuluyor.
    # bunu tarih ve durum_degisikligi fieldlarindan olusan bir listnode seklinde tutabiliriz.
    goreve_baslama_tarihi = field.Date(_(u"Göreve Başlama Tarihi"), index=True, format="%d.%m.%Y")
    baslama_sebep = HitapSebep()

    # aday ve idari memurlar icin mecburi hizmet suresi
    mecburi_hizmet_suresi = field.Date(_(u"Mecburi Hizmet Süresi"), index=True, format="%d.%m.%Y")

    # Arama için kullanılacak Flaglar
    kadro_derece = field.Integer(default=0)
    aday_memur = field.Boolean()
    arsiv = field.Boolean()  # ayrilmis personeller icin gecerlidir.

    user = User(one_to_one=True)

    class Meta:
        app = 'Personel'
        verbose_name = _(u"Personel")
        verbose_name_plural = _(u"Personeller")
        list_fields = ['ad', 'soyad', 'tckn', 'durum']
        search_fields = ['ad', 'soyad', 'cep_telefonu', 'tckn']

    def durum(self):
        return self.nufus_kayitlari.durum if self.nufus_kayitlari.key else None

    durum.title = "Durum"

    @lazy_property
    def gorunen_kazanilmis_hak_kademe(self):
        return gorunen_kademe_hesapla(int(self.kazanilmis_hak_derece),
                                      int(self.kazanilmis_hak_kademe))

    @lazy_property
    def gorunen_gorev_ayligi_kademe(self):
        return gorunen_kademe_hesapla(int(self.gorev_ayligi_derece), int(self.gorev_ayligi_kademe))

    @lazy_property
    def gorunen_emekli_muktesebat_kademe(self):
        return gorunen_kademe_hesapla(int(self.emekli_muktesebat_derece),
                                      int(self.emekli_muktesebat_kademe))

    @lazy_property
    def atama(self):
        """atama

        Personelin atama bilgilerini iceren atama nesnesini getirir.

        Returns:
            Atama örneği (instance)

        """
        # Mevcut pyoko API'i ile uyumlu olmasi icin, geriye bos bir Atama nesnesi dondurur.
        atamalar = Atama.objects.set_params(sort='goreve_baslama_tarihi desc').filter(personel=self)
        return atamalar[0] if atamalar else Atama()

    @lazy_property
    def kadro(self):
        """Kadro

        Personelin atama bilgilerinden kadrosuna erişir.

        Returns:
            Kadro örneği (instance)

        """

        return self.atama.kadro

    @lazy_property
    def sicil_no(self):
        """Kadro

        Personelin atama bilgilerinden sicil numarasina erişir.

        Returns:
            Sicil No (str)

        """

        return self.atama.kurum_sicil_no

    @property
    def kurum_sicil_no(self):
        return "%s-%s" % (SICIL_PREFIX, self.kurum_sicil_no_int)

    def __unicode__(self):
        return gettext(u"%(ad)s %(soyad)s") % {'ad': self.ad, 'soyad': self.soyad}


class AdresBilgileri(Model):
    """Adres Bilgileri Modeli

    Personele ait adres bilgilerini içeren modeldir.

    Personelin birden fazla adresi olabilir.

    """

    ad = field.String(_(u"Adres Adı"))
    adres = field.String(_(u"Adres"))
    ilce = field.String(_(u"İlçe"))
    il = field.String(_(u"İl"))
    personel = Personel()

    class Meta:
        verbose_name = _(u"Adres Bilgisi")
        verbose_name_plural = _(u"Adres Bilgileri")

    def __unicode__(self):
        return "%s %s" % (self.ad, self.il)


class KurumIciGorevlendirmeBilgileri(Model):
    """Kurum İçi Görevlendirme Bilgileri Modeli

    Personelin, kurum içi görevlendirme bilgilerine ait modeldir.

    Görevlendirme bir birim ile ilişkili olmalıdır.

    """

    gorev_tipi = field.String(_(u"Görev Tipi"), choices="gorev_tipi")
    kurum_ici_gorev_baslama_tarihi = field.Date(_(u"Başlama Tarihi"), format="%d.%m.%Y")
    kurum_ici_gorev_bitis_tarihi = field.Date(_(u"Bitiş Tarihi"), format="%d.%m.%Y")
    birim = Unit()
    soyut_rol = AbstractRole()
    aciklama = field.String(_(u"Açıklama"))
    resmi_yazi_sayi = field.String(_(u"Resmi Yazı Sayı"))
    resmi_yazi_tarih = field.Date(_(u"Resmi Yazı Tarihi"), format="%d.%m.%Y")
    personel = Personel()

    class Meta:
        """``form_grouping`` kullanıcı arayüzeyinde formun temel yerleşim planını belirler.

        Layout grid (toplam 12 sütun) içerisindeki değerdir.

        Her bir ``layout`` içinde birden fazla form grubu yer alabilir: ``groups``

        Her bir grup, grup başlığı ``group_title``, form öğeleri ``items`` ve bu grubun
        açılır kapanır olup olmadığını belirten boolen bir değerden ``collapse`` oluşur.

        """

        verbose_name = _(u"Kurum İçi Görevlendirme")
        verbose_name_plural = _(u"Kurum İçi Görevlendirmeler")
        form_grouping = [
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": _(u"Görev"),
                        "items": ["gorev_tipi", "kurum_ici_gorev_baslama_tarihi",
                                  "kurum_ici_gorev_bitis_tarihi",
                                  "birim", "aciklama"],
                        "collapse": False
                    }
                ]

            },
            {
                "layout": "2",
                "groups": [
                    {
                        "group_title": _(u"Resmi Yazi"),
                        "items": ["resmi_yazi_sayi", "resmi_yazi_tarih"],
                        "collapse": False
                    }
                ]

            },
        ]

    def __unicode__(self):
        return "%s %s" % (self.gorev_tipi, self.aciklama)


class KurumDisiGorevlendirmeBilgileri(Model):
    """Kurum Dışı Görevlendirme Bilgileri Modeli

    Personelin bağlı olduğu kurumun dışındaki görev bilgilerine ait modeldir.

    """

    gorev_tipi = field.Integer(_(u"Görev Tipi"))
    kurum_disi_gorev_baslama_tarihi = field.Date(_(u"Başlama Tarihi"), format="%d.%m.%Y")
    kurum_disi_gorev_bitis_tarihi = field.Date(_(u"Bitiş Tarihi"), format="%d.%m.%Y")
    aciklama = field.Text(_(u"Açıklama"))
    resmi_yazi_sayi = field.String(_(u"Resmi Yazı Sayı"))
    resmi_yazi_tarih = field.Date(_(u"Resmi Yazı Tarihi"), format="%d.%m.%Y")
    maas = field.Boolean(_(u"Maaş"))
    yevmiye = field.Boolean(_(u"Yevmiye"), default=False)
    yolluk = field.Boolean(_(u"Yolluk"), default=False)
    ulke = field.Integer(_(u"Ülke"), default="90", choices="ulke")
    soyut_rol = AbstractRole()
    personel = Personel()

    class Meta:
        verbose_name = _(u"Kurum Dışı Görevlendirme")
        verbose_name_plural = _(u"Kurum Dışı Görevlendirmeler")
        list_fields = ["ulke", "gorev_tipi", "kurum_disi_gorev_baslama_tarihi"]
        list_filters = ["ulke", "gorev_tipi", "kurum_disi_gorev_baslama_tarihi"]
        search_fields = ["aciklama", ]
        form_grouping = [
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": _(u"Görev"),
                        "items": ["gorev_tipi", "kurum_disi_gorev_baslama_tarihi",
                                  "kurum_disi_gorev_bitis_tarihi",
                                  "ulke",
                                  "aciklama"],
                        "collapse": False
                    }
                ]

            },
            {
                "layout": "2",
                "groups": [
                    {
                        "group_title": _(u"Resmi Yazi"),
                        "items": ["resmi_yazi_sayi", "resmi_yazi_tarih"],
                        "collapse": False
                    },
                    {
                        "items": ["maas", "yevmiye", "yolluk"],
                        "collapse": False
                    }
                ]

            },
        ]

    def __unicode__(self):
        return "%s %s %s" % (self.gorev_tipi, self.aciklama, self.ulke)


class Kadro(Model):
    """Kadro Modeli

    Kurum için ayrılmış Kadro bilgilerine modeldir.

    Kadrolar 4 halde bulunabilirler: SAKLI, IZINLI, DOLU ve BOŞ

        * SAKLI: Saklı kadro, atama yapılmaya müsadesi olmayan, etkinlik onayı alınmamış
          fakat kurum için ayrılmış potansiyel kadroyu tanımlar.
        * IZINLI: Henüz atama yapılmamış, fakat etkinlik onayı alınmış kadroyu tanımlar.
        * DOLU: Bir personel tarafından işgal edilmiş bir kadroyu tanımlar. Ataması yapılmıştır.
        * BOŞ: Çeşitli sebepler ile DOLU iken boşaltılmış kadroyu tanınmlar.

    ``unvan`` ve ``unvan_kod`` karşıt alanlardır. Birisi varken diğeri mevcut olamaz.

    """

    kadro_no = field.Integer(_(u"Kadro No"), required=False)
    derece = field.Integer(_(u"Derece"), required=False)
    durum = field.Integer(_(u"Durum"), choices="kadro_durumlari", required=False)
    birim = Unit(_(u"Birim"), required=False)
    aciklama = field.String(_(u"Açıklama"), index=True, required=False)
    unvan = field.Integer(_(u"Unvan"), index=True, choices="unvan_kod", required=False)
    unvan_aciklama = field.String(_(u"Unvan Aciklama"), index=True, required=False)

    class Meta:
        app = 'Personel'
        verbose_name = _(u"Kadro")
        verbose_name_plural = _(u"Kadrolar")
        list_fields = ['durum', 'unvan', 'aciklama']
        search_fields = ['unvan', 'derece']
        list_filters = ['durum']

    def __unicode__(self):
        # tn: Kadro bilgileri gösterilirken kullanılan mesaj
        return gettext(u"%(no)s - %(unvan)s %(derece)s. derece") % {
            'no': self.kadro_no,
            'unvan': self.get_unvan_display(),
            'derece': self.derece
        }


class Izin(Model):
    """İzin Modeli

    Personelin ücretli izin bilgilerini içeren modeldir.

    """

    tip = field.Integer(_(u"Tip"), choices="izin")
    baslangic = field.Date(_(u"Başlangıç"), format="%d.%m.%Y")
    bitis = field.Date(_(u"Bitiş"), format="%d.%m.%Y")
    onay = field.Date(_(u"Onay"), format="%d.%m.%Y")
    adres = field.String(_(u"Geçireği Adres"))
    telefon = field.String(_(u"Telefon"))
    personel = Personel()
    vekil = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = _(u"İzin")
        verbose_name_plural = _(u"İzinler")
        list_fields = ['tip', 'baslangic', 'bitis', 'onay', 'telefon']
        search_fields = ['tip', 'baslangic', 'onay']

    def __unicode__(self):
        return '%s %s' % (self.tip, self.onay)


class UcretsizIzin(Model):
    """Ücretsiz izin Modeli

    Personelin ücretsiz izin bilgilerini içeren modeldir.

    """

    tip = field.Integer(_(u"Tip"), choices="ucretsiz_izin")
    baslangic = field.Date(_(u"İzin Başlangıç Tarihi"), format="%d.%m.%Y")
    bitis = field.Date(_(u"İzin Bitiş Tarihi"), format="%d.%m.%Y")
    donus_tarihi = field.Date(_(u"Dönüş Tarihi"), format="%d.%m.%Y")
    donus_tip = field.Integer(_(u"Dönüş Tip"))
    onay_tarihi = field.Date(_(u"Onay Tarihi"), format="%d.%m.%Y")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = _(u"Ücretsiz İzin")
        verbose_name_plural = _(u"Ücretsiz İzinler")
        list_fields = ['tip', 'baslangic', 'bitis', 'donus_tarihi']
        search_fields = ['tip', 'onay_tarihi']

    def __unicode__(self):
        return '%s %s' % (self.tip, self.onay_tarihi)


class Atama(Model):
    """Atama Modeli

    Personelin atama bilgilerini içeren modeldir.

    """

    ibraz_tarihi = field.Date(_(u"İbraz Tarihi"), index=True, format="%d.%m.%Y")
    durum = HitapSebep()
    nereden = field.Integer(_(u"Nereden"), index=True)  # modele baglanacak.
    atama_aciklama = field.String(_(u"Atama Açıklama"), index=True)
    goreve_baslama_tarihi = field.Date(_(u"Göreve Başlama Tarihi"), index=True, format="%d.%m.%Y")
    goreve_baslama_aciklama = field.String(_(u"Göreve Başlama Açıklama"), index=True)
    sicil_no = field.String(_(u"Sicil No"))
    kadro = Kadro()
    personel = Personel()
    # Arama için eklendi, Orjinali personelde tutulacak
    hizmet_sinifi = field.Integer(_(u"Hizmet Sınıfı"), index=True, choices="hizmet_sinifi")

    class Meta:
        app = 'Personel'
        verbose_name = _(u"Atama")
        verbose_name_plural = _(u"Atamalar")
        list_fields = ['hizmet_sinifi', 'goreve_baslama_tarihi', 'ibraz_tarihi',
                       'durum']
        search_fields = ['hizmet_sinif', 'statu']

    def __unicode__(self):
        return '%s %s %s' % (self.personel.kurum_sicil_no,
                             self.goreve_baslama_tarihi, self.ibraz_tarihi)

    @classmethod
    def personel_guncel_atama(cls, personel):
        """
        Personelin goreve_baslama_tarihi ne göre son atama kaydını döndürür.

        Returns:
            Atama örneği (instance)

        """

        return cls.objects.set_params(
            sort='goreve_baslama_tarihi desc').filter(personel=personel)[0]

    @classmethod
    def personel_ilk_atama(cls, personel):
        """
        Personelin goreve_baslama_tarihi ne göre ilk atama kaydını döndürür.

        Returns:
            Atama örneği (instance)

        """

        return cls.objects.set_params(
            sort='goreve_baslama_tarihi asc').filter(personel=personel)[0]

    def post_save(self):
        # Personel modeline arama için eklenen kadro_derece set edilecek
        self.personel.kadro_derece = self.kadro.derece
        self.personel.save()

        # Atama sonrası kadro dolu durumuna çekilecek
        self.kadro.durum = 4
        self.kadro.save()

    def pre_save(self):
        self.hizmet_sinifi = self.personel.hizmet_sinifi
        # Atama kaydetmeden önce kadro boş durumuna çekilecek
        self.kadro.durum = 2
        self.kadro.save()

    def post_delete(self):
        # Atama silinirse kadro boş duşuma çekilecek
        self.kadro.durum = 2
        self.kadro.save()

        # personelin kadro derecesi 0 olacak
        self.personel.kadro_derece = 0
        self.personel.save()
