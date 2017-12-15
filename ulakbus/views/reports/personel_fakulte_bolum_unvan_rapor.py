# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import OrderedDict

from ulakbus.lib.data_grid import DataGrid
from ulakbus.settings import DATA_GRID_PAGE_SIZE

from ulakbus.models import Personel
from ulakbus.models.auth import Unit
from ulakbus.models import Kadro
from ulakbus.models import Atama
from zengine.lib.catalog_data import catalog_data_manager
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _

from zengine.lib.cache import Cache

unvanlar = catalog_data_manager.get_all_as_dict('unvan_kod')

unvan_choices = [
    {"name": unvanlar[1550], "value": 1550},
    {"name": unvanlar[1555], "value": 1555},
    {"name": unvanlar[1565], "value": 1565},
    {"name": unvanlar[1590], "value": 1590},
]


class AkademikDataGridCache(Cache):
    """

    """
    PREFIX = "AKADEMIKGRIDCACHE"

    def __init__(self, key):
        super(AkademikDataGridCache, self).__init__(":".join(['grid_cache', key]))


class AkademikDataGridQueryCache(Cache):
    """

    """
    PREFIX = "AKADEMIKGRIDQUERYCACHE"

    def __init__(self, key):
        super(AkademikDataGridQueryCache, self).__init__(":".join(['grid_query_cache', key]))


class AkademikDataGrid(DataGrid):
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

        query_cache = self.grid_query_cache(cache_key)
        cached_response = query_cache.get()

        fakulte_filter_param = None
        if self.filter_params and self.filter_params[0]['columnName'] == 'fakulte' and \
                self.filter_params[0]['filterParam']:
            fakulte_filter_param = self.filter_params[0]

        def responser(self):
            is_more_data_left, data = self.prepare_data()
            return is_more_data_left, {
                'gridOptions': {
                    'applyFilter': "Filtrele",
                    'cancelFilter': "Filtreleri Temizle",
                    'csvDownload': "Dışa Aktar",
                    'dataLoading': "Yükleniyor",
                    'selectColumns': "Kolon Seç",

                    'enableSorting': False,
                    'enableFiltering': True,
                    'toggleFiltering': True,
                    'enableRemoving': False,

                    'isMoreDataLeft': is_more_data_left,
                    'selectors': self.selectors,
                    'column_defs': self.column_defs,
                    'data': data

                }
            }

        if cached_response:
            return cached_response
        else:

            final_return_value = query_cache.set(responser(self)[1])

            bolumler = []
            for col_def in self.column_defs:
                if col_def['field'] == 'bolum':
                    bolumler = col_def['filter']['selectOptions']
            for b in bolumler:
                # Bolumler icin dataları hazırlar
                self.page = 1
                self.filter_params = [
                    {
                        "columnName": "fakulte",
                        "filterParam": [],
                        "columnType": "SELECT"
                    },
                    {
                        "columnName": "bolum",
                        "filterParam": [
                            OrderedDict([("condition", 8), ("value", b['value'])])],
                        "columnType": "SELECT"
                    },
                    {"columnName": "unvan", "filterParam": [], "columnType": "SELECT"},
                    {"columnName": "ad", "filterParam": [], "columnType": "INPUT"},
                    {"columnName": "soyad", "filterParam": [], "columnType": "INPUT"}]

                cache_key = hashlib.sha256(
                    "%s%s%s%s" % (
                        self.page,
                        json.dumps(self.filter_params),
                        json.dumps(self.sort_params),
                        json.dumps(self.selectors),
                    )

                ).hexdigest()
                cache_key = hashlib.sha256(cache_key).hexdigest()
                query_cache = self.grid_query_cache(cache_key)
                self.filter_params[0] = fakulte_filter_param or self.filter_params[0]
                is_more_data_left, response = responser(self)
                query_cache.set(response)
                while is_more_data_left:
                    self.page += 1
                    cache_key = hashlib.sha256(
                        "%s%s%s%s" % (
                            self.page,
                            json.dumps(self.filter_params),
                            json.dumps(self.sort_params),
                            json.dumps(self.selectors),
                        )

                    ).hexdigest()
                    cache_key = hashlib.sha256(cache_key).hexdigest()
                    query_cache = self.grid_query_cache(cache_key)
                    is_more_data_left, response = responser(self)
                    query_cache.set(response)

            return final_return_value

    def prepare_data(self, csv=False):
        page_size = DATA_GRID_PAGE_SIZE
        query_params, sort_params = self.grid_query_parser()

        if 'unvan' not in query_params:
            query_params['unvan__in'] = [1550, 1555, 1565, 1590]

        if 'fakulte' not in query_params:
            query_params['fakulte'] = self.select_options_dict['fakulte'].keys()[0]

        # Secilen fakulte icin bolum secenekleri guncellenir.
        for i, col in enumerate(self.column_defs):
            if col['field'] == 'bolum':
                # col['filter']['selectOptions'] = [
                #     {"value": bol.yoksis_no, "label": bol.name} for bol in
                #     Unit.objects.all(parent_unit_no=query_params['fakulte'], unit_type='bölüm')
                # ]
                self.column_defs[i]['filter']['selectOptions'] = [
                    {"value": bol.yoksis_no, "label": bol.name} for bol in
                    Unit.objects.all(parent_unit_no=query_params['fakulte'], unit_type='bölüm')
                ]

        active_columns = []

        for col in self.selectors:
            if col['checked']:
                active_columns.append(col['name'])

        personel_data_list = []
        if 'bolum' in query_params:
            bolum = Unit.objects.get(yoksis_no=query_params['bolum'])
            for ana_bilim in Unit.objects.all(parent_unit_no=bolum.yoksis_no,
                                              unit_type__in=['anabilim dalı', 'anasanat dalı']):
                for kadro in Kadro.objects.all(birim=ana_bilim):
                    atama = Atama.objects.get(kadro=kadro)
                    personel_data_list.append({
                        "ad": atama.personel.ad,
                        "soyad": atama.personel.soyad,
                        "fakulte": Unit.objects.get(yoksis_no=query_params['fakulte']).name,
                        "bolum": bolum.name,
                        "unvan": unvanlar[atama.personel.unvan]
                    })
        else:
            for bolum in Unit.objects.all(parent_unit_no=query_params['fakulte'], unit_type='bölüm'):
                for ana_bilim in Unit.objects.all(parent_unit_no=bolum.yoksis_no,
                                                  unit_type__in=['anabilim dalı', 'anasanat dalı']):
                    for kadro in Kadro.objects.all(birim=ana_bilim):
                        atama = Atama.objects.get(kadro=kadro)
                        personel_data_list.append({
                            "ad": atama.personel.ad,
                            "soyad": atama.personel.soyad,
                            "fakulte": Unit.objects.get(yoksis_no=query_params['fakulte']).name,
                            "bolum": bolum.name,
                            "unvan": unvanlar[atama.personel.unvan]
                        })

        agirlikli_unvanlar = {
            unvanlar[1550]: 1,
            unvanlar[1555]: 2,
            unvanlar[1565]: 3,
            unvanlar[1590]: 4,
        }
        personel_data_list = sorted(personel_data_list,
                                    key=lambda lam: agirlikli_unvanlar[lam['unvan']])

        data_size = len(personel_data_list)
        if not csv:
            from_ = (self.page - 1) * page_size
            to = min([from_ + page_size, data_size])
            personel_data_list = personel_data_list[from_:to]

        data_to_return = []
        for k in personel_data_list:
            d = OrderedDict()
            for ac in active_columns:
                d[ac] = k[ac]
            data_to_return.append(d)

        is_more_data_left = data_size / page_size > (self.page - 1)

        return is_more_data_left, data_to_return


