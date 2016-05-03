# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Mithat Raşit Özçıkrıkcı'

from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import User, Atama
import datetime

class TestCase(BaseTestCase):
	def gorev_suresi_dolan_personel(self):
		""" 
			Görev süresi dolan personel raporu sorgulanır.
		"""
		user = User.objects.get(username="mithat")
		self.prepare_client("general_reporter", user=user)
		res = self.client.post(model="GorevSuresiDolanPersonel")
		simdi = datetime.date.today()
		atamalar = Atama.objects.filter(gorev_suresi_bitis__lte=simdi)
		assert len(res.json["object"]["fields"]) == len(atamalar)