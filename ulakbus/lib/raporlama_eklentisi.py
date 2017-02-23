# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Personel
from ulakbus.models.auth import Unit
from ulakbus.models.hitap.hitap_sebep import HitapSebep
from zengine.lib.translation import gettext as _
from zengine.lib.catalog_data import catalog_data_manager


def raporlama_ekrani_secim_menulerini_hazirla():
    PAGE_SIZE = 25

    cache_data = {}
    grid_options = {}

    # Gösterilecek alanlar listesi.
    column_list = ['tckn', 'cuzdan_seri', 'cuzdan_seri_no', 'kayitli_oldugu_cilt_no',
                   'kayitli_oldugu_aile_sira_no', 'kayitli_oldugu_sira_no',
                   'kimlik_cuzdani_verildigi_yer', 'kimlik_cuzdani_verilis_nedeni',
                   'kimlik_cuzdani_kayit_no', 'kimlik_cuzdani_verilis_tarihi', 'emekli_sicil_no',
                   'emekli_giris_tarihi', 'ad', 'soyad', 'dogum_tarihi', 'dogum_yeri', 'baba_adi',
                   'ana_adi', 'cinsiyet', 'medeni_hali', 'kan_grubu', 'kayitli_oldugu_mahalle_koy',
                   'kayitli_oldugu_ilce', 'kayitli_oldugu_il', 'brans', 'hizmet_sinifi',
                   'kazanilmis_hak_derece', 'kazanilmis_hak_kademe', 'kazanilmis_hak_ekgosterge',
                   'gorev_ayligi_derece', 'gorev_ayligi_kademe', 'gorev_ayligi_ekgosterge',
                   'emekli_muktesebat_derece', 'emekli_muktesebat_kademe',
                   'emekli_muktesebat_ekgosterge', 'kh_sonraki_terfi_tarihi',
                   'ga_sonraki_terfi_tarihi', 'unvan', 'personel_turu', 'goreve_baslama_tarihi',
                   'mecburi_hizmet_suresi', 'kurum_sicil_no_int', 'birim_id', 'baslama_sebep_id']

    # Cinsiyet türlerini catalog datadan aldık
    cinsiyet = [{"value": item['value'], "label": item['name']} for item in
                 catalog_data_manager.get_all("cinsiyet")]

    # Kan gruplarını catalog datadan aldık
    kan_grubu = [{"value": item['value'], "label": item['name']} for item in
                 catalog_data_manager.get_all("kan_grubu")]

    # Medeni hal türlerini catalog datadan aldık
    # >>> [{'name': u'Evli', 'value': 1}, {'name': u'Bekar', 'value': 2}]
    medeni_hal = [{"value": item['value'], "label": item['name']} for item in
                  catalog_data_manager.get_all("medeni_hali")]

    # Birimleri aldık
    birim = [{"value": u.yoksis_no, "label": u.name} for u in Unit.objects.filter()]

    # Unvanları aldık
    unvan = [{"value": item['value'], "label": item['name']} for item in catalog_data_manager.get_all("unvan_kod")]

    # Personel türlerini aldık
    personel_turu = [{"value": item['value'], "label": item['name']} for item in
                     catalog_data_manager.get_all("personel_turu")]

    # Hizmet sınıflarını aldık
    hizmet_sinifi = [{"value": item['value'], "label": item['name']} for item in
                     catalog_data_manager.get_all("hizmet_sinifi")]

    # Personel statülerini aldık.
    personel_statu = [{"value": item['value'], "label": item['name']} for item
                      in catalog_data_manager.get_all("personel_statu")]

    # Hitap sebep kodlarını aldık
    sebep_kodlari = [{"value": sk.sebep_no, "label": sk.ad} for sk in HitapSebep.objects.filter()]

    # Başlangıçta görünecek alanlar
    default_alanlar = ['ad', 'soyad', 'cinsiyet', 'dogum_tarihi', 'personel_turu']

    grid_options['data'] = Personel.objects.filter()[0:PAGE_SIZE].values(*default_alanlar)

    alan_filter_type_map = {}

    contains_fields = []
    select_fields = ['cinsiyet', 'kan_grubu', 'medeni_hali', 'personel_turu']
    multiselect_fields = ['baslama_sebep_id', 'birim_id', 'hizmet_sinifi', 'unvan']
    range_date_fields = ['dogum_tarihi', 'em_sonraki_terfi_tarihi', 'emekli_giris_tarihi', 'ga_sonraki_terfi_tarihi',
                         'gorev_suresi_baslama', 'gorev_suresi_bitis', 'goreve_baslama_tarihi',
                         'kh_sonraki_terfi_tarihi', 'mecburi_hizmet_suresi']
    range_int_fields = ['emekli_muktesebat_derece', 'emekli_muktesebat_ekgosterge', 'emekli_muktesebat_kademe',
                        'engel_orani', 'gorev_ayligi_derece', 'gorev_ayligi_ekgosterge', 'gorev_ayligi_kademe',
                        'kazanilmis_hak_derece', 'kazanilmis_hak_ekgosterge', 'kazanilmis_hak_kademe']

    column_defs = []

    for col in column_list:
        col_def = {}
        col_def['field'] = col
        if col in contains_fields:
            col_def['type'] = "INPUT"
            col_def['filter'] = {}
            col_def['filter']['condition'] = "CONTAINS"
            col_def['filter']['placeholder'] = _(u"Contains")
            alan_filter_type_map[col] = "INPUT"
        elif col in select_fields:
            col_def['filter'] = {}
            col_def['type'] = 'SELECT'
            if col == 'cinsiyet':
                sel_opts = cinsiyet
            elif col == 'kan_grubu':
                sel_opts = kan_grubu
            elif col == 'medeni_hali':
                sel_opts = medeni_hal
            else:
                sel_opts = personel_turu
            col_def['filter']['selectOptions'] = sel_opts
            alan_filter_type_map[col] = "SELECT"
        elif col in multiselect_fields:
            col_def['filter'] = {}
            col_def['type'] = 'MULTISELECT'
            if col == 'baslama_sebep_id':
                sel_opts = sebep_kodlari
            elif col == 'birim_id':
                sel_opts = birim
            elif col == 'hizmet_sinifi':
                sel_opts = hizmet_sinifi
            elif col == 'statu':
                sel_opts = personel_statu
            else:
                sel_opts = unvan
            col_def['filter']['selectOptions'] = sel_opts
            alan_filter_type_map[col] = "MULTISELECT"
        elif col in range_date_fields:
            col_def['type'] = 'range'
            col_def['rangeType'] = 'datetime'
            filter_s = {}
            filter_s['condition'] = "START"
            filter_s['placeholder'] = _(u"Start date")
            filter_e = {}
            filter_e['condition'] = "END"
            filter_e['placeholder'] = _(u"End date")
            col_def['filters'] = [filter_s, filter_e]
            alan_filter_type_map[col] = "RANGE-DATETIME"
        elif col in range_int_fields:
            col_def['type'] = "range"
            col_def['rangeType'] = "integer"
            filter_s = {}
            filter_s['condition'] = "MAX"
            filter_s['placeholder'] = _(u"Max value")
            filter_e = {}
            filter_e['condition'] = "MIN"
            filter_e['placeholder'] = _(u"Min value")
            col_def['filters'] = [filter_s, filter_e]
            alan_filter_type_map[col] = "RANGE-INTEGER"
        else:
            col_def['type'] = "INPUT"
            col_def['filter'] = {}
            col_def['filter']['condition'] = "STARTS_WITH"
            col_def['filter']['placeholder'] = _(u"Starts with")
            alan_filter_type_map[col] = "INPUT"
        column_defs.append(col_def)
    grid_options['column_defs'] = column_defs

    selectors = []
    for col in column_list:
        select = {}
        select['name'] = col
        if col == "birim_id":
            select['label'] = _(u"Birim")
        elif col == "baslama_sebep_id":
            select['label'] = _(u"Başlama Sebep")
        else:
            select['label'] = str(Personel.get_field(col).title) if Personel.get_field(col) is not None else col
        select['checked'] = True if col in default_alanlar else False
        selectors.append(select)
    grid_options['selectors'] = selectors

    """
    useExternalSorting: true,  //if need sorting from backend side
    enableFiltering: true,
    toggleFiltering: true,
    useExternalFiltering: true, //if need filtering from backend side
    paginationPageSize: 25,
    useExternalPagination: true, //if need paginations from backend side
    enableAdding: true,
    enableRemoving: true,
    """
    grid_options['enableSorting'] = True
    grid_options['useExternalSorting'] = True
    grid_options['enableFiltering'] = True
    grid_options['toggleFiltering'] = True
    grid_options['useExternalFiltering'] = True
    grid_options['paginationPageSize'] = PAGE_SIZE
    grid_options['paginationCurrentPage'] = 1
    grid_options['useExternalPagination'] = True
    grid_options['enableAdding'] = True
    grid_options['enableRemoving'] = True
    grid_options['page'] = 1
    grid_options['totalItems'] = Personel.objects.count()
    grid_options['options'] = {}
    cache_data['gridOptions'] = grid_options
    cache_data['alan_filter_type_map'] = alan_filter_type_map
    cache_data['time_related_fields'] = range_date_fields

    return cache_data