# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import defaultdict
import random
from uuid import uuid4
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
                    self.add_crud(model_data, user_type, results)
        return results

    def add_crud(self, model_data, user_type, results):
        model = model_registry.get_model(model_data['name'])
        field_name = model_data.get('field', user_type + '_id')
        verbose_name = model_data.get('verbose_name', model.Meta.verbose_name_plural)
        category = model_data.get('category', DEFAULT_CATEGORY)
        results[user_type].append({"text": verbose_name,
                                   "wf": model_data.get('wf', "crud"),
                                   "model": model_data['name'],
                                   "kategori": category,
                                   "param": field_name})

    def get_workflow_menus(self):
        results = defaultdict(list)
        for wf in get_workflows():
            if self.current.has_permission(wf.spec.name):
                self.add_wf(wf, results)
        return results

    def add_wf(self, wf, results):
        category = wf.spec.wf_properties.get("menu_category", 'Genel')
        object_of_wf = wf.spec.wf_properties.get('object', 'other')
        if category != 'hidden':
            results[object_of_wf].append({"text": wf.spec.wf_name,
                                          "wf": wf.spec.name,
                                          "kategori": category,
                                          "param": "id"}
                                         )


from ulakbus.models import Personel, Ogrenci


class Search(BaseView):
    def __init__(self, *args, **kwargs):
        self.query = kwargs.pop('query')
        super(Search, self).__init__(*args)
        self.output['results'] = []
        self.do_search()

    def do_search(self):
        try:
            tckn = int(self.query.strip())
            objects = self.SEARCH_ON.objects.filter(tckn='%s*' % tckn)
        except:
            q = self.query.replace(' ', '\ ')
            objects = self.SEARCH_ON.objects.raw("ad:*%s* OR soyad:*%s*" % (q, q))
        for o in objects:
            self.output['results'].append(("%s %s" % (o.ad, o.soyad), o.tckn, o.key, ''))


class SearchStudent(Search):
    SEARCH_ON = Ogrenci


class SearchPerson(Search):
    SEARCH_ON = Personel


def get_random_msg():
    msgs = [{'type': 1, 'title': 'İşlem tamamlandı',
             'body': 'Uzun süren işlem başarıyla tamamlandı',
             'url': '#yeni_personel/?t=%s' % uuid4().hex},
            {'type': 2, 'title': 'Yeni İleti', 'body': 'Dene Mem\'den mesajınız var',
             'url': '#show_msg/?t=%s' % uuid4().hex},
            {'type': 3, 'title': 'Hata', 'body': 'Ulakbus ölümcül bir hatadan kurtarıldı!',
             'url': ''}
            ]
    return msgs[random.randrange(0, len(msgs))]


class Notification(BaseView):
    def __init__(self, current):
        super(Notification, self).__init__(current)

        if 'read' in current.input:
            self.mark_as_read()

        notifies = self.current.msg_cache.get_all()
        self.output['notifications'] = list(notifies)

    def mark_as_read(self):
        read_messages = self.current.input['read']
        for msg in read_messages:
            self.current.msg_cache.remove_item(msg)
