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
    PAGE_SIZE = 100

    cache_data = {}
    grid_options = {}

    # Gösterilecek alanlar listesi.
    column_list = ['tckn', 'ad', 'soyad', 'dogum_tarihi', 'cinsiyet', 'medeni_hali', 'dogum_yeri',
                   'kan_grubu', 'ana_adi', 'baba_adi', 'brans', 'unvan', 'personel_turu', 'kurum_sicil_no_int',
                   'birim_id', 'baslama_sebep_id', 'kayitli_oldugu_il', 'kayitli_oldugu_ilce',
                   'kayitli_oldugu_mahalle_koy', 'cuzdan_seri', 'cuzdan_seri_no', 'kayitli_oldugu_cilt_no',
                   'kayitli_oldugu_aile_sira_no', 'kayitli_oldugu_sira_no', 'kimlik_cuzdani_verildigi_yer',
                   'kimlik_cuzdani_verilis_nedeni', 'kimlik_cuzdani_kayit_no', 'kimlik_cuzdani_verilis_tarihi',
                   'emekli_sicil_no', 'emekli_giris_tarihi', 'hizmet_sinifi',
                   'kazanilmis_hak_derece', 'kazanilmis_hak_kademe', 'kazanilmis_hak_ekgosterge',
                   'gorev_ayligi_derece', 'gorev_ayligi_kademe', 'gorev_ayligi_ekgosterge',
                   'emekli_muktesebat_derece', 'emekli_muktesebat_kademe', 'emekli_muktesebat_ekgosterge',
                   'kh_sonraki_terfi_tarihi', 'ga_sonraki_terfi_tarihi',   'goreve_baslama_tarihi',
                   'mecburi_hizmet_suresi']

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
    # todo u.key ile göndermek mantıklı olacak, yoksa label'ları kaybediyoruz
    birim = [{"value": u.yoksis_no, "label": u.name} for u in Unit.objects.all()]

    # Unvanları aldık
    unvan = [{"value": item['value'], "label": item['name']} for item in catalog_data_manager.get_all("unvan_kod")]

    # Personel türlerini aldık
    personel_turu = [{"value": item['value'], "label": item['name']} for item in
                     catalog_data_manager.get_all("personel_turu")]

    # Hizmet sınıflarını aldık
    hizmet_sinifi = [{"value": item['value'], "label": item['name'][:10]} for item in
                     catalog_data_manager.get_all("hizmet_sinifi")]

    # Personel statülerini aldık.
    personel_statu = [{"value": item['value'], "label": item['name']} for item
                      in catalog_data_manager.get_all("personel_statu")]

    # Hitap sebep kodlarını aldık
    sebep_kodlari = [{"value": sk.sebep_no, "label": sk.ad if sk.ad is None else sk.ad[:10]} for sk
                     in HitapSebep.objects.all()]

    # Başlangıçta görünecek alanlar
    default_alanlar = ['ad', 'soyad', 'cinsiyet', 'dogum_tarihi', 'personel_turu']

    grid_options['data'] = Personel.objects.all()[0:PAGE_SIZE].values(*default_alanlar)

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
            col_def['filter']['placeholder'] = _(u"İçeren")
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
            filter_s['placeholder'] = _(u"Başlangıç")
            filter_e = {}
            filter_e['condition'] = "END"
            filter_e['placeholder'] = _(u"Bitiş")
            col_def['filters'] = [filter_s, filter_e]
            alan_filter_type_map[col] = "RANGE-DATETIME"
        elif col in range_int_fields:
            col_def['type'] = "range"
            col_def['rangeType'] = "integer"
            filter_s = {}
            filter_s['condition'] = "MAX"
            filter_s['placeholder'] = _(u"En çok")
            filter_e = {}
            filter_e['condition'] = "MIN"
            filter_e['placeholder'] = _(u"En az")
            col_def['filters'] = [filter_s, filter_e]
            alan_filter_type_map[col] = "RANGE-INTEGER"
        else:
            col_def['type'] = "INPUT"
            col_def['filter'] = {}
            col_def['filter']['condition'] = "STARTS_WITH"
            col_def['filter']['placeholder'] = _(u"Başlayan")
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
    grid_options['enableSorting'] = True
    grid_options['enableFiltering'] = True
    grid_options['toggleFiltering'] = True
    grid_options['enableRemoving'] = True
    cache_data['gridOptions'] = grid_options
    cache_data['alan_filter_type_map'] = alan_filter_type_map
    cache_data['time_related_fields'] = range_date_fields
    cache_data['page_size'] = PAGE_SIZE

    return cache_data