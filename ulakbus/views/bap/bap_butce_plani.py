# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPButcePlani, BAPProje

from zengine.views.crud import CrudView, obj_filter
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __


class ButcePlaniForm(JsonForm):
    kaydet = fields.Button(__(u"Kaydet"))
    iptal = fields.Button(__(u"İptal"), cmd='iptal', form_validation=False)


class BapButcePlani(CrudView):
    class Meta:
        model = 'BAPButcePlani'

    def __init__(self, current):
        CrudView.__init__(self, current)
        if 'object_id' in self.current.task_data and self.cmd == 'add_edit_form' and \
                'object_id' not in self.input:
            del self.current.task_data['object_id']
            self.object = BAPButcePlani()

    def butce_kalemi_sec(self):
        form = JsonForm(self.object, current=self.current, title=_(u"Bütçe Kalemi Seç"))
        form.include = ['muhasebe_kod']
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def add_edit_form(self):
        if 'bap_proje_id' in self.current.task_data:
            proje_ad = BAPProje.objects.get(self.current.task_data['bap_proje_id']).ad
        else:
            proje_ad = '(Proje Belirlenmedi!)'

        self.object.muhasebe_kod = self.input['form']['muhasebe_kod']
        self.object.kod_adi = self.object.get_muhasebe_kod_display()

        self.current.task_data['muhasebe_kod'] = self.object.muhasebe_kod
        self.current.task_data['kod_adi'] = self.object.kod_adi

        form = ButcePlaniForm(self.object, current=self.current)
        form.exclude = ['muhasebe_kod', 'kod_adi', 'onay_tarihi', 'ilgili_proje']
        form.title = "%s Kodlu / %s Bütçe Planı" % (self.object.muhasebe_kod, self.object.kod_adi)
        form.help_text = "Yapacaginiz butce plani %s adli proje icin yapilacaktir." % \
                         proje_ad
        self.form_out(form)

    def save(self):
        self.set_form_data_to_object()
        self.object.muhasebe_kod = self.current.task_data['muhasebe_kod']
        self.object.kod_adi = self.current.task_data['kod_adi']
        if 'bap_proje_id' in self.current.task_data:
            self.object.ilgili_proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.save_object()

    def confirm_deletion(self):
        form = JsonForm(title=_(u"Bütçe Planı Silme İşlemi"))
        form.help_text = _(u"%s bilgilerine sahip bütçe planını silmek "
                           u"istiyormusunuz?") % self.object
        form.iptal = fields.Button(_(u"İptal"), cmd='list')
        form.sil = fields.Button(_(u"Sil"), cmd='delete')
        self.form_out(form)

    def show(self):
        CrudView.show(self)
        self.output['object']['Muhasebe Kod'] = str(self.object.muhasebe_kod)
        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def list(self, custom_form=None):
        CrudView.list(self)
        toplam = sum(float(obj['fields'][5])for obj in self.output['objects'][1:])
        self.output['objects'].append({'fields': ['TOPLAM', '', '', '', '', str(toplam)],
                                       'actions': ''})

    @obj_filter
    def proje_turu_islem(self, obj, result):
        result['actions'] = [
            {'name': _(u'Sil'), 'cmd': 'confirm_deletion', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'}]
