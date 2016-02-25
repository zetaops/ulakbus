# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'evren kutar'

from pyoko.db.connection import client
from pyoko import Model, field, ListNode
from zengine.views.crud import CrudView, form_modifier
from zengine import forms
from zengine.forms import fields


class CatalogSelectForm(forms.JsonForm):
    class Meta:
        title = 'Katalog Data Seç'
        help_text = "Düzenlemek istediğiniz katalog data başlığını giriniz."

    katalog = fields.Integer("Kataloglar", type='typeahead')
    duzenle = fields.Button("Düzenle", cmd="get_catalog")

class CatalogEditForm(forms.JsonForm):
    kaydet = fields.Button("Kaydet", cmd="save_catalog", flow="list_catalogs")
    class CatalogDatas(ListNode):
        deger = fields.String("Değer")
        tr = fields.String("Türkçe")
        en = fields.String("English")


fixture_bucket = client.bucket_type('catalog').bucket('ulakbus_settings_fixtures')
fixtures = [{"value": i, "name": i} for i in fixture_bucket.get_keys()]

class CatalogModel(Model):
    catalog = field.Integer('catalog')


class CatalogDataView(CrudView):
    class Meta:
        model = 'User'

    def list_catalogs(self):
        self.form_out(CatalogSelectForm(current=self.current))

    def get_catalog(self):
        catalog_data = fixture_bucket.get(self.input['form']['katalog']).data
        catalog_edit_form = CatalogEditForm(current=self.current, title='%s katalog data düzenle' % self.input['form']['katalog'])
        if type(catalog_data) == list:
            # if catalog data is an array it means no other language of value defined, therefor the value is turkish
            for key, data in enumerate(catalog_data):
                catalog_edit_form.CatalogDatas(deger=key, en='', tr=data)
        if type(catalog_data) == dict:
            for key, data in catalog_data.items():
                catalog_edit_form.CatalogDatas(deger=key, en=data['en'], tr=data['tr'])

        self.form_out(catalog_edit_form)
        self.output["meta"]["allow_actions"] = False
        self.output["meta"]["allow_selection"] = False

    def save_catalog(self):
        # self.current.request
        self.output['success'] = True

    @form_modifier
    def change_form_elements(self, serialized_form):
        if 'katalog' in serialized_form['schema']['properties']:
            serialized_form['schema']['properties']['katalog']['titleMap'] = fixtures
        if 'CatalogDatas' in serialized_form['schema']['properties']:
            serialized_form['inline_edit'] = ['tr', 'en']
