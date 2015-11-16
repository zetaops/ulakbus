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
                    model = model_registry.get_model(model_data['name'])
                    field_name = model_data.get('field', user_type + '_id')
                    verbose_name = (model_data['verbose_name'] if 'verbose_name' in model_data
                                    else model.Meta.verbose_name_plural)
                    crud_path = 'crud/%s' % model_data['name']
                    category = model_data.get('category', DEFAULT_CATEGORY)
                    results[user_type].append({"text": verbose_name,
                                               "url": crud_path,
                                               "wf": "crud",
                                               "model": model_data['name'],
                                               "kategori": category,
                                               "param": field_name})
                # else:
                #     print("NONONONON PERM FOR CRUD PERM %s" % model_data['name'])
                #     print(self.current.get_permissions())
        return results

    def get_workflow_menus(self):
        get_wf_menu = lambda: ({"text": wf.spec.wf_name,
                                "url": '/%s' % wf.spec.name,
                                "wf": wf.spec.name,
                                "kategori": category,
                                "param": "id"})
        results = defaultdict(list)
        for wf in get_workflows():
            if self.current.has_permission(wf.spec.name):
                category = wf.spec.wf_properties.get("menu_category")
                if category:
                    if 'object' in wf.spec.wf_properties:
                        results[wf.spec.wf_properties['object']].append(get_wf_menu())
                    else:
                        results['other'].append(get_wf_menu())
            # else:
            #     print("NONONONON PERM FOR %s" % wf.spec.name)
        return results


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
            read_messages = current.input['read']
            for msg in read_messages:
                current.msg_cache.remove_item(msg)
        notifies = self.current.msg_cache.get_all()
        # if not notifies:
        #     notifies = [get_random_msg()]
        self.output['notifications'] = list(notifies)
