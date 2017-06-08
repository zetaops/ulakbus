#!/usr/bin/env python
# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import base64
import csv
from datetime import datetime
from io import BytesIO
from settings import DATA_GRID_PAGE_SIZE, DATE_DEFAULT_FORMAT
from ulakbus.lib.common import get_file_url
from pyoko.fields import DATE_FORMAT
from ulakbus.lib.s3_file_manager import S3FileManager
from zengine.lib.cache import Cache
from zengine.lib.translation import gettext as _
from collections import OrderedDict

__author__ = 'Anıl Can Aydın'


class GridCache(Cache):
    """

    """
    PREFIX = "GRIDCACHE"

    def __init__(self, key):
        super(GridCache, self).__init__(":".join(['grid_cache', key]))


class GridQueryCache(Cache):
    """

    """
    PREFIX = "GRIDQUERYCACHE"

    def __init__(self, key):
        super(GridQueryCache, self).__init__(":".join(['grid_query_cache', key]))


class DataGrid(object):
    def __init__(self, cache_key, model, page, filter_params, sort_params, columns, selectors=None,
                 **kwargs):
        self.model = model
        self.grid_cache = GridCache(cache_key)
        self.grid_cache_data = self.grid_cache.get() or {}
        self.page = page
        self.filter_params = filter_params
        self.sort_params = sort_params
        self.columns = columns
        self.default_fields = kwargs.get('default_fields', [])
        self.column_types_dict = kwargs.get('column_types_dict', {})

        self.selectors = selectors or self.grid_cache_data.get('selectors',
                                                               self.prepare_selectors())
        self.filter_conditions = {
            # STARTS_WITH
            2: '__startswith',
            # ENDS_WITH
            4: '__endswith',
            # EXACT
            8: '',
            # CONTAINS
            16: '__contains',
            # GREATER_THAN
            32: '__gt',
            # GREATER_THAN OR EQUAL
            64: '__gte',
            # LESS_THAN
            128: '__lt',
            # LESS_THAN OR EQUAL
            256: '__lte',
            # NOT_EQUAL
            512: ''
        }

        self.select_fields = self.column_types_dict.get('select_fields', {})
        self.multiselect_fields = self.column_types_dict.get('multiselect_fields', {})
        self.range_date_fields = self.column_types_dict.get('range_date_fields', [])

        self.field_filter_type_map = self.grid_cache_data.get('field_filter_type_map', {})
        self.select_options_dict = self.grid_cache_data.get('select_options_dict', {})
        self.column_defs = self.grid_cache_data.get('column_defs', self.prepare_column_defs())

        self.grid_cache.set(
            {
                'selectors': self.selectors,
                'column_defs': self.column_defs,
                'field_filter_type_map': self.field_filter_type_map,
                'select_options_dict': self.select_options_dict
            }
        )

    def prepare_column_defs(self):
        contains_fields = self.column_types_dict.get('contains_fields', [])
        ends_fields = self.column_types_dict.get('ends_fields', [])
        starts_fields = self.column_types_dict.get('starts_fields', [])
        range_num_fields = self.column_types_dict.get('range_num_fields', [])

        column_defs = []
        for col, label in self.columns.items():
            col_def = {}
            col_def['field'] = col
            if col in contains_fields:
                col_def['type'] = "INPUT"
                col_def['filter'] = {
                    'condition': "CONTAINS",
                    'placeholder': _(u"İçeren")
                }
                self.field_filter_type_map[col] = "INPUT"
            elif col in ends_fields:
                col_def['type'] = "INPUT"
                col_def['filter'] = {
                    'condition': "ENDS_WITH",
                    'placeholder': _(u"Biten")
                }
                self.field_filter_type_map[col] = "INPUT"
            elif col in starts_fields:
                col_def['type'] = "INPUT"
                col_def['filter'] = {
                    'condition': "STARTS_WITH",
                    'placeholder': _(u"Başlayan")
                }
                self.field_filter_type_map[col] = "INPUT"
            elif col in self.select_fields:
                col_def['type'] = 'SELECT'
                col_def['filter'] = {
                    'selectOptions': self.select_fields[col]
                }
                self.field_filter_type_map[col] = "SELECT"
                self.select_options_dict[col] = self._swith_to_dict_from_select_options(
                    self.select_fields[col])
            elif col in self.multiselect_fields:
                col_def['type'] = 'MULTISELECT'
                col_def['filter'] = {
                    'selectOptions': self.multiselect_fields[col]
                }
                self.field_filter_type_map[col] = "MULTISELECT"
                self.select_options_dict[col] = self._swith_to_dict_from_select_options(
                    self.multiselect_fields[col])
            elif col in self.range_date_fields:
                col_def['type'] = 'range'
                col_def['rangeType'] = 'datetime'
                filter_s = {
                    'condition': "START",
                    'placeholder': _(u"Başlangıç")
                }
                filter_e = {
                    'condition': "END",
                    'placeholder': _(u"Bitiş")
                }
                col_def['filters'] = [filter_s, filter_e]
                self.field_filter_type_map[col] = "RANGE-DATETIME"
            elif col in range_num_fields:
                col_def['type'] = "range"
                col_def['rangeType'] = "integer"
                filter_s = {
                    'condition': "MAX",
                    'placeholder': _(u"En çok")
                }
                filter_e = {
                    'condition': "MIN",
                    'placeholder': _(u"En az")
                }
                col_def['filters'] = [filter_s, filter_e]
                self.field_filter_type_map[col] = "RANGE-INTEGER"
            column_defs.append(col_def)
        return column_defs

    def prepare_selectors(self):
        selectors = []
        for col, lbl in self.columns.items():
            select = {
                'name': col,
                'label': lbl,
                'checked': True if col in self.default_fields else False
            }
            selectors.append(select)
        return selectors

    def build_response(self):
        import json
        import hashlib

        cache_key = hashlib.sha256(
            "%s%s%s%s" % (
                self.page,
                json.dumps(self.filter_params),
                json.dumps(self.sort_params),
                json.dumps(self.selectors),
            )

        ).hexdigest()

        cache_key = hashlib.sha256(cache_key).hexdigest()

        query_cache = GridQueryCache(cache_key)
        cached_response = query_cache.get()
        if cached_response:
            return cached_response
        else:
            is_more_data_left, data = self.prepare_data()
            response = {
                'gridOptions': {
                    'applyFilter': "Filtrele",
                    'cancelFilter': "Filtreleri Temizle",
                    'csvDownload': "Dışa Aktar",
                    'dataLoading': "Yükleniyor",
                    'selectColumns': "Kolon Seç",

                    'enableSorting': True,
                    'enableFiltering': True,
                    'toggleFiltering': True,
                    'enableRemoving': True,

                    'isMoreDataLeft': is_more_data_left,
                    'selectors': self.selectors,
                    'column_defs': self.column_defs,
                    'data': data

                }
            }
            return query_cache.set(response)

    def grid_query_parser(self):
        query_params = {}
        sort_params = []
        fc = self.filter_conditions
        for element in self.filter_params:
            f = element['columnName']
            qp = element['filterParam']
            if qp:
                if self.field_filter_type_map[f] == "INPUT":
                    query_params[f + fc.get(qp[0]['condition'])] = qp[0]['value'].lower()

                elif self.field_filter_type_map[f] == "SELECT":
                    query_params[f] = qp[0]['value']

                elif self.field_filter_type_map[f] == "MULTISELECT":
                    multiselect_list = qp[0]['value']
                    query_params[f + "__in"] = multiselect_list

                else:
                    start = end = ""
                    for item in qp:
                        if fc[item['condition']] == '__gt':
                            start = item['value']
                        if fc[item['condition']] == '__lt':
                            end = item['value']
                    if self.field_filter_type_map[f] == "RANGE-DATETIME":
                        start = datetime.strptime(start, DATE_DEFAULT_FORMAT)
                        end = datetime.strptime(end, DATE_DEFAULT_FORMAT)
                    else:
                        start, end = int(start, end)
                    query_params[f + '__range'] = [start, end]
        for col in self.sort_params:
            if col['order'] == 'desc':
                sort_params.append("%s%s" % ("-", col['columnName']))
            else:
                sort_params.append(col['columnName'])
        return query_params, sort_params

    def prepare_data(self, csv=False):
        page_size = DATA_GRID_PAGE_SIZE
        query_params, sort_params = self.grid_query_parser()
        active_columns = []

        for col in self.selectors:
            if col['checked']:
                active_columns.append(col['name'])

        data_size = self.model.objects.all(**query_params).count()
        if not csv:
            qs = self.model.objects.set_params(start=(self.page - 1) * page_size, rows=page_size)
        else:
            qs = self.model.objects

        data_to_return = []
        for data, key in qs.all(**query_params).order_by(*sort_params).data():
            d = OrderedDict()
            for ac in active_columns:
                if ac in self.select_fields or ac in self.multiselect_fields:
                    d[ac] = self.select_options_dict[ac][str(data[ac])]
                elif ac in self.range_date_fields:
                    d[ac] = datetime.strftime(
                        datetime.strptime(data[ac], DATE_FORMAT).date(), DATE_DEFAULT_FORMAT)
                else:
                    d[ac] = data[ac]
            data_to_return.append(d)

        is_more_data_left = data_size / page_size > (self.page - 1)

        return is_more_data_left, data_to_return

    def generate_csv_link(self):
        output = BytesIO()
        csv_writer = csv.writer(output, delimiter=';', quotechar="'", quoting=csv.QUOTE_MINIMAL)

        is_more_data_left, data = self.prepare_data(csv=True)

        count = 0
        for emp in data:
            if count == 0:
                header = emp.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(emp.values())

        download_url = self._generate_temp_file(
            name=self._generate_file_name(),
            content=base64.b64encode(output.getvalue()),
            file_type='text/csv',
            ext='csv'
        )

        return download_url

    @staticmethod
    def _generate_temp_file(name, content, file_type, ext):
        f = S3FileManager()
        key = f.store_file(name=name, content=content, type=file_type, ext=ext)
        return get_file_url(key)

    def _generate_file_name(self):
        return "%s-%s-%s" % (self.model().get_verbose_name(), _(u"rapor"), datetime.now().strftime(
            "%d.%m.%Y-%H.%M.%S"))

    @staticmethod
    def _swith_to_dict_from_select_options(sel_opts):
        sd = {}
        for so in sel_opts:
            sd[str(so['value'])] = so['label']
        return sd
