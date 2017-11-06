# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import OrderedDict

from ulakbus.lib.data_grid import DataGrid

from ulakbus.models import Personel
from ulakbus.models import Unit
from zengine.lib.catalog_data import catalog_data_manager
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _

from ulakbus.lib.cache import ModelLabelValue


class PersonelDataGridView(CrudView):
    def __init__(self, current=None):
        super(PersonelDataGridView, self).__init__(current)
        # Gösterilecek alanlar listesi.
        column_list = [
            'tckn', 'ad', 'soyad', 'dogum_tarihi', 'cinsiyet', 'medeni_hali', 'dogum_yeri',
            'kan_grubu', 'ana_adi', 'baba_adi', 'brans', 'unvan', 'personel_turu',
            'kurum_sicil_no_int', 'birim_id', 'kayitli_oldugu_il', 'kayitli_oldugu_ilce',
            'kayitli_oldugu_mahalle_koy', 'cuzdan_seri', 'cuzdan_seri_no',
            'kayitli_oldugu_cilt_no', 'kayitli_oldugu_aile_sira_no', 'kayitli_oldugu_sira_no',
            'kimlik_cuzdani_verildigi_yer', 'kimlik_cuzdani_verilis_nedeni',
            'kimlik_cuzdani_kayit_no', 'kimlik_cuzdani_verilis_tarihi', 'emekli_sicil_no',
            'emekli_giris_tarihi', 'hizmet_sinifi', 'kazanilmis_hak_derece',
            'kazanilmis_hak_kademe', 'kazanilmis_hak_ekgosterge',
            'gorev_ayligi_derece', 'gorev_ayligi_kademe', 'gorev_ayligi_ekgosterge',
            'emekli_muktesebat_derece', 'emekli_muktesebat_kademe', 'emekli_muktesebat_ekgosterge',
            'kh_sonraki_terfi_tarihi', 'ga_sonraki_terfi_tarihi',
            'goreve_baslama_tarihi', 'mecburi_hizmet_suresi',
        ]
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
        self.column_dict = OrderedDict(ordered_dict_param)
        select_fields = {
            'cinsiyet': prepare_options_from_catalog_data('cinsiyet'),
            'kan_grubu': prepare_options_from_catalog_data('kan_grubu'),
            'medeni_hali': prepare_options_from_catalog_data('medeni_hali'),
            'personel_turu': prepare_options_from_catalog_data('personel_turu')
        }

        birim = ModelLabelValue(Unit).get_or_set()

        # birim = [{"value": u.key, "label": u.name} for u in Unit.objects.all()]

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

        self.kwargs = {
            'default_fields': ['ad', 'soyad', 'cinsiyet', 'dogum_tarihi', 'personel_turu'],
            'column_types_dict': column_types_dict
        }

    def get_grid_data(self):
        form_data = self.current.input.get('form', {})
        return DataGrid(
            cache_key=self.current.session.sess_id,  # unique id
            model=Personel,
            page=form_data.get('page', 1),
            filter_params=form_data.get('filterColumns', []),
            sort_params=form_data.get('sortColumns', []),
            columns=self.column_dict,
            selectors=form_data.get('selectors', None),
            **self.kwargs
        )

    def grid_goster(self):
        grid = self.get_grid_data()
        self.output['gridOptions'] = grid.build_response()['gridOptions']

    def csv_indir(self):
        grid = self.get_grid_data()
        self.output['download_url'] = grid.generate_csv_link()


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
