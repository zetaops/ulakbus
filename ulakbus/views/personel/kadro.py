# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

"""Kadro İşlemleri

Kadro İşlemleri İş Akışı 5 adimdan olusmaktadir:

    * Kadro Listele
    * Saklı Kadro Ekle
    * Kaydet
    * Kadro durumunu Saklı veya İzinli yap
    * Kadro Sil Onay
    * Kadro Sil

Bu iş akışı, CrudView nesnesi genişletilerek(extend) işletilmektedir.
Adımlar arası geçiş CrudView'ın aksine otomatik değil, manuel olarak
yapılmaktadır.

Her adım başına kullanılan metodlar şu şekildedir:

Kadro Listele:
   CrudView list metodu kullanılmıştır. Liste ekranında CrudView
   standart filtreleme ve arama özellikleri kullanılmaktadır.
   Listenin her bir öğesi için object_actions filtreleri @obj_filter
   dekoratörleri yardımıyla özelleştirilmiştir.

   Kadro işlemleri kurallarına göre sadece saklı kadrolar eklenebilmekte
   veya silinebilmektedir. Bu sebeple 'sil' eylemi sadece bu türdeki
   kadrolar icin aktifdir.

   Saklı / İzinli Yap butonu ise sadece saklı veya izinli kadrolar için
   görünürdür.

Saklı Kadro Ekle:
   Kadrolar sadece ve sadece saklı olarak sisteme eklenebilirler. Bu
   amaçla iş akışı adımlarına CrudView add_edit_form metodunun
   çağrıldığı adımın hemen ardından kaydet metodu konulmuştur. Bu metod
   durum alanını SAKLI olmaya zorlayarak nesneyi kaydeder.

Kaydet:
   WF'nin 2. adımından gelen data CrudView'in set_form_data_to_object
   metoduyla bir Kadro instance oluşturularak aktarılır.

   Durum alanı saklı (1) olarak sabitlenip kaydedilir.

Kadro Durumunu Sakli veya Izinli yap:
   Bunun icin özel bir metod eklenmistir: sakli_izinli_degistir. Bu
   üzerinde işlem yapılan kadronun durumu arasında geçis yapar.

Kadro Sil
   Sadece durumu sakli (1) olan kadrolar silinebilir. Bunun için kadro
   sil metodunda bu kontrol yapilir ve delete metodu çalıştırılır.

Kadro Sil Onay
   Silme işlemi için onay adımıdır.

"""
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.lib.personel import terfi_tarhine_gore_personel_listesi
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy, format_datetime, format_date
from ulakbus.models import Personel
from pyoko import ListNode
from dateutil.relativedelta import relativedelta
import datetime


class KadroObjectForm(JsonForm):
    """KadoIslemleri için object form olarak kullanılacaktır.

    Meta değiştirilerek, formlardan durum alanı çıkarılmış, ve form
    alanları iki gruba ayrılmıştır.

    Formun sadece bir kaydet butonu mevcuttur.

    """

    class Meta:
        exclude = ['durum', ]

        grouping = [
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"Ünvan ve Derece"),
                        "items": ['unvan', 'derece', 'unvan_aciklama'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"Diğer"),
                        "items": ['kadro_no', 'aciklama', 'birim_id']
                    }
                ]
            },
            {
                "layout": "7",
                "groups": [
                    {
                        "items": ['kaydet']
                    }
                ]
            }
        ]

    save_edit = fields.Button(gettext_lazy(u"Kaydet"))


