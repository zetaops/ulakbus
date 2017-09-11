# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.lib.test_utils import BaseTestCase
from zengine.lib.translation import gettext as _


class TestCase(BaseTestCase):
    def test_bap_anasayfa(self):
        self.prepare_client('/bap_anasayfa', username='ulakbus')
        resp = self.client.post()
        assert 'menu' in resp.json
        assert 'top_action_buttons' in resp.json
        assert 'university_logo' in resp.json
        assert 'university_title' in resp.json
        assert 'bidding' in resp.json
        assert 'general' in resp.json
        assert len(resp.json['top_action_buttons']) == 5
        assert resp.json['menu']['title'] == _(u"Menü")

