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
                        "group_title": "Ünvan ve Derece",
                        "items": ['unvan', 'derece', 'unvan_aciklama'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": "Diğer",
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

    save_edit = fields.Button("Kaydet")


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
        evet = fields.Button("Evet", cmd='kadro_sil')
        hayir = fields.Button("Hayır")

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
        _form.help_text = """Akademik unvanı: **%s**
        Kadro numarası: **%s**
        Açıklaması: **%s**

        bilgilerine sahip kadroyu silmek istiyor musunuz ?""" % (
            unvan, kadro_no, aciklama)
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
                {'name': 'Sil', 'cmd': 'kadro_sil_onay_form', 'show_as': 'button'},
                {'name': 'İzinli Yap', 'cmd': 'sakli_izinli_degistir', 'show_as': 'button'}])

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
                {'name': 'Sakli Yap', 'cmd': 'sakli_izinli_degistir', 'show_as': 'button'})

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
                {'name': 'Düzenle', 'cmd': 'add_edit_form', 'show_as': 'button'},
            ])


class TerfiForm(JsonForm):
    class Meta:
        inline_edit = ['sec']

    class Personel(ListNode):
        key = fields.String("Key", hidden=True)
        sec = fields.Boolean("Seç", type="checkbox")
        tckn = fields.String("TCK No")
        ad_soyad = fields.String("Ad")
        kadro_derece = fields.String("Kadro Derece")

        gorev_ayligi = fields.String("GA")
        kazanilmis_hak = fields.String("KH")
        emekli_muktesebat = fields.String("EM")

        yeni_gorev_ayligi = fields.String("Yeni GA")
        yeni_kazanilmis_hak = fields.String("Yeni KH")
        yeni_emekli_muktesebat = fields.String("Yeni EM")

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

        help_text = """
        GA: Görev Aylığı
        KH: Kazanılmış Hak
        EM: Emekli Muktesebat

        D: Derece
        K: Kademe
        G: Gorunen
        """

    class Personel(ListNode):
        key = fields.String("Key", hidden=True)
        tckn = fields.String("T.C. No")
        ad_soyad = fields.String("İsim")
        kadro_derece = fields.String("Kadro Derece")

        gorev_ayligi = fields.String("GA")
        kazanilmis_hak = fields.String("KH")
        emekli_muktesebat = fields.String("EM")

        yeni_gorev_ayligi_derece = fields.Integer("GAD")
        yeni_gorev_ayligi_kademe = fields.Integer("GAK")
        yeni_gorev_ayligi_gorunen = fields.Integer("GAG")

        yeni_kazanilmis_hak_derece = fields.Integer("KHD")
        yeni_kazanilmis_hak_kademe = fields.Integer("KHK")
        yeni_kazanilmis_hak_gorunen = fields.Integer("KHG")

        yeni_emekli_muktesebat_derece = fields.Integer("EMD")
        yeni_emekli_muktesebat_kademe = fields.Integer("EMK")
        yeni_emekli_muktesebat_gorunen = fields.Integer("EMG")

    devam = fields.Button("Devam Et", cmd="kaydet")


class PersonelTerfiKriterleri(JsonForm):
    baslangic_tarihi = fields.Date("Başlangıç Tarihi",
                                   default=datetime.date.today().strftime('d.%m.%Y'))

    bitis_tarihi = fields.Date("Bitiş Tarihi", default=(
        datetime.date.today() + datetime.timedelta(days=15)).strftime('d.%m.%Y'))

    personel_turu = fields.Integer("Personel Türü", choices=[(1, "Akademik"), (2, "Idari")],
                                   default=2)

    devam = fields.Button("Sorgula")