class KadroIslemleri(CrudView):
    """Kadro İşlemleri

    Kado işlemleri için kullanacağımız temel model Kadro modelidir.
    Meta.model bu amaçla kullanılmıştır. Aynı şekilde Meta içerisinde
    yer alan object_actions iş akışı boyunca özel olarak doldurulacağı
    için burada boşaltılmıştır.

    """

    # Kadro Durumları
    SAKLI = 1
    IZINLI = 2
    BOS = 3
    DOLU = 4

    class Meta:

        # CrudViev icin kullanilacak temel Model
        model = 'Kadro'

        # ozel bir eylem listesi hazirlayacagiz. bu sebeple listeyi bosaltiyoruz.
        # kayit tipine bagli olarak ekleyecegimiz eylemleri .append() ile ekleyecegiz
        object_actions = [
            # boş, action dictler sonraki adımlarda bu listeye aşağıdaki biçimde eklenmeli:
            # {'fields': [0, ], 'cmd': 'show', 'mode': 'normal', 'show_as': 'link'},
        ]

    def __init__(self, current):
        """Standart ObjectForm nesnesini değil, hemen yukarıda tanımladığımız
        KadroObjectForm nesnesini kullan. Bu atamayı yapıp, üst sınıfın init
        metodu çağrılır.

        """

        self.ObjectForm = KadroObjectForm
        super(KadroIslemleri, self).__init__(current)

    def kadro_kaydet(self):
        """Formdan gelen dataları Kadro örneğine doldurur ve kaydeder.

        Kadrolar yanlızca SAKLI olarak kayıt edilebilecekleri için kaydetmeden
        önce durum alanı SAKLI yapılır.

        İş akışı bu adımdan sonra sona eriyor. İş akışını yeni bir token ile
        yenilemek için reset metodunu çağırıyoruz.

        """

        # Formdan gelen datayi, instance a gecir.
        self.set_form_data_to_object()

        # Durumu ne olursa olsun (sakli) yap!..
        self.object.durum = self.SAKLI

        # Kadroyu kaydet
        self.object.save()

        # İş akışını yenile
        self.reset()

    class SilOnayForm(JsonForm):
        evet = fields.Button(gettext_lazy(u"Evet"), cmd='kadro_sil')
        hayir = fields.Button(gettext_lazy(u"Hayır"))

    def kadro_sil_onay_form(self):
        """
        Silme işlemi için onay adımı. Kadronun detaylı açıklaması listelenir ve
        onay vermesi beklenir.

        """

        unvan = self.object.get_unvan_display()
        aciklama = self.object.aciklama
        kadro_no = self.object.kadro_no

        self.current.task_data['object_id'] = self.object.key

        _form = self.SilOnayForm(title=" ")
        _form.help_text = _(u"""Akademik unvanı: **%(unvan)s**
        Kadro numarası: **%(kadro)s**
        Açıklaması: **%(aciklama)s**

        bilgilerine sahip kadroyu silmek istiyor musunuz ?""") % {
            'unvan': unvan, 'kadro': kadro_no, 'aciklama': aciklama,
        }
        self.form_out(_form)

    def kadro_sil(self):
        """
        Saklı kontolü yaparak, silme işlemini gerçekleştirir.

        """
        # TODO: Sakli kadronun silinme denemesi loglanacak.
        assert self.object.durum == self.SAKLI, "attack detected, should be logged/banned"
        self.object.blocking_delete()
        del self.current.task_data['object_id']

    def sakli_izinli_degistir(self):
        """Saklı İzinli Değiştir

        Durum degerini SAKLI ve IZINLI arasinda degistir.

        sakliysa izinli yap 3 - SAKLI = IZINLI
        izinliyse sakli yap 3 - IZINLI = SAKLI

        """

        self.object.durum = 3 - self.object.durum
        self.object.save()

    @obj_filter
    def sakli_kadro(self, obj, result):
        """Saklı Kadro Filtresi

        Saklı kadro listesinde yer alan her bir öğeye İzinli Yap butonu ekler.

        Args:
            obj: Kadro instance
            result: dict

        """

        if obj.durum == self.SAKLI:
            result['actions'].extend([
                {'name': _(u'Sil'), 'cmd': 'kadro_sil_onay_form', 'show_as': 'button'},
                {'name': _(u'İzinli Yap'), 'cmd': 'sakli_izinli_degistir', 'show_as': 'button'}])

    @obj_filter
    def izinli_kadro(self, obj, result):
        """İzinli Kadro Filtresi

        İzinli Kadro listesinde yer alan her bir öğeye Saklı Yap butonu
        ekler.

        Args:
            obj: Kadro instance
            result: dict

        """

        if obj.durum == self.IZINLI:
            result['actions'].append(
                {'name': _(u'Sakli Yap'), 'cmd': 'sakli_izinli_degistir', 'show_as': 'button'})

    @obj_filter
    def duzenlenebilir_veya_silinebilir_kadro(self, obj, result):
        """Düzenlenebilir ve Silinebilir Kadro Filtresi

        Düzenlenebilir Kadro listesinde yer alan saklı veya izinli
        her bir öğeye Sil ve Düzenle butonu ekler.

        Args:
            obj: Kadro instance
            result: dict

        """

        if obj.durum in [self.SAKLI, self.IZINLI]:
            result['actions'].extend([
                {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'show_as': 'button'},
            ])


