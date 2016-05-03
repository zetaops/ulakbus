# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Mithat Raşit Özçıkrıkcı'

from zengine.lib.test_utils import BaseTestCase

class TestCase(BaseTestCase):

	def test_terfisi_duran_personel(self):
		""" 
			Terfisi duran personelin listelendiği bir rapordur.
		"""
		user = User.objects.get(username="test_user")
		self.prepare_client("generic_reporter", user=user)
		res = self.client.post(report="terfisi_duran_personel")
		assert len(res)>0