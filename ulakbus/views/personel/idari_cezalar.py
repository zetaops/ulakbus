# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.models.personel import Personel
import six


class IdariCezaForm(JsonForm):
    class Meta:
        exclude = ['personel']

    kaydet = fields.Button(__(u"Kaydet"), cmd="add_edit_form")
    iptal = fields.Button(__(u"İptal"), cmd='iptal', form_validation=False)


class IdariCezaTakibi(CrudView):
    class Meta:
        model = 'Ceza'

    def __init__(self, current):
        self.ObjectForm = IdariCezaForm
        CrudView.__init__(self, current)
        if 'personel_id' not in self.current.task_data:
            self.current.task_data["personel_id"] = self.current.input["id"]

    def islem_turu_belirle(self):
        msg = ''
        if self.current.task_data['cmd'] == 'add_edit_form':
                if self.input.get('object_id',None):
                    self.current.task_data['title'] = _(u"Değişiklikleriniz Kaydedildi")
                    msg = "üzerinde yapılan değişiklikler başarıyla kaydedildi."
                else:
                    self.current.task_data['title'] = _(u"İdari Ceza Oluşturuldu")
                    msg = 'oluşturuldu.'

        elif self.current.task_data['cmd'] == 'delete':
            self.current.task_data['title'] = _(u"Silme İşlemi Başarılı")
            msg = "başarıyla silindi."

        self.current.task_data['msg'] = _(u"dosya sıra numaralı ceza kaydı %s") % (msg)

    def idari_ceza_sil_onay(self):
        form = JsonForm(title=_(u"İdari Ceza Silme İşlemi"))
        form.help_text = _(

u"""Ad Soyad: **%(ad)s** **%(soyad)s**

Dosya Sıra No: **%(dosya_sira_no)s**

Açılış Tarihi: **%(acilis_tarihi)s**

Başlama Tarihi: **%(baslama_tarihi)s**

Bitiş Tarihi: **%(bitis_tarihi)s**

Ceza Türü: **%(ceza_turu)s**

Bilgilerinin bulunduğu idari cezayı silme işlemini onaylıyor musunuz?"""
        ) % {'ad': self.object.personel.ad,
             'soyad': self.object.personel.soyad,
             'dosya_sira_no': self.object.dosya_sira_no,
             'acilis_tarihi': self.object.baslama_tarihi,
             'baslama_tarihi': self.object.baslama_tarihi,
             'bitis_tarihi': self.object.bitis_tarihi,
             'ceza_turu': self.object.get_takdir_edilen_ceza_display()}

        form.evet = fields.Button(__(u"Evet"), cmd='delete')
        form.hayir = fields.Button(__(u"Hayır"), cmd='iptal')
        self.form_out(form)
        self.current.task_data['personel_adi'] = self.object.personel.__unicode__()
        self.current.task_data['dosya_sira_no'] = self.object.dosya_sira_no

    def idari_ceza_kaydet(self):
        self.set_form_data_to_object()
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        self.current.task_data['personel_adi'] = personel.__unicode__()
        self.current.task_data['dosya_sira_no'] = self.object.dosya_sira_no
        self.object.personel = personel
        self.object.blocking_save()

    def islem_sonrasi_mesaj_goster(self):
        self.current.output['msgbox'] = {"type": "info",
                                         "title": self.current.task_data['title'],
                                         "msg": "%s personeline ait %s %s" % (
                                             self.current.task_data['personel_adi'],
                                             self.current.task_data['dosya_sira_no'],
                                             self.current.task_data['msg'])}

    def objeyi_cacheden_kaldir(self):
        if 'object_id' in self.current.task_data:
            del self.current.task_data['object_id']

    def idari_ceza_goruntule(self):
        obj_form = JsonForm(self.object, current=self.current, models=False)._serialize(
            readable=True)
        self.set_client_cmd('show')
        self.output['object_title'] = "%s : %s" % (self.model_class.Meta.verbose_name, self.object)
        self.output['object_key'] = self.object.key
        obj_data = {}
        for d in obj_form:
            key = six.text_type(d['title'])
            if d['type'] == 'ListNode' and d['value'] is not None:
                sorusturmacilar = [str(v['sorusturmaci_adi_soyadi']) for v in d['value']]
                obj_data[key] = ' - '.join(sorusturmacilar)
            else:
                obj_data[key] = d['value']

        form = JsonForm()
        form.tamam = fields.Button(__(u"Tamam"), cmd='iptal')
        self.form_out(form)
        self.output['object'] = obj_data

    @obj_filter
    def idari_ceza_islem(self, obj, result):
        result['actions'].extend([
            {'name': _(u'Görüntüle'), 'cmd': 'goruntule', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Sil'), 'cmd': 'delete', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'}
        ])

    @list_query
    def list_by_personel_id(self, queryset):
        return queryset.filter(personel_id=self.current.task_data['personel_id'])
