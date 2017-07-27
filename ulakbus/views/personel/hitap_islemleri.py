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


# class ListFormHitap(JsonForm):
#     """
#     Hitapa Gönder eklenmis list view formu.
#     """
#     gonder = fields.Button(_(u"New"), cmd="gonder")


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
        # self.ListForm = ListFormHitap
        self.model = self.model_class
        if 'id' in self.input:
            self.current.task_data['personel_id'] = self.input['id']
            self.current.task_data['personel_tckn'] = Personel.objects.get(self.input['id']).tckn
        self.personel_id = self.current.task_data['personel_id']

        # self.meta = {'user': self.current.user_id,
        #              'role': self.current.role_id,
        #              'wf_name': self.current.workflow_name,
        #              # 'model_name': self.model.__name__,
        #              'personel': self.personel_id
        #              }
        #
        # self.index_fields = [('user', 'bin'), ('role', 'bin'), ('wf_name', 'bin'),
        #                      ('model_name', 'bin'), ('personel', 'bin')]

    def islem_secim(self):
        """
        Hitap ile senkronize etme ve hitapa değişiklik gönderme ekranlarından birisinin seçilmesi
        beklenir.
        """
        # Tab'li yapı implementasyonu yapılacaktır.
        self.form_out(IslemSecimForm(current=self.current))

    def get_columns(self):
        from ulakbus.views.reports import personel_genel_raporlama
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
            field_dict['key'] = obj.key
            field_dict['sync'] = obj.sync
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
                     'columns': self.get_columns(),
                     'initial_data': self.get_initial_data()
                     }
        self.output['grid_data'] = grid_data

    # def kaydet(self):
    #     """
    #     Gelen nesnenin kayit_no field'ı boş ise hitapa hiç gitmemiş demektir ve yeni bir kayıttır.
    #     Değişiklikler kaydedilir ve sync field'ı yeni kayıt anlamına gelen 2 yapılır. kayit_no
    #     fieldı mevcut ise hitapta va demektir, değişiklikler kaydedilir ve sync'i güncellenecek
    #     anlamına gelen 4 yapılır.
    #     """
    #     # self.set_form_data_to_object()
    #     self.object.sync = 4 if self.object.kayit_no else 2
    #     self.object.blocking_save(meta=self.meta, index_fields=self.index_fields)

    # def sil(self):
    #     """
    #     Silinmek istenen kayıt yeni kayıt ise direk silinir, mevcut bir kayıt ise sync'i silinecek
    #     kayıt anlamına gelen 3 yapılır.
    #     """
    #     if not self.object.kayit_no:
    #         self.object.blocking_delete(meta=self.meta, index_fields=self.index_fields)
    #     else:
    #         self.object.sync = 3
    #         self.object.blocking_save(meta=self.meta, index_fields=self.index_fields)

    # def hitaptaki_kaydi_getir(self):
    #     # Tekil hitaptaki kaydı getirip yereldeki datayı onunla değiştirecek servis yapılacaktır.
    #     pass

    # def create_grid_json(self):
    #     pass
    #
    # grid_data = {
    #     'columns': [
    #         {'field': 'tckn', 'title': 'TC Kimlik No', 'type': 'input', 'editable': False,
    #          'choices': None},
    #         {'field': 'kayit_no', 'title': 'Kursa Kayıt No', 'type': 'input', 'editable': False,
    #          'choices': None},
    #         {'field': 'mezuniyet_tarihi', 'title': 'Terfi Tarihi', 'type': 'date', 'editable': True,
    #          'choices': None},
    #         {'field': 'okul_ad', 'title': 'Okul Adı', 'type': 'select', 'editable': True,
    #          'choices': [
    #              {"value": 1, "label": "MIT"}, {"value": 2, "label": "IZTECH"}
    #          ]
    #          },
    #         {'field': 'son_senkronize_tarihi', 'title': 'Son Senkronize Tarihi', 'type': 'datetime',
    #          'editable': False, 'choices': None},
    #
    #     ],
    #     'initial_data': [
    #         {'key': '21hso1j129389102iek', 'tckn': '98548836369', 'kayit_no': "325",
    #          'mezuniyet_tarihi': '18.04.2012', 'okul_ad': "MIT",
    #          'son_senkronize_tarihi': '21.07.2017 07:45:03'},
    #         {'key': 'asbdjsa7dsak0323224', 'tckn': '52328727230', 'kayit_no': "964",
    #          'mezuniyet_tarihi': '20.05.2010', 'okul_ad': "IZTECH",
    #          'son_senkronize_tarihi': '15.05.2017 21:12:20'},
    #     ]
    # }

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
        self.list()
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_search"] = False
        model_adi = six.text_type(self.model.Meta.verbose_name)
        form = JsonForm(title=_(u"Hitap %s Bilgileri") % model_adi)

        form.senkronize = fields.Button(_(u"Hitap İle Senkronize Et"), cmd='sync')
        self.form_out(form)

    def servis_adi_belirle(self):
        self.current.task_data['hitap_operation'] = 'sync'

    def islem_mesaji_olustur(self):
        """
        Senkronizasyon işlemi gerçekleştikten sonra başarılı işlem mesajı oluşturulur.
        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'İşlem Başarılı'),
            "msg": _(u'Kayıtlar Hitap ile başarıyla senkronize edildi.')
        }

    # grid_data = {
    #     'columns': [
    #         {'field': 'tckn', 'title': 'TC Kimlik No', 'type': 'input', 'editable': False,
    #          'choices': None},
    #         {'field': 'kayit_no', 'title': 'Kursa Kayıt No', 'type': 'input', 'editable': False,
    #          'choices': None},
    #         {'field': 'mezuniyet_tarihi', 'title': 'Terfi Tarihi', 'type': 'date', 'editable': True,
    #          'choices': None},
    #         {'field': 'okul_ad', 'title': 'Okul Adı', 'type': 'select', 'editable': True,
    #          'choices': [
    #              {"value": 1, "label": "MIT"}, {"value": 2, "label": "IZTECH"}
    #          ]
    #          },
    #         {'field': 'son_senkronize_tarihi', 'title': 'Son Senkronize Tarihi', 'type': 'datetime',
    #          'editable': False, 'choices': None},
    #
    #     ],
    #     'initial_data': [
    #         {'key': '21hso1j129389102iek', 'tckn': '98548836369', 'kayit_no': "325",
    #          'mezuniyet_tarihi': '18.04.2012', 'okul_ad': "MIT",
    #          'son_senkronize_tarihi': '21.07.2017 07:45:03'},
    #         {'key': 'asbdjsa7dsak0323224', 'tckn': '52328727230', 'kayit_no': "964",
    #          'mezuniyet_tarihi': '20.05.2010', 'okul_ad': "IZTECH",
    #          'son_senkronize_tarihi': '15.05.2017 21:12:20'},
    #     ]
    # }




    # {'name': _(u'Kaydet'), 'cmd': 'save', 'mode': 'normal', 'show_as': 'button'}
    @obj_filter
    def hitap_islemleri(self, obj, result):
        result['actions'] = [
            {'name': _(u'Delete'), 'cmd': 'delete', 'mode': 'normal', 'show_as': 'button'},
        ]

    @list_query
    def list_by_personel_id(self, queryset):
        return queryset.filter(personel_id=self.personel_id, sync=1)
