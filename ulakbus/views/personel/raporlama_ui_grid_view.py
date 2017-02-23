# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.cache import RaporlamaEklentisi
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
    raporlama_cache = RaporlamaEklentisi(current.session.sess_id)
    cache_data = raporlama_cache.get_or_set()
    page_size = cache_data['gridOptions']['paginationPageSize']

    if 'selectors' in current.input:
        cache_data['gridOptions']['selectors'] = current.input['selectors']
    if 'options' in current.input:
        cache_data['gridOptions']['options'] = current.input['options']
    if 'page' in current.input:
        cache_data['gridOptions']['paginationCurrentPage'] = current.input['page']

    page = cache_data['gridOptions']['paginationCurrentPage'] - 1
    raporlama_cache.set(cache_data)

    def personel_data():
        query_params = data_grid_filter_parser(cache_data['gridOptions']['options'],
                                               cache_data['alan_filter_type_map'])

        result_size = Personel.objects.filter(**query_params).count()

        active_columns = []
        for col in cache_data['gridOptions']['selectors']:
            if col['checked']:
                active_columns.append(col['name'])

        data = Personel.objects.set_params(
            start=page * page_size, rows=page_size
        ).filter(**query_params).values(*active_columns)

        return result_size, data

    cache_data['gridOptions']['totalItems'], cache_data['gridOptions']['data'] = personel_data()
    raporlama_cache.set(cache_data)
    current.output['gridOptions'] = cache_data['gridOptions']


def data_grid_filter_parser(filters, field_types):
    query_params = {}
    for f, qp in filters.items():
        if field_types[f] == "INPUT":
            # condition: "CONTAINS", // or "STARTS_WITH", "END_WIDTH"
            if qp['condition'] == "CONTAINS":
                query_params[f + "__contains"] = qp['value']
            elif qp['condition'] == "STARTS_WITH":
                query_params[f + "__startswith"] = qp['value']
            else:
                query_params[f + "__endswith"] = qp['value']
        elif field_types[f] == "SELECT":
            query_params[f] = qp['value']
        elif field_types[f] == "MULTISELECT":
            multiselect_list = []
            for msi in qp:
                multiselect_list.append(msi)
            query_params[f + "__in"] = multiselect_list
        elif field_types[f] == "RANGE-DATETIME":
            start_raw = str(qp['start'])
            start = datetime.strptime(start_raw, DATE_DEFAULT_FORMAT)
            end_raw = str(qp['end'])
            end = datetime.strptime(end_raw, DATE_DEFAULT_FORMAT)
            query_params[f + "__range"] = [start, end]
        elif field_types[f] == "RANGE-INTEGER":
            query_params[f + "__range"] = [int(qp['min']), int(qp['max'])]
    return query_params
