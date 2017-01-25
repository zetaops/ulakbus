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

import json


def raporlama_ekrani_secim_menulerini_hazirla():

    personel_fixture_file = open('fixtures/personel.json')
    personel_fixture_str = personel_fixture_file.read()
    personel_fixture = dict(json.loads(personel_fixture_str))
    personel_fixture_file.close()

    hitap_fixture_file = open('fixtures/hitap_fixtures.json')
    hitap_fixture_str = hitap_fixture_file.read()
    hitap_fixture = dict(json.loads(hitap_fixture_str))
    hitap_fixture_file.close()

    hitap_unvan_kod_fixture_file = open('fixtures/hitap_unvankod_fixtures.json')
    hitap_unvan_kod_fixture_str = hitap_unvan_kod_fixture_file.read()
    hitap_unvan_kod_fixture = dict(json.loads(hitap_unvan_kod_fixture_str))
    hitap_unvan_kod_fixture_file.close()

    cache_data = {}

    # Personel modelindeki alanların isimlerini aldık.

    sakincali = ['arsiv', 'aday_memur', 'kadro_derece', 'deleted', 'user', 'updated_at', 'save_meta_data', 'deleted_at',
                 'timestamp', 'durum', 'gorunen_kazanilmis_hak_kademe', 'gorunen_gorev_ayligi_kademe',
                 'gorunen_emekli_muktesebat_kademe', 'atama', 'kadro', 'sicil_no', 'kurum_ici_gorevlendirme',
                 'kurum_disi_gorevlendirme', 'kurum_sicil_no']

    members = [attr for attr in tuple(set(dir(Personel)) - set(dir(Model))) if not callable(attr)
               and not attr.startswith("__") and not attr.startswith("_") and not attr.startswith("M")
               and not attr.endswith("_id") and (attr not in sakincali)]

    personel_fields = dict((name,
              str(Personel.get_field(name).title) if Personel.get_field(name) is not None else Personel.get_link(field=name)[
                  'verbose']) for name in members)

    personel_fields['birim'] = str(Unit().get_verbose_name())
    personel_fields['baslama_sebep'] = str(HitapSebep().get_verbose_name())

    cache_data['personel'] = personel_fields

    # Cinsiyet türlerini fixture dosyasından aldık

    cinsiyet = {}
    for cins in hitap_fixture['cinsiyet'].items():
        cinsiyet[cins[0]] = cins[1]['tr']
    cache_data['cinsiyet'] = cinsiyet

    # Medeni hal türlerini fixture dosyasından aldık
    medeni_hal = {}
    for mh in hitap_fixture['medeni_hali'].items():
        medeni_hal[mh[0]] = mh[1]['tr']
    cache_data['medeni_hali'] = medeni_hal

    # Birimleri aldık
    birim = []
    for u in Unit.objects.filter():
        birim.append(u.name)
    cache_data['birim'] = birim

    # Unvanları aldık
    unvan = {}
    for un in hitap_unvan_kod_fixture['unvan_kod'].items():
        unvan[un[0]] = un[1]['tr']
    cache_data['unvan'] = unvan

    # Personel türlerini aldık
    personel_turu = {}
    for pt in personel_fixture['personel_turu'].items():
        personel_turu[pt[0]] = pt[1]['tr']
    cache_data['personel_turu'] = personel_turu

    # Hizmet sınıflarını aldık
    hizmet_sinifi = {}
    for hs in hitap_fixture['hizmet_sinifi'].items():
        hizmet_sinifi[hs[0]] = hs[1]['tr']
    cache_data['hizmet_sinifi'] = hizmet_sinifi

    # Personel statülerini aldık.
    personel_statu = {}
    for ps in personel_fixture['personel_statu'].items():
        personel_statu[ps[0]] = ps[1]['tr']
    cache_data['personel_statu'] = personel_statu

    # Hitap sebep kodlarını aldık
    sebep_kodlari = {}
    for sk in HitapSebep.objects.filter():
        sebep_kodlari[sk.sebep_no] = sk.ad
    cache_data['baslama_sebep'] = sebep_kodlari

    # Baslangıçta görünecek personeller
    personeller = {}
    tum_personel = Personel.objects.filter()
    for i in range(30):
        personeller[i] = tum_personel[i].clean_value()
    cache_data['personeller'] = personeller

    # Başlangıçta görünecek alanlar
    default_alanlar = {
        'ad': personel_fields['ad'],
        'soyad': personel_fields['soyad'],
        'cinsiyet': personel_fields['cinsiyet'],
        'dogum_tarihi': personel_fields['dogum_tarihi'],
        'personel_turu': personel_fields['personel_turu']
    }

    cache_data['default_alanlar'] = default_alanlar

    return cache_data



