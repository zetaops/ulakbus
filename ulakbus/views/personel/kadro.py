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
import datetime
from dateutil.relativedelta import relativedelta
from pyoko import ListNode
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.lib.personel import terfi_tarhine_gore_personel_listesi, suren_terfi_var_mi
from ulakbus.lib.personel import terfi_durum_kontrol, derece_ilerlet, terfi_tikanma_kontrol, gorunen_kademe_hesapla
from ulakbus.models import Personel, Permission, User
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView, obj_filter


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


class TerfiIslemForm(JsonForm):
    """
        Tek bir personel üzerinde yapılacak olan terfi işlemi için oluşturulmuş
        JsonForm class dan extend edilerek oluşturulmuş bir class dır.

    """
    yeni_gorev_ayligi_gorunen = fields.Integer("Görünen Görev Aylığı Kademe")
    key = fields.String("Key", hidden=True)
    tckn = fields.String("T.C. No")
    ad_soyad = fields.String("İsim")
    kadro_derece = fields.Integer("Kadro Derece")

    # Burada personelin şimdiki kadro ve dereceleride gösterilir.
    gorev_ayligi = fields.String("Görev Aylığı")
    kazanilmis_hak = fields.String("Kazanılmış Hak")
    emekli_muktesebat = fields.String("Emekli Müktesebat")

    # Burada da personelin terfiden sonraki kademe ve derece durumlarının sistem tarafından hesaplanmış hali vardır.
    yeni_gorev_ayligi_derece = fields.Integer("Yeni Görev Aylığı Derece")
    yeni_gorev_ayligi_kademe = fields.Integer("Yeni Görev Aylığı Kademe")


    yeni_kazanilmis_hak_derece = fields.Integer("Yeni Kazanılmış Hak Derece")
    yeni_kazanilmis_hak_kademe = fields.Integer("Yeni Kazanılmış Hak Kademe")
    yeni_kazanilmis_hak_gorunen = fields.Integer("Görünen Kazanılmış Hak Kademe")

    yeni_emekli_muktesebat_derece = fields.Integer("Yeni Emekli Müktesebat Derece")
    yeni_emekli_muktesebat_kademe = fields.Integer("Yeni Emekli Müktesebat Kademe")
    yeni_emekli_muktesebat_gorunen = fields.Integer("Görünen Emekli Müktesebat Kademe")

    devam = fields.Button("Devam Et", cmd="kaydet")


class TerfiOnayForm(JsonForm):
    """
        Personel Daire başkanlığı tarafından terfisi gerçekleştirilmiş bir personelin
        terfiden sonraki derece ve kademe durumlarının onay veya red için genel sekreterlik veya
        rektör tarafından görüntülendiği formdur.

    """
    key = fields.String("Key", hidden=True)
    tckn = fields.String("TCK No")
    ad_soyad = fields.String("Ad")
    kadro_derece = fields.String("Kadro Derece")

    # TerfiIslemForm class da olduğu gibi personelin terfiden önceki derece ve kademe durumunu ifade eder.
    gorev_ayligi = fields.String("Görev Aylığı")
    kazanilmis_hak = fields.String("Kazanılmış Hak")
    emekli_muktesebat = fields.String("Emekli Müktesebat")

    # Personelin terfiden sonraki kademe ve derece durumunu ifade eder.
    yeni_gorev_ayligi = fields.String("Yeni Görev Aylığı")
    yeni_kazanilmis_hak = fields.String("Yeni Kazanılmış Hak")
    yeni_emekli_muktesebat = fields.String("Yeni Emekli Müktesebat")

    onay_buton = fields.Button("Onayla", cmd="terfi_onay")
    red_buton = fields.Button("Red", cmd="terfi_red")


