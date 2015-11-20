#!/usr/bin/env python
# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from zengine.management_commands import *

class CreateUser(Command):
    CMD_NAME = 'create_user'
    HELP = 'Creates a new user'
    PARAMS = [
        {'name':  'username', 'required': True, 'help': 'Login username'},
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
        role = Role(user=user, abstract_role=abs_role).save()
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


environ['PYOKO_SETTINGS'] = 'ulakbus.settings'
environ['ZENGINE_SETTINGS'] = 'ulakbus.settings'

if __name__ == '__main__':
    ManagementCommands()
