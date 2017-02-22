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
                                checked: true or false
                            },
                            {
                                name: "some field name (name, age etc)",
                                checked: true or false
                            },
                            {
                                name: "some field name (name, age etc)",
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
                                        checked: true or false
                                    },
                                    {
                                        name: "some field name (name, age etc)",
                                        checked: true or false
                                    },
                                    {
                                        name: "some field name (name, age etc)",
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
                                        term: '2',
                                        selectOptions: [ { value: '1', label: 'male' }, { value: '2', label: 'female' }, { value: '3', label: 'unknown'} ]
                                    },
                                    // multiselect
                                    {
                                        field: 'graduation',
                                        type: 'MULTISELECT',
                                        filter: {
                                        selectOptions: [ { value: 'university', label: 'university' }, { value: 'high school', label: 'high school' } ]
                                    },
                                    // examples for editing
                                    { field: 'last_name', enableCellEdit: true },
                                    { field: 'age', enableCellEdit: true, type: 'number'},
                                    { field: 'registered', displayName: 'Registered' , type: 'date'},
                                    { field: 'address', displayName: 'Address', type: 'object'}, //not editable if type==='object'
                                    { field: 'address.city', enableCellEdit: true, displayName: 'Address (even rows editable)' }
                                    { field: 'isActive', enableCellEdit: true, type: 'boolean'},
                                ],
                                initialData: [
                                    {
                                        "name": "Cox",
                                        "company": "Enormo",
                                        "gender": "male",
                                        "graduation": "university",
                                        ...
                                    },
                                    {
                                        "name": "Lorraine",
                                        "company": "Comveyer",
                                        "gender": "female",
                                        "graduation": "high school",
                                        ...
                                    },
                                    {
                                        "name": "Nancy",,
                                        "company": "Fuelton",
                                        "gender": "female",
                                        "graduation": "university",
                                        ...
                                    },
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
    page = current.input['page'] - 1 if 'page' in current.input else 0
    page_size = cache_data['gridOptions']['paginationPageSize']
    time_related_fields = cache_data['time_related_fields']
    alan_filter_type_map = cache_data['alan_filter_type_map']

    if 'selectors' in current.input and not 'options' in current.input:
        selectors = current.input['selectors']
        active_selectors = []
        for selector in selectors:
            if selector['checked']:
                active_selectors.append(selector['name'])

        previous_options = cache_data['gridOptions']['options']
        if not previous_options:
            total_items, data = personel_data_filtresiz(selectors, page, page_size, time_related_fields)

        else:
            total_items, data = personel_data_filtreli(previous_options, selectors, page, page_size,
                                                       time_related_fields, alan_filter_type_map)

        current.output['totalItems'] = total_items
        current.output['data'] = data
        cache_data['gridOptions']['selectors'] = selectors
        raporlama_cache.set(cache_data)
    elif not ('selectors' in current.input and 'options' in current.input):
        if not page == 0:
            selectors = cache_data['gridOptions']['selectors']
            total_items, data = personel_data_filtresiz(selectors, page, page_size, time_related_fields)
            current.output['totalItems'] = total_items
            current.output['data'] = data
        else:
            current.output['gridOptions'] = cache_data['gridOptions']
    else:
        options = current.input['options']
        selectors = current.input['selectors']

        total_items, data = personel_data_filtreli(options, selectors, page, page_size,
                                                   time_related_fields, alan_filter_type_map)
        current.output['totalItems'] = total_items
        current.output['data'] = data
        cache_data['gridOptions']['selectors'] = selectors
        cache_data['gridOptions']['options'] = options
        raporlama_cache.set(cache_data)


def personel_data_filtresiz(selectors, page, page_size, time_related_fields):
    """
    :param selectors:
    :param page:
    :param page_size:
    :param time_related_fields:
    :return:
    """
    active_selectors = []
    for selector in selectors:
        if selector['checked']:
            active_selectors.append(selector['name'])

    personeller = Personel.objects.filter()[page * page_size:page * page_size + page_size]
    data = []
    for p in personeller:
        pd = {}
        for active_selector in active_selectors:
            if active_selector in ['birim', 'baslama_sebep']:
                pd[active_selector] = p.__getattribute__(str(active_selector) + "_id")
            elif active_selector in time_related_fields:
                pd[active_selector] = p.__getattribute__(active_selector).strftime(DATE_DEFAULT_FORMAT)
            else:
                pd[active_selector] = p.__getattribute__(active_selector)
        data.append(pd)

    return Personel.objects.count(), data


def personel_data_filtreli(options, selectors, page, page_size, time_related_fields, alan_filter_type_map):
    """
    :param options:
    :param selectors:
    :param page:
    :param page_size:
    :param time_related_fields:
    :param alan_filter_type_map:
    :return:
    """
    query_params = {}
    for f, qp in options.items():
        if alan_filter_type_map[f] == "INPUT":
            # condition: "CONTAINS", // or "STARTS_WITH", "END_WIDTH"
            if qp['condition'] == "CONTAINS":
                query_params[f + "__contains"] = qp['value']
            elif qp['condition'] == "STARTS_WITH":
                query_params[f + "__startswith"] = qp['value']
            else:
                query_params[f + "__endswith"] = qp['value']
        elif alan_filter_type_map[f] == "SELECT":
            query_params[f] = qp['value']
        elif alan_filter_type_map[f] == "MULTISELECT":
            multiselect_list = []
            for msi in qp:
                multiselect_list.append(msi)
            query_params[f + "__in"] = multiselect_list
        elif alan_filter_type_map[f] == "RANGE-DATETIME":
            start_raw = str(qp['start'])
            start = datetime.strptime(start_raw, DATE_DEFAULT_FORMAT)
            end_raw = str(qp['end'])
            end = datetime.strptime(end_raw, DATE_DEFAULT_FORMAT)
            query_params[f + "__range"] = [start, end]
        elif alan_filter_type_map[f] == "RANGE-INTEGER":
            min = qp['min']
            max = qp['max']
            query_params[f + "__range"] = [int(min), int(max)]

    result_size = Personel.objects.filter(**query_params).count()
    if result_size >= page * page_size + page_size:
        result_set = Personel.objects.set_params(start=page * page_size, rows=page_size).filter(**query_params)
    else:
        rows = result_size - page * page_size
        result_set = Personel.objects.set_params(start=page * page_size, rows=rows).filter(**query_params)

    active_selectors = []
    for selector in selectors:
        if selector['checked']:
            active_selectors.append(selector['name'])

    initial_data = []
    for p in result_set:
        pd = {}
        for active_selector in active_selectors:
            if active_selector in ['birim', 'baslama_sebep']:
                pd[active_selector] = p.__getattribute__(str(active_selector) + "_id")
            elif active_selector in time_related_fields:
                pd[active_selector] = p.__getattribute__(active_selector).strftime(DATE_DEFAULT_FORMAT)
            else:
                pd[active_selector] = p.__getattribute__(active_selector)
        initial_data.append(pd)

    return result_size, initial_data