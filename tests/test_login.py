# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from time import sleep

from tests.test_utils import BaseTestCase

RESPONSES = {}

class TestCase(BaseTestCase):

    def test_employee_edit(self):
        self.prepare_client('crud')


        resp = self.client.post(model='Employee', clear_wf=True)
        assert 'objects' in resp.json
        list_objects = resp.json['objects']
        if list_objects:
            assert list_objects[0]['data']['first_name'] == 'Em1'
        resp = self.client.post(model='Employee',cmd='add', clear_wf=True)
        resp = self.client.post(model='Employee',cmd='add', subcmd="do",
                                form=dict(first_name="Em1", pno="12323121443"))
        resp.raw()




