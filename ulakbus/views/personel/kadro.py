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

"""

from zengine.views.crud import CrudView, obj_filter, form_modifier
from collections import OrderedDict
from pyoko.model import field
from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.models import Personel
from pyoko import ListNode
from dateutil.relativedelta import relativedelta
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

    def kadro_sil(self):
        # sadece sakli kadrolar silinebilir
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

        """

        if obj.durum == self.SAKLI:
            result['actions'].extend([
                {'name': 'Sil', 'cmd': 'delete', 'show_as': 'button'},
                {'name': 'İzinli Yap', 'cmd': 'sakli_izinli_degistir', 'show_as': 'button'}])

    @obj_filter
    def izinli_kadro(self, obj, result):
        """İzinli Kadro Filtresi

        İzinli Kadro listesinde yer alan her bir öğeye Saklı Yap butonu
        ekler.

        Args:
            obj: Kadro instance

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
        yeni_gorev_ayligi = fields.String("Yeni Görev Aylığı")
        yeni_kazanilmis_hak = fields.String("Yeni Kazanılmış Hak")
        yeni_emekli_muktesebat = fields.String("Yeni Emekli Müktesebat")
    kaydet = fields.Button("Kaydet", cmd="kaydet")
    duzenle = fields.Button("Düzenle", cmd="duzenle")

class TerfiDuzenleForm(JsonForm):
    key = fields.String("Key", hidden=True)
    yeni_gorev_ayligi_derece = fields.String("Yeni Görev Aylığı Derece")
    yeni_gorev_ayligi_kademe = fields.String("Yeni Görev Aylığı Kademe")
    yeni_kazanilmis_hak_derece = fields.String("Yeni Kazanılmış Hak Derece")
    yeni_kazanilmis_hak_kademe = fields.String("Yeni Kazanılmış Hak Kademe")
    yeni_emekli_muktesebat_derece = fields.String("Yeni Emekli Müktesebat Derece")
    yeni_emekli_muktesebat_kademe = fields.String("Yeni Emekli Müktesebat Kademe")
    kaydet = fields.Button("Kaydet")

class TerfiListe(CrudView):
    class Meta:
        model = "Personel"

    def liste_olustur(self):
        simdi = datetime.date.today()
        kontrol = simdi + datetime.timedelta(days = 90)
        personel_liste = Personel.objects.filter(
            sonraki_terfi_tarihi__lte = kontrol
            )
        personeller = {}
        for personel in personel_liste:
            personeller[personel.key] = {}
            personeller[personel.key]["tckn"] = personel.tckn
            personeller[personel.key]["ad"] = personel.ad
            personeller[personel.key]["soyad"] = personel.soyad
            personeller[personel.key]["guncel_gorev_ayligi_derece"] = personel.guncel_gorev_ayligi_derece
            personeller[personel.key]["guncel_gorev_ayligi_kademe"] = personel.guncel_gorev_ayligi_kademe
            personeller[personel.key]["guncel_kazanilmis_hak_derece"] = personel.guncel_kazanilmis_hak_derece
            personeller[personel.key]["guncel_kazanilmis_hak_kademe"] = personel.guncel_kazanilmis_hak_kademe
            personeller[personel.key]["guncel_emekli_muktesebat_derece"] = personel.guncel_emekli_muktesebat_derece
            personeller[personel.key]["guncel_emekli_muktesebat_kademe"] = personel.guncel_emekli_muktesebat_kademe                        
            personeller[personel.key]["gorev_ayligi_derece"] = personel.guncel_gorev_ayligi_derece
            personeller[personel.key]["gorev_ayligi_kademe"] = personel.guncel_gorev_ayligi_kademe
            personeller[personel.key]["kazanilmis_hak_derece"] = personel.guncel_kazanilmis_hak_derece
            personeller[personel.key]["kazanilmis_hak_kademe"] = personel.guncel_kazanilmis_hak_kademe
            personeller[personel.key]["emekli_muktesebat_derece"] = personel.guncel_emekli_muktesebat_derece
            personeller[personel.key]["emekli_muktesebat_kademe"] = personel.guncel_emekli_muktesebat_kademe            
            if personeller[personel.key]["gorev_ayligi_derece"] == personeller[personel.key]["kazanilmis_hak_derece"]:
                if personeller[personel.key]["gorev_ayligi_derece"] == personeller[personel.key]["emekli_muktesebat_derece"]:                    
                    personeller[personel.key]["gorev_ayligi_kademe"] += 1
            personeller[personel.key]["kazanilmis_hak_kademe"] += 1
            personeller[personel.key]["emekli_muktesebat_kademe"] += 1            
            if personel.kadro.derece != personel.guncel_gorev_ayligi_derece:
                if personeller[personel.key]["gorev_ayligi_kademe"] == 4:
                    personeller[personel.key]["gorev_ayligi_derece"] -= 1
                    personeller[personel.key]["gorev_ayligi_kademe"] = 1
                if personeller[personel.key]["kazanilmis_hak_kademe"] == 4:
                    personeller[personel.key]["kazanilmis_hak_derece"] -= 1
                    personeller[personel.key]["kazanilmis_hak_kademe"] = 1
                if personeller[personel.key]["emekli_muktesebat_kademe"] == 4:
                    personeller[personel.key]["emekli_muktesebat_derece"] -=1
                    personeller[personel.key]["emekli_muktesebat_kademe"] = 1
        self.current.task_data["duzenlemeler"] = []
        self.current.task_data["personeller"] = personeller            

    def terfi_duzenle_form(self):
        veri = self.current.task_data["duzenlemeler"][0]
        del self.current.task_data["duzenlemeler"][0]
        yeni_gorev_ayligi_derece = veri["yeni_gorev_ayligi"].split("/")[0]
        yeni_gorev_ayligi_kademe = veri["yeni_gorev_ayligi"].split("/")[1]
        yeni_kazanilmis_hak_derece = veri["yeni_kazanilmis_hak"].split("/")[0]
        yeni_kazanilmis_hak_kademe = veri["yeni_kazanilmis_hak"].split("/")[1]
        yeni_emekli_muktesebat_derece = veri["yeni_emekli_muktesebat"].split("/")[0]
        yeni_emekli_muktesebat_kademe = veri["yeni_emekli_muktesebat"].split("/")[1]
        form = TerfiDuzenleForm(
            current = self.current,
            title = "Terfi Bilgileri Düzenle"
            )
        form.key = veri["key"],
        form.gorev_ayligi = veri["gorev_ayligi"],
        form.kazanilmis_hak = veri["kazanilmis_hak"],
        form.emekli_muktesebat = veri["emekli_muktesebat"],
        form.yeni_gorev_ayligi_derece = yeni_gorev_ayligi_derece,
        form.yeni_gorev_ayligi_kademe = yeni_gorev_ayligi_kademe,
        form.yeni_kazanilmis_hak_derece = yeni_kazanilmis_hak_derece,
        form.yeni_kazanilmis_hak_kademe = yeni_kazanilmis_hak_kademe,
        form.yeni_emekli_muktesebat_derece = yeni_emekli_muktesebat_derece,
        form.yeni_emekli_muktesebat_kademe = yeni_emekli_muktesebat_kademe
    
        self.form_out(form)

    def terfi_tablo_duzenle(self):
        form_veri = self.current.input["form"]
        veri = self.current.task_data["personeller"][form_veri["key"][0]]
        veri["gorev_ayligi_derece"] = int(form_veri["yeni_gorev_ayligi_derece"][0])
        veri["gorev_ayligi_kademe"] = int(form_veri["yeni_gorev_ayligi_kademe"][0])
        veri["kazanilmis_hak_derece"] = int(form_veri["yeni_kazanilmis_hak_derece"][0])
        veri["kazanilmis_hak_kademe"] = int(form_veri["yeni_kazanilmis_hak_kademe"][0])
        veri["emekli_muktesebat_derece"] = int(form_veri["yeni_emekli_muktesebat_derece"][0])
        veri["emekli_muktesebat_kademe"] = int(form_veri["yeni_emekli_muktesebat_kademe"][0])
        self.current.task_data["personeller"][form_veri["key"][0]] = veri
        if len(self.current.task_data["duzenlemeler"]) > 0:
            self.current.task_data["flow"] = "continue"
        else:
            self.current.task_data["flow"] = "end"

    def terfisi_gelen_personel_liste(self):
        self.current.output['client_cmd'] = ['show', ]
        form = TerfiForm(current = self.current, title = "Terfi İşlemi")
        for key, value in self.current.task_data["personeller"].iteritems():
            form.Personel(
                key = key,
                sec = False, 
                tckn = value["tckn"],
                isim = value["ad"],
                soyisim = value["soyad"],
                gorev_ayligi = "%i/%i"%(value["guncel_gorev_ayligi_derece"], value["guncel_gorev_ayligi_kademe"]),
                kazanilmis_hak = "%i/%i"%(value["guncel_kazanilmis_hak_derece"], value["guncel_kazanilmis_hak_kademe"]),
                emekli_muktesebat = "%i/%i"%(value["guncel_emekli_muktesebat_derece"], value["guncel_emekli_muktesebat_kademe"]),
                yeni_gorev_ayligi = "%i/%i"%(value["gorev_ayligi_derece"], value["gorev_ayligi_kademe"]),
                yeni_kazanilmis_hak = "%i/%i"%(value["kazanilmis_hak_derece"], value["kazanilmis_hak_kademe"]),
                yeni_emekli_muktesebat = "%i/%i"%(value["emekli_muktesebat_derece"], value["emekli_muktesebat_kademe"])
                )

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def terfi_duzenleme_yapilandir(self):
        for personel in self.current.input["form"]["Personel"]:
                if personel["sec"]:
                    self.current.task_data["duzenlemeler"].append({
                            "key" : personel["key"],
                            "gorev_ayligi" : personel["gorev_ayligi"],
                            "kazanilmis_hak" : personel["kazanilmis_hak"],
                            "emekli_muktesebat" : personel["emekli_muktesebat"],
                            "yeni_gorev_ayligi" : personel["yeni_gorev_ayligi"],
                            "yeni_kazanilmis_hak" : personel["yeni_kazanilmis_hak"],
                            "yeni_emekli_muktesebat" : personel["yeni_emekli_muktesebat"]
                        })                

    @form_modifier
    def terfi_form_inline_edit(self, serialized_form):
        if 'Personel' in serialized_form["schema"]["properties"]:
            serialized_form["inline_edit"] = ["sec"] 

    def kaydet(self):
        personel_liste = self.current.input["form"]["Personel"]
        simdi = datetime.date.today()
        sonraki_terfi_tarihi = simdi + relativedelta(years=1)
        for personel_data in personel_liste:
            if personel_data["sec"]:
                yeni_gorev_ayligi_derece = personel_data["yeni_gorev_ayligi"].split("/")[0]
                yeni_gorev_ayligi_kademe = personel_data["yeni_gorev_ayligi"].split("/")[1]
                yeni_kazanilmis_hak_derece = personel_data["yeni_kazanilmis_hak"].split("/")[0]
                yeni_kazanilmis_hak_kademe = personel_data["yeni_kazanilmis_hak"].split("/")[1]
                yeni_emekli_muktesebat_derece = personel_data["yeni_emekli_muktesebat"].split("/")[0]
                yeni_emekli_muktesebat_kademe = personel_data["yeni_emekli_muktesebat"].split("/")[1]
                personel = Personel.objects.get(personel_data["key"])
                personel.guncel_gorev_ayligi_derece = yeni_gorev_ayligi_derece
                personel.guncel_gorev_ayligi_kademe = yeni_gorev_ayligi_kademe
                personel.guncel_kazanilmis_hak_derece = yeni_kazanilmis_hak_derece
                personel.guncel_kazanilmis_hak_kademe = yeni_kazanilmis_hak_kademe
                personel.guncel_emekli_muktesebat_derece = yeni_emekli_muktesebat_derece
                personel.guncel_emekli_muktesebat_kademe = yeni_emekli_muktesebat_kademe
                personel.sonraki_terfi_tarihi = sonraki_terfi_tarihi
                personel.save()