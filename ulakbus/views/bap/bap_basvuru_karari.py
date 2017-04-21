# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from datetime import datetime


class ProjeKararForm(JsonForm):
    class Meta:
        title = _(u"İnceleme Sonrası Proje Kararı")

    revizyon = fields.Button(_(u"Revizyon İste"), cmd='revizyon')
    onayla = fields.Button(_(u"Projeyi Onayla"), cmd='onayla')
    iptal = fields.Button(_(u"İptal"), cmd='iptal')


class RevizyonGerekceForm(JsonForm):
    class Meta:
        title = _(u"Revizyon İsteme Gerekçeleri")
        help_text = _(u"Lütfen revizyon isteme gerekçelerinizi açıkça belirtiniz.")

    revizyon_gerekce = fields.Text(_(u"Revizyon Gerekçe"))
    gonder = fields.Button(_(u"Revizyona Gönder"), cmd='gonder')
    iptal = fields.Button(_(u"İptal"), cmd='iptal')


class BasvuruKarari(CrudView):
    class Meta:
        model = "BAPProje"

    def karar_sor(self):
        self.current.task_data['karar'] = 'iptal'
        form = ProjeKararForm(current=self.current)
        form.help_text = _(
            u"Lütfen %s adlı personelin %s projesi hakkındaki kararınızı belirleyiniz.") % (
                             self.object.yurutucu.__unicode__(), self.object.ad)

        self.form_out(form)

    def revizyon_gerekce_gir(self):
        form = RevizyonGerekceForm(current=self.current)
        self.form_out(form)

    def revizyon_kaydet_gonder(self):
        gerekce = self.input['form']['revizyon_gerekce']
        self.current.task_data['karar'] = 'revizyon'
        self.current.task_data['revizyon_gerekce'] = gerekce
        self.object.ProjeIslemGecmisi(eylem='Revizyon', aciklama='Revizyona gönderildi',
                                      tarih=datetime.now().date())
        self.object.durum = 3
        self.object.save()

    def onayla(self):
        self.object.durum = 4
        self.current.task_data['karar'] = 'onayla'
        self.object.ProjeIslemGecmisi(eylem='Gündeme Alındı',
                                      aciklama='Onaylandı ve gündeme alındı',
                                      tarih=datetime.now().date())
        self.object.save()
