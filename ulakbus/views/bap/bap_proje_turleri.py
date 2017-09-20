# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import OrderedDict

import six

from ulakbus.models.form import Form
from ulakbus.models import BAPProjeTurleri, Permission

from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy as __

from pyoko import ListNode

from datetime import datetime


class ProjeTuruForm(JsonForm):
    ileri = fields.Button(__(u"İlerle"))


class ProjeTuruFormlari(JsonForm):
    class Meta:
        title = __(u"Proje Türü İçin Gerekli Formlar")
        inline_edit = ['sec', 'gereklilik']

    class BapFormListesi(ListNode):
        class Meta:
            title = __(u"BAP Form Listesi")
        key = fields.String("Key", hidden=True)
        sec = fields.Boolean(__(u"Projeye Dahil Et"), type="checkbox")
        ad = fields.String(__(u"Form Adı"), index=True)
        file = fields.File(__(u"File"), index=True,
                           random_name=True)  # form eger PDF olarak yulendiyse bu alan kullanilir.
        gereklilik = fields.Boolean(__(u"Zorunluluk"), type="checkbox", required=False)

    def bap_proje_turu_form(self):
        formlar = Form.objects.all(tag="BAP")

        for form in formlar:
            self.BapFormListesi(
                key=form.key,
                sec=False,
                ad=form.ad,
                file=form.file,
                gereklilik=False
            )

    ileri = fields.Button(__(u"İlerle"))
    iptal = fields.Button(__(u"İptal"), cmd='iptal')


class ProjeTurleri(CrudView):
    class Meta:
        model = 'BAPProjeTurleri'

    def __init__(self, current):
        CrudView.__init__(self, current)
        if 'object_id' in self.current.task_data and self.cmd == 'add_edit_form' and \
                'object_id' not in self.input:
            del self.current.task_data['object_id']
            self.object = BAPProjeTurleri()

    def add_edit_form(self):
        self.form_out(_form=ProjeTuruForm(self.object, exclude=['Belgeler', 'Formlar']))

    def proje_belge_sec(self):
        self.current.task_data['proje_turu_bilgileri'] = self.input['form']
        form_belgeler = ProjeTuruForm(self.object, include=['Belgeler'])
        form_belgeler.title = _(u"Proje Türü İçin Gerekli Belgeler")
        form_belgeler.iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(_form=form_belgeler)

    def proje_form_sec(self):
        if 'form' in self.input and 'Belgeler' in self.input['form']:
            self.current.task_data['proje_turu_belgeler'] = self.input['form']['Belgeler']
        form = ProjeTuruFormlari()
        if not self.object.Formlar:
            form.bap_proje_turu_form()
        else:
            [form.BapFormListesi(key=f.proje_formu.key,
                                 ad=f.proje_formu.ad,
                                 file=f.proje_formu.file,
                                 date=f.proje_formu.date,
                                 sec=f.secili,
                                 gereklilik=f.gereklilik) for f in self.object.Formlar]
        self.form_out(form)

    def save(self):
        belgeler = self.current.task_data['proje_turu_belgeler']
        form_listesi = []
        for f in self.current.input['form']['BapFormListesi']:
            if f['sec']:
                form_listesi.append(f)

        if 'object_id' in self.current.task_data:
            proje_turu = BAPProjeTurleri.objects.get(self.current.task_data['object_id'])
            proje_turu.Belgeler.clear()
            proje_turu.Formlar.clear()
        else:
            proje_turu = BAPProjeTurleri()

        proje_turu.kod = self.current.task_data['proje_turu_bilgileri']['kod']
        proje_turu.ad = self.current.task_data['proje_turu_bilgileri']['ad']
        proje_turu.aciklama = self.current.task_data['proje_turu_bilgileri']['aciklama']
        proje_turu.min_sure = self.current.task_data['proje_turu_bilgileri']['min_sure']
        proje_turu.max_sure = self.current.task_data['proje_turu_bilgileri']['max_sure']
        proje_turu.butce_ust_limit = \
            self.current.task_data['proje_turu_bilgileri']['butce_ust_limit']
        proje_turu.gerceklestirme_gorevlisi_yurutucu_ayni_mi = \
        self.current.task_data['proje_turu_bilgileri']['gerceklestirme_gorevlisi_yurutucu_ayni_mi']
        if belgeler:
            [proje_turu.Belgeler(
                ad=belge['ad'],
                gereklilik=belge['gereklilik']
            ) for belge in belgeler]

        for form in form_listesi:
            if 'key' in form:
                f = Form.objects.get(form['key'])
            else:
                f = Form()
                f.ad = form['ad']
                f.file = form['file']
                f.permissions = Permission.objects.get(name='BAPProjeTurleri')
                f.tag = "BAP"
                f.save()
            proje_turu.Formlar(proje_formu=f, gereklilik=form['gereklilik'], secili=True)
        proje_turu.blocking_save()

    def show(self):
        self.set_client_cmd('show')
        obj_form = JsonForm(self.object, current=self.current,
                            models=False)._serialize(readable=True)
        obj_data = OrderedDict()
        for d in obj_form:
            key = six.text_type(d['title'])
            if d['type'] == 'ListNode' and d['value'] is not None:
                data = []
                for v in d['value']:
                    if 'proje_formu_id' in v:
                        string = str(v['proje_formu_id']['unicode']) + \
                                 ("(Zorunlu)" if v['gereklilik'] else "(Zorunlu Değil)")
                    else:
                        string = str(v['ad']) + \
                                 ("(Zorunlu)" if v['gereklilik'] else "(Zorunlu Değil)")
                    data.append(string)
                obj_data[key] = ' - '.join(data)
            else:
                obj_data[key] = str(d['value']) if d['value'] is not None else ''
        durum = (
        obj_data[u'Projenin gerçekleştirme görevlisi ile yürütücüsü aynı kişi mi?'] == 'True')
        obj_data[
            u'Projenin gerçekleştirme görevlisi ile yürütücüsü aynı kişi mi?'] = 'Evet' if durum else 'Hayır'
        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)
        self.output['object_title'] = "%s : %s" % (self.model_class.Meta.verbose_name, self.object)
        self.output['object_key'] = self.object.key
        self.output['object'] = obj_data

    @obj_filter
    def proje_turu_islem(self, obj, result):
        result['actions'].extend([
            {'name': _(u'Sil'), 'cmd': 'delete', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'}])
