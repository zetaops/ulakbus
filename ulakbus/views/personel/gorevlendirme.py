# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

"""
    Görevlendirme

    İki tür görevlendirme vardır.
    - Kurum içi görevlendirme
    - Kurum dışı görevlendirme

    Bu iş akışı CrudView nesnesi extend edilerek işletilmektedir.
"""

from pyoko.exceptions import ObjectDoesNotExist
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView, obj_filter
from pyoko import ListNode
from ulakbus.models import AbstractRole, Unit, Personel
from ulakbus.models import KurumDisiGorevlendirmeBilgileri, KurumIciGorevlendirmeBilgileri

class GorevlendirmeTurSecForm(JsonForm):
    gorevlendirme_tur = fields.Integer("Görevlendirme Tür", choices="gorev_tipi")
    kaydet_buton = fields.Button("Kaydet ve Devam Et", cmd="gorevlendirme_tur_kaydet")

class Gorevlendirme(CrudView):
    class Meta:
        model = "Personel"

    def gorevlendirme_tur_sec(self):
        """
            Görevlendirme tipinin seçildiği formu return eden bir metoddur.
        """

        # Seçili personel id si saklanıyor
        self.current.task_data["personel_id"] = self.current.input["id"]
        self.form_out(GorevlendirmeTurSecForm(current=self.current))

    def gorevlendirme_tur_kaydet(self):
        # Görevlendirme türü wf nin ilerleyen adımları için task data da saklandı
        self.current.task_data["gorevlendirme_tur"] = self.current.input["form"]["gorevlendirme_tur"]

class KurumIciGorevlendirmeForm(JsonForm):
    class Meta:
        include = ["kurum_ici_gorev_baslama_tarihi", "kurum_ici_gorev_bitis_tarihi", "birim", "soyut_rol",
                   "aciklama", "resmi_yazi_sayi", "resmi_yazi_tarih"]
        title = "KURUM İÇİ GÖREVLENDİRME FORM"

    kaydet_buton = fields.Button("Kaydet ve Devam Et", cmd="kaydet")

class KurumIciGorevlendirme(CrudView):
    class Meta:
        model = "KurumIciGorevlendirmeBilgileri"

    def gorevlendirme_form(self):
        self.form_out(KurumIciGorevlendirmeForm(self.object, current=self.current))

    def kaydet(self):
        self.set_form_data_to_object()
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        self.object.personel = personel
        self.object.save()

        if (
                    (self.current.input["form"]["soyut_rol_id"] == "JdT303huG7WYAF4FhKiEMOG3OuQ") or
                    (self.current.input["form"]["soyut_rol_id"] == "5xanqtlXnY9dsQhWNV8gMK1rXcm")
           ):
            self.current.task_data["hizmet_cetvel_giris"] = True
        else:
            self.current.task_data["hizmet_cetvel_giris"] = False

class KurumDisiGorevlendirmeForm(JsonForm):
    class Meta:
        include = ["kurum_disi_gorev_baslama_tarihi", "kurum_disi_gorev_bitis_tarihi", "aciklama",
                   "resmi_yazi_sayi", "resmi_yazi_tarih", "maas", "yevmiye", "yolluk", "ulke",
                   "soyut_rol"]
        title = "KURUM DIŞI GÖREVLENDİRME FORM"

    kaydet_buton = fields.Button("Kaydet ve Devam Et", cmd="kaydet")

class KurumDisiGorevlendirme(CrudView):
    class Meta:
        model = "KurumDisiGorevlendirmeBilgileri"

    def gorevlendirme_form(self):
        self.form_out(KurumDisiGorevlendirmeForm(self.object, current=self.current))

    def kaydet(self):
        self.set_form_data_to_object()
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        self.object.personel = personel
        self.object.save()

        if (
                    (self.current.input["form"]["soyut_rol_id"] == "JdT303huG7WYAF4FhKiEMOG3OuQ") or
                    (self.current.input["form"]["soyut_rol_id"] == "5xanqtlXnY9dsQhWNV8gMK1rXcm")
           ):
            self.current.task_data["hizmet_cetvel_giris"] = True
        else:
            self.current.task_data["hizmet_cetvel_giris"] = False

class HizmetCetveliForm(JsonForm):
    class Meta:
        include = ["kayit_no", "baslama_tarihi", "bitis_tarihi", "gorev", "unvan_kod", "yevmiye", "ucret", "hizmet_sinifi",
                    "kadro_derece", "odeme_derece", "odeme_kademe", "odeme_ekgosterge", "kazanilmis_hak_ayligi_derece",
                    "kazanilmis_hak_ayligi_kademe", "kazanilmis_hak_ayligi_ekgosterge", "emekli_derece", "emekli_kademe",
                    "emekli_ekgosterge", "sebep_kod", "kurum_onay_tarihi"]

class HizmetCetveli(CrudView):
    class Meta:
        model = "HizmetKayitlari"

    def giris_form(self):
        self.form_out(HizmetCetveliForm(self.object, current = self.current))

    def kaydet(self):
        self.set_form_data_to_object()
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        self.object.personel = personel
        self.object.tckn = personel.tckn
        self.object.save()
