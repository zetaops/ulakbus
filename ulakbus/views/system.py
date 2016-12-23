# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko.modelmeta import model_registry
from pyoko.conf import settings

from ulakbus.views.reports import ReporterRegistry
from zengine.views.base import SysView
from ulakbus.models import Personel, Ogrenci
from zengine.views.menu import Menu


class Search(SysView):
    SEARCH_ON = None
    PATH = None

    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        self.query = self.current.input['query']
        self.output['results'] = []
        self.do_search()

    def do_search(self):
        try:
            tckn = int(self.query.strip())
            objects = self.SEARCH_ON.objects.filter(
                tckn__startswith=tckn).values('ad', 'soyad', 'tckn', 'key')
        except ValueError:
            q = self.query.split(" ")
            objects = []
            if len(q) == 1:
                # query Ali, Ayşe, Demir gibi boşluksuz bir string
                # içeriyorsa, ad ve soyad içerisinde aranmalıdır.
                objects = self.SEARCH_ON.objects.search_on(
                    'ad', 'soyad', contains=q[0]).values('ad', 'soyad', 'tckn', 'key')

            if len(q) > 1:
                # query Ali Rıza, Ayşe Han Demir, Neşrin Hasibe Gül Yakuphanoğullarından
                # gibi boşluklu cok parçali bir string ise, öncelikle son parça soyad ile
                # `contains`, önceki parçalar ise isim ile `contains` şeklinde
                # aranmalıdır. Sonuç bulunamaz ise tüm parçalar isim ile
                # `contains` şeklinde aranmalıdır.

                objects = self.SEARCH_ON.objects.search_on(
                    'ad', contains=" ".join(q[:-1])).search_on(
                    'soyad', contains=q[-1]).values('ad', 'soyad', 'tckn', 'key')

                objects_by_name = []
                if not objects:
                    objects = self.SEARCH_ON.objects.search_on(
                        'ad', contains=" ".join(q)).values('ad', 'soyad', 'tckn', 'key')

        self.output['results'] = [("{ad} {soyad}".format(**o), o['tckn'], o['key'], '') for o in
                                  objects]


# @basic_view('ogrenci_ara')
class SearchStudent(Search):
    PATH = 'ogrenci_ara'
    SEARCH_ON = Ogrenci


class SearchPerson(Search):
    PATH = 'personel_ara'
    SEARCH_ON = Personel


class GetCurrentUser(SysView):
    PATH = 'get_current_user'

    def __init__(self, current):
        super(GetCurrentUser, self).__init__(current)
        self.output['current_user'] = {}
        self.getUser(current.user)

    def getUser(self, userObject):
        currentUser = {
            "name": userObject.name,
            "surname": userObject.surname,
            "username": userObject.username,
            "roles": [{"role": role.__unicode__()} for role in userObject.role_set]
        }
        self.output['current_user'] = currentUser


class UlakbusMenu(Menu):
    PATH = 'dashboard'

    def __init__(self, current):
        super(UlakbusMenu, self).__init__(current)
        self.add_reporters()
        self.add_user_data()
        self.add_settings()
        self.add_admin_crud()

    def add_admin_crud(self):
        if self.current.user.superuser:
            for mdl in model_registry.get_base_models():
                self.output['other'].append({
                    "text": mdl.Meta.verbose_name_plural,
                    "wf": 'crud',
                    "model": mdl.__name__,
                    "kategori": 'Admin'})

    def add_settings(self):
        self.output['settings'] = {
            'static_url': settings.S3_PUBLIC_URL,
        }

    def add_user_data(self):
        # add data of current logged in user
        usr = self.current.user
        role = self.current.role
        usr_total_roles = [{"role": roleset.role.__unicode__()} for roleset in
                      self.current.user.role_set]
        self.output['current_user'] = {
            "name": usr.name,
            "surname": usr.surname,
            "username": usr.username,
            "role": self.current.role.abstract_role.name,
            "avatar": usr.get_avatar_url(),
            "is_staff": role.is_staff,
            "is_student": role.is_student,
            "roles": usr_total_roles,
            "role_details": {'unit_name': role.unit.name,
                             'abs_name': role.abstract_role.name,
                             'role_count': len(usr_total_roles)}
        }
        if role.is_student:
            # insert student specific data here
            self.output['current_user'].update({
            })

        elif role.is_staff:
            # insert staff specific data here
            self.output['current_user'].update({
            })

    def add_reporters(self):
        for mdl in ReporterRegistry.get_reporters():
            perm = "report.%s" % mdl['model']
            if self.current.has_permission(perm):
                self.output['other'].append(mdl)
