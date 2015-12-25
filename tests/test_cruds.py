# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from .base_test_case import BaseTestCase


class TestCase(BaseTestCase):
    def test_list_add_delete_with_employee_model(self):
        # setup workflow
        def len_1(lst):
            return len(lst) - 1

        self.prepare_client('/crud')

        # calling the crud view without any model should list available models
        # resp = self.client.post()
        # assert resp.json['models'] == [[m.Meta.verbose_name_plural, m.__name__] for m in
        #                                model_registry.get_base_models()]

        # calling with just model name (without any cmd) equals to cmd="list"
        resp = self.client.post(model='Personel')
        assert 'objects' in resp.json

        # list_objects = resp.json['objects']
        # if list_objects and len(list_objects) > 1:
        #     assert list_objects[1][1] == 'Em1'

        # count number of records
        num_of_objects = len_1(resp.json['objects'])

        # add a new employee record, then go to list view (do_list subcmd)
        self.client.post(model='Personel', cmd='add_edit_form')
        resp = self.client.post(model='Personel',
                                cmd='save::list',
                                form=dict(ad="Em1", tckn="12323121443"))

        # we should have 1 more object relative to previous listing
        assert num_of_objects + 1 == len_1(resp.json['objects'])

        # delete the first object then go to list view
        resp = self.client.post(model='Personel',
                                cmd='delete',
                                object_id=resp.json['objects'][1]['key'])

        # number of objects should be equal to starting point
        assert 'reload' in resp.json['client_cmd']

    def test_add_search_filter(self):
        # setup workflow
        self.prepare_client('/crud')
        resp = self.client.post(model='Personel')
        resp = self.client.post(model='Personel', query="1234567")
        if len(resp.json['objects']) < 2:
            self.client.post(model='Personel', cmd='add_edit_form')
            for i in range(9):
                resp = self.client.post(model='Personel',
                                        cmd='save::add_edit_form',
                                        form=dict(ad="Per%s" % i, tckn="123456789%s" % i))
            time.sleep(3)
        resp = self.client.post(model='Personel')
        resp = self.client.post(model='Personel', query="12345678")
        assert len(resp.json['objects']) > 8
