# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import random
from uuid import uuid4
from zengine.views.base import BaseView
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
            # objects = self.SEARCH_ON.objects.raw("ad:*%s* OR soyad:*%s*" % (q, q))
            objects = self.SEARCH_ON.objects.search_on('ad', 'soyad', contains=q)
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
