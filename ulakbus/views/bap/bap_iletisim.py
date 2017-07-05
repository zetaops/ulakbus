# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import AbstractRole
from ulakbus.models import Personel
from ulakbus.models import Role
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _


class BAPIletisimView(CrudView):
    def iletisim_bilgilerini_goster(self):
        self.current.output["meta"]["allow_search"] = False
        self.current.output["meta"]["allow_actions"] = False
        self.output['object_title'] = _(u"BAP Koordinatörlüğü İletişim")
        self.output['objects'] = [
            [_(u"Ad Soyad"), _(u"Telefon"), _(u"E-posta")]
        ]
        abstract_role = AbstractRole.objects.get(
            name='Bilimsel Arastirma Projesi - Koordinasyon Birimi')
        for r in Role.objects.all(abstract_role_id=abstract_role.key):
            p = Personel.objects.get(user=r.user())
            self.output['objects'].append({
                "fields": [p.__unicode__(), p.oda_tel_no, p.e_posta],
                "actions": []
            })
