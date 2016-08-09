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
from ulakbus.lib.personel import gorunen_kademe_hesapla
from .auth import Unit, User
from ulakbus.settings import SICIL_PREFIX
from datetime import timedelta


class Personel(Model):
    """Personel Modeli

    Personelin özlük ve iletişim bilgilerini içerir.

    """

    tckn = field.String("TC No")
    kurum_sicil_no_int = field.Integer("Kurum Sicil No")
    ad = field.String("Adı")
    soyad = field.String("Soyadı")
    cinsiyet = field.Integer("Cinsiyet", choices='cinsiyet')
    uyruk = field.String("Uyruk")
    ikamet_adresi = field.String("İkamet Adresi")
    ikamet_il = field.String("İkamet İl")
    ikamet_ilce = field.String("İkamet İlçe")
    adres_2 = field.String("Adres 2")
    oda_no = field.String("Oda Numarası")
    oda_tel_no = field.String("Oda Telefon Numarası")
    cep_telefonu = field.String("Cep Telefonu")
    e_posta = field.String("E-Posta")
    e_posta_2 = field.String("E-Posta 2")
    e_posta_3 = field.String("E-Posta 3")
    web_sitesi = field.String("Web Sitesi")
    yayinlar = field.String("Yayınlar")
    projeler = field.String("Projeler")
    kan_grubu = field.String("Kan Grubu")
    ehliyet = field.String("Ehliyet")
    verdigi_dersler = field.String("Verdiği Dersler")
    biyografi = field.Text("Biyografi")
    notlar = field.Text("Notlar")
    engelli_durumu = field.String("Engellilik")
    engel_grubu = field.String("Engel Grubu")
    engel_derecesi = field.String("Engel Derecesi")
    engel_orani = field.Integer("Engellilik Oranı")
    cuzdan_seri = field.String("Seri")
    cuzdan_seri_no = field.String("Seri No")
    baba_adi = field.String("Ana Adı")
    ana_adi = field.String("Baba Adı")
    dogum_tarihi = field.Date("Doğum Tarihi", format="%d.%m.%Y")
    dogum_yeri = field.String("Doğum Yeri")
    medeni_hali = field.Integer("Medeni Hali", choices="medeni_hali")
    kayitli_oldugu_il = field.String("İl")
    kayitli_oldugu_ilce = field.String("İlçe")
    kayitli_oldugu_mahalle_koy = field.String("Mahalle/Köy")
    kayitli_oldugu_cilt_no = field.String("Cilt No")
    kayitli_oldugu_aile_sira_no = field.String("Aile Sıra No")
    kayitli_oldugu_sira_no = field.String("Sıra No")
    kimlik_cuzdani_verildigi_yer = field.String("Cüzdanın Verildiği Yer")
    kimlik_cuzdani_verilis_nedeni = field.String("Cüzdanın Veriliş Nedeni")
    kimlik_cuzdani_kayit_no = field.String("Cüzdan Kayıt No")
    kimlik_cuzdani_verilis_tarihi = field.String("Cüzdan Kayıt Tarihi")

    kazanilmis_hak_derece = field.Integer("Güncel Kazanılmış Hak Derece", index=True)
    kazanilmis_hak_kademe = field.Integer("Güncel Kazanılmış Hak Kademe", index=True)
    kazanilmis_hak_ekgosterge = field.Integer("Kazanılmış Hak Ek Gösterge", index=True)

    gorev_ayligi_derece = field.Integer("Güncel Görev Aylığı Derece", index=True)
    gorev_ayligi_kademe = field.Integer("Güncel Görev Aylığı Kademe", index=True)
    gorev_ayligi_ekgosterge = field.Integer("Görev Aylığı Ek Gösterge", index=True)

    emekli_muktesebat_derece = field.Integer("Güncel Emekli Müktesebat Derece", index=True)
    emekli_muktesebat_kademe = field.Integer("Güncel Emekli Müktesebat Kademe", index=True)
    emekli_muktesebat_ekgosterge = field.Integer("Emekli Müktesebat Ek Gösterge", index=True)

    kh_sonraki_terfi_tarihi = field.Date("Kazanılmış Hak Sonraki Terfi Tarihi", index=True,
                                         format="%d.%m.%Y")
    ga_sonraki_terfi_tarihi = field.Date("Görev Aylığı Sonraki Terfi Tarihi", index=True,
                                         format="%d.%m.%Y")
    em_sonraki_terfi_tarihi = field.Date("Emekli Müktesebat Sonraki Terfi Tarihi", index=True,
                                         format="%d.%m.%Y")

    birim = Unit("Birim")

    # Personelin Kendi Ünvanı
    unvan = field.Integer("Personel Unvan", index=True, choices="unvan_kod", required=False)

    # Aşağıdaki bilgiler atama öncesi kontrol edilecek, Doldurulması istenecek
    emekli_sicil_no = field.String("Emekli Sicil No", index=True)
    emekli_giris_tarihi = field.Date("Emekliliğe Giriş Tarihi", index=True, format="%d.%m.%Y")

    personel_turu = field.Integer("Personel Türü", choices="personel_turu")
    hizmet_sinifi = field.Integer("Hizmet Sınıfı", choices="hizmet_sinifi")
    statu = field.Integer("Statü", choices="personel_statu")
    brans = field.String("Branş", index=True)

    # akademik personeller icin sozlesme sureleri
    gorev_suresi_baslama = field.Date("Görev Süresi Başlama", index=True, format="%d.%m.%Y")
    gorev_suresi_bitis = field.Date("Görev Süresi Bitiş", index=True, format="%d.%m.%Y")

    # todo: durum_degisikligi yonetimi
    # kurumda ilk goreve baslama bilgileri, atama modelinden elde edilip
    # edilemeyecegini soracagiz. mevcut otomasyonda ayrilmalar da burada tutuluyor.
    # bunu tarih ve durum_degisikligi fieldlarindan olusan bir listnode seklinde tutabiliriz.
    goreve_baslama_tarihi = field.Date("Göreve Başlama Tarihi", index=True, format="%d.%m.%Y")
    baslama_sebep = HitapSebep()
    baslama_sebep.title = "Durum"

    # aday ve idari memurlar icin mecburi hizmet suresi
    mecburi_hizmet_suresi = field.Date("Mecburi Hizmet Süresi", index=True, format="%d.%m.%Y")

    # Arama için kullanılacak Flaglar
    kadro_derece = field.Integer(default=0)
    aday_memur = field.Boolean()
    arsiv = field.Boolean()  # ayrilmis personeller icin gecerlidir.

    user = User(one_to_one=True)

    class Meta:
        app = 'Personel'
        verbose_name = "Personel"
        verbose_name_plural = "Personeller"
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
        return "%s %s" % (self.ad, self.soyad)


