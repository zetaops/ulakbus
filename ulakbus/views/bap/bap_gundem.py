# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _


class Gundem(CrudView):
    class Meta:
        model = "BAPGundem"

    def list(self, custom_form=None):
        custom_form = JsonForm(current=self.current, title=_(u"Gündem Listesi"))
        CrudView.list(self, custom_form=custom_form)

    def add_edit_form(self):
        form = JsonForm(self.object)
        form.title = _(u"%s / %s  - Komisyon Kararı") % (self.object.proje.ad,
                                                          self.object.get_gundem_tipi_display())
        form.exclude = ['proje', 'gundem_tipi', 'sonuclandi']
        form.kaydet = fields.Button(_(u"Kaydet"), cmd='save')
        form.iptal = fields.Button(_(u"İptal"), form_validation=False)
        self.form_out(_form=form)

    def show(self):
        CrudView.show(self)
        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def komisyon_kararini_ilet(self):
        self.object.proje.yurutucu.user.send_notification(
            title=_(u"Komisyon Kararı"),
            message=_(u"%s adlı projenizin %s komisyon kararı Karar: %s") % (
                self.object.proje.ad,
                self.object.get_gundem_tipi_display(),
                self.input['form']['karar']),
            sender=self.current.role.user)

    def karar_sonrasi_adimlar(self):
        pass

    def bilgilendirme(self):
        self.object.sonuclandi = True
        self.object.save()
        self.set_client_cmd('reload')

    @obj_filter
    def proje_turu_islem(self, obj, result):
        sonuc = {'name': _(u'Sonuç'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'}
        goster = {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'}
        if obj.sonuclandi:
            result['actions'] = ([goster])
        else:
            result['actions'] = ([sonuc, goster])
