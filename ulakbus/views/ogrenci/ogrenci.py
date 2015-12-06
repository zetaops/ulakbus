# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import random
from pyoko import form,exceptions
from zengine.lib.forms import JsonForm
from zengine.views.crud import CrudView
from ulakbus.models.ogrenci import Ogrenci

class TcKnForm(JsonForm):
    class Meta:
        include = ['tckn']

    sorgula = form.Button("Sorgula", "ogrenci_sorgula")

class KimlikBilgileri(CrudView):
    class Meta:
        model = "Ogrenci"

    def tckn_gir(self):
        self.form_out(TcKnForm(self.object, current = self.current))

    def tckn_al(self):
        self.set_form_data_to_object()
        self.current.task_data["tckn"] = self.object.tckn

    def ogrenci_sorgula(self):
        #try:
        self.set_form_data_to_object()
        self.current.task_data["ogrenci"] = Ogrenci.objects.filter(tckn = self.current.task_data["tckn"])
        self.current.task_data["resutl"] = True
        #except exceptions.ObjectDoesNotExist:
        if len(self.current.task_data["ogrenci"]) == 0:
            self.current.task_data["result"] = False

    def kimlik_bilgileri_getir(self):
        ogrenci = self.current.task_data["ogrenci"]
        self.current.output["ogrenci_bilgiler"].append({
            "tckn" : ogrenci.tckn,
            "ogrenci_no" : ogrenci.ogrenci_no,
            "ad" : ogrenci.ad,
            "soyad" : ogrenci.soyad,
            "ikamet_adresi" : ogrenci.ikamet_adresi,
            "dogum_tarihi" : ogrenci.dogum_tarihi,
            "dogum_yeri" : ogrenci.dogum_yeri,
            "uyruk" : ogrenci.uyruk,
            "medeni_hali" : ogrenci.medeni_hali,
            "ehliyet" : ogrenci.ehliyet,
            "giris_tarihi" : ogrenci.giris_tarihi,
            "mezuniyet_tarihi" : ogrenci.mezuniyet_tarihi,
            "bolum" : ogrenci.bolum,
            "fakulte" : ogrenci.fakulte,
            "e_posta" : ogrenci.e_posta,
            "tel_no" : ogrenci.tel_no,
            "akademik_yil" : ogrenci.akademik_yil,
            "aktif_donem" : ogrenci.aktif_donem,
            "kan_grubu" : ogrenci.kan_grubu,
            "basari_durumu" : ogrenci.basari_durumu,
            "danisman" : "%s %s"%(ogrenci.danisman.ad,ogrenci.danisman.soyad)
        })

    def hata_mesaji_ver(self):
        self.current.output["msg"] = "Kayıt Bulunamadı"