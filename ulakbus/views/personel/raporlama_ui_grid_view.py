# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import base64
import csv
from io import BytesIO

from ulakbus.lib.cache import RaporlamaEklentisi
from ulakbus.lib.s3_file_manager import S3FileManager
from zengine.lib.decorators import view
from ulakbus.models import Personel
from datetime import datetime
from ulakbus.settings import DATE_DEFAULT_FORMAT

__author__ = 'Anıl Can Aydın'


@view()
def get_report_data(current):
    """
        Populates the report screen data.

        .. code-block:: python

               #  request:
                   {
                   'view': '_zops_get_report_data',
                   'page': 1,
                    selectors: [
                            {
                                name: "some field name (name, age etc)",
                                label: "Some Field Name To Show (Name, Age etc.)",
                                checked: true or false
                            },
                            ...
                        ],
                    options: {
                            some_input_field: {
                                condition: "CONTAINS", // or "STARTS_WITH", "END_WIDTH"
                                value: "some value"
                            },
                            some_select_field: {
                                value: "some value"
                            },
                            some_multiselect_field: {
                                some_name: "some value",
                                some_name: "some value",
                                some_name: "some value",
                                ...
                            },
                            some_range_field: {
                                start (or min): "some value",
                                end (or max): "some value"
                            }
                        }
                   }

               #  response:
                    {
                            'gridOptions': {
                                enableSorting: true,
                                useExternalSorting: true,  //if need sorting from backend side
                                enableFiltering: true,
                                toggleFiltering: true,
                                useExternalFiltering: true, //if need filtering from backend side
                                paginationPageSize: 25,
                                useExternalPagination: true, //if need paginations from backend side
                                enableAdding: true,
                                enableRemoving: true,
                                selectors: [
                                    {
                                        name: "some field name (name, age etc)",
                                        label: "Some Field Name To Show (Name, Age etc.)",
                                        checked: true or false
                                    },
                                    ...
                                ],
                                columnDefs: [
                                    // input contain filter example
                                    {
                                        field: "age",
                                        type: "INPUT"
                                        filter: {
                                            condition: "CONTAINS",
                                            placeholder: "contains"
                                        }
                                    },
                                    // multiple input filters example
                                    {
                                        field: "age",
                                        type: "INPUT",
                                        filter: {
                                            condition: "STARTS_WITH",
                                            placeholder: "starts with"
                                        }
                                    },
                                    {
                                        field: "age",
                                        type: "INPUT",
                                        filter: {
                                            condition: "ENDS_WITH",
                                            placeholder: "ends with"
                                        }
                                    },
                                    // range input integer example
                                    {
                                        field: "age",
                                        type: "range",
                                        rangeType: "integer",
                                        filters: [
                                            {
                                                condition: "MAX",
                                                placeholder: "max value"
                                            },
                                            {
                                                condition: "MIN",
                                                placeholder: "min value"
                                            }
                                        ]
                                    },
                                    // range input datetime example
                                    {
                                    field: "date",
                                    type: "range",
                                    rangeType: "datetime",
                                    filters: [
                                            {
                                                condition: "START",
                                                placeholder: "start date"
                                            },
                                            {
                                                condition: "END",
                                                placeholder: "end date"
                                            }
                                        ]
                                    },
                                    // select
                                    {
                                    field: 'gender',
                                    type: 'SELECT',
                                    filter: {
                                        selectOptions: [
                                            { value: '1', label: 'male' },
                                            { value: '2', label: 'female' },
                                            { value: '3', label: 'unknown'}
                                        ]
                                    },
                                    // multiselect
                                    {
                                        field: 'graduation',
                                        type: 'MULTISELECT',
                                        filter: {
                                        selectOptions: [
                                            { value: 'university', label: 'university' },
                                            { value: 'high school', label: 'high school' }
                                    ]
                                    }
                                ],
                                data: [
                                    {
                                        "name": "Cox",
                                        "company": "Enormo",
                                        "gender": "male",
                                        "graduation": "university",
                                        ...
                                    },

                                    ...,

                                    {
                                        "name": "Misty",
                                        "company": "Letpro",
                                        "gender": "female",
                                        "graduation": "university",
                                        ...
                                    }
                                ]
                        }
                    }
    """

    page_default = 1
    raporlama_cache = RaporlamaEklentisi(current.session.sess_id)
    cache_data = raporlama_cache.get_or_set()
    page_size = cache_data['page_size']

    if 'selectors' in current.input:
        cache_data['gridOptions']['selectors'] = current.input['selectors']
    if 'filterColumns' in current.input:
        cache_data['gridOptions']['filter_columns'] = current.input['filterColumns']
    if 'sortColumns' in current.input:
        cache_data['gridOptions']['sort_columns'] = current.input['sortColumns']
    if 'page' in current.input:
        page_default = current.input['page']

    page = page_default - 1

    def personel_data():
        gos = cache_data['gridOptions']
        query_params = data_grid_filter_parser(gos.get('filter_columns', []),
                                               cache_data['alan_filter_type_map'])

        sort_params = data_grid_order_parser(gos.get('sort_columns', []))
        active_columns = []
        for col in cache_data['gridOptions']['selectors']:
            if col['checked']:
                active_columns.append(col['name'])
        data_size = Personel.objects.all(**query_params).count()
        data = Personel.objects.set_params(
            start=page * page_size, rows=page_size
        ).all(**query_params).order_by(*sort_params).values(*active_columns)

        is_more_data_left = data_size / page_size > page

        return is_more_data_left, data

    cache_data['gridOptions']['isMoreDataLeft'], cache_data['gridOptions']['data'] = personel_data()
    raporlama_cache.set(cache_data)
    del cache_data['gridOptions']['filter_columns']
    del cache_data['gridOptions']['sort_columns']
    current.output['gridOptions'] = cache_data['gridOptions']


