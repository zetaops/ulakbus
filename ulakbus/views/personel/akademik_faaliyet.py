# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Ali Riza Keles'

from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext_lazy as __
from zengine.lib.translation import gettext as _
from ulakbus.models.akademik_faaliyet import AkademikFaaliyetTuru as Aft
from ulakbus.models.akademik_faaliyet import AkademikFaaliyet as Af


def faaliyet_secenekler():
    turler = Aft.objects.distinct_values_of("faaliyet")
    return [(tur.title(), tur.title()) for tur in turler.keys()]


def alt_faaliyet_secenekler(faaliyet):
    turler = Aft.objects.filter(faaliyet=faaliyet).distinct_values_of("alt_faaliyet")
    return [(tur.title(), tur.title()) for tur in turler.keys()]


class FaaliyetSec(JsonForm):
    faaliyet = fields.String("Faaliyet Seçiniz", choices=faaliyet_secenekler())
    ileri = fields.Button(__(u"Ileri"))


class AltFaaliyetSec(JsonForm):
    ileri = fields.Button(__(u"Ileri"))


class AkademikFaaliyet(CrudView):
    class Meta:
        model = "AkademikFaaliyet"

    def listele(self):
        self.list()

    def goruntule(self):
        pass

    def faaliyet_sec(self):
        _form = FaaliyetSec(title=_("Faaliyet Türünü Seçiniz"))
        self.form_out(_form)

    def faaliyet_kaydet(self):
        self.current.task_data['faaliyet'] = self.current.input['form']['faaliyet']
        self.current.task_data['alt_faaliyetler'] = alt_faaliyet_secenekler(
            self.current.task_data['faaliyet'])

    def alt_faaliyet_sec(self):
        _form = AltFaaliyetSec(title=_("Alt Faaliyet Seçiniz"))
        _form.alt_faaliyet = fields.String("Alt Faaliyet Seçiniz", choices=alt_faaliyet_secenekler(
            self.current.task_data['faaliyet']
        ))
        self.form_out(_form)

    def alt_faaliyet_kaydet(self):
        self.current.task_data['alt_faaliyet'] = self.current.input['form']['alt_faaliyet']

    def detay_sec(self):
        _form = JsonForm(title=_("Detay Seçiniz"))

        if 'alt_faaliyet' in self.current.task_data:
            q = Aft.objects.filter(
                alt_faaliyet=self.current.task_data['alt_faaliyet'])
        else:
            q = Aft.objects.filter(
                faaliyet=self.current.task_data['faaliyet'])

        turler = q.values("key", "detay")

        _form.detay = fields.String(choices=[(tur['key'], tur['detay']) for tur in turler])
        self.form_out(_form)

    def detay_kaydet(self):
        self.current.task_data['detay'] = self.current.input['form']['detay']

    def gorev_sec(self):
        pass

    def kaydet(self):
        tur = Aft.objects.get(
            faaliyet=self.current.task_data['faaliyet'],
            detay=self.current.task_data['detay']
        )

        faaliyet = Af(
            tur=tur,
            personel=self.current.role.user.personel
        )

        faaliyet.save()

    def kayit_bilgisi_ver(self):
        self.current.output['msgbox'] = {
            "type": "info",
            "title": _(u"Başarılı"),
            "msg": """Yeni faaliyet aşağıdaki bilgiler ile kaydedilmiştir:
            %s %s %s
            """ % (self.current.task_data['detay'])}
