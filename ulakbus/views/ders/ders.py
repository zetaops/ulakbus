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
from ulakbus.models.ogrenci import Program

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
	sec = form.Button("Seç", cmd="program_sec")

class DersBilgileriForm(JsonForm):
	class Meta:
		include = ['ad', 'kod', 'tanim', 'aciklama', 'onkosul', 'uygulama_saati', 'teori_saati', 'ects_kredisi',
		'yerel_kredisi', 'zorunlu', 'ders_dili', 'ders_turu', 'ders_amaci', 'ogrenme_ciktilari', 'ders_icerigi',
		'ders_kategorisi', 'ders_kaynaklari', 'ders_mufredati', 'verilis_bicimi', 'donem', 'ders_koordinatoru']
	kaydet = form.Button("Kaydet", cmd="save")
	kaydet_yeni_kayit = form.Button("Kaydet/Yeni Kayıt Ekle", cmd="kaydet_yeni_kayit")

class DersEkle(CrudView):
	class Meta:
		model = "Ders"

	def program_sec(self):
		self.current.task_data['program_id'] = self.object.program.key

	def kaydet_yeni_kayit(self):
		self.set_form_data_to_object()
		self.object.program = Program.objects.get(self.current.task_data['program_id'])
		self.save_object()

	def ders_bilgileri(self):
		self.form_out(DersBilgileriForm(self.object, current = self.current))

	def program_bilgisi(self):
		self.form_out(ProgramBilgisiForm(self.object, current = self.current))