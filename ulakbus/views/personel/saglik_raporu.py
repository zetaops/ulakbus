# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView, obj_filter
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.models.personel import Personel


class SaglikRaporuForm(JsonForm):
    class Meta:
        exclude = ['personel', ]

    kaydet = fields.Button(__(u"Kaydet"))


class SaglikRaporuOlustur(CrudView):
    class Meta:
        model = 'SaglikRaporu'

    def __init__(self, current):
        self.ObjectForm = SaglikRaporuForm
        CrudView.__init__(self, current)
        if 'personel_id' not in self.current.task_data:
            self.current.task_data["personel_id"] = self.current.input["id"]

    def saglik_raporunu_sil_onay(self):
        form = JsonForm(title=_(u"Sağlık Raporu Silme İşlemi"))
        form.help_text = _(
            u"""Ad Soyad: **%(ad)s** **%(soyad)s**
            Başlama Tarihi: **%(baslama_tarihi)s**
            Bitiş Tarihi: **%(bitis_tarihi)s**
            Gün: **%(sure)s**
            Nereden: **%(nerden_alindigi)s**
            Rapor Çeşidi: **%(rapor_cesidi)s**
            Bilgilerin bulunduğu raporu silmek istiyor musunuz?"""
        ) % {'ad': self.object.personel.ad,
             'soyad': self.object.personel.soyad,
             'baslama_tarihi': self.object.baslama_tarihi,
             'bitis_tarihi': self.object.bitis_tarihi,
             'sure': self.object.sure,
             'nerden_alindigi': self.object.nerden_alindigi,
             'rapor_cesidi': self.object.get_rapor_cesidi_display()}
        form.evet = fields.Button(__(u"Evet"), cmd='delete')
        form.hayir = fields.Button(__(u"Hayır"))
        self.form_out(form)

    def delete(self):
        self.current.task_data['deleted_obj'] = self.object.key
        if 'object_id' in self.current.task_data:
            del self.current.task_data['object_id']
        self.object.delete()
        # self.current.output['msgbox'] = {"type": "info",
        #                                  "title": _(u"Sağlık Raporu Başarılı Bir Şekilde silindi."),
        #                                  "msg": "Silme işlemi gerçekleştirildi."}
        self.set_client_cmd('list')

    def saglik_raporunu_kaydet(self):
        self.set_form_data_to_object()
        self.object.personel = Personel.objects.get(self.current.task_data['personel_id'])
        self.object.save()
        self.current.output['msgbox'] = {"type": "info",
                                         "title": _(u"Sağlık Raporu Oluşturuldu"),
                                         "msg": _(u"%s %s adlı personelin %s günlük sağlık raporu oluşturuldu.") %
                                                 (self.object.personel.ad, self.object.personel.soyad,
                                                  self.object.sure)}

    @obj_filter
    def saglik_raporu_islem(self, obj, result):
        result['actions'].extend([
            {'name': _(u'Sil'), 'cmd': 'sil', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'}])
