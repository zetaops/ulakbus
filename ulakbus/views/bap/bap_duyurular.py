# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPDuyurular

from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import JsonForm, fields


class DuyurularAddEditForm(JsonForm):
    class Meta:
        exclude = ['ekleyen', 'yayinlanmismi']

    kaydet = fields.Button(__(u"Kaydet"), cmd='save')
    iptal = fields.Button(__(u"İptal"), form_validation=False)


class BapDuyurular(CrudView):
    class Meta:
        model = "BAPDuyurular"

    def __init__(self, current):
        CrudView.__init__(self, current)
        if 'object_id' in self.current.task_data and self.cmd == 'add_edit_form' and \
                'object_id' not in self.input:
            del self.current.task_data['object_id']
            self.object = BAPDuyurular()
            self.object_form = DuyurularAddEditForm(self.object, current=self.current)

    def list(self, custom_form=None):
        CrudView.list(self)
        form = JsonForm(title=_(u"BAP Duyurular"))
        form.duyuru_yayinla = fields.Button(_(u"Yayınla"), cmd='yayinla')
        form.ekle = fields.Button(_(u"Ekle"), cmd='add_edit_form')
        self.form_out(form)

    def add_edit_form(self):
        self.form_out(DuyurularAddEditForm(self.object, current=self.current))

    def save(self):
        CrudView.save(self)
        self.object.ekleyen = self.current.user
        self.object.yayinlanmismi = False
        self.object.blocking_save()

    def duyuru_detay_goster(self):
        self.output['object_title'] = _(u"%s") % self.object

        obj_data = {'Ekleyen': _(u"%s") % self.object.ekleyen,
                    'Eklenme Tarihi': _(u"%s") % self.object.eklenme_tarihi,
                    'Son Geçerlilik Tarihi': _(u"%s") % self.object.son_gecerlilik_tarihi,
                    'Başlık': _(u"%s") % self.object.duyuru_baslik,
                    'Duyuru': _(u"%s") % self.object.duyuru_icerik,
                    'Durum': _(u"%s") % ("Yayınlandı" if self.object.yayinlanmismi else
                                         "Yayınlanmadı"),
                    'Ek Dosyalar': ''.join(["""%s\n""" % dosya.dosya_aciklamasi
                                            for dosya in self.object.EkDosyalar])}

        self.output['object'] = obj_data

        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def duyuru_yayinla_onay(self):
        form = JsonForm(title=_(u"Duyuruları Yayınlama Onay Ekranı"))
        form.help_text = _(u"Duyuruları yayınlamak istiyor musunuz?")
        form.evet = fields.Button(_(u"Evet"), cmd='bitir')
        form.iptal = fields.Button(_(u"İptal"))
        self.form_out(form)

    def duyuru_yayinla(self):
        duyurular = BAPDuyurular.objects.all()
        yayinlanmamis_duyurular = duyurular.filter(yayinlanmismi=False)

        for d in yayinlanmamis_duyurular:
            d.yayinlanmismi = True
            d.blocking_save()

        self.current.output['cmd'] = 'reload'


    def confirm_deletion(self):
        form = JsonForm(title=_(u"Silme İşlemi"))
        form.help_text = _(u"%s duyurusunu silmek istiyor musunuz?") % self.object
        form.evet = fields.Button(_(u"Evet"), cmd='delete')
        form.iptal = fields.Button(_(u"İptal"))
        self.form_out(form)

    @obj_filter
    def duyuru_islem(self, obj, result):
        result['actions'] = [
            {'name': _(u'Sil'), 'cmd': 'confirm_deletion', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'}]