class TerfiForm(JsonForm):
    class Meta:
        inline_edit = ['sec']

    class Personel(ListNode):
        key = fields.String("Key", hidden=True)
        sec = fields.Boolean(gettext_lazy(u"Seç"), type="checkbox")
        tckn = fields.String(gettext_lazy(u"TCK No"))
        ad_soyad = fields.String(gettext_lazy(u"Ad"))
        kadro_derece = fields.String(gettext_lazy(u"Kadro Derece"))

        #tn: Görev Aylığı
        gorev_ayligi = fields.String(gettext_lazy(u"GA"))
        #tn: Kazanılmış Hak
        kazanilmis_hak = fields.String(gettext_lazy(u"KH"))
        #tn: Emekli Muktesebat
        emekli_muktesebat = fields.String(gettext_lazy(u"EM"))

        # tn: Yeni Görev Aylığı
        yeni_gorev_ayligi = fields.String(gettext_lazy(u"Yeni GA"))
        #tn: Yeni Kazanılmış Hak
        yeni_kazanilmis_hak = fields.String(gettext_lazy(u"Yeni KH"))
        #tn: Yeni Emekli Muktesebat
        yeni_emekli_muktesebat = fields.String(gettext_lazy(u"Yeni EM"))

    def generate_form(self):
        """
        Generates form with given data ``personel_data``

        """

        for p_key, p_data in self.context.task_data["personeller"].items():
            self.Personel(
                key=p_key,
                sec=False,
                tckn=p_data["tckn"],
                ad_soyad="%s %s" % (p_data["ad"], p_data["soyad"]),
                kadro_derece=p_data["kadro_derece"],

                gorev_ayligi="%s/%s(%s)" % (
                    p_data["guncel_gorev_ayligi_derece"], p_data["guncel_gorev_ayligi_kademe"],
                    p_data["gorunen_gorev_ayligi_kademe"]),

                kazanilmis_hak="%s/%s(%s)" % (
                    p_data["guncel_kazanilmis_hak_derece"], p_data["guncel_kazanilmis_hak_kademe"],
                    p_data["gorunen_kazanilmis_hak_kademe"]),

                emekli_muktesebat="%s/%s(%s)" % (
                    p_data["guncel_emekli_muktesebat_derece"],
                    p_data["guncel_emekli_muktesebat_kademe"],
                    p_data["gorunen_emekli_muktesebat_kademe"]),

                yeni_gorev_ayligi="%s/%s(%s)" % (
                    p_data["terfi_sonrasi_gorev_ayligi_derece"],
                    p_data["terfi_sonrasi_gorev_ayligi_kademe"],
                    p_data["terfi_sonrasi_gorunen_gorev_ayligi_kademe"]),

                yeni_kazanilmis_hak="%s/%s(%s)" % (
                    p_data["terfi_sonrasi_kazanilmis_hak_derece"],
                    p_data["terfi_sonrasi_kazanilmis_hak_kademe"],
                    p_data["terfi_sonrasi_gorunen_kazanilmis_hak_kademe"]),

                yeni_emekli_muktesebat="%s/%s(%s)" % (
                    p_data["terfi_sonrasi_emekli_muktesebat_derece"],
                    p_data["terfi_sonrasi_emekli_muktesebat_kademe"],
                    p_data["terfi_sonrasi_gorunen_emekli_muktesebat_kademe"])
            )


