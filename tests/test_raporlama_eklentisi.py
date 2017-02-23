# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.cache import RaporlamaEklentisi
from ulakbus.models import Personel
from zengine.current import Current
from zengine.lib.test_utils import BaseTestCase
import datetime
from pyoko.manage import FlushDB, LoadData
from ulakbus.views.personel.raporlama_ui_grid_view import get_report_data


class TestCase(BaseTestCase):
    def test_rapor_query(self):
        random_key = 'some_random_key'
        raporlama_cache = RaporlamaEklentisi(random_key).get_or_set()
        page = raporlama_cache['gridOptions']['paginationPageSize']

        a = "01.01.1950"
        b = "01.01.1980"
        a_ = datetime.date(1950, 01, 01)
        b_ = datetime.date(1980, 01, 01)

        selectors = [{"name": "ad", "checked": True}, {"name": "soyad", "checked": True},
                     {"name": "cinsiyet", "checked": True},
                     {"name": "dogum_tarihi", "checked": True},
                     {"name": "unvan", "checked": True}]

        options1 = {
            "ad": {"condition": "STARTS_WITH", "value": "M"},
            "cinsiyet": {"value": "1"},
            "unvan": {3975: "3975", 42647: "42647"},
            "dogum_tarihi": {"start": a, "end": b}
        }

        query1 = {
            "view": "_zops_get_report_data",
            "selectors": selectors,
            "options": options1,
            "page": 1
        }

        current = Current()
        current.input = query1

        get_report_data(current)

        db_cnt = len(Personel.objects.filter(ad__startswith="M", cinsiyet=1,
                                             unvan__in=[3975, 42647],
                                             dogum_tarihi__range=[a_, b_]))

        if db_cnt > page:
            assert len(current.output['gridOptions']['data']) == page
        else:
            assert len(current.output['gridOptions']['data']) == db_cnt

        options2 = {"ad": {"condition": "STARTS_WITH", "value": "Ah"}, "cinsiyet": {"value": "2"},
                    "unvan": {1: "1", 2: "2"}, "dogum_tarihi": {"start": a, "end": b}}

        query2 = {"view": "_zops_get_report_data", "selectors": selectors, "options": options2,
                  "page": 1}

        current.input = query2

        get_report_data(current)

        db_cnt = len(Personel.objects.filter(ad__startswith="Ah", cinsiyet=2,
                                             unvan__in=[1, 2],
                                             dogum_tarihi__range=[a_, b_]))

        if db_cnt > page:
            assert len(current.output['gridOptions']['data']) == page
        else:
            assert len(current.output['gridOptions']['data']) == db_cnt

        options3 = {"cinsiyet": {"value": "2"}, "dogum_tarihi": {"start": a, "end": b}}
        query3 = {"view": "_zops_get_report_data", "selectors": selectors, "options": options3,
                  "page": 1}

        current.input = query3

        get_report_data(current)

        db_cnt = len(Personel.objects.filter(cinsiyet=2, dogum_tarihi__range=[a_, b_]))

        if db_cnt > page:
            assert len(current.output['gridOptions']['data']) == page
        else:
            assert len(current.output['gridOptions']['data']) == db_cnt

        options4 = {"cinsiyet": {"value": "1"}, "dogum_tarihi": {"start": a, "end": b},
                    "unvan": {3975: "3975", 42647: "42647"}}
        query4 = {"view": "_zops_get_report_data", "selectors": selectors, "options": options4,
                  "page": 1}

        current.input = query4

        get_report_data(current)

        db_cnt = len(Personel.objects.filter(cinsiyet=1, unvan__in=[3975, 42647],
                                             dogum_tarihi__range=[a_, b_]))

        if db_cnt > page:
            assert len(current.output['gridOptions']['data']) == page
        else:
            assert len(current.output['gridOptions']['data']) == db_cnt
