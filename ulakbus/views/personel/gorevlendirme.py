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
from ulakbus.models import AbstractRole, Unit, Personel, HizmetKayitlari
from ulakbus.models import KurumDisiGorevlendirmeBilgileri, KurumIciGorevlendirmeBilgileri
import datetime

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
        #self.set_form_data_to_object()
        #baslangic = datetime.date.strptime("%d.%m.%Y")
        gorevlendirme = KurumIciGorevlendirmeBilgileri()
        gorevlendirme.gorev_tipi = self.current.task_data["gorevlendirme_tur"]
        gorevlendirme.kurum_ici_gorev_baslama_tarihi = self.current.input["form"]["kurum_ici_gorev_baslama_tarihi"]
        gorevlendirme.kurum_ici_gorev_bitis_tarihi = self.current.input["form"]["kurum_ici_gorev_bitis_tarihi"]
        gorevlendirme.birim = Unit.objects.get(self.current.input["form"]["birim_id"])
        if self.current.input["form"]["soyut_rol_id"] != None:
            gorevlendirme.soyut_rol = AbstractRole.objects.get(self.current.input["form"]["soyut_rol_id"])
        gorevlendirme.aciklama = self.current.input["form"]["aciklama"]
        gorevlendirme.resmi_yazi_sayi = self.current.input["form"]["resmi_yazi_sayi"]
        gorevlendirme.resmi_yazi_tarih = self.current.input["form"]["resmi_yazi_tarih"]
        gorevlendirme.personel = Personel.objects.get(self.current.task_data["personel_id"])
        gorevlendirme.blocking_save()
        #personel = Personel.objects.get(self.current.task_data["personel_id"])
        #self.object.personel = personel
        #self.object.save()

        if (
                (self.current.input["form"]["soyut_rol_id"] == "EsDTPb8K5e7HlocpZPlVvX2VDAI") or
                (self.current.input["form"]["soyut_rol_id"] == "H6h6y7gIdX1JprWlljJniCgXtjU")
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
        gorevlendirme = KurumDisiGorevlendirmeBilgileri()
        gorevlendirme.kurum_disi_gorev_baslama_tarihi = self.current.input["form"]["kurum_disi_gorev_baslama_tarihi"]
        gorevlendirme.kurum_disi_gorev_bitis_tarihi = self.current.input["form"]["kurum_disi_gorev_bitis_tarihi"]
        gorevlendirme.aciklama = self.current.input["form"]["aciklama"]
        gorevlendirme.resmi_yazi_sayi = self.current.input["form"]["resmi_yazi_sayi"]
        gorevlendirme.resmi_yazi_tarih = self.current.input["form"]["resmi_yazi_tarih"]
        gorevlendirme.maas = self.current.input["form"]["maas"]
        gorevlendirme.yevmiye = self.current.input["form"]["yevmiye"]
        gorevlendirme.yolluk = self.current.input["form"]["yolluk"]
        gorevlendirme.ulke = self.current.input["form"]["ulke"]
        gorevlendirme.soyut_rol = AbstractRole.objects.get(self.current.input["form"]["soyut_rol_id"])
        gorevlendirme.personel = Personel.objects.get(self.current.task_data["personel_id"])
        gorevlendirme.blocking_save()
        #self.set_form_data_to_object()
        #personel = Personel.objects.get(self.current.task_data["personel_id"])
        #self.object.personel = personel
        #self.object.save()

        if (
                    (self.current.input["form"]["soyut_rol_id"] == "EsDTPb8K5e7HlocpZPlVvX2VDAI") or
                    (self.current.input["form"]["soyut_rol_id"] == "H6h6y7gIdX1JprWlljJniCgXtjU")
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
    kaydet_buton = fields.Button("Kaydet")

class HizmetCetveli(CrudView):
    class Meta:
        model = "HizmetKayitlari"

    def giris_form(self):
        self.form_out(HizmetCetveliForm(self.object, current = self.current))

    def kaydet(self):
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        hizmet_kayitlari = HizmetKayitlari()
        hizmet_kayitlari.personel = personel
        hizmet_kayitlari.tckn = personel.tckn
        hizmet_kayitlari.baslama_tarihi = self.current.input["form"]["baslama_tarihi"]
        hizmet_kayitlari.bitis_tarihi = self.current.input["form"]["bitis_tarihi"]
        hizmet_kayitlari.gorev = self.current.input["form"]["gorev"]
        hizmet_kayitlari.unvan_kod = self.current.input["form"]["unvan_kod"]
        hizmet_kayitlari.yevmiye = self.current.input["form"]["yevmiye"]
        hizmet_kayitlari.ucret = self.current.input["form"]["ucret"]
        hizmet_kayitlari.hizmet_sinifi = self.current.input["form"]["hizmet_sinifi"]
        hizmet_kayitlari.kadro_derece = self.current.input["form"]["kadro_derece"]
        hizmet_kayitlari.odeme_derece = self.current.input["form"]["odeme_derece"]
        hizmet_kayitlari.odeme_kademe = self.current.input["form"]["odeme_kademe"]
        hizmet_kayitlari.odeme_ekgosterge = self.current.input["form"]["odeme_ekgosterge"]
        hizmet_kayitlari.kazanilmis_hak_ayligi_derece = self.current.input["form"]["kazanilmis_hak_ayligi_derece"]
        hizmet_kayitlari.kazanilmis_hak_ayligi_kademe = self.current.input["form"]["kazanilmis_hak_ayligi_kademe"]
        hizmet_kayitlari.kazanilmis_hak_ayligi_ekgosterge = self.current.input["form"]["kazanilmis_hak_ayligi_ekgosterge"]
        hizmet_kayitlari.emekli_derece = self.current.input["form"]["emekli_derece"]
        hizmet_kayitlari.emekli_kademe = self.current.input["form"]["emekli_kademe"]
        hizmet_kayitlari.emekli_ekgosterge = self.current.input["form"]["emekli_ekgosterge"]
        if "sebep_kod" in self.current.input["form"]:
            hizmet_kayitlari.sebep_kod = self.current.input["form"]["sebep_kod"]
        hizmet_kayitlari.kurum_onay_tarihi = self.current.input["form"]["kurum_onay_tarihi"]
        hizmet_kayitlari.blocking_save()
