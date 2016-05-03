# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Mithat Raşit Özçıkrıkcı'

from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import User

class TestCase(BaseTestCase):

	def test_terfisi_tikanan_personel(self):
		""" 
			Terfisi duran personelin listelendiği bir rapordur.
		"""
		user = User.objects.get(username="mithat")
		self.prepare_client("generic_reporter", user=user)
		res = self.client.post(model="TerfisiTikananPersonel")
		assert "object" in res.json
		assert len(res.json["object"]["fields"]) == 1