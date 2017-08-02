# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPButcePlani, BAPProje, Personel, Okutman

from zengine.views.crud import CrudView, obj_filter, list_query
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

    def kontrol(self):
        self.current.task_data['proje_sec'] = False
        self.current.task_data['proje_data'] = []
        if 'bap_proje_id' not in self.current.task_data:
            personel = Personel.objects.get(user=self.current.user)
            okutman = Okutman.objects.get(personel=personel)
            self.current.task_data['proje_data'] = [(proje.key, proje.ad) for proje in
                                                    BAPProje.objects.filter(yurutucu=okutman)]
            self.current.task_data['proje_sec'] = True

    def proje_sec(self):
        form = JsonForm(title=_(u"Proje Seçiniz"))
        form.proje = fields.String(choices=self.current.task_data['proje_data'])
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def butce_kalemi_sec(self):
        form = JsonForm(self.object, current=self.current, title=_(u"Bütçe Kalemi Seç"))
        form.include = ['muhasebe_kod_genel']
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def add_edit_form(self):
        proje_ad = BAPProje.objects.get(self.current.task_data['bap_proje_id']).ad
        self.object.muhasebe_kod_genel = self.input['form']['muhasebe_kod_genel']
        self.object.kod_adi = self.object.get_muhasebe_kod_genel_display()

        self.current.task_data['muhasebe_kod_genel'] = self.object.muhasebe_kod_genel
        self.current.task_data['kod_adi'] = self.object.kod_adi

        form = ButcePlaniForm(self.object, current=self.current)
        form.exclude = ['muhasebe_kod', 'muhasebe_kod_genel', 'kod_adi', 'onay_tarihi',
                        'ilgili_proje', 'durum', 'toplam_fiyat', 'kazanan_firma']
        form.title = "%s Bütçe Planı" % self.object.kod_adi
        form.help_text = "Yapacağınız bütçe planı %s adlı proje için yapılacaktır." % \
                         proje_ad
        self.form_out(form)

    def save(self):
        self.set_form_data_to_object()
        self.object.muhasebe_kod_genel = self.current.task_data['muhasebe_kod_genel']
        self.object.kod_adi = self.current.task_data['kod_adi']
        self.object.toplam_fiyat = self.object.birim_fiyat * self.object.adet
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
        self.output['object']['Muhasebe Kod'] = str(self.object.muhasebe_kod_genel)
        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def list(self, custom_form=None):
        if 'form' in self.input and 'proje' in self.input['form']:
            self.current.task_data['bap_proje_id'] = self.input['form']['proje']
        CrudView.list(self)
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        if 'GenelBilgiGirForm' in self.current.task_data:
            ad = self.current.task_data['GenelBilgiGirForm']['ad']
        else:
            ad = proje.ad
        toplam = sum(BAPButcePlani.objects.filter(ilgili_proje=proje).values_list('toplam_fiyat'))
        self.output['objects'].append({'fields': ['TOPLAM', '', '', '', str(toplam)],
                                       'actions': ''})
        form = JsonForm(title=_(u"%s projesi için Bütçe Planı") % ad)
        form.ekle = fields.Button(_(u"Ekle"), cmd='add_edit_form')
        form.bitir = fields.Button(_(u"Bitir"), cmd='bitir')
        self.form_out(form)

    def bilgilendirme(self):
        if 'proje_yok' in self.current.task_data:
            self.current.msg_box(
                msg="""Yürütücüsü olduğunuz herhangi bir proje
                    bulunamadı. Size bağlı olan proje
                    olmadığı için yeni bir bütçe planı yapamazsınız.""",
                title='Proje Bulunamadı')

    @obj_filter
    def proje_turu_islem(self, obj, result):
        result['actions'] = [
            {'name': _(u'Sil'), 'cmd': 'confirm_deletion', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'}]

    @list_query
    def list_by_bap_proje_id(self, queryset):
        return queryset.filter(ilgili_proje_id=self.current.task_data['bap_proje_id'])