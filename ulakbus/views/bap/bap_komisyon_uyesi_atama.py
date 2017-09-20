# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPProje
from ulakbus.models import AbstractRole
from ulakbus.models import Personel
from ulakbus.models import Role

from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _


class KomisyonUyesiAtama(CrudView):

    def komisyon_uyesi_sec(self):
        if 'object_id' in self.input:
            self.current.task_data['bap_proje_id'] = self.input['object_id']

        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        if proje.komisyon_uyesi.exist:
            help_text = _(u"%s projesinin zaten bir komisyon üyesi bulunmaktadır. Mevcut komisyon "
                          u"üyesinin ismi: %s 'dir. Eğer mevcut komisyon üyesinin yerine bir "
                          u"başkasını atamak istiyorsanız işleme devam ediniz.") % \
                        (proje.ad, proje.komisyon_uyesi.user())
        else:
            help_text = ''

        abrol_kom_uye = AbstractRole.objects.get(name='Bilimsel Arastirma Projesi Komisyon Uyesi')
        komisyon_uyeleri = list()
        for r in Role.objects.all(abstract_role_id=abrol_kom_uye.key):
            p = Personel.objects.get(user=r.user())
            komisyon_uyeleri.append((r.key, p.__unicode__()))

        form = JsonForm(title=_(u"Komisyon Üyesi Seç"))
        form.help_text = help_text
        form.komisyon_uyesi = fields.String(_(u"Komisyon Üyeleri"), choices=komisyon_uyeleri)
        form.ilerle = fields.Button(_(u"İlerle"))
        form.iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)

    def onay_ekrani(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.current.task_data['komisyon_uyesi_role'] = self.input['form']['komisyon_uyesi']
        r = Role.objects.get(self.input['form']['komisyon_uyesi'])
        p = Personel.objects.get(user=r.user())
        form = JsonForm(title=_(u"Komisyon Üyesi Atama Onay"))
        form.help_text = _(u"%s projesine %s komisyon üyesini "
                           u"atayacaksınız.") % (proje.ad,  p.__unicode__())
        form.onayla = fields.Button(_(u"Onayla"))
        form.iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)

    def projeye_komisyon_uyesini_ata(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        komisyon_uyesi_role = Role.objects.get(self.current.task_data['komisyon_uyesi_role'])
        proje.komisyon_uyesi = komisyon_uyesi_role
        proje.save()

    def bilgilendirme_mesaji(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        r = Role.objects.get(self.current.task_data['komisyon_uyesi_role'])

        form = JsonForm(title=_(u"Komisyon Atama İşlemi Başarıyla Gerçekleşti"))
        form.help_text = _(u"%s projesine %s adlı komisyon üyesini başarıyla atadınız.") % (
            proje.ad, r.user())
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def listelemeye_geri_don(self):
        form = JsonForm(title=_(u" "))
        form.help_text = _(u"Başvuru listeleme ekranına geri dönüyorsunuz")
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)
