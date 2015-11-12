# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from pyoko.model import model_registry
from .base_test_case import BaseTestCase


class TestCase(BaseTestCase):
    def test_list_add_delete_with_employee_model(self):
        # setup workflow
        self.prepare_client('/crud')

        # calling the crud view without any model should list available models
        # resp = self.client.post()
        # assert resp.json['models'] == [[m.Meta.verbose_name_plural, m.__name__] for m in
        #                                model_registry.get_base_models()]

        # calling with just model name (without any cmd) equals to cmd="list"
        resp = self.client.post(model='Personel')
        assert 'nobjects' in resp.json

        # list_objects = resp.json['nobjects']
        # if list_objects and len(list_objects) > 1:
        #     assert list_objects[1][1] == 'Em1'

        # count number of records
        num_of_objects = len(resp.json['nobjects']) - 1

        # add a new employee record, then go to list view (do_list subcmd)
        self.client.post(model='Personel', cmd='add')
        resp = self.client.post(model='Personel',
                                cmd='add',
                                subcmd="do_list",
                                form=dict(ad="Em1", tckn="12323121443"))
        # we should have 1 more object relative to previous listing
        assert num_of_objects + 1 == len(resp.json['nobjects']) - 1

        # delete the first object then go to list view
        resp = self.client.post(model='Personel',
                                cmd='delete',
                                subcmd="do_list",
                                object_id=resp.json['nobjects'][1][0])

        # number of objects should be equal to starting point
        assert num_of_objects == len(resp.json['nobjects']) - 1

    def test_add_search_filter(self):
        # setup workflow
        self.prepare_client('/crud')
        resp = self.client.post(model='Personel')
        resp = self.client.post(model='Personel', query="1234567")
        if len(resp.json['nobjects']) < 2:
            self.client.post(model='Personel', cmd='add')
            for i in range(9):
                resp = self.client.post(model='Personel',
                                        cmd='add',
                                        subcmd="do_add",
                                        form=dict(ad="Per%s" % i, tckn="123456789%s" % i))
            time.sleep(3)
        resp = self.client.post(model='Personel')
        resp = self.client.post(model='Personel', query="12345678")
        assert len(resp.json['nobjects']) > 8
