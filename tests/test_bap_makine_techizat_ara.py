# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Demirbas
from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_makine_techizat_ara(self):
        user = User.objects.get(username='ulakbus')
        self.prepare_client('/bap_makine_techizat_ara', user=user)
        resp = self.client.post()

        assert resp.json['forms']['model']['form_name'] == 'MakineTechizatAraForm'

        form = {
            'ad': 'masa',
            'ara': 1,
            'birim_id': None
        }

        resp = self.client.post(form=form, cmd='ara')

        count = Demirbas.objects.all().search_on(
            'ad', 'etiketler', 'teknik_ozellikler', contains='masa').count()
        assert len(resp.json['objects']) == count + 1
        assert len(resp.json['objects'][1]['actions']) == 1

        resp = self.client.post(cmd='goruntule', object_id='MaPAfIYMgFGI2dcl1ercl5mYd65')

        demirbas = Demirbas.objects.get('MaPAfIYMgFGI2dcl1ercl5mYd65')

        assert resp.json['object']['Url'] == demirbas.url

        resp = self.client.post()

        form['birim_id'] = 'PNrGNyS35dmw9WHKPyl9Er0CiWN'

        resp = self.client.post(form=form, cmd='ara')

        assert 'msgbox' in resp.json
