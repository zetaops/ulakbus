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

        raporlama_cache = RaporlamaEklentisi().get_or_set()
        page = raporlama_cache['gridOptions']['paginationPageSize']
        p = 1

        a = "01.01.1950"
        b = "01.01.1980"
        a_= datetime.date(1950, 01, 01)
        b_= datetime.date(1980, 01, 01)

        selectors = [{"name": "ad", "checked": True}, {"name": "soyad", "checked": True},
                     {"name": "cinsiyet", "checked": True}, {"name": "dogum_tarihi", "checked": True},
                     {"name": "unvan", "checked": True}]

        query1 = {}
        options1 = {}
        options1["ad"] = {"condition": "STARTS_WITH", "value": "M"}
        options1["cinsiyet"] = {"value": "1"}
        options1["unvan"] = {3975: "3975", 42647: "42647"}
        options1["dogum_tarihi"] = {"start": a, "end": b}
        query1["view"] = "_zops_get_report_data"
        query1["selectors"] = selectors
        query1["options"] = options1
        query1["page"] = p

        current = Current()
        current.input = query1

        get_report_data(current)

        db_cnt = len(Personel.objects.filter(ad__startswith="M", cinsiyet=1,
                                                                          unvan__in=[3975, 42647],
                                                                          dogum_tarihi__range=[a_, b_]))

        if db_cnt > page:
            assert len(current.output['data']) == page
        else:
            assert len(current.output['data']) == db_cnt

        query2 = {}
        options2 = {}
        options2["ad"] = {"condition": "STARTS_WITH", "value": "Ah"}
        options2["cinsiyet"] = {"value": "2"}
        options2["unvan"] = {1: "1", 2: "2"}
        options2["dogum_tarihi"] = {"start": a, "end": b}
        query2["view"] = "_zops_get_report_data"
        query2["selectors"] = selectors
        query2["options"] = options2
        query2["page"] = p

        current.input = query2

        get_report_data(current)

        db_cnt = len(Personel.objects.filter(ad__startswith="Ah", cinsiyet=2,
                                                                          unvan__in=[1, 2],
                                                                          dogum_tarihi__range=[a_, b_]))

        if db_cnt > page:
            assert len(current.output['data']) == page
        else:
            assert len(current.output['data']) == db_cnt

        query3 = {}
        options3 = {}
        options3["cinsiyet"] = {"value": "2"}
        options3["dogum_tarihi"] = {"start": a, "end": b}
        query3["view"] = "_zops_get_report_data"
        query3["selectors"] = selectors
        query3["options"] = options3
        query3["page"] = p

        current.input = query3

        get_report_data(current)

        db_cnt = len(Personel.objects.filter(cinsiyet=2, dogum_tarihi__range=[a_, b_]))

        if db_cnt > page:
            assert len(current.output['data']) == page
        else:
            assert len(current.output['data']) == db_cnt

        query4 = {}
        options4 = {}
        options4["cinsiyet"] = {"value": "1"}
        options4["dogum_tarihi"] = {"start": a, "end": b}
        options4["unvan"] = {3975: "3975", 42647: "42647"}
        query4["view"] = "_zops_get_report_data"
        query4["selectors"] = selectors
        query4["options"] = options4
        query4["page"] = p

        current.input = query4

        get_report_data(current)

        db_cnt = len(Personel.objects.filter(cinsiyet=1, unvan__in=[3975, 42647],
                                                                          dogum_tarihi__range=[a_, b_]))

        if db_cnt > page:
            assert len(current.output['data']) == page
        else:
            assert len(current.output['data']) == db_cnt








