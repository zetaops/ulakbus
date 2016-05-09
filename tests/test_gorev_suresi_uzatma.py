# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Mithat Raşit Özçıkrıkcı'

from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import User, Personel
from dateutil.relativedelta import relativedelta
import datetime

class TestCase(BaseTestCase):
	def test_gorev_suresi_uzatma(self):
		"""
		 	Test data'daki mithat kullanıcısı ile test işlemi gerçekleştirilir.
		 	Seçilen personelin görev süresinin açılan formda görev süresi bitiş
		 	tarihi girilerek görev süresini uzatma mantığına dayanır.
		"""

		user = User.objects.get(username="mithat")
		personel_id = "9W67I6JzfD729QLoeuq7chGSc0"
		personel = Personel.objects.get(personel_id)
		eski_gorev_suresi_bitis = personel.gorev_suresi_bitis
		yeni_gorev_suresi_bitis = eski_gorev_suresi_bitis + relativedelta(years=1)
		self.prepare_client("/gorev_suresi_uzatma", user=user)

		# Görev süresi uzatılacak personel seçilir.

		self.client.post(
			id = personel_id, 
			model = "Perosnel",
			param = "personel_id",
			wf = "gorev_suresi_uzatma"
			)

		# Görev süresi uzatma formu doldurulur.

		resp = self.client.post(
			cmd= "kaydet",
			wf = "gorev_suresi_uzatma",
			form = dict(gorev_suresi_bitis=yeni_gorev_suresi_bitis.strftime("%d.%m.%Y"), personel_id=personel.key)
		)

		# Perosnelin görev süresi bitiş tarihinin belirlediğimiz şekilde değişip değişmediği kontrol ediliyor.
		personel = Personel.objects.get(personel.key)
		assert  personel.gorev_suresi_bitis == yeni_gorev_suresi_bitis