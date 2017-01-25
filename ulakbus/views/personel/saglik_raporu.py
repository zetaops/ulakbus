# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.models.personel import Personel, SaglikRaporu


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

    def add_edit_form(self):
        if 'kontrol_msg' in self.current.task_data:
            msg = _(u"%s") % self.current.task_data['kontrol_msg']
            self.current.output['msgbox'] = {"type": "warning",
                                             "title": _(u"Hatalı Veri Girişi"),
                                             "msg": msg}
            del self.current.task_data['kontrol_msg']
            self.set_form_data_to_object()
        CrudView.add_edit_form(self)

    def saglik_raporunu_kaydet(self):

        personel = Personel.objects.get(self.current.task_data['personel_id'])

        saglik_raporlari = SaglikRaporu.objects.filter(personel=personel, rapor_cesidi=1)
        tek_hekim_rapor_sayisi = reduce(lambda x, y: x + y, [rapor.sure for rapor in saglik_raporlari], 0)

        self.set_form_data_to_object()
        self.object.personel = personel

        kontrol_msg = self.rapor_kontrol(tek_hekim_rapor_sayisi)

        if not kontrol_msg:
            self.object.save()
            self.current.task_data['object_id'] = self.object.key
            cmd = 'bilgilendir'
        else:
            self.current.task_data['kontrol_msg'] = kontrol_msg
            cmd = 'add_edit_form'

        self.current.task_data['cmd'] = cmd

    def bilgilendirme(self):
        # self.set_form_data_to_object()
        msg = _(u"%s %s adlı personelin %s başarılı bir şekilde kaydedildi.") % \
              (self.object.personel.ad, self.object.personel.soyad, self.object.get_rapor_cesidi_display())

        # Düzenleme işleminden sonra yeni bir kayit eklemek istediğimizde,
        # form ekranı düzenlenen modelin bilgileriyle
        # geliyor. Bunu önlemek için aşağıdaki çözümü uyguladık
        if 'object_id' in self.current.task_data:
            del self.current.task_data['object_id']

        form = JsonForm(title=_(u"Sağlık Raporu"))
        form.help_text = msg
        form.raporlar = fields.Button(_(u"Raporlar"))
        self.form_out(form)

    @obj_filter
    def saglik_raporu_islem(self, obj, result):
        result['actions'].extend([
            {'name': _(u'Sil'), 'cmd': 'sil', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'}])

    @list_query
    def list_by_personel_id(self, queryset):
        return queryset.filter(personel_id=self.current.task_data['personel_id'])

    def rapor_kontrol(self, rapor_sayisi):
        """
        Formda girilen gun ve darihleri kontrol eder.
        Args:
            rapor_sayisi: rapor cesidi tek hekim olan raporlarin sayisi

        Returns: str ("Gun negetif deger alamaz")

        """
        kontrol_msg = ''

        if self.object.sure <= 0:
            kontrol_msg = _(u'Gün sayısı 0 veya negatif bir değer alamaz!')
        elif self.object.baslama_tarihi > self.object.bitis_tarihi:
            kontrol_msg = _(u'Başlangıç tarihi bitiş tarihinden büyük olmamalıdır!')
        elif not (self.object.bitis_tarihi - self.object.baslama_tarihi).days + 1 == self.object.sure:
            kontrol_msg = _(u'Gün süresi ile tarih aralıkları eşleşmiyor!')

        if self.object.rapor_cesidi == 1 and not kontrol_msg:
            if self.object.sure > 10:
                kontrol_msg = _(u'%s süresi 10 günden fazla olamaz!') % self.object.get_rapor_cesidi_display()
            elif rapor_sayisi + self.object.sure > 40:
                kontrol_msg = _(u'% s için yıl içerisinde 40 günden fazla rapor alamazsınız!') \
                              % self.object.get_rapor_cesidi_display()

        return kontrol_msg
