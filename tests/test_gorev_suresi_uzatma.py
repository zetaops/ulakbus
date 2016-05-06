# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Mithat Raşit Özçıkrıkcı'

from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import User, Personel

class TestCase(BaseTestCase):
	def test_gorev_suresi_uzatma(self):
		"""
		 	Test data'daki mithat kullanıcısı ile test işlemi gerçekleştirilir.
		 	Seçilen personelin görev süresinin açılan formda görev süresi bitiş
		 	tarihi girilerek görev süresini uzatma mantığına dayanır.
		"""

		user = User.objects.get(username="mithat")
		personel = Personel.objects.get(personel_id)
		personel_id = "9W67I6JzfD729QLoeuq7chGSc0"
		self.prepare_client("/gorev_suresi_uzatma", user=user)
		self.client.post(
			id = personel_id, 
			model = "Atama", 
			param = "personel_id",
			wf = "gorev_suresi_uzatma"
			)
