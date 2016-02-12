#!/usr/bin/env python
# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from zengine.management_commands import *
from ulakbus.lib.unitime import *

class CreateUser(Command):
    CMD_NAME = 'create_user'
    HELP = 'Creates a new user'
    PARAMS = [
        {'name': 'username', 'required': True, 'help': 'Login username'},
        {'name': 'password', 'required': True, 'help': 'Login password'},
        {'name': 'abstract_role', 'default': 'BaseAbsRole', 'help': 'Name of the AbstractRole'},
        {'name': 'super', 'action': 'store_true', 'help': 'This is a super user'},
        {'name': 'permission_query', 'default': "code:crud* OR code:login* OR code:logout*",
         'help': 'Permissions which will be returned from this query will be granted to the user. '
                 'Defaults to: "code:crud* OR code:login* OR code:logout*"'},
    ]

    def run(self):
        from ulakbus.models import AbstractRole, User, Role, Permission
        if User.objects.filter(username=self.manager.args.username).count():
            print("User already exists!")
            return
        abs_role, new = AbstractRole.objects.get_or_create(name=self.manager.args.abstract_role)
        user = User(username=self.manager.args.username, superuser=self.manager.args.super)
        user.set_password(self.manager.args.password)
        user.save()
        role = Role(user=user, abstract_role=abs_role)
        role.save()
        perm_list = []
        for perm in Permission.objects.raw(self.manager.args.permission_query):
            role.Permissions(permission=perm)
            perm_list.append(perm.name)
        role.save()
        user_type = 'super user' if self.manager.args.super else 'user'
        print("New %s created with these permissions: \n\n%s" % (user_type, "\n".join(perm_list)))


class LoadFixture(Command):
    CMD_NAME = 'load_fixture'
    HELP = 'Load fixtures from given json file or files in given directory and ' \
           'dumps into ulakbus_settings_fixtures bucket, overwriting data of all existing keys.'
    PARAMS = [
        {'name': 'path', 'required': True, 'help': 'Load fixture file or directory'},
    ]

    def run(self):
        from pyoko.db.connection import client
        import os

        fixture_bucket = client.bucket_type('catalog').bucket('ulakbus_settings_fixtures')
        path = self.manager.args.path

        if os.path.isdir(path):
            from glob import glob
            for fixture_file in glob(os.path.join(path, "*.json")):
                self.dump(fixture_file, fixture_bucket)
        else:
            self.dump(path, fixture_bucket)

    @staticmethod
    def dump(fixture_file, fixture_bucket):
        try:
            with open(fixture_file) as f:
                import json
                try:
                    fixtures = json.load(f)
                    for fix in fixtures:
                        f = fixture_bucket.get(fix)
                        f.data = fixtures[fix]
                        print("%s: %s stored.." % (fix, fixtures[fix]))
                        f.store()
                except ValueError as e:
                    print("please validate your json file: %s" % e)
        except IOError:
            print("file not found: %s" % fixture_file)


class GenerateBuildingList(Command):
    CMD_NAME = 'generate_buildings'
    HELP = 'Generates fake Building model objects from Unit Faculties'
    PARAMS = []

    def run(self):
        from tests.fake.building import yeni_bina
        yeni_bina()


class GenerateRandomPersonel(Command):
    CMD_NAME = 'random_personel'
    HELP = 'Generates Random Personel'
    PARAMS = [

        {'name': 'length', 'required': False, 'help': 'Amount of random personel', 'default': 1},

    ]

    def run(self):
        from tests.fake.ogrenci_program import yeni_personel
        length = int(self.manager.args.length)
        yeni_personel(personel_say=length)


class GenerateRandomOkutman(Command):
    CMD_NAME = 'random_okutman'
    HELP = 'Generates Random Okutman From Personel Objects'
    PARAMS = [
        {'name': 'personel', 'required': True, 'help': 'Personel object'},
    ]

    def run(self):
        from tests.fake.ogrenci_program import yeni_okutman
        personel = self.manager.args.personel
        yeni_okutman(personel=personel)


class GenerateRandomHariciOkutman(Command):
    CMD_NAME = 'random_harici_okutman'
    HELP = 'Generates Random Okutman From Personel Objects'
    PARAMS = [

        {'name': 'length', 'required': True, 'help': 'Amount of random harici okutman', 'default': 1},

    ]

    def run(self):
        from tests.fake.ogrenci_program import yeni_harici_okutman
        length = int(self.manager.args.length)
        yeni_harici_okutman(harici_okutman_say=length)


class GenerateRandomOgrenci(Command):
    CMD_NAME = 'random_ogrenci'
    HELP = 'Generates Random Ogrenci Model Objects'
    PARAMS = [
        {'name': 'length', 'required': False, 'help': 'Amount of random ogrenci', 'default': 1},
    ]

    def run(self):
        from tests.fake.ogrenci_program import yeni_ogrenci
        length = int(self.manager.args.length)
        yeni_ogrenci(ogrenci_say=length)


class GenerateProgramList(Command):
    CMD_NAME = 'generate_programs'
    HELP = 'Generates Program Records From Unit Object'
    PARAMS = [
        {'name': 'length', 'required': False, 'help': 'Amount of random program', 'default': 1},
        {'name': 'yoksis_program', 'required': True, 'help': 'Unit object'},
    ]

    def run(self):
        from tests.fake.ogrenci_program import yeni_program
        length = int(self.manager.args.length)
        yoksis_program = self.manager.args.yoksis_program
        yeni_program(yoksis_program=yoksis_program, program_say=length)


class GenerateDersList(Command):
    CMD_NAME = 'generate_ders'
    HELP = 'Generates fake Ders model objects'
    PARAMS = [
        {'name': 'length', 'required': False, 'help': 'Amount of random program', 'default': 1},
        {'name': 'program', 'required': True, 'help': 'Program object'},
        {'name': 'personel', 'required': True, 'help': 'Personel object'},
    ]

    def run(self):
        from tests.fake.ogrenci_program import yeni_ders
        length = int(self.manager.args.length)
        personel = self.manager.args.personel
        program = self.manager.args.program
        yeni_ders(program=program, personel=personel, ders_say=length)

environ['PYOKO_SETTINGS'] = 'ulakbus.settings'
environ['ZENGINE_SETTINGS'] = 'ulakbus.settings'

if __name__ == '__main__':
    ManagementCommands()
