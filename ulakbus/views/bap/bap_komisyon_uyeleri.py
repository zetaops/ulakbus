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


class BapKomisyonUyeleri(CrudView):
    """
    Komisyon uyelerinin goruntulendigi is akisidir.
    """
    def komisyon_uyelerini_listele(self):
        self.current.output["meta"]["allow_search"] = False
        self.current.output["meta"]["allow_actions"] = False
        self.output['object_title'] = _(u"BAP Komisyonu Üyeleri")
        self.output['objects'] = [
            [_(u'Ad Soyad'), _(u'Statü'), _(u"Telefon"), _(u"E-posta")]
        ]

        rol_kom_uye = AbstractRole.objects.get(name='Bilimsel Arastirma Projesi Komisyon Uyesi')
        rol_kom_bas = AbstractRole.objects.get(name='Bilimsel Arastirma Projesi Komisyon Baskani')

        r = Role.objects.get(abstract_role_id=rol_kom_bas.key)
        p = Personel.objects.get(user=r.user())
        self.output['objects'].append({
            "fields": [p.__unicode__(), _(u"Başkan"), p.oda_tel_no, p.e_posta],
            "actions": []
        })

        for r in Role.objects.all(abstract_role_id=rol_kom_uye.key):
            p = Personel.objects.get(user=r.user())
            self.output['objects'].append({
                "fields": [p.__unicode__(), _(u"Üye"), p.oda_tel_no, p.e_posta],
                "actions": []
            })

