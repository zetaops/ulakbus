# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPSSS

from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import JsonForm, fields


class SSSAddEditForm(JsonForm):
    class Meta:
        exclude = ['yayinlanmis_mi']

    kaydet = fields.Button(__(u"Kaydet"), cmd='save')
    iptal = fields.Button(__(u"İptal"), form_validation=False)


class BAPSikcaSorulanSorular(CrudView):
    class Meta:
        model = "BAPSSS"

    def __init__(self, current):
        CrudView.__init__(self, current)
        if 'object_id' in self.current.task_data and self.cmd == 'add_edit_form' and \
                'object_id' not in self.input:
            del self.current.task_data['object_id']
            self.object = BAPSSS()
            self.object_form = SSSAddEditForm(self.object, current=self.current)

# -------------- Bap Koordinasyon Birimi --------------

    def list(self, custom_form=None):
        CrudView.list(self)
        form = JsonForm(title=_(u"Sıkça Sorulan Sorular"))
        form.ekle = fields.Button(_(u"Ekle"), cmd='add_edit_form')
        self.form_out(form)

    def add_edit_form(self):
        self.form_out(SSSAddEditForm(self.object, current=self.current))

    def show(self):
        CrudView.show(self)
        self.output['object']['Yayınlanmış mı?'] = 'Evet' if self.object.yayinlanmis_mi else 'Hayır'
        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def yayinla(self):
        if self.input['cmd'] == 'yayinla':
            self.object.yayinlanmis_mi = True
        else:
            self.object.yayinlanmis_mi = False

        self.object.blocking_save()

    def confirm_deletion(self):
        form = JsonForm(title=_(u"Silme İşlemi"))
        form.help_text = _(u"%s sorusunu silmek istiyor musunuz?") % self.object
        form.evet = fields.Button(_(u"Evet"), cmd='delete')
        form.iptal = fields.Button(_(u"İptal"))
        self.form_out(form)

    @obj_filter
    def sss_islem(self, obj, result):
        yayinla = {'name': _(u'Yayınla'), 'cmd': 'yayinla',
                   'mode': 'normal', 'show_as': 'button'}
        yayindan_kaldir = {'name': _(u'Yayından Kaldır'), 'cmd': 'yayindan_kaldir',
                           'mode': 'normal', 'show_as': 'button'}
        result['actions'] = [
            {'name': _(u'Sil'), 'cmd': 'confirm_deletion', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'},
            yayindan_kaldir if obj.yayinlanmis_mi else yayinla]

# -------------- Bap Koordinasyon Birimi --------------

# -------------- Anonim Wf ----------------

    def bap_sss_goruntule(self):
        self.output['object_title'] = _(u"BAP Sıkça Sorulan Sorular")
        self.output['objects'] = [['Soru', 'Cevap']]
        for sss in BAPSSS.objects.all(yayinlanmis_mi=True):
            item = {
                "fields": [sss.soru, sss.cevap],
                "actions": []
            }
            self.output['objects'].append(item)

        self.current.output["meta"]["allow_actions"] = False
