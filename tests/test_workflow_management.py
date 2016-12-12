# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def test_workflow_management(self):

        types_workflow = [{'wf_key': 'BSxRLRUij5pXZxSpB3qD9GVUA0J',    # Type A
                           'fields': {'abstract_role_id': 'OGRETIM_ELEMANI',
                                      'start_date': '09.12.2016',
                                      'finish_date': '20.12.2016',
                                      'unit_id': 'BpmGHdZo8sQC85cL6wffYr4CEKh',
                                      'object_query_code': 'okutman=r.user.personel.okutman',
                                      'object_type': 'Şube',
                                      'recursive_units': ''}},
                          {'wf_key': 'SZTD5VxYP0Ivk0iMuAu3L1bv4yU',    # Type B
                           'fields': {'abstract_role_id': 'DAIRE_PERSONELI',
                                      'start_date': '09.12.2016',
                                      'finish_date': '20.12.2016',
                                      'get_roles_from': '',
                                      'unit_id': '7QrxVwobdBkrnKHbUpWcHhxnEX3',
                                      'object_query_code': 'personel_turu=2',
                                      'object_type': 'Personel',
                                      'recursive_units': ''}},
                          {'wf_key': 'GrWaaHsBhD2uBd8ZOji7p25tomo',    # Type C
                           'fields': {'abstract_role_id': 'H2teltns7WCwTeslCq49Ip7cGrE',
                                      'start_date': '09.12.2016',
                                      'finish_date': '20.12.2016',
                                      'get_roles_from': ''}},
                          {'wf_key': 'VeGkMNyiozU5ULq6tKSn9WBCDsi',    # Type D
                           'fields': {'abstract_role_id': 'DERS_PROGRAMI_KOORDINATORU',
                                      'start_date': '09.12.2016',
                                      'finish_date': '20.12.2016',
                                      'get_roles_from': '',
                                      'unit_id': 'T71IQ6c7YIeEYOoIJKlHE9GrF72',
                                      'recursive_units': ''}}]

        for i in range(4):
            self.prepare_client('/is_akisi_atama', username='sistem_yoneticisi_1')

            key = types_workflow[i]["wf_key"]

            self.client.post(form={"workflow": key,
                                   "gonder": 1})

            resp = self.client.post()

            fields = types_workflow[i]['fields']

            type_keys = fields.keys()
            resp_keys = resp.json['forms']['model'].keys()

            for k in type_keys:
                assert k in resp_keys

            fields['gonder'] = 1

            resp = self.client.post(form=fields)

            assert resp.json['msgbox']['title'] == 'İşlem Başarılı'
