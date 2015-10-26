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

DEFAULT_CATEGORY = 'Genel'

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
                    crud_path = 'crud/%s/' % model_data['name']
                    category = model_data.get('category', DEFAULT_CATEGORY)
                    results[user_type].append({"text": verbose_name,
                                               "url": crud_path,
                                               "kategori": category,
                                               "param": field_name})
        return results

    def get_workflow_menus(self):
        get_wf_menu = lambda: ({"text": wf.spec.wf_name,
                                "url": '/%s' % wf.spec.name,
                                "kategori": category,
                                "param": "id"})
        results = defaultdict(list)
        for wf in get_workflows():
            if self.current.has_permission(wf.spec.name):
                category = wf.spec.wf_properties.get("menu_category", DEFAULT_CATEGORY)
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

        def do_search(self, obj):
            try:
                tckn = int(self.query.strip())
                objects = obj.objects.filter(tckn='%s*' % tckn)
            except:
                q = self.query.replace(' ', '\ ')
                objects = obj.objects.raw("ad:*%s* OR soyad:*%s*" % (q, q))
            for o in objects:
                self.output['results'].append(("%s %s" % (o.ad, o.soyad), o.tckn, o.key, ''))


class SearchStudent(Search):
    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        self.do_search(Personel)


class SearchPerson(Search):
    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        self.do_search(Ogrenci)


class Notification(BaseView):
    def __init__(self, current):
        super(Notification, self).__init__(current)
        self.output['notifications'] = self.current.msg_cache.get_all()
