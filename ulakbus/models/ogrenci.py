# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Öğrenci Modülü

Bu modül Ulakbüs uygulaması için öğrenci modeli ve öğrenciyle ilişkili data modellerini içerir.

"""

import six

from pyoko import Model, field, ListNode, LinkProxy
from pyoko.exceptions import ObjectDoesNotExist
from pyoko.lib.utils import lazy_property
from ulakbus.lib.cache import GuncelDonem
from ulakbus.lib.ogrenci import HarfNotu
from zengine.lib.translation import gettext_lazy as _, gettext, format_date
from .auth import Role, User
from .auth import Unit
from .buildings_rooms import Room, RoomType
from .personel import Personel
from ulakbus.lib.date_time_helper import yil_ve_aya_gore_ilk_ve_son_gun
from zengine.messaging.model import Channel


class OgretimYili(Model):
    """
    Öğretim yılını bilgilerini tutan modeldir.
    """

    yil = field.Integer(_(u"Yıl"), unique=True)  # 2015
    ad = field.String(_(u"Öğretim Yılı"))  # 2015 - 2016 Öğretim Yılı

    def post_creation(self):
        self.ad = "%s - %s Öğretim Yılı" % (self.yil, int(self.yil) + 1)
        self.save()

    def __unicode__(self):
        return "%s" % self.ad


class Donem(Model):
    """Dönem Modeli

    Güz, bahar ve yaz akademik dönemlerinin bilgilerine ait modeldir.

    Güncel alanı, içerisinde bulunulan akademik dönemi işaret eder.

    """

    ad = field.String(_(u"Ad"), index=True)
    baslangic_tarihi = field.Date(_(u"Başlangıç Tarihi"), index=True, format="%d.%m.%Y")
    bitis_tarihi = field.Date(_(u"Bitiş Tarihi"), index=True, format="%d.%m.%Y")
    guncel = field.Boolean(index=True)
    ogretim_yili = OgretimYili(_(u"Öğretim Yılı"), index=True)

    def donem_fields_to_dict(self):
        """
        Güncel dönem nesnesinin fieldlarını dict haline döndüren method.

        Args:
            guncel_donem: (object) güncel dönem objesi

        Returns:
            donem_fields(dict): güncel dönemin fieldlarının dict hali.

        """
        return {
            'ad': self.ad,
            'baslangic_tarihi': self.baslangic_tarihi.strftime("%d.%m.%Y"),
            'bitis_tarihi': self.bitis_tarihi.strftime("%d.%m.%Y"),
            'guncel': self.guncel,
            'ogretim_yili_id': self.ogretim_yili.key,
            'key': self.key
        }

    @classmethod
    def guncel_donem(cls, current=None):

        if current:
            return Donem(**current.task_data['wf_initial_values']['guncel_donem'])
        else:
            return Donem(**GuncelDonem().get_or_set())

    def pre_save(self):

        if not self.bitis_tarihi > self.baslangic_tarihi:
            raise Exception("Bitiş tarihi başlangıç tarihinden büyük olmalıdır.")
        if self.onceki_donem() and not self.baslangic_tarihi >= self.onceki_donem().bitis_tarihi:
            raise Exception("Başlangıç tarihi önceki dönemin bitiş tarihinden büyük olmalıdır.")
        if self.guncel:
            try:
                old = Donem.objects.get(guncel=True)
                old.guncel = False
                old.save()
                GuncelDonem().delete()
            except ObjectDoesNotExist:
                pass

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Dönem")
        verbose_name_plural = _(u"Dönemler")
        list_fields = ['ad', 'baslangic_tarihi']
        search_fields = ['ad']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.baslangic_tarihi)

    def onceki_donemler(self, n=1):
        """
        Args:
            n: geriye doğru kaç dönem döndürmeli.
        Returns:
            (list) önceki dönemler listesi

        """

        return self.objects.filter(baslangic_tarihi__lt=self.baslangic_tarihi).order_by(
            '-baslangic_tarihi')[0:n]

    def onceki_donem(self):
        """
        Returns:
            (donem) donemden bir önceki dönemi dondurur.

        """
        try:
            return list(self.onceki_donemler())[0]
        except IndexError:
            return None

    def sonraki_donemler(self, n=1):
        """
        Args:
            n: ileriye dogru kac donem dondurmeli.
        Returns:
            (list) önceki dönemler listesi

        """

        return self.objects.filter(baslangic_tarihi__gt=self.baslangic_tarihi).order_by(
            'baslangic_tarihi')[0:n]

    def sonraki_donem(self):
        """
        Returns:
            (donem) donemden bir sonraki dönemi dondurur.

        """
        try:
            return list(self.sonraki_donemler())[0]
        except IndexError:
            return None

    @classmethod
    def son_donem(cls):
        """
        Returns:
            Veritabanında kayıtlı olan en son dönemi döndürür.

        """

        return cls.objects.filter().order_by('-baslangic_tarihi')[0]

    @staticmethod
    def takvim_ayina_rastlayan_donemler(yil, ay):
        """
        Bir takvim ayına rastlayan dönemleri döndürür.

        Args:
            yil (int): takvim yili
            ay (int): takvim ayi

        Returns:
            (list) donem nesneleri listesi
        """
        baslangic, bitis = yil_ve_aya_gore_ilk_ve_son_gun(yil, ay)

        donem_list = []

        donem_list.extend(list(Donem.objects.filter(bitis_tarihi__gte=baslangic,
                                                    bitis_tarihi__lte=bitis)))

        donem_list.extend(list(Donem.objects.filter(baslangic_tarihi__gte=baslangic,
                                                    baslangic_tarihi__lte=bitis)))

        donem_list.extend(list(Donem.objects.filter(bitis_tarihi__gt=bitis,
                                                    baslangic_tarihi__lt=baslangic)))

        donem_list = sorted(donem_list, key=lambda d: d.baslangic_tarihi)

        return donem_list


class HariciOkutman(Model):
    """Harici Okutman Modeli

    Harici okutmanın özlük ve iletişim bilgilerini içerir.

    """

    tckn = field.String(_(u"TC No"), index=True)
    ad = field.String(_(u"Adı"), index=True)
    soyad = field.String(_(u"Soyadı"), index=True)
    cinsiyet = field.Integer(_(u"Cinsiyet"), index=True, choices='cinsiyet')
    uyruk = field.String(_(u"Uyruk"), index=True)
    medeni_hali = field.Integer(_(u"Medeni Hali"), index=True, choices="medeni_hali",
                                required=False)
    ikamet_adresi = field.String(_(u"İkamet Adresi"), index=True, required=False)
    ikamet_il = field.String(_(u"İkamet İl"), index=True, required=False)
    ikamet_ilce = field.String(_(u"İkamet İlçe"), index=True, required=False)
    adres_2 = field.String(_(u"Adres 2"), index=True, required=False)
    adres_2_posta_kodu = field.String(_(u"Adres 2 Posta Kodu"), index=True, required=False)
    telefon_no = field.String(_(u"Telefon Numarası"), index=True, required=True)
    oda_no = field.String(_(u"Oda Numarası"), index=True, required=False)
    oda_tel_no = field.String(_(u"Oda Telefon Numarası"), index=True, required=False)
    e_posta = field.String(_(u"E-Posta"), index=True)
    e_posta_2 = field.String(_(u"E-Posta 2"), index=True, required=False)
    e_posta_3 = field.String(_(u"E-Posta 3"), index=True, required=False)
    web_sitesi = field.String(_(u"Web Sitesi"), index=True, required=False)
    yayinlar = field.String(_(u"Yayınlar"), index=True, required=False)
    projeler = field.String(_(u"Projeler"), index=True, required=False)
    kan_grubu = field.String(_(u"Kan Grubu"), index=True, required=False)
    ehliyet = field.String(_(u"Ehliyet"), index=True, required=False)
    biyografi = field.Text(_(u"Biyografi"))
    notlar = field.Text(_(u"Notlar"))
    engelli_durumu = field.String(_(u"Engellilik"), index=True)
    engel_grubu = field.String(_(u"Engel Grubu"), index=True)
    engel_derecesi = field.String(_(u"Engel Derecesi"))
    engel_orani = field.Integer(_(u"Engellilik Orani"))
    cuzdan_seri = field.String(_(u"Seri"), index=True)
    cuzdan_seri_no = field.String(_(u"Seri No"), index=True)
    baba_adi = field.String(_(u"Ana Adi"), index=True)
    ana_adi = field.String(_(u"Baba Adi"), index=True)
    dogum_tarihi = field.Date(_(u"Doğum Tarihi"), index=True, format="%d.%m.%Y")
    dogum_yeri = field.String(_(u"Doğum Yeri"), index=True)
    kayitli_oldugu_il = field.String(_(u"İl"), index=True)
    kayitli_oldugu_ilce = field.String(_(u"İlçe"), index=True)
    kayitli_oldugu_mahalle_koy = field.String(_(u"Mahalle/Koy"))
    kayitli_oldugu_cilt_no = field.String(_(u"Cilt No"))
    kayitli_oldugu_aile_sira_no = field.String(_(u"Aile Sıra No"))
    kayitli_oldugu_sira_no = field.String(_(u"Sıra No"))
    kimlik_cuzdani_verildigi_yer = field.String(_(u"Cüzdanin Verildiği Yer"))
    kimlik_cuzdani_verilis_nedeni = field.String(_(u"Cüzdanin Veriliş Nedeni"))
    kimlik_cuzdani_kayit_no = field.String(_(u"Cüzdan Kayıt No"))
    kimlik_cuzdani_verilis_tarihi = field.String(_(u"Cüzdan Kayıt Tarihi"))
    akademik_yayinlari = field.String(_(u"Akademik Yayınları"), index=True, required=False)
    verdigi_dersler = field.String(_(u"Verdiği Dersler"), index=True, required=False)
    unvan = field.Integer(_(u"Unvan"), index=True, choices="akademik_unvan", required=False)
    aktif = field.Boolean(_(u"Aktif"), index=True, required=False)
    user = User(one_to_one=True)

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Harici Okutman")
        verbose_name_plural = _(u"Harici Okutmanlar")
        search_fields = ['unvan', 'ad', 'soyad']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.soyad)

    def post_save(self):
        """
        Okutman modelinden bu modele one-to-one bir bağlantı mevcuttur. Bu sebeple
        modelimizden de karşılıklı bir bağ oluşmuştur.

        Bu modelde yapılan değişiklik, bu metod sayesinde Okutman modeline yansıtılır.

        """

        if self.okutman.exist:
            self.okutman.ad = self.ad
            self.okutman.soyad = self.soyad
            self.okutman.unvan = self.unvan
            self.okutman.save()


class Okutman(Model):
    """Okutman Modeli

    Okutman bilgileri için data modelidir.

    Okutman, ders veren tüm öğretim elemanlarının (öğretim üyesi, öğretim elemanı,
    okutman ve harici okutman) genel adıdır.

    Bu model, aynı amaçla iki ayrı modele bağlıdır: Personel veya Harici Okutman.
    Ancak herbir kaydın sadece bir tanesine bağı olabilir. Okutman universite personeli
    veya dışarıdan harici bir personel olabilir. Aynı anda ikisi birden olamaz.

    Birim alanı okutmanın bağlı olduğu bölümü ifade eder. Harici okutmanlar da bu bölümlerin
    yetkisi altındadır.

    """

    ad = field.String(_(u"Ad"), index=True, required=False)
    soyad = field.String(_(u"Soyad"), index=True, required=False)
    unvan = field.String(_(u"Unvan"), index=True, required=False)
    personel = Personel(one_to_one=True)
    harici_okutman = HariciOkutman(one_to_one=True)

    class GorevBirimi(ListNode):
        donem = Donem()
        yoksis_no = field.String(_(u"Yoksis No"), index=True, required=False)

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Okutman")
        verbose_name_plural = _(u"Okutmanlar")
        search_fields = ['unvan', 'personel', 'ad', 'soyad', 'birim_no']

    @lazy_property
    def okutman(self):
        """Okutmanın bağlı olduğu personel veya harici okutmanı döndürür.

        Example:
            Okutman örneği (instance) üzerinden erişilebilir. Aşağıdaki örnek ilgili okutmanın
            eposta bilgisine erişim sağlar. Okutman personel ise Personel modeli eposta alanı,
            harici okutman ise HariciOkutman modeli eposta alanı kullanılır::

                ders_okutman = Okutman.objects.get(ad="Yeter", soyad="Demir")
                eposta = ders_okutman.okutman.eposta

        """

        return self.personel if self.personel.exist else self.harici_okutman

    def __unicode__(self):
        return gettext(u'%(ad)s %(soyad)s') % {'ad': self.ad, 'soyad': self.soyad}

    def is_not_unique(self):
        """Personel veya Harici Okutman sayısını bulur.

        Returns:
            personel veya harici okutman sayısı

        """

        if self.personel.key:
            return len(self.objects.filter(personel=self.personel))
        elif self.harici_okutman.key:
            return len(self.objects.filter(harici_okutman=self.harici_okutman))

    def pre_save(self):
        """Bu metot nesne kayıt edilmeden hemen önce çalışır.

        Okutmanın bağlı olduğu personel veya harici okutman kaydı tekil olmalıdır. Bir okutmanın
        ya personel ya da harici okutman kaydı bulunabilir.

        Ayrıca aynı personel veya aynı harici okutmanın birden fazla Okutman kaydı bulunamaz.

        Bu metot ilgili kontrolleri yapıp, nesneyi kaydetmeye hazır hale getirir.


        Raises:
            Exception: Eğer kaydedilen nesne, veritabanında varsa ve tekil değilse


        """
        if self.okutman.key:
            self.ad = self.okutman.ad
            self.soyad = self.okutman.soyad
            self.unvan = self.okutman.unvan
        if not self.is_in_db() and self.is_not_unique():
            raise Exception("Okutman %s must be unique" % self.okutman)

    def donem_subeleri(self, donem=None):
        donem = donem or Donem.guncel_donem()
        return [s for s in Sube.objects.filter(okutman=self, donem=donem)]

    def donemdeki_gorev_yeri(self, donem):
        gorev_birimi_dct = {gorev_birimi.donem.key: gorev_birimi.yoksis_no for gorev_birimi in
                            self.GorevBirimi}
        if donem.key in gorev_birimi_dct:
            return gorev_birimi_dct[donem.key]


class Program(Model):
    """Program Modeli

     Bir bölümün öğrenim programı (ders ve uygulamalardan oluşan) bilgilerinin
     saklandığı modeldir.

    """

    yoksis_no = field.String(_(u"YOKSIS ID"), index=True)
    bolum_adi = field.String(_(u"Bölüm"), index=True)
    ucret = field.Integer(_(u"Ücret"), index=True)
    yil = field.String(_(u"Yıl"), index=True)
    adi = field.String(_(u"Adı"), index=True)
    tanim = field.String(_(u"Tanım"), index=True)
    yeterlilik_kosullari_aciklamasi = field.String(_(u"Yeterlilik Koşulları Açıklaması"),
                                                   index=True)
    program_ciktilari = field.String(_(u"Program Çıktıları"), index=True)
    mezuniyet_kosullari = field.String(_(u"Mezuniyet Koşulları"), index=True)
    kabul_kosullari = field.String(_(u"Kabul Koşulları"), index=True)
    donem_sayisi = field.Integer(_(u"Sürdüğü Dönem Sayısı"), index=True)
    farkli_programdan_ders_secebilme = field.Boolean(_(u"Farklı Bir Programdan Ders Seçebilme"),
                                                     default=False, index=True)
    bolum_baskani = Role(verbose_name=_(u'Bölüm Başkanı'), reverse_name='bolum_baskani_program')
    ects_bolum_kordinator = Role(verbose_name=_(u'ECTS Bölüm Koordinator'),
                                 reverse_name='ects_koordinator_program')
    akademik_kordinator = Role(verbose_name=_(u'Akademik Koordinator'),
                               reverse_name='akademik_koordinator_program')
    birim = Unit(reverse_name="yoksis_program_program", verbose_name=_(u"YÖKSİS Program"))

    bolum = Unit(reverse_name="bolum_program", verbose_name=_(u"Bölüm"))

    # todo: to be removed
    # class Donemler(ListNode):
    #     donem = Donem()

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Program")
        verbose_name_plural = _(u"Programlar")
        list_fields = ['adi', 'yil']
        search_fields = ['adi', 'yil', 'tanim']

    def __unicode__(self):
        return '%s %s' % (self.adi, self.yil)


class Ders(Model):
    """Ders Modeli

    Program dahilinde açılan derslerin bilgilerinin saklandığı modeldir.

    """

    ad = field.String(_(u"Ad"), index=True)
    kod = field.String(_(u"Kod"), index=True)
    tanim = field.String(_(u"Tanım"), index=True)
    aciklama = field.String(_(u"Açıklama"), index=True)
    onkosul = field.String(_(u"Önkoşul"), index=True)
    uygulama_saati = field.Integer(_(u"Uygulama Saati"), index=True)
    teori_saati = field.Integer(_(u"Teori Saati"), index=True)
    ects_kredisi = field.Integer(_(u"ECTS Kredisi"), index=True)
    yerel_kredisi = field.Integer(_(u"Yerel Kredisi"), index=True)
    zorunlu = field.Boolean(_(u"Zorunlu"), index=True)
    ders_dili = field.String(_(u"Ders Dili"), index=True)
    ders_turu = field.Integer(_(u"Ders Türü"), index=True, choices="ders_turleri")
    ders_amaci = field.String(_(u"Ders Amacı"), index=True)
    ogrenme_ciktilari = field.String(_(u"Öğrenme Çıktıları"), index=True)
    ders_icerigi = field.String(_(u"Ders İçeriği"), index=True)
    ders_kategorisi = field.Integer(_(u"Ders Kategorisi"), index=True, choices="ders_kategorileri")
    ders_kaynaklari = field.String(_(u"Ders Kaynakları"), index=True)
    ders_mufredati = field.String(_(u"Ders Müfredatı"), index=True)
    verilis_bicimi = field.Integer(_(u"Veriliş Biçimi"), index=True,
                                   choices="ders_verilis_bicimleri")
    katilim_sarti = field.Integer(_(u"Katılım Şartı"), index=True)
    ontanimli_kontenjan = field.Integer(_(u'Kontenjan'), default=30)
    ontanimli_dis_kontenjan = field.Integer(_(u'Dış Kontenjan'), default=5)
    program = Program()
    program_donemi = field.Integer(_(u'Programda Yeraldığı Dönem'), index=True)
    donem = Donem()
    ders_koordinatoru = Personel()
    yerine_ders = LinkProxy("Ders", verbose_name=_(u"Yerine Açılan Ders"), reverse_name="")

    class Degerlendirme(ListNode):
        tur = field.Integer(_(u"Değerlendirme Türü"), choices="sinav_turleri", index=True)
        sinav_suresi = field.Integer(_(u"Sınav Süresi (dakika)"))
        toplam_puana_etki_yuzdesi = field.Integer(_(u"Toplam Puana Etki Yüzdesi"), index=True)

    class DersYardimcilari(ListNode):
        ders_yardimcilari = Personel()

    class DersVerenler(ListNode):
        dersi_verenler = Okutman()

    class DerslikTurleri(ListNode):
        """
        Bir dersin hangi derslik türlerinde kaç saat yapılacağı burada saklanır.
        Örneğin 5 saatlik bir dersin 3 saati sınıfta, 2 saati laboratuvarda
        yapılacaksa bu bilgi burada saklanır.

        Bir ders içini iki ayrı etkinlik planlanması isteniyorsa, örneğin 4 saat
        teorik dersi olan bir dersin 2 saatinin bir gün, 2 saatinin ise farklı
        bir gün yapılması için burada 2 ayrı kayıt oluşturulmalıdır.
        """
        sinif_turu = RoomType()
        ders_saati = field.Integer(_(u"Ders Saati"), index=True)

        # teori = field.Integer("Ders Teori Saati", index=True)
        # uygulama = field.Integer("Ders Uygulama Saati", index=True)
        # dersin süresinin ne kadarı teori ne kadarı uygulama gibi 2+2, 4+0 gibi

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Ders")
        verbose_name_plural = _(u"Dersler")
        list_fields = ['ad', 'kod', 'ders_dili']
        search_fields = ['ad', 'kod']

    def __unicode__(self):
        return '%s %s %s' % (self.ad, self.kod, self.ders_dili)

    def ontanimli_sube_olustur(self):
        sube = Sube()
        sube.ad = 'Varsayılan Şube'
        sube.kontenjan = self.ontanimli_kontenjan
        sube.dis_kontenjan = self.ontanimli_dis_kontenjan
        sube.ders = self
        sube.donem = Donem.guncel_donem()
        sube.save()

    def post_creation(self):
        self.ontanimli_sube_olustur()


class Sube(Model):
    """Şube Modeli

    Ders şubelerine ait bilgilerin saklandığı modeldir.

    Şube, bir dersin, bir dönem içerisinde okutmanı ile birlikte tanımlanmasıyla ortaya çıkar.

    Her şubenin önceden belirlenmiş bir kontenjanı vardır.

    Dış kontenjan ise, o şubeyi, dersin ait olduğu bölüm dışından seçebilecek
    öğrenci sayısını ifade eder.

    """

    ad = field.String(_(u"Ad"), index=True)
    kontenjan = field.Integer(_(u"Kontenjan"), index=True)
    dis_kontenjan = field.Integer(_(u"Dış Kontenjan"), index=True)
    okutman = Okutman()
    ders = Ders()
    donem = Donem()
    ders_adi = field.String(_(u"Ders Adi"), index=True)

    class NotDonusumTablosu(ListNode):
        """Not Donusum Tablosu

        Bu tablo, settings seklinde universite geneli icin tanimlanmistir.
        Eger okutman baska bir not donusum tablosu kullanmak isterse,
        harflendirme wf da bu tabloyu duzenlerse, tablo bir list node
        olarak bu modelde saklanir.

        """

        harf = field.String(_(u"Harf"), index=True, choices=HarfNotu.generate_choices())
        dortluk_katsayi = field.Float("", choices=HarfNotu.generate_choices_for_4())
        yuzluk_not_baslangic = field.Float(_(u"Başlangıç"), index=True)
        yuzluk_not_bitis = field.Float(_(u"Bitis"), index=True)

        def __unicode__(self):
            return '%s %s %s %s' % (
                self.harf, self.yuzluk_not_baslangic, self.yuzluk_not_bitis, self.dortluk_katsayi)

    class Programlar(ListNode):
        programlar = Program()

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Şube")
        verbose_name_plural = _(u"Şubeler")
        list_fields = ['ad', 'kontenjan']
        search_fields = ['ad', 'kontenjan']

    def sube_sinavlarini_olustur(self):
        for dg in self.ders.Degerlendirme:
            sinav = Sinav(tur=dg.tur, sube=self, ders=self.ders)
            sinav.save()

    def ders_adi_olustur(self):
        self.ders_adi = "%s - %s %s" % (self.ders.ad, self.ad, str(self.kontenjan))
        self.save()

    def sube_kanal_olustur(self):
        """Yeni bir şube oluşturulduğunda mesajlaşma kanalı oluşturur ve o şubenin
            öğretim görevlisini o kanala yönetici olarak atar."""
        channel = Channel()
        channel.name = "%s %s" % (self.ders.kod, self.ad)
        channel.typ = 15  # public kanal
        channel.description = "%s Dersi %s Şubesi Mesajlaşma Kanalı" % (self.ders.ad, self.ad)
        channel.owner = self.okutman.personel.user
        channel.save()

    def post_creation(self):
        self.sube_sinavlarini_olustur()
        self.ders_adi_olustur()
        self.sube_kanal_olustur()

    def __unicode__(self):
        return '%s' % self.ders_adi


class Sinav(Model):
    """Sınav Modeli

    Derse ait sınav(ara sınav, genel sınav, bütünleme, tek ders, muafiyet)
    bilgilerinin saklandığı modeldir.

    Sınavlar şubeler için ders dolayısı ile otomatik açılırlar. Bu sebeple temel bağ Şube
    modelidir.

    Ders arama kolaylığı için eklenmiştir.

    """

    tarih = field.Date(_(u"Sınav Tarihi"), index=True)
    yapilacagi_yer = field.String(_(u"Yapılacağı Yer"), index=True)
    tur = field.Integer(_(u"Sınav Türü"), index=True, choices="sinav_turleri")
    aciklama = field.String(_(u"Açıklama"), index=True)
    sube = Sube()
    degerlendirme = field.Boolean(_(u"Değerlendirme Durumu"), index=True, default=False)

    # arama amacli
    ders = Ders()
    puan = field.Integer(_(u"Puan"), index=True)
    okutman = Okutman()

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Sınav")
        verbose_name_plural = _(u"Sınavlar")
        list_fields = ['tarih', 'yapilacagi_yer']
        search_fields = ['aciklama', 'tarih']

    def pre_save(self):
        if not self.okutman:
            self.okutman = self.sube.okutman

    def __unicode__(self):
        return '%s %s' % (self.get_tur_display(), self.sube)


class DersProgrami(Model):
    """Ders Programı Modeli

    Dersin işlenecegi gün, saat, şube ve derslik bilgilerini saklayan modeldir.

    """

    gun = field.String(_(u"Ders Günü"), index=True)
    saat = field.Integer(_(u"Ders Saati"), index=True)
    sube = Sube()
    derslik = Room()

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Ders Programı")
        verbose_name_plural = _(u"Ders Programları")
        list_fields = ['gun', 'saat']
        search_fields = ['gun', 'saat']

    def __unicode__(self):
        return '%s %s' % (self.gun, self.saat)


class Ogrenci(Model):
    """Öğrenci Modeli

    Öğrencinin özlük ve iletişim bilgilerinin saklandığı modeldir.

    Öğrenciler, sisteme giriş yapar ve yetkileri doğrultusunda iş akışları
    çalıştırır. Bu amaçla User bağlantısı kurulmuştur.

    """

    ad = field.String(_(u"Ad"), index=True)
    soyad = field.String(_(u"Soyad"), index=True)
    cinsiyet = field.Integer(_(u"Cinsiyet"), index=True, choices="cinsiyet")
    tckn = field.String(_(u"TC Kimlik No"), index=True)
    cuzdan_seri = field.String(_(u"Seri"), index=True)
    cuzdan_seri_no = field.String(_(u"Seri No"), index=True)
    kayitli_oldugu_il = field.String(_(u"İl"), index=True)
    kayitli_oldugu_ilce = field.String(_(u"İlçe"), index=True)
    kayitli_oldugu_mahalle_koy = field.String(_(u"Mahalle/Köy"))
    kayitli_oldugu_cilt_no = field.String(_(u"Cilt No"))
    kayitli_oldugu_aile_sira_no = field.String(_(u"Aile Sıra No"))
    kayitli_oldugu_sira_no = field.String(_(u"Sıra No"))
    kimlik_cuzdani_verildigi_yer = field.String(_(u"Nüfus Cüzdanı Verildiği Yer"))
    kimlik_cuzdani_verilis_nedeni = field.String(_(u"Nüfus Cüzdanı Veriliş Nedeni"))
    kimlik_cuzdani_kayit_no = field.String(_(u"Nüfus Cüzdanı Kayıt No"))
    kimlik_cuzdani_verilis_tarihi = field.Date(_(u"Nüfus Cüzdanı Veriliş Tarihi"), index=True,
                                               format="%d.%m.%Y")
    baba_adi = field.String(_(u"Ana Adı"), index=True)
    ana_adi = field.String(_(u"Baba Adı"), index=True)
    ikamet_il = field.String(_(u"İkamet İl"), index=True)
    ikamet_ilce = field.String(_(u"İkamet İlçe"), index=True)
    ikamet_adresi = field.String(_(u"İkametgah Adresi"), index=True)
    adres2 = field.String(_(u"2.Adres"), index=True)
    posta_kodu = field.String(_(u"Posta Kodu"), index=True)
    dogum_tarihi = field.Date(_(u"Doğum Tarihi"), index=True, format="%d.%m.%Y")
    dogum_yeri = field.String(_(u"Doğum Yeri"), index=True)
    uyruk = field.String(_(u"Uyruk"), index=True)
    medeni_hali = field.Integer(_(u"Medeni Hali"), index=True, choices="medeni_hali")
    ehliyet = field.String(_(u"Ehliyet"), index=True)
    e_posta = field.String(_(u"E-Posta"), index=True)
    e_posta2 = field.String(_(u"2.E-Posta"), index=True)
    tel_no = field.String(_(u"Telefon Numarası"), index=True)
    gsm = field.String(_(u"Cep Tel"), index=True)
    kan_grubu = field.String(_(u"Kan Grubu"), index=True)
    baba_aylik_kazanc = field.Integer(_(u"Babanızın Aylık Kazancı"), index=True)
    baba_ogrenim_durumu = field.Integer(_(u"Babanızın Öğrenim Durumu"), index=True,
                                        choices="ogrenim_durumu")
    baba_meslek = field.String(_(u"Babanızın Mesleği"), index=True)
    anne_ogrenim_durumu = field.Integer(_(u"Annenizin Öğrenim Durumu"), index=True,
                                        choices="ogrenim_durumu")
    anne_meslek = field.String(_(u"Annenizin Mesleği"), index=True)
    anne_aylik_kazanc = field.Integer(_(u"Annenizin Aylık Kazancı"), index=True)
    masraf_sponsor = field.Integer(_(u"Masraflarınız Kim Tarafından Karşılanacak"), index=True,
                                   choices="masraf_sponsorlar")
    emeklilik_durumu = field.String(_(u"Velinizin Emeklilik Durumu"), index=True)
    kiz_kardes_sayisi = field.Integer(_(u"Kız Kardeş Sayısı"), index=True)
    erkek_kardes_sayisi = field.Integer(_(u"Erkek Kardeş Sayısı"), index=True)
    ogrenim_goren_kardes_sayisi = field.Integer(_(u"Öğrenim Gören Kardeş Sayısı"), index=True)
    burs_kredi_no = field.String(_(u"Kredi ve Yurtlar Kurumundan Aldığınız Kredi ve Burs No"),
                                 index=True)
    aile_tel = field.String(_(u"Ailenizin Ev Tel"), index=True)
    aile_gsm = field.String(_(u"Ailenizin Cep Tel"), index=True)
    aile_adres = field.String(_(u"Ailenizin Daimi İkamet Ettiği Adres"), index=True)
    ozur_durumu = field.Integer(_(u"Varsa Özür Durumunuz"), index=True, choices="ozur_durumu")
    ozur_oran = field.Integer(_(u"Varsa Özür Oranınız %"), index=True)
    user = User(one_to_one=True)

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Ögrenci")
        verbose_name_plural = _(u"Ögrenciler")
        list_fields = ['ad', 'soyad']
        search_fields = ['ad', 'soyad']

    def __unicode__(self):
        return gettext(u'%(ad)s %(soyad)s') % {'ad': self.ad, 'soyad': self.soyad}

    def donem_dersleri(self, donem=None):
        return [d.ders for d in
                OgrenciDersi.objects.filter(ogrenci=self, donem=donem or Donem.guncel_donem())]

    def donem_subeleri(self, donem=None):
        return [d.sube for d in
                OgrenciDersi.objects.filter(ogrenci=self, donem=donem or Donem.guncel_donem())]


class OncekiEgitimBilgisi(Model):
    """Öncekı Eğitim Bilgisi Modeli

    Öğrenciye ait önceki eğitim bilgisi modelidir.

    """

    okul_adi = field.String(_(u"Mezun Olduğu Okul"), index=True)
    diploma_notu = field.Float(_(u"Diploma Notu"), index=True)
    mezuniyet_yili = field.String(_(u"Mezuniyet Yılı"), index=True)
    ogrenci = Ogrenci()

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Önceki Eğitim Bilgisi")
        verbose_name_plural = _(u"Önceki Eğitim Bilgileri")
        list_fields = ['okul_adi', 'diploma_notu', 'mezuniyet_yili']
        search_fields = ['okul_adi', 'diploma_notu', 'mezuniyet_yili']

    def __unicode__(self):
        return '%s %s %s' % (self.okul_adi, self.mezuniyet_yili, self.ogrenci.ad)


class OgrenciProgram(Model):
    """Öğrenci Program Modeli

    Öğrencilerin kayıt yaptırdığı programların saklandığı modeldir.

    Öğrenciler birden fazla programa kayıt yaptırabilirler. Herbir program için ayrı bir öğrenci
    numarası alırlar.

    Aktif dönem öğrencinin ilgili programda geldiği aşamayı ifade eder. Buna göre ilgili program
    derslerinden faydalanabilir.

    Başarı durumu, Genel Ağırlıklı Not Ortalamasını ifade eder:
    http://www.ulakbus.org/wiki/standart_fakulteler_icin_yazilim_ihtiyac_analizi_belgesi.html#basari-hesaplama

    Öğrencinin ilgili programdaki danışman bilgisi de burada saklanır.

    """

    ogrenci_no = field.String(_(u"Öğrenci Numarası"), index=True)
    giris_tarihi = field.Date(_(u"Giriş Tarihi"), index=True, format="%d.%m.%Y")
    mezuniyet_tarihi = field.Date(_(u"Mezuniyet Tarihi"), index=True, format="%d.%m.%Y")
    giris_puan_turu = field.Integer(_(u"Puan Türü"), index=True, choices="giris_puan_turleri")
    giris_puani = field.Float(_(u"Giriş Puani"), index=True)
    aktif_donem = field.String(_(u"Dönem"), index=True)
    ogrencilik_statusu = field.Integer(_(u'Öğrencilik Statüsü'), index=True,
                                       choices="ogrenci_program_durumlar")
    ogrenci_ders_kayit_status = field.Integer(_(u'Öğrencilik Ders Kayıt Statüsü'), index=True,
                                              choices="ogrenci_ders_kayit_durum")
    ayrilma_nedeni = field.Integer(_(u'Ayrılma Nedeni'), index=True, choices='ayrilma_nedeni')
    basari_durumu = field.String(_(u"Başarı Durumu"), index=True)
    diploma_no = field.String(_(u"Diploma No"), index=True)
    ders_programi = DersProgrami()
    danisman = Personel()
    program = Program()
    ogrenci = Ogrenci()
    bagli_oldugu_bolum = Unit(_(u"Bölüm"))

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Öğrenci Programı")
        verbose_name_plural = _(u"Öğrenci Programları")

    class Belgeler(ListNode):
        tip = field.Integer(_(u"Belge Tipi"), choices="belge_tip", index=True)
        aciklama = field.String(_(u"Ek Açıklama"), index=True, default="-", required=False)
        tamam = field.Boolean(_(u"Belge kontrol edildi"), index=True, required=True)

    class OgrenciDonem(ListNode):
        donem = Donem()

    def __unicode__(self):
        return '%s - %s / %s' % (self.ogrenci, self.program.adi, self.program.yil)

    def tarih_sirasiyla_donemler(self):
        r = []
        for ogd in self.OgrenciDonem:
            r.append((ogd.donem.ad, ogd.donem.baslangic_tarihi))
        r.sort(key=lambda tup: tup[1])
        return r


class OgrenciDersi(Model):
    """Öğrenci Dersi Modeli

    Öğrencilerin ders seçimlerinin saklandığı modeldir.

    Ders alanı Şube modeli ile ilişkilendirilmiştir. Bunun sebebi öğrencilerin ders seçiminin,
    ders ve okutmanın birleştiği şube seçimi olmasıdır. Detaylı bilgiler Şube modelinde bulunabilir.

    Bir öğrencinin devamsızlıktan kalıp kalmadığı devamsizliktan_kalma alanı ile kontrol edilir.
    Bu alan False olduğu zaman öğrenci devamsızlıktan kalır.

    """

    alis_bicimi = field.Integer(_(u"Dersi Alış Biçimi"), index=True)
    sube = Sube(unique=True)
    ogrenci_program = OgrenciProgram()
    ogrenci = Ogrenci(unique=True)
    basari_ortalamasi = field.Float(_(u"Ortalama"), index=True)
    harflendirilmis_not = field.String(_(u"Harf"), index=True)
    katilim_durumu = field.Boolean(_(u"Devamsızlıktan Kalma"), default=False, index=True)

    # arama amaçlı alanlar
    ders = Ders()
    donem = Donem()

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Ögrenci Dersi")
        verbose_name_plural = _(u"Öğrenci Dersleri")
        list_fields = ['ders', 'alis_bicimi']
        search_fields = ['alis_bicimi', ]
        unique_together = [('ogrenci', 'sube')]

    def post_creation(self):
        """
        Yeni bir ``OgrenciDers``'i ilk defa yaratılınca ``donem`` ve ``ders`` alanları,
        bağlı şubeden atanır.

        """

        self.donem = self.sube.donem
        self.ders = self.sube.ders
        self.save()

    def ders_adi(self):
        """
        Şubenin bağlı olduğu ders adı.

        Returns:
            Şubenin bağlı olduğu ders örneğinin adını döndürür.

        """

        return six.text_type(self.ders.ad)

    ders_adi.title = 'Ders'

    def __unicode__(self):
        return '%s %s %s' % (self.ders.kod, self.ders.ad, self.alis_bicimi)


class DersKatilimi(Model):
    """Ders Katılımı Modeli

    Öğrencilerin devam durumları hakkında bilgilerin saklandığı modeldir. Okutman tarafından
    verilecek yüzdelik bir ifadeyle katılım durumu alanında saklanır.

    Temel ilişki Ogrenci ve Ders modelleri ile kurulmuştur.

    Note:
        Okutman arama kolaylığı amacıyla saklanmıştır.

    """

    # TODO: Neden float, soralım?
    katilim_durumu = field.Integer(_(u"Katılım Durumu"), index=True)
    sube = Sube()
    ogrenci = Ogrenci()
    okutman = Okutman()
    aciklama = field.String(_(u"Açıklama"))

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Ders Devamsızlığı")
        verbose_name_plural = _(u"Ders Devamsızlıklari")
        list_fields = ['katilim_durumu', 'sube_dersi']
        search_fields = ['sube_dersi', 'katilim_durumu']

    def sube_dersi(self):
        """
        Şubenin bağlı olduğu ders adı.

        Returns:
            Şubenin bağlı olduğu ders örneğinin adını döndürür.

        """

        return six.text_type(self.sube.ders)

    sube_dersi.title = 'Ders'

    def __unicode__(self):
        return '%s %s' % (self.katilim_durumu, self.ogrenci)


class Borc(Model):
    """Borç modeli

    Öğrencilerin ödemesi gereken ücret (harc, belge, belgeler, kimlik
    ücretleri vb.) bilgilerinin saklandığı modeldir.

    ``tahakkuk_referans_no`` sistem tarafından üretilen ve
    3. taraflara (banka veya ilgili diğer kurumlar) iletilen tekil
    takip koddur.

    """

    miktar = field.Float(_(u"Borç Miktarı"), index=True)
    para_birimi = field.Integer(_(u"Para Birimi"), index=True, choices="para_birimleri")
    sebep = field.Integer(_(u"Borç Sebebi"), index=True, choices="ogrenci_borc_sebepleri")
    son_odeme_tarihi = field.Date(_(u"Son Ödeme Tarihi"), index=True)
    tahakkuk_referans_no = field.String(_(u"Tahakkuk Referans No"), index=True)
    aciklama = field.String(_(u"Borç Açıklaması"), index=True)
    ogrenci = Ogrenci()
    donem = Donem()

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Borç")
        verbose_name_plural = _(u"Borçlar")
        list_fields = ['miktar', 'son_odeme_tarihi']
        search_fields = ['miktar', 'odeme_tarihi']

    def __unicode__(self):
        return '%s %s %s %s' % (self.miktar, self.para_birimi, self.sebep, self.son_odeme_tarihi)


class Banka(Model):
    """Banka Modeli

    Basitçe banka adı ve tekil bir banka kodu ile saklanır.

    """

    ad = field.String("Banka Adi", index=True)
    kod = field.String("Banka Kodu", index=True)

    class Meta:
        verbose_name = "Banka"
        verbose_name_plural = "Bankalar"

    def __unicode__(self):
        return '%s %s' % (self.ad, self.kod)


class Odeme(Model):
    """Ödeme Modeli

    Öğrencilerin borçlarına karşılık, banka veya diğer yollar ile tahsil
    edilen ödemelerin saklandığı data modelidir.

    """

    miktar = field.Float("Borç Miktarı", index=True)
    para_birimi = field.Integer("Para Birimi", index=True, choices="para_birimleri")
    aciklama = field.String("Borç Açıklaması", index=True)
    odeme_sekli = field.Integer("Ödeme Şekli", index=True, choices="odeme_sekli")
    odeme_tarihi = field.Date("Ödeme Tarihi", index=True)
    borc = Borc()
    ogrenci = Ogrenci()
    banka = Banka()
    banka_sube_kodu = field.String("Banka Sube Kodu", index=True)
    banka_kanal_kodu = field.String("Kanal Kodu", index=True)
    tahsilat_referans_no = field.String("Tahsilat Referans No", index=True)
    donem = Donem()

    class Meta:
        app = 'Ogrenci'
        verbose_name = "Borc"
        verbose_name_plural = "Borclar"
        list_fields = ['miktar', 'son_odeme_tarihi']
        search_fields = ['miktar', 'odeme_tarihi']

    def __unicode__(self):
        return '%s %s %s %s' % (self.miktar, self.para_birimi, self.sebep,
                                format_date(self.son_odeme_tarihi))


class BankaAuth(Model):
    """Banka Doğrulama Modeli

    Banka kullanıcılarının doğrulanması için gereken bilgilerin
    tutulduğu data modelidir.

    """

    username = field.String(_(u"Username"), index=True)
    password = field.String(_(u"Password"), index=True)
    banka = Banka()

    class Meta:
        verbose_name = _(u"Banka Kullanicisi")
        verbose_name_plural = _(u"Banka Kullanicilari")

    def __unicode__(self):
        return '%s %s' % (self.username, self.banka.ad)


class DegerlendirmeNot(Model):
    """Değerlendirme Notu Modeli

    Ders değerlendirmeleri (sınavlar, sunum, proje, odev vb.) için okutmanlar
    tarafından verilen notların saklandığı data modelidir.

    Temel ilişki Sınav ve Öğrenci modeli ile kurulmuştur. Değerlendirme
    bilgisi puan alanında saklanır.

    Note:
        Ders, öğretim elemeanı, yıl ve donem, alanları arama kolaylığı
        açısından saklanmaktadır.

    """

    puan = field.Integer(_(u"Puan"), index=True)
    sinav = Sinav()
    ogrenci = Ogrenci()
    aciklama = field.String(_(u"Puan Açıklaması"), index=True, required=False)

    # Arama amacli alanlar.
    yil = field.String(_(u"Yıl"), index=True)
    donem = field.String(_(u"Dönem"), index=True)
    ogretim_elemani = field.String(_(u"Öğretim Elemanı"), index=True)
    ogrenci_no = field.String(_(u"Öğrenci No"), index=True)
    sinav_tarihi = field.Date(_(u"Sınav Tarihi"), index=True)
    ders = Ders()

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Not")
        verbose_name_plural = _(u"Notlar")
        list_fields = ['puan', 'ders_adi']
        search_fields = ['aciklama', 'puan', 'ogrenci_no']
        list_filters = ['donem', ]

    def post_save(self):
        self.sinav.degerlendirme = True
        self.sinav.puan = self.puan
        self.sinav.save()

    def ders_adi(self):
        return "%s" % self.ders.ad

    ders_adi.title = "Ders"

    def __unicode__(self):
        return '%s %s' % (self.puan, self.sinav)


AKADEMIK_TAKVIM_ETKINLIKLERI = [
    ('1', _(u'Yeni Öğrenci Ön Kayıt')),
    ('2', _(u'Güz Dönem Başlangıcı')),
    ('3', _(u'Derslerin Acılması')),
    ('4', _(u'Subelendirme ve Ders Programının Ilan Edilmesi')),
    ('5', _(u'Öğrenci Harç')),
    ('6', _(u'Öğrenci Ek Harç')),
    ('7', _(u'Mazeretli Öğrenci Harç')),
    ('8', _(u'Yeni Öğrenci Ders Kayıt')),
    ('9', _(u'Yeni Öğrenci Danışman Onay')),
    ('10', _(u'Ders Kayıt')),
    ('11', _(u'Danışman Onay')),
    ('12', _(u'Mazeretli Ders Kayıt')),
    ('13', _(u'Mazeretli Danışman Onay')),
    ('14', _(u'Derslerin Başlangıcı')),
    ('15', _(u'Ders Ekle/Bırak')),
    ('16', _(u'Ders Ekle/Bırak Danışman Onay')),
    ('17', _(u'Danışman Dersten Çekilme İşlemleri')),
    ('18', _(u'Ara Sinav')),
    ('19', _(u'Ara Sınav Not Giriş')),
    ('20', _(u'Ara Sınav Notlarının Öğrenciye Yayınlanması')),
    ('21', _(u'Ara Sinav Mazeretli')),
    ('22', _(u'Ara Sınav Mazeret Not Giriş')),
    ('23', _(u'Ara Sınav Mazeret Notlarının Öğrenciye Yayınlanması')),
    ('24', _(u'Sınav Maddi Hata Düzeltme')),
    ('25', _(u'Derslerin Bitişi')),
    ('26', _(u'Yariyil Sinav')),
    ('27', _(u'Yarıyıl Sınavı Not Giriş')),
    ('28', _(u'Yarıyıl Sınavı Notlarının Öğrenciye Yayınlanmasi')),
    ('29', _(u'Bütünleme ve Yarı Yıl Sonu Mazeret Sınavı')),
    ('30', _(u'Bütünleme ve Yarı Yıl Sonu Mazeret Sınavı Not Giriş')),
    ('31', _(u'Bütünleme ve Yarı Yıl Sonu Mazeret Sınavı Notlarının Öğrenciye Yayınlanması')),
    ('32', _(u'Harf Notlarının Öğrenciye Yayınlanması')),
    ('33', _(u'Bütünleme Harf Notlarının Öğrenciye Yayınlanması')),
    ('34', _(u'Öğretim Elemanı Yoklama Girişi')),
    ('35', _(u'Güz Dönemi Bitiş')),
    ('36', _(u'Bahar Dönemi Başlangıcı')),
    ('37', _(u'Bahar Donemi Derslerin Acilmasi')),
    ('38', _(u'Bahar Donemi Subelendirme ve Ders Programının Ilan Edilmesi')),
    ('39', _(u'Bahar Dönem Başlangıcı')),
    ('40', _(u'Öğrenci Harç')),
    ('41', _(u'Öğrenci Ek Harç')),
    ('42', _(u'Mazeretli Öğrenci Harç')),
    ('43', _(u'Ders Kayıt')),
    ('44', _(u'Danışman Onay')),
    ('45', _(u'Mazeretli Ders Kayıt')),
    ('46', _(u'Mazeretli Danışman Onay')),
    ('47', _(u'Derslerin Başlangıcı')),
    ('48', _(u'Ders Ekle / Bırak')),
    ('49', _(u'Ders Ekle / Bırak Onay')),
    ('50', _(u'Ara Sinav')),
    ('51', _(u'Ara Sınav Not Giriş')),
    ('52', _(u'Ara Sınav Notlarının Öğrenciye Yayınlanması')),
    ('53', _(u'Ara Sinav Mazeretli')),
    ('54', _(u'Ara Sınav Mazeret Not Giriş')),
    ('55', _(u'Ara Sınav Mazeret Notlarının Öğrenciye Yayınlanması')),
    ('56', _(u'Sınav Maddi Hata Düzeltme')),
    ('57', _(u'Derslerin Bitişi')),
    ('58', _(u'Yariyil Sinav baslangic')),
    ('59', _(u'Yarıyıl Sınavı Not Giriş')),
    ('60', _(u'Yarıyıl Sınavı Notlarının Öğrenciye Yayınlanmasi')),
    ('61', _(u'Öğretim Elemanı Yoklama Girişi')),
    ('62', _(u'Bahar Dönem Bitişi')),
    ('63', _(u'Yaz Dönemi Başlangıcı')),
    ('64', _(u'Yaz Dönemi Derslerin Bitişi')),
    ('65', _(u'Yaz Dönemi Sınavların Başlangıcı')),
    ('66', _(u'Yaz Dönemi Bitişi')),
    ('67', _(u'Güz Dönemi Dersler')),
    ('68', _(u'Bahar Dönemi Dersler')),
    ('69', _(u'Yaz Dönemi Dersler')),
    ('70', _(u'1 Mayıs İşçi Bayrami')),
    ('71', _(u'23 Nisan Ulusal Egemenlik ve Çocuk Bayramı')),
    ('72', _(u'19 Mayıs Genclik ve Spor Bayramı'))

]


class AkademikTakvim(Model):
    """Akademik Takvim Modeli

    Akademik Takvim etkinlikleri bilgileri modeldir. AKADEMIK_TAKVIM_ETKINLIKLERI ile
    tanımlanmış her bir etkinlik için tarih veya tarih aralığı bigisi saklanır.

    Universiteye ait bir takvim zorunlu olarak varolmakla birlikte
    istenirse etkinlikler birimlere göre farklılık gösterebilirler.

    """

    birim = Unit(_(u"Birim"), index=True)
    # yil = field.Date("Yıl", index=True)
    ogretim_yili = OgretimYili(_(u"Öğretim Yılı"), index=True)

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Akademik Takvim")
        verbose_name_plural = _(u"Akademik Takvimler")
        list_fields = ['_birim', 'ogretim_yili']
        # search_fields = ['yil']

    def _birim(self):
        return "%s" % self.birim

    _birim.title = 'Birim'

    def __unicode__(self):
        return '%s %s' % (self.birim, self.ogretim_yili.ad)

    def etkinlikler(self):
        return Takvim.objects.filter(akademik_takvim=self)

    def timeline(self):
        tl = []
        for e in self.etkinlikler():
            if not e.baslangic:
                tl.append((e.etkinlik, e.bitis))
            elif not e.bitis:
                tl.append((e.etkinlik, e.baslangic))
            elif e.baslangic and e.bitis:
                if e.baslangic.date == e.bitis.date:
                    tl.append((e.etkinlik, e.baslangic))
                else:
                    tl.append((gettext(u"%s başlangıç") % e.etkinlik, e.baslangic))
                    tl.append((gettext(u"%s bitiş") % e.etkinlik, e.bitis))


class Takvim(Model):
    """
    olay, bir zaman araliginda gerceklesiyorsa(ayni gunun saat araliklari dahil),
                                                    baslangic ve bitis zamanlari ayri ayri verilir,
    olay, bir gun icinde ancak kesin zaman bagimsiz/belirsiz gerceklesiyorsa,
                                                    baslangic ve bitis zamanlari ayni verilir,
    olay, belirsiz bir baslangic yani son gun belirtilmisse, sadece bitis tarihi verilir,
    olay, belirsiz bir son yani baslama gun belirtilmisse, sadece baslangic tarihi verilir,
    """
    etkinlik = field.Integer(_(u"Etkinlik"), index=True, choices=AKADEMIK_TAKVIM_ETKINLIKLERI)
    baslangic = field.DateTime(_(u"Başlangıç"), index=True, format="%d.%m.%Y", required=False)
    bitis = field.DateTime(_(u"Bitiş"), index=True, format="%d.%m.%Y", required=False)
    akademik_takvim = AkademikTakvim(_(u"Akademik Takvim"))
    resmi_tatil = field.Boolean(_(u"Resmi Tatil"), index=True)

    def pre_save(self):
        if not self.baslangic and not self.bitis:
            raise Exception("Tarihlerden en az bir tanesi dolu olmalidir.")

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Takvim")
        verbose_name_plural = _(u"Takvimler")
        list_filters = ["etkinlik", "baslangic", "bitis", 'resmi_tatil']

    def __unicode__(self):
        return '%s %s %s' % (
            self.akademik_takvim.birim, self.akademik_takvim.ogretim_yili, self.etkinlik)


class DonemDanisman(Model):
    """Dönem Danışmanları Modeli

    Dönem, Bölüm ve Program bazlı olarak öğrencilere danışman
    atanabilecek olan öğretim elemanlarının saklandığı data modelidir.

    """

    donem = Donem()
    okutman = Okutman()
    bolum = Unit()
    aciklama = field.String(_(u"Açıklama"), index=True, required=False)

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Dönem Danışman")
        verbose_name_plural = _(u"Dönem Danışmanları")
        list_fields = ['program', 'okutman', 'bolum', 'donem']
        search_fields = ['aciklama']

    def __unicode__(self):
        return '%s %s' % (self.bolum, self.okutman)


class DondurulmusKayit(Model):
    """Dondurulmuş Kayıt Modeli

    Dondurulmuş öğrenci kayıtlarının saklandığı data modelidir.

    """

    donem = Donem()
    ogrenci_program = OgrenciProgram()
    baslangic_tarihi = field.Date(_(u"Başlangıç Tarihi"), index=True)
    aciklama = field.String(_(u"Açıklama"), index=True, required=False)

    class Meta:
        app = 'Ogrenci'
        verbose_name = _(u"Dondurulmuş Kayıt")
        verbose_name_plural = _(u"Dondurulmuş Kayıtlar")
        list_fields = ['ogrenci_program', 'baslangic_tarihi', 'aciklama', 'donem']
        search_fields = ['aciklama', 'baslangic_tarihi']

    def __unicode__(self):
        return '%s %s' % (self.ogrenci_program, self.donem)
