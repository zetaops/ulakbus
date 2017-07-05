# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import AbstractRole
from ulakbus.models import User
from ulakbus.models import Role
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_komisyon_uyeleri(self):
        user = User.objects.get(username='ulakbus')
        self.prepare_client('/bap_komisyon_uyeleri', user=user)
        resp = self.client.post()

        rol_kom_uye = AbstractRole.objects.get(name='Bilimsel Arastirma Projesi Komisyon Uyesi')
        rol_kom_bas = AbstractRole.objects.get(name='Bilimsel Arastirma Projesi Komisyon Baskani')

        assert len(resp.json["objects"]) - 1 == Role.objects.all(
            abstract_role_id__in=[rol_kom_uye.key, rol_kom_bas.key]).count()