def data_grid_filter_parser(filters, field_types):
    filter_conditions = {
        "STARTS_WITH": 2,
        "ENDS_WITH": 4,
        "EXACT": 8,
        "CONTAINS": 16,
        "GREATER_THAN": 32,
        "GREATER_THAN_OR_EQUAL": 64,
        "LESS_THAN": 128,
        "LESS_THAN_OR_EQUAL": 256,
        "NOT_EQUAL": 512
    }
    query_params = {}
    for element in filters:
        f = element['columnName']
        qp = element['filterParam']
        if qp:
            if field_types[f] == "INPUT":
                # condition: "CONTAINS", // or "STARTS_WITH", "END_WIDTH"
                cond = qp[0]['condition']
                val = qp[0]['value']
                if cond == filter_conditions["CONTAINS"]:
                    query_params[f + "__contains"] = val
                elif cond == filter_conditions["STARTS_WITH"]:
                    query_params[f + "__startswith"] = val
                elif cond == filter_conditions["ENDS_WITH"]:
                    query_params[f + "__endswith"] = val
                else:
                    query_params[f] = val
            elif field_types[f] == "SELECT":
                query_params[f] = qp[0]['value']
            elif field_types[f] == "MULTISELECT":
                multiselect_list = qp[0]['value']
                query_params[f + "__in"] = multiselect_list
            elif field_types[f] == "RANGE-DATETIME":
                start_raw = ""
                end_raw = ""
                for date_item in qp:
                    if date_item['condition'] == filter_conditions["GREATER_THAN"]:
                        start_raw = str(date_item['value'])
                    if date_item['condition'] == filter_conditions["LESS_THAN"]:
                        end_raw = str(date_item['value'])
                start = datetime.strptime(start_raw, DATE_DEFAULT_FORMAT)
                end = datetime.strptime(end_raw, DATE_DEFAULT_FORMAT)
                query_params[f + "__range"] = [start, end]
            elif field_types[f] == "RANGE-INTEGER":
                minn = maxx = 0
                for int_item in qp:
                    if int_item['condition'] == filter_conditions["GREATER_THAN"]:
                        minn = int_item['value']
                    if int_item['condition'] == filter_conditions["LESS_THAN"]:
                        maxx = int_item['value']
                query_params[f + "__range"] = [int(minn), int(maxx)]
    return query_params


def data_grid_order_parser(sort_columns):
    sort_params = []
    for col in sort_columns:
        if col['order'] == 'desc':
            sort_params.append("%s%s" % ("-", col['columnName']))
        else:
            sort_params.append(col['columnName'])
    return sort_params


@view()
def get_csv_data(current):
    raporlama_cache = RaporlamaEklentisi(current.session.sess_id)
    cache_data = raporlama_cache.get_or_set()

    if 'selectors' in current.input:
        cache_data['gridOptions']['selectors'] = current.input['selectors']
    if 'filterColumns' in current.input:
        cache_data['gridOptions']['filter_columns'] = current.input['filterColumns']
    if 'sortColumns' in current.input:
        cache_data['gridOptions']['sort_columns'] = current.input['sortColumns']

    def personel_data():
        gos = cache_data['gridOptions']
        query_params = data_grid_filter_parser(gos.get('filter_columns', []),
                                               cache_data['alan_filter_type_map'])

        sort_params = data_grid_order_parser(gos.get('sort_columns', []))
        active_columns = []
        for col in cache_data['gridOptions']['selectors']:
            if col['checked']:
                active_columns.append(col['name'])
        data = Personel.objects.all(**query_params).order_by(*sort_params).values(
            *active_columns)

        return data

    output = BytesIO()
    csv_writer = csv.writer(output, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)

    count = 0
    for emp in personel_data():
        if count == 0:
            header = emp.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(emp.values())

    download_url = generate_temp_file(
        name=generate_file_name(),
        content=base64.b64encode(output.getvalue()),
        file_type='text/csv',
        ext='csv'
    )

    current.output['download_url'] = download_url


def generate_temp_file(name, content, file_type, ext):
    f = S3FileManager()
    key = f.store_file(name=name, content=content, type=file_type, ext=ext)
    return f.get_url(key)


def generate_file_name():
    return "personel-rapor-%s" % datetime.now().strftime("%d.%m.%Y-%H.%M.%S")