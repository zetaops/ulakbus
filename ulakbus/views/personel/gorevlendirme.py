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

from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from ulakbus.models import Personel, HizmetKayitlari
from ulakbus.models import KurumDisiGorevlendirmeBilgileri, KurumIciGorevlendirmeBilgileri
from zengine.lib.translation import gettext_lazy as __
from ulakbus.lib.role import AbsRole


class GorevlendirmeTurSecForm(JsonForm):
    gorevlendirme_tur = fields.Integer(__(u"Görevlendirme Tür"), choices="gorev_tipi")
    kaydet = fields.Button(__(u"Kaydet ve Devam Et"), cmd="gorevlendirme_tur_kaydet")


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
        self.current.task_data["gorevlendirme_tur"] = self.current.input["form"][
            "gorevlendirme_tur"]


class KurumIciGorevlendirmeForm(JsonForm):
    class Meta:
        include = ["kurum_ici_gorev_baslama_tarihi", "kurum_ici_gorev_bitis_tarihi",
                   "birim", "soyut_rol", "aciklama",
                   "resmi_yazi_sayi", "resmi_yazi_tarih"]

        title = __(u"Kurum İçi Görevlendirme")

    kaydet = fields.Button(__(u"Kaydet ve Devam Et"), cmd="kaydet")


class KurumIciGorevlendirme(CrudView):
    class Meta:
        model = "KurumIciGorevlendirmeBilgileri"

    def gorevlendirme_form(self):
        self.form_out(KurumIciGorevlendirmeForm(self.object, current=self.current))

    def kaydet(self):
        form_data = self.current.input["form"]
        gorevlendirme = KurumIciGorevlendirmeBilgileri(
            gorev_tipi=self.current.task_data["gorevlendirme_tur"],
            kurum_ici_gorev_baslama_tarihi=form_data["kurum_ici_gorev_baslama_tarihi"],
            kurum_ici_gorev_bitis_tarihi=form_data["kurum_ici_gorev_bitis_tarihi"],
            aciklama=form_data["aciklama"],
            resmi_yazi_sayi=form_data["resmi_yazi_sayi"],
            resmi_yazi_tarih=form_data["resmi_yazi_tarih"],
            birim_id=form_data["birim_id"],
            personel_id=self.current.task_data["personel_id"],
            soyut_rol_id=form_data["soyut_rol_id"]
        )

        gorevlendirme.blocking_save()

        self.current.task_data["hizmet_cetvel_giris"] = form_data["soyut_rol_id"] in [
            AbsRole.FAKULTE_DEKANI.name, AbsRole.REKTOR.name]


class KurumDisiGorevlendirmeForm(JsonForm):
    class Meta:
        include = ["kurum_disi_gorev_baslama_tarihi", "kurum_disi_gorev_bitis_tarihi", "aciklama",
                   "resmi_yazi_sayi", "resmi_yazi_tarih", "maas", "yevmiye", "yolluk", "ulke",
                   "soyut_rol"]
        title = __(u"Kurum Dışı Görevlendirme")

    kaydet = fields.Button(__(u"Kaydet ve Devam Et"), cmd="kaydet")


class KurumDisiGorevlendirme(CrudView):
    class Meta:
        model = "KurumDisiGorevlendirmeBilgileri"

    def gorevlendirme_form(self):
        self.form_out(KurumDisiGorevlendirmeForm(self.object, current=self.current))

    def kaydet(self):
        form_data = self.current.input["form"]
        gorevlendirme = KurumDisiGorevlendirmeBilgileri(
            kurum_disi_gorev_baslama_tarihi=form_data["kurum_disi_gorev_baslama_tarihi"],
            kurum_disi_gorev_bitis_tarihi=form_data["kurum_disi_gorev_bitis_tarihi"],
            aciklama=form_data["aciklama"],
            resmi_yazi_sayi=form_data["resmi_yazi_sayi"],
            resmi_yazi_tarih=form_data["resmi_yazi_tarih"],
            maas=form_data["maas"],
            yevmiye=form_data["yevmiye"],
            yolluk=form_data["yolluk"],
            ulke=form_data["ulke"],
            soyut_rol_id=form_data["soyut_rol_id"],
            personel_id=self.current.task_data["personel_id"]
        )
        gorevlendirme.blocking_save()

        self.current.task_data["hizmet_cetvel_giris"] = form_data["soyut_rol_id"] in [
            AbsRole.FAKULTE_DEKANI.name, AbsRole.REKTOR.name]


class HizmetCetveliForm(JsonForm):
    class Meta:
        include = ["kayit_no", "baslama_tarihi", "bitis_tarihi", "gorev", "unvan_kod", "yevmiye",
                   "ucret", "hizmet_sinifi",
                   "kadro_derece", "odeme_derece", "odeme_kademe", "odeme_ekgosterge",
                   "kazanilmis_hak_ayligi_derece",
                   "kazanilmis_hak_ayligi_kademe", "kazanilmis_hak_ayligi_ekgosterge",
                   "emekli_derece", "emekli_kademe",
                   "emekli_ekgosterge", "sebep_kod", "kurum_onay_tarihi"]

    kaydet_buton = fields.Button(__(u"Kaydet"))


class HizmetCetveli(CrudView):
    class Meta:
        model = "HizmetKayitlari"

    def giris_form(self):
        self.form_out(HizmetCetveliForm(self.object, current=self.current))

    def kaydet(self):
        form_data = self.current.input["form"]
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        hizmet_kayitlari = HizmetKayitlari(
            personel_id=personel.key,
            tckn=personel.tckn,
            baslama_tarihi=form_data["baslama_tarihi"],
            bitis_tarihi=form_data["bitis_tarihi"],
            gorev=form_data["gorev"],
            unvan_kod=form_data["unvan_kod"],
            yevmiye=form_data["yevmiye"],
            ucret=form_data["ucret"],
            hizmet_sinifi=form_data["hizmet_sinifi"],
            kadro_derece=form_data["kadro_derece"],
            odeme_derece=form_data["odeme_derece"],
            odeme_kademe=form_data["odeme_kademe"],
            odeme_ekgosterge=form_data["odeme_ekgosterge"],
            kazanilmis_hak_ayligi_derece=form_data["kazanilmis_hak_ayligi_derece"],
            kazanilmis_hak_ayligi_kademe=form_data["kazanilmis_hak_ayligi_kademe"],
            kazanilmis_hak_ayligi_ekgosterge=form_data["kazanilmis_hak_ayligi_ekgosterge"],
            emekli_derece=form_data["emekli_derece"],
            emekli_kademe=form_data["emekli_kademe"],
            emekli_ekgosterge=form_data["emekli_ekgosterge"],
            kurum_onay_tarihi=form_data["kurum_onay_tarihi"]
        )
        if "sebep_kod" in form_data:
            hizmet_kayitlari.sebep_kod = form_data["sebep_kod"]
        hizmet_kayitlari.blocking_save()
