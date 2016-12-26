# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def test_workflow_management(self):

        types_workflow = [{'wf_name': 'okutman_not_girisi',    # Type A
                           'fields': {'abstract_role_id': 'OGRETIM_ELEMANI',
                                      'start_date': '09.12.2016',
                                      'finish_date': '20.12.2016',
                                      'unit_id': 'BpmGHdZo8sQC85cL6wffYr4CEKh',
                                      'object_query_code': 'okutman=r.user.personel.okutman',
                                      'object_type': 'Sube',
                                      'recursive_units': ''}},
                          {'wf_name': 'terfisi_gelen_personel_listesi',    # Type B
                           'fields': {'abstract_role_id': 'DAIRE_PERSONELI',
                                      'start_date': '09.12.2016',
                                      'finish_date': '20.12.2016',
                                      'get_roles_from': '',
                                      'unit_id': '7QrxVwobdBkrnKHbUpWcHhxnEX3',
                                      'object_query_code': 'personel_turu=2',
                                      'object_type': 'Personel',
                                      'recursive_units': ''}},
                          {'wf_name': 'yeni_donem_olusturma',    # Type C
                           'fields': {'abstract_role_id': 'H2teltns7WCwTeslCq49Ip7cGrE',
                                      'start_date': '09.12.2016',
                                      'finish_date': '20.12.2016',
                                      'get_roles_from': ''}},
                          {'wf_name': 'zaman_dilimi_duzenle',    # Type D
                           'fields': {'abstract_role_id': 'DERS_PROGRAMI_KOORDINATORU',
                                      'start_date': '09.12.2016',
                                      'finish_date': '20.12.2016',
                                      'get_roles_from': '',
                                      'unit_id': 'T71IQ6c7YIeEYOoIJKlHE9GrF72',
                                      'recursive_units': ''}}]

        for i in range(4):
            self.prepare_client('/is_akisi_atama', username='sistem_yoneticisi_1')

            self.client.post()

            name = types_workflow[i]["wf_name"]

            resp = self.client.post(form={"workflow": name,
                                          "gonder": 1})

            fields = types_workflow[i]['fields']

            type_keys = fields.keys()
            resp_keys = resp.json['forms']['model'].keys()

            for k in type_keys:
                assert k in resp_keys

            fields['gonder'] = 1

            resp = self.client.post(form=fields)

            assert resp.json['msgbox']['title'] == 'İşlem Başarılı'