class TerfiDuzenleForm(JsonForm):
    class Meta:
        inline_edit = [
            'yeni_gorev_ayligi_derece', 'yeni_gorev_ayligi_kademe', 'yeni_gorev_ayligi_gorunen',
            'yeni_kazanilmis_hak_derece', 'yeni_kazanilmis_hak_kademe',
            'yeni_kazanilmis_hak_gorunen', 'yeni_emekli_muktesebat_derece',
            'yeni_emekli_muktesebat_kademe', 'yeni_emekli_muktesebat_gorunen']

        help_text = gettext_lazy(u"""
        GA: Görev Aylığı
        KH: Kazanılmış Hak
        EM: Emekli Muktesebat

        D: Derece
        K: Kademe
        G: Gorunen
        """)

    class Personel(ListNode):
        key = fields.String("Key", hidden=True)
        tckn = fields.String(gettext_lazy(u"T.C. No"))
        ad_soyad = fields.String(gettext_lazy(u"İsim"))
        kadro_derece = fields.String(gettext_lazy(u"Kadro Derece"))

        #tn: Görev Aylığı
        gorev_ayligi = fields.String(gettext_lazy(u"GA"))
        #tn: Kazanılmış Hak
        kazanilmis_hak = fields.String(gettext_lazy(u"KH"))
        #tn: Emekli Muktesebat
        emekli_muktesebat = fields.String(gettext_lazy(u"EM"))

        #tn: Yeni Görev Aylığı Derece
        yeni_gorev_ayligi_derece = fields.Integer(gettext_lazy(u"GAD"))
        #tn: Yeni Görev Aylığı Kademe
        yeni_gorev_ayligi_kademe = fields.Integer(gettext_lazy(u"GAK"))
        #tn: Yeni Görev Aylığı Görünen
        yeni_gorev_ayligi_gorunen = fields.Integer(gettext_lazy(u"GAG"))

        #tn: Kazanılmış Görev Aylığı Derece
        yeni_kazanilmis_hak_derece = fields.Integer(gettext_lazy(u"KHD"))
        #tn: Kazanılmış Görev Aylığı Derece
        yeni_kazanilmis_hak_kademe = fields.Integer(gettext_lazy(u"KHK"))
        #tn: Kazanılmış Görev Aylığı Derece
        yeni_kazanilmis_hak_gorunen = fields.Integer(gettext_lazy(u"KHG"))

        #tn: Emekli Muktesebat Derece
        yeni_emekli_muktesebat_derece = fields.Integer(gettext_lazy(u"EMD"))
        #tn: Emekli Muktesebat Derece
        yeni_emekli_muktesebat_kademe = fields.Integer(gettext_lazy(u"EMK"))
        #tn: Emekli Muktesebat Derece
        yeni_emekli_muktesebat_gorunen = fields.Integer(gettext_lazy(u"EMG"))

    devam = fields.Button(gettext_lazy(u"Devam Et"), cmd="kaydet")


class PersonelTerfiKriterleri(JsonForm):
    baslangic_tarihi = fields.Date(gettext_lazy(u"Başlangıç Tarihi"),
                                   default=datetime.date.today().strftime('%d.%m.%Y'))

    bitis_tarihi = fields.Date(gettext_lazy(u"Bitiş Tarihi"), default=(
        datetime.date.today() + datetime.timedelta(days=15)).strftime('%d.%m.%Y'))

    personel_turu = fields.Integer(gettext_lazy(u"Personel Türü"),
                                   choices=[(1, gettext_lazy(u"Akademik")),
                                            (2, gettext_lazy(u"İdari"))],
                                   default=2)

    devam = fields.Button(gettext_lazy(u"Sorgula"))


