# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.common import prepare_options_from_catalog_data
from ulakbus.settings import DATE_DEFAULT_FORMAT
from pyoko.lib.utils import un_camel
from ulakbus.models import Personel
from zengine.views.crud import CrudView, list_query, obj_filter
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
import six


class HitapBilgileriForm(JsonForm):
    """
    
    """

    class Meta:
        title = _(u"Hitap {} Bilgileri")

    sync = fields.Button(_(u"Hitap İle Senkronize Et"), cmd='sync')
    geri_don = fields.Button(_(u"Geri Dön"), cmd='geri_don')


class IslemSecimForm(JsonForm):
    """
    
    """

    class Meta:
        title = _(u"İşlem Seçeneği")

    degisiklik = fields.Button(_(u"Değişiklik Ekranı"), cmd='degisiklik')
    hitap_bilgileri = fields.Button(_(u"Hitap Bilgileri"), cmd='hitap_bilgileri')


class HitapIslemleri(CrudView):
    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.model = self.model_class
        if 'id' in self.input:
            self.current.task_data['personel_id'] = self.input['id']
            self.current.task_data['personel_tckn'] = Personel.objects.get(self.input['id']).tckn
        self.personel_id = self.current.task_data['personel_id']

    def islem_secim(self):
        """
        Hitap ile senkronize etme ve hitapa değişiklik gönderme ekranlarından birisinin seçilmesi
        beklenir.
        """
        # Tab'li yapı implementasyonu yapılacaktır.
        self.form_out(IslemSecimForm(current=self.current))

    def get_columns(self):
        columns = []
        for field_name in self.model.Meta.list_fields:
            model_field = self.model._fields[field_name]
            field = model_field.name
            type = 'select' if model_field.choices else model_field.solr_type
            choices = prepare_options_from_catalog_data(
                model_field.choices) if type == 'select' else []
            title = model_field.title

            columns.append({'field': field,
                            'title': six.text_type(title),
                            'type': type,
                            'choices': choices
                            })
        return columns

    def get_initial_data(self):
        initial_data = []
        for obj in self.model.objects.filter(personel_id=self.personel_id):
            list_fields = self.model.Meta.list_fields
            field_dict = {field: self.get_field_as_str(obj, field) for field in list_fields}
            field_dict.update({'key': obj.key, 'sync': obj.sync})
            initial_data.append(field_dict)
        return initial_data

    def get_field_as_str(self, obj, field_name):
        field = self.model._fields[field_name]
        type = 'select' if field.choices else field.solr_type

        if type == 'select':
            display = getattr(obj, "get_{}_display".format(field_name))()
            return display if display else ""

        obj_field = getattr(obj, field_name)
        if type == 'date':
            return obj_field.strftime(DATE_DEFAULT_FORMAT) if obj_field else ""

        return str(obj_field) if obj_field else ""

    def degisiklik_ekrani_hazirla(self):
        grid_data = {'read_only_fields': ['tckn', 'kayit_no', 'son_senkronize_tarihi'],
                     'hidden_fields': ['key', 'sync'],
                     'columns': self.get_columns(),
                     'initial_data': self.get_initial_data()
                     }
        self.output['grid_data'] = grid_data

    def tekil_sync_bilgi_hazirla(self):
        self.current.task_data['hitap_islemleri']['tekil_sync'] = 'Dto0uUbtn2zVSHw1f6HAeqKFL95'

    def hitapa_gonder(self):
        """
        Yerelden hitapa gönderilecek kayıtlar için servisler çağırılır. Silinecek olan servisler için
        hitap_delete, yeni veya güncellenecek kayıtlar için hitap_save servisi çağırılır.
    
        """

        self.get_columns()
        service_name = un_camel(self.model_class.__name__, dash='-')

        # UI Grid ile beraber aşağı taraf düzeltilecektir. Test etmek için yazılmıştır.

        hitap_kayitlar = self.model.objects.filter(personel_id=self.personel_id, sync__in=[2, 3, 4])
        for kayit in hitap_kayitlar:
            kayit.tckn = str(self.current.task_data['personel_tckn'])
            kayit.blocking_save()
            args = [kayit, service_name]
            kwargs = {'meta': self.meta, 'index_fields': self.index_fields}
            # hitap_delete(*args, **kwargs) if kayit.sync == 3 else hitap_save(*args, **kwargs)

            if 'object_id' in self.current.task_data:
                del self.current.task_data['object_id']

    def hitap_bilgileri_goster(self):
        """
        Yerelde bulunan en son senkronize edilmiş bilgiler gösterilir. Hitap ile senkronize et
        butonuna basıldığında senkronize servis çağrısı gerçekleşir.
        """
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_search"] = False
        form = HitapBilgileriForm(current=self.current)
        form.title = form.title.format(six.text_type(self.model.Meta.verbose_name))
        self.list(custom_form=form)

    def sync_bilgi_hazirla(self):
        self.current.task_data['hitap_islemleri']['sync'] = True

    def islem_mesaji_olustur(self):
        """
        Senkronizasyon işlemi gerçekleştikten sonra başarılı işlem mesajı oluşturulur.
        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'İşlem Başarılı'),
            "msg": _(u'Kayıtlar Hitap ile başarıyla senkronize edildi.')
        }

        @list_query
        def list_by_personel_id(self, queryset):
            return queryset.filter(personel_id=self.personel_id, sync=1)