class TerfiIslemleri(CrudView):
    """
        Kanunla verilen terfiler gibi tek bir personel üzerinde gerçekleştirilecek olan terfi işlemlerinin
        gerçekleştirilmesi amacıyla CrudView claas dan extend edilerek oluşturulmuş bir class dır.

    """

    class Meta:
        model = "Personel"

    def terfi_form(self):
        """
        Bu metod seçilmiş olan personele dair bilgiler veritabanından çekilir. Sonra seçili personel
        üzerinde bir takım kontroller gerçekleştirilir.
        Bu kontroller:
        - Seçili personelin devam eden bir terfi süreci varmı ?
        - Seçili personelin terfisi durdurulmuşmu ?

        Seçili personel yukarıdaki kontrollerden geçtiği takdirde terfi işlemi gerçekleştirilir.

        """
        self.current.task_data["personel_id"] = self.current.input["id"]
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        self.current.task_data["tckn"] = personel.tckn
        self.current.task_data["ad_soyad"] = "%s %s" % (personel.ad, personel.soyad)
        if suren_terfi_var_mi(personel.key):
            self.current.output['msgbox'] = {
                'type': 'error', "title": 'HATA !',
                "msg": '%s %s isim soyisimli personelin devam eden bir terfi süreci bulunmaktadır' % (
                    personel.ad, personel.soyad)
            }
        else:
            if terfi_durum_kontrol(personel.key):
                # Terfi işlemi sırasında seçili personelin terfiden önceki derece
                # ve kademe durumu gösterilmek amacıyla saklanıyor.
                eski_gorev_ayligi_kademe = personel.gorev_ayligi_kademe
                eski_gorev_ayligi_derece = personel.gorev_ayligi_derece
                eski_kazanilmis_hak_kademe = personel.kazanilmis_hak_kademe
                eski_kazanilmis_hak_derece = personel.kazanilmis_hak_derece
                eski_emekli_muktesebat_kademe = personel.emekli_muktesebat_kademe
                eski_emekli_muktesebat_derece = personel.emekli_muktesebat_derece

                # Seçili personelin terfi tıkanma durumu kontrol edilip,
                # derece_ilerlet metoduna parametre olarak girilmek amacıyla saklanıyor.
                terfi_tikanma = terfi_tikanma_kontrol(personel.key)

                personel.gorev_ayligi_derece, personel.gorev_ayligi_kademe = derece_ilerlet(
                    personel.kadro_derece,
                    personel.gorev_ayligi_derece,
                    personel.gorev_ayligi_kademe,
                    terfi_tikanma
                )
                # Terfi tıkanma durumu sadece görev aylığına göre kontrol edildiği için kazanılmış hak
                # ve emekli müktesebat için false girilir.
                personel.kazanilmis_hak_derece, personel.kazanilmis_hak_kademe = derece_ilerlet(
                    personel.kadro_derece,
                    personel.kazanilmis_hak_derece,
                    personel.kazanilmis_hak_kademe,
                    False
                )
                personel.emekli_muktesebat_derece, personel.emekli_muktesebat_kademe = derece_ilerlet(
                    personel.kadro_derece,
                    personel.emekli_muktesebat_derece,
                    personel.emekli_muktesebat_kademe,
                    False
                )
                # Form nesnesi oluşturulur ve attribute lerin değerleri verilir.
                _form = TerfiIslemForm(current=self.current, title="Terfi İşlemleri")
                _form.key = personel.key
                _form.ad_soyad = "%s %s" % (personel.ad, personel.soyad)
                _form.tckn = personel.tckn
                _form.kadro_derece = personel.kadro_derece
                _form.gorev_ayligi = "%s/%s" % (eski_gorev_ayligi_derece, eski_gorev_ayligi_kademe),
                _form.kazanilmis_hak = "%s/%s" % (eski_kazanilmis_hak_derece, eski_kazanilmis_hak_kademe)
                _form.emekli_muktesebat = "%s/%s" % (eski_emekli_muktesebat_derece,
                                                     eski_emekli_muktesebat_kademe)
                _form.yeni_gorev_ayligi_derece = personel.gorev_ayligi_derece
                _form.yeni_gorev_ayligi_kademe = personel.gorev_ayligi_kademe
                _form.yeni_gorev_ayligi_gorunen = gorunen_kademe_hesapla(personel.gorev_ayligi_derece,
                                                                         personel.gorev_ayligi_kademe)
                _form.yeni_kazanilmis_hak_derece = personel.kazanilmis_hak_derece
                _form.yeni_kazanilmis_hak_kademe = personel.kazanilmis_hak_kademe
                _form.yeni_kazanilmis_hak_gorunen = gorunen_kademe_hesapla(personel.kazanilmis_hak_derece,
                                                                           personel.kazanilmis_hak_kademe)
                _form.yeni_emekli_muktesebat_derece = personel.emekli_muktesebat_derece
                _form.yeni_emekli_muktesebat_kademe = personel.emekli_muktesebat_kademe
                _form.yeni_emekli_muktesebat_gorunen = gorunen_kademe_hesapla(personel.emekli_muktesebat_derece,
                                                                              personel.emekli_muktesebat_kademe)
                self.current.task_data["islem_gerceklestiren_personel_id"] = self.current.user.key
                self.form_out(_form)
            else:
                # Terfisi duran personel için terfi işlemi yapılamayacağına yönelik uyarı mesajı
                self.current.output['msgbox'] = {
                    'type': 'error', "title": 'HATA !',
                    "msg": '%s %s isim soyisimli personelin terfisi durdurulmuştur' % (
                        personel.ad, personel.soyad)
                }

    def kaydet_onaya_gonder(self):
        """
            Burada seçili personelin terfi sonrası derece ve kademe durumları belirlendikten sonra
            Onay aşamasına geçilir. Düzenlenen Kıdem ve kademe durumları henüz onaylanmadığı için
            task data içerisinde tutulur. Wf nin sonraki aşamasındaki formda da değerler bu task data dan
            çekilir.

        """
        self.current.task_data["personel_id"] = self.current.input["form"]["key"]
        self.current.task_data["yeni_gorev_ayligi_derece"] = self.current.input["form"]["yeni_gorev_ayligi_derece"]
        self.current.task_data["yeni_gorev_ayligi_kademe"] = self.current.input["form"]["yeni_gorev_ayligi_kademe"]
        self.current.task_data["yeni_kazanilmis_hak_derece"] = self.current.input["form"]["yeni_kazanilmis_hak_derece"]
        self.current.task_data["yeni_kazanilmis_hak_kademe"] = self.current.input["form"]["yeni_kazanilmis_hak_kademe"]
        self.current.task_data["yeni_emekli_muktesebat_derece"] = self.current.input["form"][
            "yeni_emekli_muktesebat_derece"]
        self.current.task_data["yeni_emekli_muktesebat_kademe"] = self.current.input["form"][
            "yeni_emekli_muktesebat_kademe"]
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        user_permission = None

        # Seçili personel eğer akademik personel ise terfiyi onaylayacak kişi rektördür.
        # Seçili personel eğer idari personel ise terfiyi onaylayacak kişi genel sekreterdir.
        # Akademik personel için terfi onay permission = akademik_personel_terfi_onay
        # İdari personel için terfi onay permission = idari_personel_terfi_onay

        if personel.personel_turu == 1:
            user_permission = Permission.objects.get(name="akademik_personel_terfi_onay")
        elif personel.personel_turu == 2:
            user_permission = Permission.objects.get(name="idari_personel_terfi_onay")
        user_list = user_permission.get_permitted_users()
        self.current.invite_other_parties(user_list)
        msg = {"title": 'İşlem Gerçekleştirildi!',
               "body": 'Terfi işlemi, onay sürecine girmiştir.'}
        self.current.task_data["LANE_CHANGE_MSG"] = msg

    def terfi_kontrol(self):
        """
            Terfi işlemini onaylayacak olan personelin (rektör veya genel sekreter)
            seçili personelin (Terfisi yapılacak personel) terfi sonrası ve öncesi derece ve kademe durumlarını
            görüntülediği terfi işlemini onayladığı veya reddettiği formu görüntüleyen bir metoddur.

        """
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        _form = TerfiOnayForm(current=self.current, title="Terfi Kontrol")
        _form.tckn = personel.tckn
        _form.ad_soyad = "%s/%s" % (personel.ad, personel.soyad)
        _form.kadro_derece = personel.kadro_derece
        _form.gorev_ayligi = "%s/%s" % (personel.gorev_ayligi_derece, personel.gorev_ayligi_kademe)
        _form.kazanilmis_hak = "%s/%s" % (personel.kazanilmis_hak_derece, personel.kazanilmis_hak_kademe)
        _form.emekli_muktesebat = "%s/%s" % (personel.emekli_muktesebat_derece, personel.emekli_muktesebat_kademe)
        _form.yeni_gorev_ayligi = "%s/%s" % (
            self.current.task_data["yeni_gorev_ayligi_derece"],
            self.current.task_data["yeni_gorev_ayligi_kademe"]
        )
        _form.yeni_kazanilmis_hak = "%s/%s" % (
            self.current.task_data["yeni_kazanilmis_hak_derece"],
            self.current.task_data["yeni_kazanilmis_hak_kademe"]
        )
        _form.yeni_emekli_muktesebat = "%s/%s" % (
            self.current.task_data["yeni_emekli_muktesebat_derece"],
            self.current.task_data["yeni_emekli_muktesebat_kademe"]
        )

        self.form_out(_form)

    def terfi_onay(self):
        """
            Terfi sonrası derece ve kademe durumu veritabanına onaylanma durumunda kaydedilmektedir.
        """
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        personel.gorev_ayligi_derece = self.current.task_data["yeni_gorev_ayligi_derece"]
        personel.gorev_ayligi_kademe = self.current.task_data["yeni_gorev_ayligi_kademe"]
        personel.kazanilmis_hak_derece = self.current.task_data["yeni_kazanilmis_hak_derece"]
        personel.kazanilmis_hak_kademe = self.current.task_data["yeni_kazanilmis_hak_kademe"]
        personel.emekli_muktesebat_derece = self.current.task_data["yeni_emekli_muktesebat_derece"]
        personel.emekli_muktesebat_kademe = self.current.task_data["yeni_emekli_muktesebat_kademe"]
        personel.save()
        msg = {
            "title": "TERFİ İŞLEMİ SONUÇ BİLGİSİ",
            "body": "%s T.C. No %s isim soyisimli personelin terfisi gerçekleştirilmiştir" % (
                self.current.task_data["tckn"],
                self.current.task_data["ad_soyad"]
            )
        }
        self.current.task_data["LANE_CHANGE_MSG"] = msg

    def red_aciklama_yaz(self):
        """
            Terfi işleminin reddedilmesi durumunda açıklama girilmesi amacıyla çalışacak olan metoddur.
            Burada yeni bir JsonForm nesnesi türetilerek attributeleri belirlenmektedir.
            Son olarakda form ekrana basılmaktadır.
        """
        _form = JsonForm(title="Terfi İşleminiz Reddedildi.")
        _form.Meta.help_text = """Terfi işlemini onaylamadınız. İlgili personele bir açıklama
                                  yazmak ister misiniz?"""
        _form.red_aciklama = fields.String("Açıklama")
        _form.devam = fields.Button("Devam Et")
        self.form_out(_form)

    def red_aciklama_kaydet(self):
        """
            Burada terfi red açıklaması task data içerisine atılıp, lane değişim mesajı oluşturulmaktadır.
            Ayrıca ilgili lane kullanıcısına notification gönderilmektedir.
        """
        self.current.task_data["red_aciklama"] = self.current.input["form"]["red_aciklama"]
        msg = {
            "title": "TERFİ İŞLEMİ SONUÇ BİLGİSİ",
            "body": "Terfi işlemi reddedildi"
        }
        self.current.task_data["LANE_CHANGE_MSG"] = msg

    def red_aciklama_goster(self):
        """
         Work Flow da lane değişimi sırasında terfi işlemini yapan personele giden notificationa tıklanarak
         çalıştırılan metoddur.
         Burada amaçlanan, terfi işlemi reddedildiği takdirde terfi red mesajını, terfi işlemini yapan personele
         göstermektir.
        """
        self.current.output['msgbox'] = {
            'type': 'error', "title": 'Terfi İŞLEMİ SONUÇ BİLGİSİ !',
            "msg": '%s T.C. No ve %s isim soyisimli personelin terfi işlemi reddedilmiştir. %s' % (
                self.current.task_data["tckn"], self.current.task_data["ad_soyad"],
                self.current.task_data["red_aciklama"])
        }

    def taraflari_bilgilendir(self):
        """
            Terfi işlemini gerçekleştiren personele terfi onay mesajını gösteren metoddur.
        """
        self.current.output["msgbox"] = {
            "type": "info",
            "title": "TERFİ İŞLEMİ SONUÇ BİLGİSİ",
            "msg": "%s T.C. No %s isim soyisimli personelin terfisi gerçekleştirilmiştir" % (
                self.current.task_data["tckn"],
                self.current.task_data["ad_soyad"]
            )
        }

    def onay_belgesi_uret(self):
        """
            Terfi Onay belgesi üreten metod.
        """
        # TODO : Belge üretme işlemi daha sonra tamamlanacak.
        _form = JsonForm(title="Onay Belgesi")
        _form.Meta.help_text = "Onay Belgesi Üretmek İster misiniz ?"
        _form.evet = fields.Button("Evet")
        _form.hayir = fields.Button("Hayır")
        self.form_out(_form)



