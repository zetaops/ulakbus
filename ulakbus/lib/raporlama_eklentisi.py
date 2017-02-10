# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Personel
from ulakbus.models.auth import Unit
from ulakbus.models.hitap.hitap_sebep import HitapSebep
from pyoko.model import Model
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus import settings

import json


def raporlama_ekrani_secim_menulerini_hazirla():

    personel_fixture_file = open(settings.PROJECT_PATH + '/ulakbus/fixtures/personel.json')
    personel_fixture_str = personel_fixture_file.read()
    personel_fixture = dict(json.loads(personel_fixture_str))
    personel_fixture_file.close()

    hitap_fixture_file = open(settings.PROJECT_PATH + '/ulakbus/fixtures/hitap_fixtures.json')
    hitap_fixture_str = hitap_fixture_file.read()
    hitap_fixture = dict(json.loads(hitap_fixture_str))
    hitap_fixture_file.close()

    hitap_unvan_kod_fixture_file = open(settings.PROJECT_PATH + '/ulakbus/fixtures/hitap_unvankod_fixtures.json')
    hitap_unvan_kod_fixture_str = hitap_unvan_kod_fixture_file.read()
    hitap_unvan_kod_fixture = dict(json.loads(hitap_unvan_kod_fixture_str))
    hitap_unvan_kod_fixture_file.close()

    cache_data = {}
    grid_options = {}

    # Personel modelindeki alanların isimlerini aldık.

    sakincali = ['arsiv', 'aday_memur', 'kadro_derece', 'deleted', 'user', 'updated_at', 'save_meta_data', 'deleted_at',
                 'timestamp', 'durum', 'gorunen_kazanilmis_hak_kademe', 'gorunen_gorev_ayligi_kademe',
                 'gorunen_emekli_muktesebat_kademe', 'atama', 'kadro', 'sicil_no', 'kurum_ici_gorevlendirme',
                 'kurum_disi_gorevlendirme', 'kurum_sicil_no', 'biyografi']

    members = [attr for attr in tuple(set(dir(Personel)) - set(dir(Model))) if not callable(attr)
               and not attr.startswith("__") and not attr.startswith("_") and not attr.startswith("M")
               and not attr.endswith("_id") and (attr not in sakincali)]

    personel_fields = dict((name,
              str(Personel.get_field(name).title) if Personel.get_field(name) is not None else Personel.get_link(field=name)[
                  'verbose']) for name in members)

    personel_fields['birim'] = str(Unit().get_verbose_name())
    personel_fields['baslama_sebep'] = str(HitapSebep().get_verbose_name())

    # Cinsiyet türlerini fixture dosyasından aldık

    cinsiyet = {}
    for cins in hitap_fixture['cinsiyet'].items():
        cinsiyet[cins[0]] = cins[1]['tr']

    # Kan grupları için choices oluşturduk

    kan_grubu = {}
    kan_grubu['1'] = '0Rh-'
    kan_grubu['2'] = '0Rh+'
    kan_grubu['3'] = 'ARh-'
    kan_grubu['4'] = 'ARh+'
    kan_grubu['5'] = 'BRh-'
    kan_grubu['6'] = 'BRh+'
    kan_grubu['7'] = 'ABRh-'
    kan_grubu['8'] = 'ABRh+'

    # Medeni hal türlerini fixture dosyasından aldık
    medeni_hal = {}
    for mh in hitap_fixture['medeni_hali'].items():
        medeni_hal[mh[0]] = mh[1]['tr']

    # Birimleri aldık
    birim = {}
    for u in Unit.objects.filter():
        birim[u.yoksis_no] = u.name

    # Unvanları aldık
    unvan = {}
    for un in hitap_unvan_kod_fixture['unvan_kod'].items():
        unvan[un[0]] = un[1]['tr']

    # Personel türlerini aldık
    personel_turu = {}
    for pt in personel_fixture['personel_turu'].items():
        personel_turu[pt[0]] = pt[1]['tr']

    # Hizmet sınıflarını aldık
    hizmet_sinifi = {}
    for hs in hitap_fixture['hizmet_sinifi'].items():
        hizmet_sinifi[hs[0]] = hs[1]['tr']

    # Personel statülerini aldık.
    personel_statu = {}
    for ps in personel_fixture['personel_statu'].items():
        personel_statu[ps[0]] = ps[1]['tr']

    # Hitap sebep kodlarını aldık
    sebep_kodlari = {}
    for sk in HitapSebep.objects.filter():
        sebep_kodlari[sk.sebep_no] = sk.ad

    # Baslangıçta görünecek personeller
    personeller = {}
    tum_personel = Personel.objects.filter()
    if len(tum_personel) > 50:
        for i in range(50):
            personeller[i] = tum_personel[i].clean_value()
    else:
        for i, p in enumerate(tum_personel):
            personeller[i] = p.clean_value()

    # Başlangıçta görünecek alanlar
    default_alanlar = ['ad', 'soyad', 'cinsiyet', 'dogum_tarihi', 'personel_turu']

    alan_filter_type_map = {}

    contains_fields = ['adres_2', 'ikamet_adresi', 'notlar', 'projeler', 'verdigi_dersler', 'yayinlar']
    select_fields = ['cinsiyet', 'kan_grubu', 'medeni_hali', 'personel_turu']
    multiselect_fields = ['baslama_sebep', 'birim', 'hizmet_sinifi', 'statu', 'unvan']
    range_date_fields = ['dogum_tarihi', 'em_sonraki_terfi_tarihi', 'emekli_giris_tarihi', 'ga_sonraki_terfi_tarihi',
                         'gorev_suresi_baslama', 'gorev_suresi_bitis', 'goreve_baslama_tarihi',
                         'kh_sonraki_terfi_tarihi', 'mecburi_hizmet_suresi']
    range_int_fields = ['emekli_muktesebat_derece', 'emekli_muktesebat_ekgosterge', 'emekli_muktesebat_kademe',
                        'engel_orani', 'gorev_ayligi_derece', 'gorev_ayligi_ekgosterge', 'gorev_ayligi_kademe',
                        'kazanilmis_hak_derece', 'kazanilmis_hak_ekgosterge', 'kazanilmis_hak_kademe']

    column_defs = []

    for k, v in personel_fields.items():
        col_def = {}
        col_def['field'] = k
        if k in contains_fields:
            col_def['type'] = "INPUT"
            col_def['filter'] = {}
            col_def['filter']['condition'] = "CONTAINS"
            col_def['filter']['placeholder'] = _(u"Contains")
            alan_filter_type_map[k] = "INPUT"
        elif k in select_fields:
            col_def['filter'] = {}
            col_def['filter']['term'] = ''  # todo term ne?
            col_def['type'] = 'SELECT'
            if k == 'cinsiyet':
                sel_opts = get_selection_options(cinsiyet)
            elif k == 'kan_grubu':
                sel_opts = get_selection_options(kan_grubu)
            elif k == 'medeni_hali':
                sel_opts = get_selection_options(medeni_hal)
            else:
                sel_opts = get_selection_options(personel_turu)
            col_def['filter']['selectOptions'] = sel_opts
            alan_filter_type_map[k] = "SELECT"
        elif k in multiselect_fields:
            col_def['filter'] = {}
            col_def['type'] = 'MULTISELECT'
            if k == 'baslama_sebep':
                sel_opts = get_selection_options(sebep_kodlari)
            elif k == 'birim':
                sel_opts = get_selection_options(birim)
            elif k == 'hizmet_sinifi':
                sel_opts = get_selection_options(hizmet_sinifi)
            elif k == 'statu':
                sel_opts = get_selection_options(personel_statu)
            else:
                sel_opts = get_selection_options(unvan)
            col_def['filter']['selectOptions'] = sel_opts
            alan_filter_type_map[k] = "MULTISELECT"
        elif k in range_date_fields:
            col_def['type'] = 'range'
            col_def['rangeType'] = 'datetime'
            filter_s = {}
            filter_s['condition'] = "START"
            filter_s['placeholder'] = _(u"Start date")
            filter_e = {}
            filter_e['condition'] = "END"
            filter_e['placeholder'] = _(u"End date")
            col_def['filters'] = [filter_s, filter_e]
            alan_filter_type_map[k] = "RANGE-DATETIME"
        elif k in range_int_fields:
            col_def['type'] = "range"
            col_def['rangeType'] = "integer"
            filter_s = {}
            filter_s['condition'] = "MAX"
            filter_s['placeholder'] = _(u"Max value")
            filter_e = {}
            filter_e['condition'] = "MIN"
            filter_e['placeholder'] = _(u"Min value")
            col_def['filters'] = [filter_s, filter_e]
            alan_filter_type_map[k] = "RANGE-INTEGER"
        else:
            col_def['type'] = "INPUT"
            col_def['filter'] = {}
            col_def['filter']['condition'] = "STARTS_WITH"
            col_def['filter']['placeholder'] = _(u"Starts with")
            alan_filter_type_map[k] = "INPUT"
        column_defs.append(col_def)
    grid_options['column_defs'] = column_defs

    selectors = []
    for k, v in personel_fields.items():
        select = {}
        select['name'] = k
        select['checked'] = True if k in default_alanlar else False
        selectors.append(select)
    grid_options['selectors'] = selectors

    initial_data = []
    for pi, pp in personeller.items():
        per = {}
        for d in default_alanlar:
            per[d] = pp[d]
        initial_data.append(per)
    grid_options['initialData'] = initial_data

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
    grid_options['paginationPageSize'] = True
    grid_options['useExternalPagination'] = True
    grid_options['enableAdding'] = True
    grid_options['enableRemoving'] = True
    cache_data['gridOptions'] = grid_options
    cache_data['alan_filter_type_map'] = alan_filter_type_map
    cache_data['time_related_fields'] = range_date_fields

    return cache_data


def get_selection_options(items_d):
    """
    Takes a dictionary and returns a list of dict which is in form of:
        [
            { value: 'key1', label: 'value1' },
            { value: 'key2', label: 'value2' },
             ...
        ]
    """
    items_ = []
    for k, v in items_d.items():
        item = {}
        item['value'] = k
        item['label'] = v
        items_.append(item)
    return items_