class TerfiListe(CrudView):
    class Meta:
        model = "Personel"

    def personel_kriterleri(self):
        _form = PersonelTerfiKriterleri(current=self.current,
                                        title="Terfisi Yapılacak Personel Kriterleri")
        self.form_out(_form)

    def terfisi_gelen_personel_liste(self):

        try:
            self.current.task_data["personeller"]
        except KeyError:
            personel_turu = self.current.input['form']['personel_turu']

            baslangic_tarihi = datetime.datetime.strptime(
                self.current.input['form']['baslangic_tarihi'], '%d.%m.%Y')
            bitis_tarihi = datetime.datetime.strptime(
                self.current.input['form']['bitis_tarihi'], '%d.%m.%Y')
            self.current.task_data["personeller"] = terfi_tarhine_gore_personel_listesi(
                baslangic_tarihi=baslangic_tarihi, bitis_tarihi=bitis_tarihi,
                personel_turu=personel_turu)

        if self.current.task_data["personeller"]:
            _form = TerfiForm(current=self.current, title="Terfi İşlemi")
            _form.generate_form()

            _form.kaydet = fields.Button("Onaya Gönder", cmd="onaya_gonder")
            _form.duzenle = fields.Button("Terfi Düzenle", cmd="terfi_liste_duzenle")

            self.form_out(_form)
            self.current.output["meta"]["allow_actions"] = False
            self.current.output["meta"]["allow_add_listnode"] = False
        else:
            datetime.datetime.today()
            self.current.output['msgbox'] = {
                'type': 'info', "title": 'Terfi Bekleyen Personel Bulunamadı',
                "msg": '%s - %s tarih aralığında terfi bekleyen personel bulunamadı.' % (
                    baslangic_tarihi.strftime('%d-%m-%Y'),
                    bitis_tarihi.strftime('%d-%m-%Y'))
            }

    def terfi_liste_duzenle(self):
        _form = TerfiDuzenleForm()
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

        msg = {"title": 'Personeller Onay Icin Gonderildi!',
               "body": 'Talebiniz Basariyla iletildi.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def onay_kontrol(self):
        _form = TerfiForm(current=self.current, title="Terfi İşlemi")
        _form.generate_form()
        _form.Meta.inline_edit = []

        _form.kaydet = fields.Button(title="Onayla", cmd="terfi_yap")
        _form.duzenle = fields.Button(title="Reddet", cmd="red_aciklamasi_yaz")

        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def red_aciklamasi_yaz(self):
        _form = JsonForm(title="Terfi Islemi Reddedildi.")
        _form.Meta.help_text = """Terfi işlemini onaylamadınız. İlgili personele bir açıklama
                                  yazmak ister misiniz?"""
        _form.red_aciklama = fields.String("Açıklama")
        _form.devam = fields.Button("Devam Et")
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
        msg = {"title": 'Personel Terfi Islemi Onaylandi!',
               "body": 'Onay Belgesi icin Personel Islerine Gonderildi.'}
        self.current.output['msgbox'] = msg
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def onay_belgesi_uret(self):
        self.current.output['msgbox'] = {
            'type': 'info',
            'title': 'Terfi İşlemleri Onay Belgesi!',
            'msg': 'Toplu terfi İşleminiz Onaylandı'
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

        self.gorev_suresi_bitis = fields.Date("Görev Süresi Bitiş Tarihi",
                                              default=kwargs.pop('gorev_suresi_bitis_tarihi'))
        self.personel_id = fields.String("personel_id", hidden=True,
                                         default=kwargs.pop('personel_id'))

        # Üst sınıfın constructor metodu çağrılmaktadır.        
        super(GorevSuresiForm, self).__init__()

    kaydet = fields.Button("Kaydet", cmd="kaydet")


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
                    gorev_suresi_bitis = personel.gorev_suresi_bitis.strftime("%Y-%m-%d")
                else:
                    gorev_suresi_bitis = None

                _form = GorevSuresiForm(current=self.current, title="Görev Süresi Uzat",
                                        gorev_suresi_bitis_tarihi=gorev_suresi_bitis,
                                        personel_id=personel.key)
                self.form_out(_form)
            else:
                self.current.output['msgbox'] = {
                    'type': 'info', "title": 'HATA !',
                    "msg": '%s %s akademik bir personel değildir.' % (
                        personel.ad,
                        personel.soyad)
                }

        except ObjectDoesNotExist:
            self.current.output["msgbox"] = {
                'type': "info", "title": "HATA !",
                "msg": "%s %s e ait bir atama kaydı bulunamadı" % (personel.ad,
                                                                     personel.soyad)
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
