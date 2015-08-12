# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from time import sleep

from tests.test_utils import BaseTestCase
from ulakbus.models import User


RESPONSES = {}

class TestCase(BaseTestCase):

    def test_employee_edit(self):
        self.prepare_client('personel_duzenle_basitlestirilmis')
        resp = self.client.post(cmd='add_object', clear_wf=True)
        resp.raw()
