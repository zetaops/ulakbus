# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import base64
import csv
from collections import OrderedDict
from io import BytesIO

from ulakbus.data_grid import DataGrid

from ulakbus.lib.cache import RaporlamaEklentisi
from ulakbus.lib.s3_file_manager import S3FileManager
from zengine.lib.catalog_data import catalog_data_manager
from zengine.lib.decorators import view
from ulakbus.models import Personel, Unit
from datetime import datetime
from ulakbus.settings import DATE_DEFAULT_FORMAT
from pyoko.fields import DATE_FORMAT
from zengine.lib.translation import gettext as _

__author__ = 'Anıl Can Aydın'


@view()
def get_report_data(current):
    """
        Rapor ekranı verilerini oluşturur. Gelen sorgulara uyan verileri rapor ekranına gönderir.
        .. code-block:: python

               #  request:
                   {

                   'view': '_zops_get_report_data',
                   'page': 1,
                   'selectors': [ //Gösterilen kolonlar değiştiğinde gönderilir.
                            {
                                name: "some field name (name, age etc)",
                                label: "Some Field Name To Show (Name, Age etc.)",
                                checked: true or false
                            },
                            ...
                        ],
                   'filterColumns': [
                        {
                            'columnName': "ad",
                            'columnType': "INPUT",
                            'filterParam': [
                                {
                                    'condition': 2,
                                    'value': "A"
                                }
                            ]
                        },
                        {
                            'columnName': "soyad",
                            'columnType': "INPUT",
                            'filterParam': [
                                {
                                    'condition': 2,
                                    'value': "B"
                                }
                            ]
                        },
                        {
                            'columnName': "dogum_tarihi",
                            'columnType': "datetime",
                            'filterParam': [
                                {
                                    'condition': 32,
                                    'value': "01.01.1960"
                                },
                                {
                                    'condition': 128,
                                    'value': "01.01.1990"
                                }
                            ]
                        },
                        {   'columnName': "cinsiyet",
                            'columnType': "SELECT",
                            'filterParam': [
                                {
                                    'condition': 8,
                                    'value': 1
                                }
                            ]
                        },
                        {
                            'columnName': "personel_turu",
                            'columnType': "SELECT",
                            'filterParam': [
                                {
                                    'condition': 8,
                                    'value': 1
                                }
                            ]
                        }
                    ],
                    'sortColumns': [{columnName: "dogum_tarihi", order: "asc"}]
                   }

               #  response:
                    {
                            'gridOptions': {
                                'applyFilter': "Filtrele",
                                'cancelFilter': "Filtreleri Temizle",
                                'csvDownload': "Dışa Aktar",
                                'dataLoading': "Yükleniyor",
                                'selectColumns': "Kolon Seç",

                                'enableSorting': true,
                                'enableFiltering': true,
                                'toggleFiltering': true,
                                'enableRemoving': true,

                                'isMoreDataLeft': true,

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
    # Gösterilecek alanlar listesi.
    column_list = ['tckn', 'ad', 'soyad', 'dogum_tarihi', 'cinsiyet', 'medeni_hali', 'dogum_yeri',
                   'kan_grubu', 'ana_adi', 'baba_adi', 'brans', 'unvan', 'personel_turu',
                   'kurum_sicil_no_int',
                   'birim_id', 'kayitli_oldugu_il', 'kayitli_oldugu_ilce',
                   'kayitli_oldugu_mahalle_koy', 'cuzdan_seri', 'cuzdan_seri_no',
                   'kayitli_oldugu_cilt_no',
                   'kayitli_oldugu_aile_sira_no', 'kayitli_oldugu_sira_no',
                   'kimlik_cuzdani_verildigi_yer',
                   'kimlik_cuzdani_verilis_nedeni', 'kimlik_cuzdani_kayit_no',
                   'kimlik_cuzdani_verilis_tarihi',
                   'emekli_sicil_no', 'emekli_giris_tarihi', 'hizmet_sinifi',
                   'kazanilmis_hak_derece', 'kazanilmis_hak_kademe', 'kazanilmis_hak_ekgosterge',
                   'gorev_ayligi_derece', 'gorev_ayligi_kademe', 'gorev_ayligi_ekgosterge',
                   'emekli_muktesebat_derece', 'emekli_muktesebat_kademe',
                   'emekli_muktesebat_ekgosterge',
                   'kh_sonraki_terfi_tarihi', 'ga_sonraki_terfi_tarihi', 'goreve_baslama_tarihi',
                   'mecburi_hizmet_suresi']

    ordered_dict_param = []
    for col in column_list:
        if col == "birim_id":
            ordered_dict_param.append((col, _(u"Birim")))
        elif col == "baslama_sebep_id":
            ordered_dict_param.append((col, _(u"Başlama Sebep")))
        else:
            ordered_dict_param.append(
                (col, str(Personel.get_field(col).title) if Personel.get_field(
                    col) is not None else col))
    column_dict = OrderedDict(ordered_dict_param)

    select_fields = {
        'cinsiyet': prepare_options_from_catalog_data('cinsiyet'),
        'kan_grubu': prepare_options_from_catalog_data('kan_grubu'),
        'medeni_hali': prepare_options_from_catalog_data('medeni_hali'),
        'personel_turu': prepare_options_from_catalog_data('personel_turu')
    }

    birim = [{"value": u.key, "label": u.name} for u in Unit.objects.all()]
    multiselect_fields = {
        'birim_id': birim,
        'hizmet_sinifi': prepare_options_from_catalog_data('hizmet_sinifi'),
        'unvan': prepare_options_from_catalog_data('unvan_kod'),
        'statu': prepare_options_from_catalog_data('personel_statu')
    }
    range_date_fields = ['dogum_tarihi', 'em_sonraki_terfi_tarihi', 'emekli_giris_tarihi',
                         'ga_sonraki_terfi_tarihi',
                         'gorev_suresi_baslama', 'gorev_suresi_bitis', 'goreve_baslama_tarihi',
                         'kh_sonraki_terfi_tarihi', 'mecburi_hizmet_suresi']
    range_int_fields = ['emekli_muktesebat_derece', 'emekli_muktesebat_ekgosterge',
                        'emekli_muktesebat_kademe',
                        'engel_orani', 'gorev_ayligi_derece', 'gorev_ayligi_ekgosterge',
                        'gorev_ayligi_kademe',
                        'kazanilmis_hak_derece', 'kazanilmis_hak_ekgosterge',
                        'kazanilmis_hak_kademe']
    starts_fields = ['tckn', 'ad', 'soyad', 'dogum_yeri', 'ana_adi', 'baba_adi', 'brans',
                     'kurum_sicil_no_int', 'kayitli_oldugu_il', 'kayitli_oldugu_ilce',
                     'kayitli_oldugu_mahalle_koy', 'cuzdan_seri', 'cuzdan_seri_no',
                     'kayitli_oldugu_cilt_no', 'kayitli_oldugu_aile_sira_no',
                     'kayitli_oldugu_sira_no', 'kimlik_cuzdani_verildigi_yer',
                     'kimlik_cuzdani_verilis_nedeni', 'kimlik_cuzdani_kayit_no',
                     'kimlik_cuzdani_verilis_tarihi', 'emekli_sicil_no']

    column_types_dict = {
        'select_fields': select_fields,
        'multiselect_fields': multiselect_fields,
        'range_date_fields': range_date_fields,
        'range_num_fields': range_int_fields,
        'starts_fields': starts_fields
    }

    kwargs = {
        'default_fields': ['ad', 'soyad', 'cinsiyet', 'dogum_tarihi', 'personel_turu'],
        'column_types_dict': column_types_dict
    }

    grid = DataGrid(
        current.session.sess_id,
        Personel,
        current.input['page'],
        current.input['filterColumns'],
        current.input['sortColumns'],
        column_dict,
        current.input.get('selectors', None),
        **kwargs
    )
    current.output['gridOptions'] = grid.build_response()['gridOptions']


def prepare_options_from_catalog_data(catalog_key):
    """
    prepare options from for field from catalog data
    Args:

        catalog_key (str): catalog key, e.g gender
    Returns:
        list: list of dict of options [{"value": 1, "label": "Male"},
        {"value": 2, "label": "Female"}]
    """
    return [
        {
            "value": item['value'],
            "label": item['name']
        } for item in catalog_data_manager.get_all(catalog_key)
        ]


@view()
def get_csv_data(current):
    """
    Rapor ekranındaki verileri kullanarak csv  dosyası oluşturur. Output olarak bu csv linkini
    döndürür.
        .. code-block:: python

               #  request:
                    {
                        'filterColumns': [
                        {
                            'columnName': "ad",
                            'columnType': "INPUT",
                            'filterParam': [
                                {
                                    'condition': 2,
                                    'value': "A"
                                }
                            ]
                        },
                        {
                            'columnName': "soyad",
                            'columnType': "INPUT",
                            'filterParam': [
                                {
                                    'condition': 2,
                                    'value': "B"
                                }
                            ]
                        },
                        {
                            'columnName': "dogum_tarihi",
                            'columnType': "datetime",
                            'filterParam': [
                                {
                                    'condition': 32,
                                    'value': "01.01.1960"
                                },
                                {
                                    'condition': 128,
                                    'value': "01.01.1990"
                                }
                            ]
                        },
                        {   'columnName': "cinsiyet",
                            'columnType': "SELECT",
                            'filterParam': [
                                {
                                    'condition': 8,
                                    'value': 1
                                }
                            ]
                        },
                        {
                            'columnName': "personel_turu",
                            'columnType': "SELECT",
                            'filterParam': [
                                {
                                    'condition': 8,
                                    'value': 1
                                }
                            ]
                        }
                    ],
                    'page': 1,
                    'sortColumns': [{columnName: "dogum_tarihi", order: "asc"}]
                    }

               #  response:
                    {
                        'download_url': "http://ulakbus.3s.ulakbus.net:18177/personel-rapor-10.05.
2017-14.53.csv"
                    }



    """
    column_list = ['tckn', 'ad', 'soyad', 'dogum_tarihi', 'cinsiyet', 'medeni_hali', 'dogum_yeri',
                   'kan_grubu', 'ana_adi', 'baba_adi', 'brans', 'unvan', 'personel_turu',
                   'kurum_sicil_no_int',
                   'birim_id', 'kayitli_oldugu_il', 'kayitli_oldugu_ilce',
                   'kayitli_oldugu_mahalle_koy', 'cuzdan_seri', 'cuzdan_seri_no',
                   'kayitli_oldugu_cilt_no',
                   'kayitli_oldugu_aile_sira_no', 'kayitli_oldugu_sira_no',
                   'kimlik_cuzdani_verildigi_yer',
                   'kimlik_cuzdani_verilis_nedeni', 'kimlik_cuzdani_kayit_no',
                   'kimlik_cuzdani_verilis_tarihi',
                   'emekli_sicil_no', 'emekli_giris_tarihi', 'hizmet_sinifi',
                   'kazanilmis_hak_derece', 'kazanilmis_hak_kademe', 'kazanilmis_hak_ekgosterge',
                   'gorev_ayligi_derece', 'gorev_ayligi_kademe', 'gorev_ayligi_ekgosterge',
                   'emekli_muktesebat_derece', 'emekli_muktesebat_kademe',
                   'emekli_muktesebat_ekgosterge',
                   'kh_sonraki_terfi_tarihi', 'ga_sonraki_terfi_tarihi', 'goreve_baslama_tarihi',
                   'mecburi_hizmet_suresi']

    ordered_dict_param = []
    for col in column_list:
        if col == "birim_id":
            ordered_dict_param.append((col, _(u"Birim")))
        elif col == "baslama_sebep_id":
            ordered_dict_param.append((col, _(u"Başlama Sebep")))
        else:
            ordered_dict_param.append(
                (col, str(Personel.get_field(col).title) if Personel.get_field(
                    col) is not None else col))
    column_dict = OrderedDict(ordered_dict_param)

    select_fields = {
        'cinsiyet': prepare_options_from_catalog_data('cinsiyet'),
        'kan_grubu': prepare_options_from_catalog_data('kan_grubu'),
        'medeni_hali': prepare_options_from_catalog_data('medeni_hali'),
        'personel_turu': prepare_options_from_catalog_data('personel_turu')
    }

    birim = [{"value": u.key, "label": u.name} for u in Unit.objects.all()]
    multiselect_fields = {
        'birim_id': birim,
        'hizmet_sinifi': prepare_options_from_catalog_data('hizmet_sinifi'),
        'unvan': prepare_options_from_catalog_data('unvan_kod'),
        'statu': prepare_options_from_catalog_data('personel_statu')
    }
    range_date_fields = ['dogum_tarihi', 'em_sonraki_terfi_tarihi', 'emekli_giris_tarihi',
                         'ga_sonraki_terfi_tarihi',
                         'gorev_suresi_baslama', 'gorev_suresi_bitis', 'goreve_baslama_tarihi',
                         'kh_sonraki_terfi_tarihi', 'mecburi_hizmet_suresi']
    range_int_fields = ['emekli_muktesebat_derece', 'emekli_muktesebat_ekgosterge',
                        'emekli_muktesebat_kademe',
                        'engel_orani', 'gorev_ayligi_derece', 'gorev_ayligi_ekgosterge',
                        'gorev_ayligi_kademe',
                        'kazanilmis_hak_derece', 'kazanilmis_hak_ekgosterge',
                        'kazanilmis_hak_kademe']
    starts_fields = ['tckn', 'ad', 'soyad', 'dogum_yeri', 'ana_adi', 'baba_adi', 'brans',
                     'kurum_sicil_no_int', 'kayitli_oldugu_il', 'kayitli_oldugu_ilce',
                     'kayitli_oldugu_mahalle_koy', 'cuzdan_seri', 'cuzdan_seri_no',
                     'kayitli_oldugu_cilt_no', 'kayitli_oldugu_aile_sira_no',
                     'kayitli_oldugu_sira_no', 'kimlik_cuzdani_verildigi_yer',
                     'kimlik_cuzdani_verilis_nedeni', 'kimlik_cuzdani_kayit_no',
                     'kimlik_cuzdani_verilis_tarihi', 'emekli_sicil_no']

    column_types_dict = {
        'select_fields': select_fields,
        'multiselect_fields': multiselect_fields,
        'range_date_fields': range_date_fields,
        'range_num_fields': range_int_fields,
        'starts_fields': starts_fields
    }

    kwargs = {
        'default_fields': ['ad', 'soyad', 'cinsiyet', 'dogum_tarihi', 'personel_turu'],
        'column_types_dict': column_types_dict
    }

    grid = DataGrid(
        current.session.sess_id,
        Personel,
        current.input['page'],
        current.input['filterColumns'],
        current.input['sortColumns'],
        column_dict,
        current.input.get('selectors', None),
        **kwargs
    )
    current.output['download_url'] = grid.generate_csv_link()