class TerfiListe(CrudView):
    class Meta:
        model = "Personel"

    def personel_kriterleri(self):
        _form = PersonelTerfiKriterleri(current=self.current,
                                        title=_(u"Terfisi Yapılacak Personel Kriterleri"))
        self.form_out(_form)

    def terfisi_gelen_personel_liste(self):

        try:
            self.current.task_data["personeller"]
        except KeyError:
            personel_turu = self.current.input['form']['personel_turu']

            baslangic_tarihi = datetime.datetime.strptime(
                self.current.input['form']['baslangic_tarihi'], '%d.%m.%Y').date()
            bitis_tarihi = datetime.datetime.strptime(
                self.current.input['form']['bitis_tarihi'], '%d.%m.%Y').date()
            self.current.task_data["personeller"] = terfi_tarhine_gore_personel_listesi(
                baslangic_tarihi=baslangic_tarihi, bitis_tarihi=bitis_tarihi,
                personel_turu=personel_turu)

        if self.current.task_data["personeller"]:
            _form = TerfiForm(current=self.current, title=_(u"Terfi İşlemi"))
            _form.generate_form()

            _form.kaydet = fields.Button(_(u"Onaya Gönder"), cmd="onaya_gonder")
            _form.duzenle = fields.Button(_(u"Terfi Düzenle"), cmd="terfi_liste_duzenle")

            self.form_out(_form)
            self.current.output["meta"]["allow_actions"] = False
            self.current.output["meta"]["allow_add_listnode"] = False
        else:
            datetime.datetime.today()
            self.current.output['msgbox'] = {
                'type': 'info', "title": _(u'Terfi Bekleyen Personel Bulunamadı'),
                "msg": _(u'%(baslangic)s - %(bitis)s tarih aralığında terfi bekleyen '
                         u'personel bulunamadı.') % {
                    'baslangic': format_datetime(baslangic_tarihi),
                    'bitis': format_datetime(bitis_tarihi),
                }
            }

    def terfi_liste_duzenle(self):
        _form = TerfiDuzenleForm(title=_(u"Terfi Düzenleme Form Ekranı"))
        for p in self.current.input['form']['Personel']:
            if p['sec']:
                p_data = self.current.task_data['personeller'][p['key']]
                _form.Personel(
                    key=p_data['key'],
                    tckn=p_data["tckn"],
                    ad_soyad="%s %s" % (p_data["ad"], p_data["soyad"]),
                    kadro_derece=p_data["kadro_derece"],

                    gorev_ayligi="%s/%s(%s)" % (
                        p_data["guncel_gorev_ayligi_derece"], p_data["guncel_gorev_ayligi_kademe"],
                        p_data["gorunen_gorev_ayligi_kademe"]),

                    kazanilmis_hak="%s/%s(%s)" % (
                        p_data["guncel_kazanilmis_hak_derece"],
                        p_data["guncel_kazanilmis_hak_kademe"],
                        p_data["gorunen_kazanilmis_hak_kademe"]),

                    emekli_muktesebat="%s/%s(%s)" % (
                        p_data["guncel_emekli_muktesebat_derece"],
                        p_data["guncel_emekli_muktesebat_kademe"],
                        p_data["gorunen_emekli_muktesebat_kademe"]),

                    yeni_gorev_ayligi_derece=p_data["terfi_sonrasi_gorev_ayligi_derece"],
                    yeni_gorev_ayligi_kademe=p_data["terfi_sonrasi_gorev_ayligi_kademe"],
                    yeni_gorev_ayligi_gorunen=p_data["terfi_sonrasi_gorunen_gorev_ayligi_kademe"],

                    yeni_kazanilmis_hak_derece=p_data["terfi_sonrasi_kazanilmis_hak_derece"],
                    yeni_kazanilmis_hak_kademe=p_data["terfi_sonrasi_kazanilmis_hak_kademe"],
                    yeni_kazanilmis_hak_gorunen=p_data[
                        "terfi_sonrasi_gorunen_kazanilmis_hak_kademe"],

                    yeni_emekli_muktesebat_derece=p_data["terfi_sonrasi_emekli_muktesebat_derece"],
                    yeni_emekli_muktesebat_kademe=p_data["terfi_sonrasi_emekli_muktesebat_kademe"],
                    yeni_emekli_muktesebat_gorunen=p_data[
                        "terfi_sonrasi_gorunen_emekli_muktesebat_kademe"]

                )

        self.form_out(_form)
        self.current.output["meta"]["allow_add_listnode"] = False
        self.current.output["meta"]["allow_actions"] = False

    def terfi_duzenle_kaydet(self):
        for p in self.current.input['form']['Personel']:
            p_data = self.current.task_data['personeller'][p['key']]

            p_data["terfi_sonrasi_gorev_ayligi_derece"] = p["yeni_gorev_ayligi_derece"]
            p_data["terfi_sonrasi_gorev_ayligi_kademe"] = p["yeni_gorev_ayligi_kademe"]
            p_data["terfi_sonrasi_gorunen_gorev_ayligi_kademe"] = p["yeni_gorev_ayligi_gorunen"]

            p_data["terfi_sonrasi_kazanilmis_hak_derece"] = p["yeni_kazanilmis_hak_derece"]
            p_data["terfi_sonrasi_kazanilmis_hak_kademe"] = p["yeni_kazanilmis_hak_kademe"]
            p_data["terfi_sonrasi_gorunen_kazanilmis_hak_kademe"] = p["yeni_kazanilmis_hak_gorunen"]

            p_data["terfi_sonrasi_emekli_muktesebat_derece"] = p["yeni_emekli_muktesebat_derece"]
            p_data["terfi_sonrasi_emekli_muktesebat_kademe"] = p["yeni_emekli_muktesebat_kademe"]
            p_data["terfi_sonrasi_gorunen_emekli_muktesebat_kademe"] = p[
                "yeni_emekli_muktesebat_gorunen"]

    # todo: lane geicisi
    def mesaj_goster(self):

        msg = {"title": _(u'Personeller Onay Icin Gonderildi!'),
               "body": _(u'Talebiniz Basariyla iletildi.')}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def onay_kontrol(self):
        _form = TerfiForm(current=self.current, title=_(u"Terfi İşlemi"))
        _form.generate_form()
        _form.Meta.inline_edit = []

        _form.kaydet = fields.Button(title=_(u"Onayla"), cmd="terfi_yap")
        _form.duzenle = fields.Button(title=_(u"Reddet"), cmd="red_aciklamasi_yaz")

        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def red_aciklamasi_yaz(self):
        _form = JsonForm(title=_(u"Terfi İşlemi Reddedildi."))
        _form.Meta.help_text = _(u"""Terfi işlemini onaylamadınız. İlgili personele bir açıklama
                                  yazmak ister misiniz?""")
        _form.red_aciklama = fields.String(_(u"Açıklama"))
        _form.devam = fields.Button(_(u"Devam Et"))
        self.form_out(_form)

    def red_aciklamasi_kaydet(self):
        self.current.task_data["red_aciklama"] = self.current.input['form']['red_aciklama']

    def terfi_yap(self):
        for key, p_data in self.current.task_data['personeller'].items():
            try:
                personel = Personel.objects.get(key)

                personel.gorev_ayligi_derece = p_data["terfi_sonrasi_gorev_ayligi_derece"]
                personel.gorev_ayligi_kademe = p_data["terfi_sonrasi_gorev_ayligi_kademe"]

                personel.kazanilmis_hak_derece = p_data["terfi_sonrasi_kazanilmis_hak_derece"]
                personel.kazanilmis_hak_kademe = p_data["terfi_sonrasi_kazanilmis_hak_kademe"]

                personel.emekli_muktesebat_derece = p_data["terfi_sonrasi_emekli_muktesebat_derece"]
                personel.emekli_muktesebat_kademe = p_data["terfi_sonrasi_emekli_muktesebat_kademe"]

                personel.kh_sonraki_terfi_tarihi = personel.kh_sonraki_terfi_tarihi + relativedelta(
                    years=1)

                personel.save()

            except ObjectDoesNotExist:
                # TODO: LOG for sysadmin. Artik olmayan bir personel uzerinde terfi islemi..
                pass

    # todo: lane geicisi
    def taraflari_bilgilendir(self):
        msg = {"title": _(u'Personel Terfi Islemi Onaylandi!'),
               "body": _(u'Onay Belgesi icin Personel Islerine Gonderildi.')}
        self.current.output['msgbox'] = msg
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def onay_belgesi_uret(self):
        self.current.output['msgbox'] = {
            'type': 'info',
            'title': _(u'Terfi İşlemleri Onay Belgesi!'),
            'msg': _(u'Toplu terfi İşleminiz Onaylandı')
        }


