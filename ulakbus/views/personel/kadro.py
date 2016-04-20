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

from zengine.views.crud import CrudView, obj_filter, form_modifier
from collections import OrderedDict

from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.models import Personel
from pyoko import ListNode
import datetime


class KadroObjectForm(JsonForm):
    """KadoIslemleri için object form olarak kullanılacaktır.

    Meta değiştirilerek, formlardan durum alanı çıkarılmış, ve form
    alanları iki gruba ayrılmıştır.

    Formda bulunan iki alan unvan ve unvan_kod karşıt alanlardır. İkisi
    aynı kayıtta bulunamazlar. Bu sebeple Meta'ya constraints
    eklenmiştir. Bu sayede UI tarafında forma kontroller eklenecek, biri
    seçildiğinde diğerinin değeri boşaltılacaktır. Benzer şekilde, arka
    uçta aynı kontrol bu ifadeler kullanılarak yapılacaktr.

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
                        "items": ['unvan', 'derece', 'unvan_kod'],
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
        constraints = [
            {
                'cons': [{'id': 'unvan_kod', 'cond': 'exists'}],
                'do': 'change_fields', 'fields': [{'unvan': None}]
            },
            {
                'cons': [{'id': 'unvan', 'cond': 'exists'}],
                'do': 'change_fields', 'fields': [{'unvan_kod': None}]
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
        unvan_kod = self.object.get_unvan_kod_display()

        self.current.task_data['object_id'] = self.object.key

        _form = self.SilOnayForm(title=" ")
        _form.help_text = """Akademik unvanı: **%s**
        Kadro numarası: **%s**
        Unvan Kodu: **%s**
        Açıklaması: **%s**

        bilgilerine sahip kadroyu silmek istiyor musunuz ?""" % (
            unvan, kadro_no, unvan_kod, aciklama)
        self.form_out(_form)

    def kadro_sil(self):
        """
        Saklı kontolü yaparak, silme işlemini gerçekleştirir.

        """
        # TODO: Sakli kadronun silinme denemesi loglanacak.
        assert self.object.durum == self.SAKLI, "attack detected, should be logged/banned"
        self.delete()

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
    class Personel(ListNode):
        key = fields.String("Key", hidden=True)
        sec = fields.Boolean("Seç", type="checkbox")
        tckn = fields.String("T.C. No")
        isim = fields.String("İsim")
        soyisim = fields.String("Soyisim")
        gorev_ayligi = fields.String("Görev Aylığı")
        kazanilmis_hak = fields.String("Kazanılmış Hak")
        emekli_muktesebat = fields.String("Emekli Müktesebat")
    terfi = fields.Button("Terfi Ettir", cmd="terfi_ettir")

class TerfiListe(CrudView):
    class Meta:
        model = "Personel"
        
    def terfisi_gelen_personel_liste(self):
        self.current.output['client_cmd'] = ['show', ]
        simdi = datetime.date.today()
        kontrol = simdi + datetime.timedelta(days = 90)
        personel_liste = Personel.objects.filter(
            sonraki_terfi_tarihi__lte = kontrol
            )
        form = TerfiForm(current = self.current, title = "Terfi İşlemi")
        for personel in personel_liste:
            form.Personel(
                key = personel.key,
                sec = False, 
                tckn = personel.tckn,
                isim = personel.ad,
                soyisim = personel.soyad,
                gorev_ayligi = "%i/%i"%(personel.guncel_gorev_ayligi_derece, personel.guncel_gorev_ayligi_kademe),
                kazanilmis_hak = "%i/%i"%(personel.guncel_kazanilmis_hak_derece, personel.guncel_kazanilmis_hak_kademe),
                emekli_muktesebat = "%i/%i"%(personel.guncel_emekli_muktesebat_derece, personel.guncel_emekli_muktesebat_kademe)
                )

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    @form_modifier
    def terfi_form_inline_edit(self, serialized_form):
        if 'Personel' in serialized_form["schema"]["properties"]:
            serialized_form["inline_edit"] = ["sec"] 

    def terfi_ettir(self):
        personel_liste = self.current.input["form"]["Personel"]
        for personel_data in personel_liste:
            personel = Personel.objects.get(personel_data["key"])
            g_ayligi = personel.guncel_gorev_ayligi_derece
            k_hak = personel.guncel_kazanilmis_hak_derece
            e_muktesebat = personel.guncel_emekli_muktesebat_derece
            if personel.kadro.derece != personel.guncel_gorev_ayligi_derece:
                personel.sonraki_terfi_tarihi += simdi + datetime.timedelta(years = 1)
                personel.guncel_gorev_ayligi_kademe += 1
                if (g_ayligi == k_hak) & (g_ayligi == e_muktesebat):
                    personel.guncel_kazanilmis_hak_kademe += 1
                    personel.guncel_emekli_muktesebat_kademe +=1
                if personel.guncel_gorev_ayligi_kademe == 4:
                    personel.guncel_gorev_ayligi_derece -= 1
                if personel.guncel_kazanilmis_hak_kademe == 4:
                    personel.guncel_kazanilmis_hak_derece -= 1
                if personel.guncel_emekli_muktesebat_kademe == 4:
                    personel.guncel_emekli_muktesebat_derece -= 1

            personel.save()