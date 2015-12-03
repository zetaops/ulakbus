# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import random
from pyoko import form
from pyoko.model import field
from zengine.lib.forms import JsonForm
from zengine.views.base import SimpleView, BaseView
from zengine.views.crud import CrudView
from ulakbus.models import ogrenci

class Ders_View(CrudView):
	class Meta:
		model = "Ders"
		title = "Ders Ekle"
	def __init__(self, current):
		super(Ders_View, self).__init__(current)

	def kayit():
		# to do

	def isim_kontrol():
		#to do

class DersEkleForm(JsonForm):
	class Meta:
		title = "Yeni Ders Ekle"

    ad = field.String("Ad")
    kod = field.String("Kod")
    tanim = field.String("Tanım")
    aciklama = field.String("Açıklama")
    onkosul = field.String("Önkoşul")
    uygulama_saati = field.Integer("Uygulama Saati")
    teori_saati = field.Integer("Teori Saati")
    ects_kredisi = field.Integer("ECTS Kredisi")
    yerel_kredisi = field.Integer("Yerel Kredisi")
    zorunlu = field.Boolean("Zorunlu")
    ders_dili = field.String("Ders Dili")
    ders_turu = field.Integer("Ders Türü")
    ders_amaci = field.String("Ders Amacı")
    ogrenme_ciktilari = field.String("Öğrenme Çıktıları")
    ders_icerigi = field.String("Ders İçeriği")
    ders_kategorisi = field.Integer("Ders Kategorisi")
    ders_kaynaklari = field.String("Ders kaynakları")
    ders_mufredati = field.String("Ders Müfredatı")
    verilis_bicimi = field.Integer("Veriliş Biçimi")
    cmd = form.Button("Kaydet")

class DersEkle(SimpleView):
	def show_view(self):
		form = DersEkleForm()
		form.ad = self.current.input['ders_bilgileri']['ad']
		form.kod = self.current.input['ders_bilgileri']['kod']
		form.tanim = self.current.input['ders_bilgileri']['tanim']
		form.aciklama = self.current.input['ders_bilgileri']['aciklama']
		form.onkosul = self.current.input['ders_bilgileri']['onkosul']
		form.uygulama_saati = self.current.input['ders_bilgileri']['uygulama_saati']
		form.teori_saati = self.current.input['ders_bilgileri']['teori_saati']
		form.ects_kredisi = self.current.input['ders_bilgileri']['ects_kredisi']
		form.yerel_kredisi = self.current.input['ders_bilgileri']['yerel_kredisi']
		form.zorunlu = self.current.input['ders_bilgileri']['zorunlu']
		form.ders_dili = self.current.input['ders_bilgileri']['ders_dili']
		form.ders_turu = self.current.input['ders_bilgileri']['ders_turu']
		form.ders_amaci = self.current.input['ders_bilgileri']['ders_amaci']
		form.ogrenme_ciktilari = self.current.input['ders_bilgileri']['ogrenme_ciktilari']
		form.ders_icerigi = self.current.input['ders_bilgileri']['ders_icerigi']
		form.ders_kategorisi = self.current.input['ders_bilgileri']['ders_kategorisi']
		form.ders_kaynaklari = self.current.input['ders_bilgileri']['ders_kaynaklari']
		form.ders_mufredati = self.current.input['ders_bilgileri']['ders_mufredati']
		form.verilis_bicimi = self.current.input['ders_bilgileri']['verilis_bicimi']
		self.current.output['forms'] = form.serialize()