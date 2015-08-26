# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from time import sleep

from tests.test_utils import BaseTestCase
from ulakbus.models import Employee

RESPONSES = {}

class TestCase(BaseTestCase):

    def test_employee_edit(self):
        Employee.objects._clear_bucket()
        sleep(2)
        self.prepare_client('crud')
        resp = self.client.post(model='Employee')
        assert 'objects' in resp.json
        list_objects = resp.json['objects']
        if list_objects:
            assert list_objects[0]['data']['first_name'] == 'Em1'

        # count
        num_of_objects = len(resp.json['objects'])

        # add then list
        self.client.post(model='Employee',cmd='add')
        resp = self.client.post(model='Employee',cmd='add', subcmd="do_list",
                                form=dict(first_name="Em1", pno="12323121443"))

        assert num_of_objects + 1 == len(resp.json['objects'])

        # delete then list
        resp = self.client.post(model='Employee', cmd='delete', subcmd="do_list",
                                object_id=resp.json['objects'][0]['key'])
        assert num_of_objects == len(resp.json['objects'])







