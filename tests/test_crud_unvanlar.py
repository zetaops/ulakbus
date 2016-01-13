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
    def test_list_add_delete_with_hizmet_unvan_model(self):
        # setup workflow
        def len_1(lst):
            return len(lst) - 1

        self.prepare_client('/crud')
        # calling with just model name (without any cmd) equals to cmd="list"
        resp = self.client.post(model='HizmetUnvan')
        assert 'objects' in resp.json
        print '+++++++++++++++++++++++++++++++++++++'
        print len(resp.json['objects'])
        # count number of records
        num_of_objects = len_1(resp.json['objects'])
        # delete the first object then go to list view
        resp = self.client.post(model='HizmetUnvan',
                                cmd='delete',
                                object_id=resp.json['objects'][1]['key'])

        resp = self.client.post(model='HizmetUnvan')
        print '__________________________________________________________'
        print len(resp.json['objects'])
        # Silinen objectin ardindan object sayisini olcmek icin once
        # resp = self.client.post(model='HizmetUnvan')
        # print len(resp.json['objects'])
        # Unvan formuna yeni bir deger ekliyoruz.
        # refresh the model to new records
        # resp = self.client.post(model='HizmetUnvan')
        # assert num_of_objects - 1 == len_1(resp.json['objects'])
        # add a new record
        resp = self.client.post(model='HizmetUnvan', cmd='add_edit_form', form=dict(add=1))
        # save the record and list the records
        resp = self.client.post(model='HizmetUnvan',
                                cmd='save::list',
                                form=dict(tckn="12323121443"))
        # assert num_of_objects == len_1(resp.json['objects'])
        print len(resp.json['objects'])
        """
        # duzenle ve sil islemleri icin object_id degerine ihtiyacimiz var.
        resp = self.client.post(model='HizmetUnvan',
                                cmd='add_edit_form',
                                object_id=resp.json['objects'][1]['key'])

        form_data = resp.json['forms']['model']
        form_token = self.client.token
        self.client.token = ''
        resp = self.client.post(model='Personel',
                                cmd='select_list',
                                query='e')
        personel_key, personel_ad = resp.json['objects'][0]['key'], resp.json['objects'][0]['value']
        self.client.token = form_token
        form_data['personel_id'] = personel_key
        form_data['kurum_onay_tarihi'] = '12.09.2011'
        form_data['unvan_bitis_tarihi'] = '11.03.2010'
        form_data['unvan_tarihi'] = '09.04.2909'
        self.client.post(model='HizmetUnvan', cmd='save::list', form=form_data)"""
