# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import random
from pyoko import form
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
		 	pass
		# to do

	def isim_kontrol():
		pass
		#to do

class ProgramBilgisiForm(JsonForm):
	class Meta:
		include = ['program']

class DersBilgileriForm(JsonForm):
	class Meta:
		include = ['ad', 'kod', 'tanim', 'aciklama', 'onkosul', 'uygulama_saati', 'teori_saati', 'ects_kredisi',
		'yerel_kredisi', 'zorunlu', 'ders_dili', 'ders_turu', 'ders_amaci', 'ogrenme_ciktilari', 'ders_icerigi',
		'ders_kategorisi', 'ders_kaynaklari', 'ders_mufredati', 'verilis_bicimi', 'donem', 'ders_koordinatoru']
	kaydet = form.Button("Kaydet", cmd="kaydet")
	kaydet_yeni_kayit = form.Button("Kaydet/Yeni Kayıt Ekle", cmd="kaydet_yeni_kayit")

class DersEkle(CrudView):
	class Meta:
		model = "Ders"

	def ders_bilgileri(self):
		self.form_out(DersBilgileriForm(self.object, current = self.current))

	def program_bilgisi(self):
		self.form_out(ProgramBilgisiForm(self.object, current = self.current))