class PersonelFakulteBolumUnvanRaporDataGridView(CrudView):
    def __init__(self, current=None):
        super(PersonelFakulteBolumUnvanRaporDataGridView, self).__init__(current)
        self.column_dict = OrderedDict(
            [
                ('fakulte', _(u"Fakülte")), ('bolum', _(u"Bölüm")), ('unvan', _(u"Unvan")),
                ('ad', _(u"Ad")), ('soyad', _(u"Soyad")),

            ])

        fakulte_choices = [
            {"name": fak.name, "value": fak.yoksis_no} for fak in
            Unit.objects.all(unit_type='fakülte').order_by('yoksis_no')
        ]
        bolum_choices = [
            {"name": fak.name, "value": fak.yoksis_no} for fak in
            Unit.objects.all(parent_unit_no=fakulte_choices[0]['value'], unit_type='bölüm')
        ]
        select_fields = {
            'unvan': self.prepare_options(unvan_choices),
            'fakulte': self.prepare_options(fakulte_choices),
            'bolum': self.prepare_options(bolum_choices),
        }

        column_types_dict = {
            'select_fields': select_fields,
            'multiselect_fields': {},
            'range_date_fields': [],
            'range_num_fields': [],
            'starts_fields': ['ad', 'soyad'],
        }

        self.kwargs = {
            'default_fields': ['fakulte', 'bolum', 'ad', 'soyad', 'unvan'],
            'column_types_dict': column_types_dict
        }

    def get_grid_data(self):
        form_data = self.current.input.get('form', {})
        return AkademikDataGrid(
            cache_key=self.current.session.sess_id,  # unique id
            model=Personel,
            page=form_data.get('page', 1),
            filter_params=form_data.get('filterColumns', []),
            sort_params=form_data.get('sortColumns', []),
            columns=self.column_dict,
            selectors=form_data.get('selectors', None),
            cache=AkademikDataGridCache,
            query_cache=AkademikDataGridQueryCache,
            **self.kwargs
        )

    def grid_goster(self):
        grid = self.get_grid_data()
        self.output['gridOptions'] = grid.build_response()['gridOptions']

    def csv_indir(self):
        grid = self.get_grid_data()
        self.output['download_url'] = grid.generate_csv_link()

    def prepare_options(self, options):
        return [
            {
                "value": item['value'],
                "label": item['name']
            } for item in options
        ]