class AdresBilgileri(Model):
    """Adres Bilgileri Modeli

    Personele ait adres bilgilerini içeren modeldir.

    Personelin birden fazla adresi olabilir.

    """

    ad = field.String("Adres Adı")
    adres = field.String("Adres")
    ilce = field.String("İlçe")
    il = field.String("İl")
    personel = Personel()

    class Meta:
        verbose_name = "Adres Bilgisi"
        verbose_name_plural = "Adres Bilgileri"

    def __unicode__(self):
        return "%s %s" % (self.ad, self.il)


class KurumIciGorevlendirmeBilgileri(Model):
    """Kurum İçi Görevlendirme Bilgileri Modeli

    Personelin, kurum içi görevlendirme bilgilerine ait modeldir.

    Görevlendirme bir birim ile ilişkili olmalıdır.

    """

    gorev_tipi = field.String("Görev Tipi", choices="gorev_tipi")
    kurum_ici_gorev_baslama_tarihi = field.Date("Başlama Tarihi", format="%d.%m.%Y")
    kurum_ici_gorev_bitis_tarihi = field.Date("Bitiş Tarihi", format="%d.%m.%Y")
    birim = Unit()
    aciklama = field.String("Açıklama")
    resmi_yazi_sayi = field.String("Resmi Yazı Sayı")
    resmi_yazi_tarih = field.Date("Resmi Yazı Tarihi", format="%d.%m.%Y")
    personel = Personel()

    class Meta:
        """``form_grouping`` kullanıcı arayüzeyinde formun temel yerleşim planını belirler.

        Layout grid (toplam 12 sütun) içerisindeki değerdir.

        Her bir ``layout`` içinde birden fazla form grubu yer alabilir: ``groups``

        Her bir grup, grup başlığı ``group_title``, form öğeleri ``items`` ve bu grubun
        açılır kapanır olup olmadığını belirten boolen bir değerden ``collapse`` oluşur.

        """

        verbose_name = "Kurum İçi Görevlendirme"
        verbose_name_plural = "Kurum İçi Görevlendirmeler"
        form_grouping = [
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": "Gorev",
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
                        "group_title": "Resmi Yazi",
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

    gorev_tipi = field.Integer("Görev Tipi")
    kurum_disi_gorev_baslama_tarihi = field.Date("Başlama Tarihi", format="%d.%m.%Y")
    kurum_disi_gorev_bitis_tarihi = field.Date("Bitiş Tarihi", format="%d.%m.%Y")
    aciklama = field.Text("Açıklama")
    resmi_yazi_sayi = field.String("Resmi Yazı Sayı")
    resmi_yazi_tarih = field.Date("Resmi Yazı Tarihi", format="%d.%m.%Y")
    maas = field.Boolean("Maaş")
    yevmiye = field.Boolean("Yevmiye", default=False)
    yolluk = field.Boolean("Yolluk", default=False)
    ulke = field.Integer("Ülke", default="90", choices="ulke")
    personel = Personel()

    class Meta:
        verbose_name = "Kurum Dışı Görevlendirme"
        verbose_name_plural = "Kurum Dışı Görevlendirmeler"
        list_fields = ["ulke", "gorev_tipi", "kurum_disi_gorev_baslama_tarihi"]
        list_filters = ["ulke", "gorev_tipi", "kurum_disi_gorev_baslama_tarihi"]
        search_fields = ["aciklama", ]
        form_grouping = [
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": "Gorev",
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
                        "group_title": "Resmi Yazi",
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

    kadro_no = field.Integer("Kadro No", required=False)
    derece = field.Integer("Derece", required=False)
    durum = field.Integer("Durum", choices="kadro_durumlari", required=False)
    birim = Unit("Birim", required=False)
    aciklama = field.String("Açıklama", index=True, required=False)
    unvan = field.Integer("Unvan", index=True, choices="unvan_kod", required=False)
    unvan_aciklama = field.String("Unvan Aciklama", index=True, required=False)

    class Meta:
        app = 'Personel'
        verbose_name = "Kadro"
        verbose_name_plural = "Kadrolar"
        list_fields = ['durum', 'unvan', 'aciklama']
        search_fields = ['unvan', 'derece']
        list_filters = ['durum']

    def __unicode__(self):
        return "%s - %s %s. derece" % (self.kadro_no, self.get_unvan_display(), self.derece)


class Izin(Model):
    """İzin Modeli

    Personelin ücretli izin bilgilerini içeren modeldir.

    """

    tip = field.Integer("Tip", choices="izin")
    baslangic = field.Date("Başlangıç", format="%d.%m.%Y")
    bitis = field.Date("Bitiş", format="%d.%m.%Y")
    onay = field.Date("Onay", format="%d.%m.%Y")
    adres = field.String("Geçireği Adres")
    telefon = field.String("Telefon")
    personel = Personel()
    vekil = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "İzin"
        verbose_name_plural = "İzinler"
        list_fields = ['tip', 'baslangic', 'bitis', 'onay', 'telefon']
        search_fields = ['tip', 'baslangic', 'onay']

    def __unicode__(self):
        return '%s %s' % (self.tip, self.onay)

    @staticmethod
    def personel_izin_gunlerini_getir(okutman,yil,ay):
        """
        Args:
            okutman: okutman object
            yil: 2016
            ay: 7

        Returns: Seçilen yıl ve ay içinde
        okutmanın izin ve ücretsiz izinlerini
        gün şeklinde döndüren liste.

        """
        personel_izin_list = []

        personel_izinler = Izin.objects.filter(personel = okutman.personel)

        for personel_izin in personel_izinler:
            for gun in Izin.zaman_araligi(personel_izin.baslangic, personel_izin.bitis):
                if gun.month == ay and gun.year == yil:
                    personel_izin_list.append(gun.day)

        personel_ucretsiz_izinler = UcretsizIzin.objects.filter(personel=okutman.personel)

        for personel_izin in personel_ucretsiz_izinler:
            for gun in Izin.zaman_araligi(personel_izin.baslangic_tarihi, personel_izin.bitis_tarihi):
                if gun.month == ay and gun.year == yil:
                    personel_izin_list.append(gun.day)

        return personel_izin_list

    @staticmethod
    def zaman_araligi(baslangic, bitis):
        """
        Verilen iki tarih arasinda kalan tarihleri
        donduren method.

        Args:
            baslangic: Date 02.04.2016
            bitis: Date 04.04.2016

        Returns:
            [02.04.2016,03.04.2016,04.04.2016]

        """

        for n in range(int((bitis - baslangic).days) + 1):
            yield baslangic + timedelta(n)


class UcretsizIzin(Model):
    """Ücretsiz izin Modeli

    Personelin ücretsiz izin bilgilerini içeren modeldir.

    """

    tip = field.Integer("Tip", choices="ucretsiz_izin")
    baslangic_tarihi = field.Date("İzin Başlangıç Tarihi", format="%d.%m.%Y")
    bitis_tarihi = field.Date("İzin Bitiş Tarihi", format="%d.%m.%Y")
    donus_tarihi = field.Date("Dönüş Tarihi", format="%d.%m.%Y")
    donus_tip = field.Integer("Dönüş Tip")
    onay_tarihi = field.Date("Onay Tarihi", format="%d.%m.%Y")
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = "Ücretsiz İzin"
        verbose_name_plural = "Ücretsiz İzinler"
        list_fields = ['tip', 'baslangic_tarihi', 'bitis_tarihi', 'donus_tarihi']
        search_fields = ['tip', 'onay_tarihi']

    def __unicode__(self):
        return '%s %s' % (self.tip, self.onay_tarihi)


class Atama(Model):
    """Atama Modeli

    Personelin atama bilgilerini içeren modeldir.

    """

    ibraz_tarihi = field.Date("İbraz Tarihi", index=True, format="%d.%m.%Y")
    durum = HitapSebep()
    durum.title = "Durum"
    nereden = field.Integer("Nereden", index=True)  # modele baglanacak.
    atama_aciklama = field.String("Atama Açıklama", index=True)
    goreve_baslama_tarihi = field.Date("Göreve Başlama Tarihi", index=True, format="%d.%m.%Y")
    goreve_baslama_aciklama = field.String("Göreve Başlama Açıklama", index=True)
    kadro = Kadro()
    personel = Personel()
    # Arama için eklendi, Orjinali personelde tutulacak
    hizmet_sinifi = field.Integer("Hizmet Sınıfı", index=True, choices="hizmet_sinifi")

    class Meta:
        app = 'Personel'
        verbose_name = "Atama"
        verbose_name_plural = "Atamalar"
        list_fields = ['hizmet_sinif', 'gorev_suresi_baslama', 'ibraz_tarihi',
                       'durum']
        search_fields = ['hizmet_sinif', 'statu']

    def __unicode__(self):
        return '%s %s %s' % (self.personel.kurum_sicil_no,
                             self.gorev_suresi_baslama, self.ibraz_tarihi)

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
