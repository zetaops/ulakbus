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


class RevizyonGerekceForm(JsonForm):
    """
    Proje hakkında revizyon istenirse, gerekçelerin girileceği form.

    """

    class Meta:
        title = _(u"Revizyon İsteme Gerekçeleri")
        help_text = _(u"Lütfen revizyon isteme gerekçelerinizi açıkça belirtiniz.")

    revizyon_gerekce = fields.Text(__(u"Revizyon Gerekçe"))
    gonder = fields.Button(__(u"Revizyona Gönder"), cmd='gonder')
    iptal = fields.Button(__(u"İptal"), cmd='iptal', form_validation=False)


class BasvuruKarari(CrudView):
    class Meta:
        model = "BAPProje"

    def __init__(self, current):
        CrudView.__init__(self, current)
        if not self.object.key:
            self.object = self.model_class.objects.get(self.current.task_data['bap_proje_id'])

    def karar_sor(self):
        """
        İnceleme sonrası koordinasyon birimi proje hakkında karar verir.

        2: Öğretim elemanı tarafından koordinasyon birimine onaya gönderildi.
        3: Koordinasyon birimi tarafından öğretim elemanına revizyon için gönderildi.
        4: Koordinasyon birimi projeyi onayladı.

        """

        self.current.task_data['karar'] = 'iptal'
        form = JsonForm(current=self.current, title=_(u"İnceleme Sonrası Proje Kararı"))

        if self.object.durum == 2:
            form.onayla = fields.Button(__(u"Projeyi Onayla"), cmd='onayla')

        if not self.object.durum == 3:
            form.revizyon = fields.Button(__(u"Revizyon İste"), cmd='revizyon')

        form.iptal = fields.Button(__(u"Daha Sonra Karar Ver"), cmd='iptal')

        form.help_text = _(
u"""Lütfen %s adlı personelin %s projesi hakkındaki kararınızı belirleyiniz.\n
Projenin güncel durumu: %s
""") % (self.object.yurutucu.__unicode__(), self.object.ad,
        self.object.get_durum_display())

        self.form_out(form)

    def revizyon_gerekce_gir(self):
        """
        Projeye neden revizyon istendiği açıkça belirtilir.

        """

        form = RevizyonGerekceForm(current=self.current)
        self.form_out(form)

    def revizyon_kaydet_gonder(self):
        """
        Revizyon gerekçeleri öğretim elemanına gönderilmek üzere kaydedilir, projenin durumu
        revizyonda olarak değiştirilir ve işlem geçmişi güncellenir.

        """

        gerekce = self.input['form']['revizyon_gerekce']
        self.current.task_data['karar'] = 'revizyon'
        self.current.task_data['revizyon_gerekce'] = gerekce
        self.object.ProjeIslemGecmisi(eylem='Revizyon', aciklama='Revizyona gönderildi',
                                      tarih=datetime.now())
        self.object.durum = 3
        self.object.save()

    def onayla(self):
        """
        Projenin durumu onaylandı olarak değiştirilir ve işlem geçmişi güncellenir.

        """

        self.current.task_data['karar'] = 'onayla'
        self.object.ProjeIslemGecmisi(eylem='Onaylandı',
                                      aciklama='Onaylandı ve gündeme alındı',
                                      tarih=datetime.now())
        self.object.durum = 4
        self.object.save()