class GorevSuresiForm(JsonForm):
    """ 
        Akademik personel görev süresini uzatma işlemi için kullanılan
        JsonForm dan türetilmiş bir form sınıfıdır.
    """

    def __init__(self, **kwargs):
        """ 
            form nesnesi üretilirken girilen parametrelerin form elemanlarının
            default değeri olarak kullanıla bilmesi amacıyla yazılan constructor
            metoddur. Akademik personelin görev süresi Atama modelinde tutulduğu
            için form nesnesi instance üretilirken ilgili atama nın id ne
            ihtiyacımız bulunmaktadır.
        """

        self.gorev_suresi_bitis = fields.Date(_(u"Görev Süresi Bitiş Tarihi"),
                                              default=kwargs.pop('gorev_suresi_bitis_tarihi'))
        self.personel_id = fields.String("personel_id", hidden=True,
                                         default=kwargs.pop('personel_id'))

        # Üst sınıfın constructor metodu çağrılmaktadır.        
        super(GorevSuresiForm, self).__init__()

    kaydet = fields.Button(gettext_lazy(u"Kaydet"), cmd="kaydet")


class GorevSuresiUzat(CrudView):
    class Meta:
        model = "Personel"

    """ 
        Görev süresi uzatma işlemini gerçekleştiren CrudView den türetilmiş
        bir sınıftır.
    """

    def gorev_suresi_form(self):
        """ 
        Öncelikle anasayfadaki personel seçim formundan seçilen personelin
        id si elde edilir. Personel id ile atama kaydı elde edilir.
        Eğer personel akademik personel değilse hata mesajı görüntülenir.
        Her akademik personele ait sadece bir adet atama kaydı bulunabilir.
        Elde edilen atama nesnesinden çekilen görev süresi bitiş tarihi
        form nesnesi instance üretilirken parametre olarak verilir.
        Son olarak da form görüntülenir.
        """

        try:
            personel = Personel.objects.get(self.current.input["id"])

            if personel.personel_turu == 1:
                if type(personel.gorev_suresi_bitis) is datetime.date:
                    gorev_suresi_bitis = format_date(personel.gorev_suresi_bitis)
                else:
                    gorev_suresi_bitis = None

                _form = GorevSuresiForm(current=self.current, title=_(u"Görev Süresi Uzat"),
                                        gorev_suresi_bitis_tarihi=gorev_suresi_bitis,
                                        personel_id=personel.key)
                self.form_out(_form)
            else:
                self.current.output['msgbox'] = {
                    'type': 'info', "title": _(u'HATA !'),
                    "msg": _(u'%(ad)s %(soyad)s akademik bir personel değildir.') % {
                        'ad': personel.ad,
                        'soyad': personel.soyad,
                    }
                }

        except ObjectDoesNotExist:
            self.current.output["msgbox"] = {
                'type': "info", "title": _(u"HATA !"),
                "msg": _(u"%(ad)s %(soyad)s e ait bir atama kaydı bulunamadı") % {
                    'ad': personel.ad,
                    'soyad': personel.soyad,
                }
            }

    def kaydet(self):
        """ 
        Formdan gelen personel id ile personel kaydı elde edilir. Sonrasındada
        görev süresi başlama ve bitiş tarihleri değiştirilerek kaydedilir.
        Yeni görev süresi başlama tarihi işlemin yapıldığı tarih,
        yeni görev süresi bitiş tarihi formdan gelen tarih olur.
        """
        personel = Personel.objects.get(self.current.input["form"]["personel_id"])
        personel.gorev_suresi_baslama = datetime.date.today()
        personel.gorev_suresi_bitis = self.current.input["form"]["gorev_suresi_bitis"]
        personel.save()
