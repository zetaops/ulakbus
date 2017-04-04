# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.cache import HitapPersonelGirisBilgileri
from ulakbus.models import Personel
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy
import six


class ListFormHitap(JsonForm):
    """
    HITAP Sync eklenmis list view formu.
    """
    add = fields.Button(gettext_lazy(u"Ekle"), cmd="add")
    gonder = fields.Button(gettext_lazy(u"Hitap'a Gönder"), cmd="gonder")


class HitapIslemleri(CrudView):
    def __init__(self, current=None):
        super(HitapIslemleri, self).__init__(current)
        self.ListForm = ListFormHitap
        if 'id' in self.input:
            self.current.task_data['personel_id'] = self.input['id']
            self.current.task_data['personel_tckn'] = Personel.objects.get(self.input['id']).tckn

    def hitap_bilgileri_kontrol(self):

        self.current.task_data['hitap_bilgileri'] = False
        if HitapPersonelGirisBilgileri(self.current.task_data['personel_id']).get():
            self.current.task_data['hitap_bilgileri'] = True
            if 'giris_bilgileri' not in self.current.task_data:
                personel_id = self.current.task_data['personel_id']
                giris_bilgileri = HitapPersonelGirisBilgileri(personel_id).get()
                self.current.task_data['giris_bilgileri'] = giris_bilgileri

    def hitap_bilgileri_isteme(self):
        form = JsonForm(title=_(u"Hitap Servisi Giriş Bilgileri"))
        form.help_text = _(u"Bu iş akışı hitap servisine bağlanmayı gerektirmektedir. Lütfen "
                           u"Hitap kullanıcı adı ve parola bilgilerinizi giriniz. Girdiğiniz bilgiler"
                           u" sistemimizde iki saat tutulduktan sonra silinecektir. Böylelikle iki "
                           u"saat içerisinde yapacağınız HİTAP işlemlerinde sizden şifre istenmeyecektir.")

        form.hitap_k_adi = fields.String(_(u"Hitap kullanıcı adınızı giriniz."))
        form.hitap_parola = fields.String(_(u"Hitap parolanızı giriniz."), type="password")
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def hitap_giris_bilgileri_kontrol(self):
        # Giriş bilgileriyle servis call yapılıp giriş bilgileri kontrol edilecek.
        self.current.task_data['hitap_bilgi_kontrol'] = True

    def hitap_giris_bilgileri_hata_mesaji_uret(self):
        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'Hatalı Hitap Giriş Bilgileri'),
            "msg": _(u'Hitap giriş bilgileriniz hatalıdır. Lütfen kontrol ederek tekrar deneyiniz.')
        }

    def hitap_bilgileri_cache_kaydet(self):
        personel_id = self.current.task_data['personel_id']
        k_adi = self.input['form']['hitap_k_adi']
        parola = self.input['form']['hitap_parola']
        giris_bilgileri = {'k_adi': k_adi, 'parola': parola}
        HitapPersonelGirisBilgileri(personel_id).set(giris_bilgileri, 30)

    def hitap_bilgileri_task_data_kaydet(self):
        personel_id = self.current.task_data['personel_id']
        giris_bilgileri = HitapPersonelGirisBilgileri(personel_id).get()
        self.current.task_data['giris_bilgileri'] = giris_bilgileri

    def islem_secim(self):
        form = JsonForm(title=_(u"İşlem Seçeneği"))
        form.degisiklik = fields.Button(_(u"Değişiklik Ekranı"), cmd='degisiklik')
        form.hitap_bilgileri = fields.Button(_(u"Hitap Bilgileri"), cmd='hitap_bilgileri')
        self.form_out(form)

    def listele(self):
        # Sync durumuna göre renklendirme yapılacak.
        personel_id = self.current.task_data['personel_id']
        model = self.model_class

        sync = model.objects.filter(personel_id=personel_id, sync=1)
        updated = model.objects.filter(personel_id=personel_id, sync=2)
        deleted = model.objects.filter(personel_id=personel_id, sync=3)
        new_record = model.objects.filter(personel_id=personel_id, sync=4)

    def hitap_bilgileri_goster(self):
        self.list()
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_search"] = False

        model_adi = six.text_type(self.model_class.Meta.verbose_name)
        form = JsonForm(title=_(u"Hitap %s Bilgileri") % model_adi)
        kayitlar = self.list_by_personel_id(self.model_class.objects)
        if kayitlar:
            form.help_text = _(u"Son Senkronize Tarihi: %s" % kayitlar[0].son_senkronize_tarihi)
        form.senkronize = fields.Button(_(u"Hitap İle Senkronize Et"), cmd='sync')
        self.form_out(form)

    def islem_mesaji_olustur(self):
        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'İşlem Başarılı'),
            "msg": _(u'Kayıtlar Hitap ile başarıyla senkronize edildi.')
        }

    def save(self):
        # 2 updated, 4 new record
        self.object.sync = 2 if self.object.is_in_db() else 4
        self.object.save()

    def delete(self):
        # 3 deleted
        self.object.sync = 3
        self.object.save()

    # def ekle(self):
    #     obj = self.model_class()
    #     list_obj = self._parse_object_actions(obj)
    #     for i in range(len(list_obj['fields'])):
    #         list_obj['fields'][i] = ''
    #     list_obj['actions'] = sorted(list_obj['actions'], key=lambda x: x.get('name', ''))
    #     self.output['objects'].append(list_obj)

    # @obj_filter
    # def hitap_islemleri_buton_edit(self, obj, result):
    #     del result['actions'][0]
    #     result['actions'].extend([
    #         {'name': _(u'Kaydet'), 'cmd': 'save', 'mode': 'normal', 'show_as': 'button'}
    #     ])

    @list_query
    def list_by_personel_id(self, queryset):
        return queryset.filter(personel_id=self.current.task_data['personel_id'], sync=1)
