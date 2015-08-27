# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from time import sleep
from pyoko.model import model_registry
from tests.test_utils import BaseTestCase
RESPONSES = {}

class CRUDTestCase(BaseTestCase):
    def test_list_add_delete_with_employee_model(self):

        # setup workflow
        self.prepare_client('crud')

        # calling the crud view without any model should list available models
        resp = self.client.post()
        assert resp.json['models'] == [m.__name__ for m in
                                       model_registry.get_base_models()]

        # calling with just model name (without any cmd) equals to cmd="list"
        resp = self.client.post(model='Employee')
        assert 'objects' in resp.json
        list_objects = resp.json['objects']
        if list_objects:
            assert list_objects[0]['data']['first_name'] == 'Em1'

        # count number of records
        num_of_objects = len(resp.json['objects'])

        # add a new employee record, then go to list view (do_list subcmd)
        self.client.post(model='Employee',cmd='add')
        resp = self.client.post(model='Employee',
                                cmd='add',
                                subcmd="do_list",
                                form=dict(first_name="Em1", pno="12323121443"))

        # we should have 1 more object relative to previous listing
        assert num_of_objects + 1 == len(resp.json['objects'])

        # delete the first object then go to list view
        resp = self.client.post(model='Employee',
                                cmd='delete',
                                subcmd="do_list",
                                object_id=resp.json['objects'][0]['key'])

        # number of objects should be equal to starting point
        assert num_of_objects == len(resp.json['objects'])







