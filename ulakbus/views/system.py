# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import defaultdict
from pyoko.model import model_registry
from zengine.auth.permissions import get_workflows
from zengine.views.base import BaseView
from zengine.config import settings


class Menu(BaseView):
    def __init__(self, current):
        super(Menu, self).__init__(current)
        result = self.get_crud_menus()
        for k, v in self.get_workflow_menus().items():
            result[k].extend(v)
        self.output.update(result)

    def get_crud_menus(self):
        results = defaultdict(list)
        for user_type in settings.CRUD_MENUS:
            for model_data in settings.CRUD_MENUS[user_type]:
                if self.current.has_permission(model_data['name']):
                    model = model_registry.get_model(model_data['name'])
                    field_name = model_data['field'] if 'field' in model_data else user_type
                    verbose_name = (model_data['verbose_name'] if 'verbose_name' in model_data
                                    else model.Meta.verbose_name_plural)
                    crud_path = 'crud/%s/?%s=' % (model_data['name'], field_name)
                    results[user_type].append((verbose_name, crud_path))
        return results

    def get_workflow_menus(self):
        get_wf_menu = lambda: (wf.spec.wf_name, '/%s?id=' % wf.spec.name)
        results = defaultdict(list)
        for wf in get_workflows():
            if self.current.has_permission(wf.spec.name):
                if 'object' in wf.spec.wf_properties:
                    results[wf.spec.wf_properties['object']].append(get_wf_menu())
                else:
                    results['other'].append(get_wf_menu())
        return results

from ulakbus.models import Personel, Ogrenci
class Search(BaseView):
    def __init__(self, current, query):
        super(Search, self).__init__(current)
        self.query = query
        self.output['results'] = []
        self.do_search()

class SearchStudent(Search):
    def do_search(self):
        try:
            tckn = int(self.query.strip())
            objects = Ogrenci.objects.filter(tckn=tckn)
        except:
            objects = Ogrenci.objects.raw('ad:*%s* OR soyad:*%s*' % (self.query, self.query))
        for o in objects:
            self.output['results'].append(("%s %s" % (o.ad, o.soyad), o.tckn, o.key, ''))


class SearchPerson(Search):
    def do_search(self):
        try:
            tckn = int(self.query.strip())
            objects = Personel.objects.filter(tckn=tckn)
        except:
            objects = Personel.objects.raw('ad:*%s* OR soyad:*%s*' % (self.query, self.query))
        for o in objects:
            self.output['results'].append(("%s %s" % (o.ad, o.soyad), o.tckn, o.key, ''))



