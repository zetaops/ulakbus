# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.s3_file_manager import S3FileManager
from ulakbus.models import BAPDuyuru

from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import JsonForm, fields


class DuyurularAddEditForm(JsonForm):
    class Meta:
        exclude = ['ekleyen', 'yayinlanmis_mi']

    kaydet = fields.Button(__(u"Kaydet"), cmd='save')
    iptal = fields.Button(__(u"İptal"), form_validation=False)


class BapDuyurular(CrudView):
    class Meta:
        model = "BAPDuyuru"

    def __init__(self, current):
        CrudView.__init__(self, current)
        if 'object_id' in self.current.task_data and self.cmd == 'add_edit_form' and \
                'object_id' not in self.input:
            del self.current.task_data['object_id']
            self.object = BAPDuyuru()
            self.object_form = DuyurularAddEditForm(self.object, current=self.current)

    def list(self, custom_form=None):
        CrudView.list(self)
        form = JsonForm(title=_(u"BAP Duyurular"))
        form.ekle = fields.Button(_(u"Ekle"), cmd='add_edit_form')
        self.form_out(form)

    def add_edit_form(self):
        self.form_out(DuyurularAddEditForm(self.object, current=self.current))

    def save(self):
        CrudView.save(self)
        self.object.ekleyen = self.current.user
        self.object.yayinlanmis_mi = False
        self.object.blocking_save()

    def duyuru_detay_goster(self):
        self.output['object_title'] = _(u"%s") % self.object

        obj_data = {'Ekleyen': _(u"%s") % self.object.ekleyen,
                    'Eklenme Tarihi': _(u"%s") % self.object.eklenme_tarihi,
                    'Son Geçerlilik Tarihi': _(u"%s") % self.object.son_gecerlilik_tarihi,
                    'Başlık': _(u"%s") % self.object.duyuru_baslik,
                    'Duyuru': _(u"%s") % self.object.duyuru_icerik,
                    'Durum': _(u"%s") % ("Yayınlandı" if self.object.yayinlanmis_mi else
                                         "Yayınlanmadı"),
                    'Ek Dosyalar': ''.join(["""%s\n""" % dosya.dosya_aciklamasi
                                            for dosya in self.object.EkDosyalar])}

        self.output['object'] = obj_data

        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def duyuru_yayinla(self):
        if self.input['cmd'] == 'yayinla':
            self.object.yayinlanmis_mi = True
        else:
            self.object.yayinlanmis_mi = False

        self.object.blocking_save()

    def confirm_deletion(self):
        form = JsonForm(title=_(u"Silme İşlemi"))
        form.help_text = _(u"%s duyurusunu silmek istiyor musunuz?") % self.object
        form.evet = fields.Button(_(u"Evet"), cmd='delete')
        form.iptal = fields.Button(_(u"İptal"))
        self.form_out(form)

    @obj_filter
    def duyuru_islem(self, obj, result):
        yayinla = {'name': _(u'Yayınla'), 'cmd': 'yayinla',
                   'mode': 'normal', 'show_as': 'button'}
        yayindan_kaldir = {'name': _(u'Yayından Kaldır'), 'cmd': 'yayindan_kaldir',
                           'mode': 'normal', 'show_as': 'button'}
        result['actions'] = [
            {'name': _(u'Sil'), 'cmd': 'confirm_deletion', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'},
            yayindan_kaldir if obj.yayinlanmis_mi else yayinla]

    def duyurulari_goruntule(self):
        self.output['object_title'] = _(u"BAP Genel Duyurular")
        self.output['objects'] = [['Duyuru Başlık', 'Eklenme Tarihi', 'Son Geçerlilik Tarihi',
                                   'Ekleyen']]
        for duyuru in BAPDuyuru.objects.all(yayinlanmis_mi=True):
            item = {
                "fields": [duyuru.duyuru_baslik,
                           duyuru.eklenme_tarihi.strftime("%d.%m.%Y"),
                           duyuru.son_gecerlilik_tarihi.strftime("%d.%m.%Y"),
                           "%s %s" % (duyuru.ekleyen.name, duyuru.ekleyen.surname)],
                "actions": [{'name': _(u'Göster'), 'cmd': 'detay',
                             'mode': 'normal', 'show_as': 'button'}],
                "key": duyuru.key
            }
            self.output['objects'].append(item)

    def duyuru_goruntule_detay(self):
        self.output['object_title'] = _(u"%s") % self.object

        obj_data = {'Ekleyen': _(u"%s") % self.object.ekleyen,
                    'Eklenme Tarihi': _(u"%s") % self.object.eklenme_tarihi,
                    'Son Geçerlilik Tarihi': _(u"%s") % self.object.son_gecerlilik_tarihi,
                    'Başlık': _(u"%s") % self.object.duyuru_baslik,
                    'Duyuru': _(u"%s") % self.object.duyuru_icerik,
                    'Ek Dosyalar': ''.join(["""%s\n""" % dosya.dosya_aciklamasi
                                            for dosya in self.object.EkDosyalar])}

        self.output['object'] = obj_data

        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        if self.object.EkDosyalar:
            form.indir = fields.Button(_(u"Ek Dosyaları İndir"), cmd='belge_indir')
        self.form_out(form)

    def duyuru_belge_indir(self):
        s3 = S3FileManager()
        keys = [dosya.ek_dosya for dosya in self.object.EkDosyalar]
        zip_name = "%s-duyuru-belgeler" % self.object.__unicode__()
        zip_url = s3.download_files_as_zip(keys, zip_name)
        self.set_client_cmd('download')
        self.output['download_url'] = zip_url
