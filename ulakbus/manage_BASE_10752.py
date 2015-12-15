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


class GenerateRandomOkutman(Command):
    CMD_NAME = 'random_okutman'
    HELP = 'Generates Random Okutmans'
    PARAMS = [
        {'name': 'length', 'required': True, 'help': 'Amount of random okutman'},
    ]

    def run(self):
        from tests.fake.personel import yeni_personel
        length = int(self.manager.args.length)
        for x in range(0, length):
            yeni_personel()


class ExportRoomsToXml(Command):
    CMD_NAME = 'export_rooms'
    HELP = 'Generates Unitime XML import file for rooms'
    PARAMS = []

    def run(self):
        import os
        import datetime
        from lxml import etree
        from ulakbus.models import *
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        campuses = Campus.objects.filter()

        # create XML
        for campus in campuses:
            if campus.building_set:
                root = etree.Element('buildingsRooms', campus="%s" % uni, term="%s" % term.ad, \
                                     year="%s" % term.baslangic_tarihi.year)
                for building in campus.building_set:
                    buildingel = etree.SubElement(root, 'building', externalId="%s" % building.building.key, \
                                                  abbreviation="%s" % building.building.code, \
                                                  locationX="%s" % building.building.coordinate_x, \
                                                  locationY="%s" % building.building.coordinate_y, \
                                                  name="%s" % building.building.name)
                    if building.building.room_set:

                        for room in building.building.room_set:
                            etree.SubElement(buildingel, 'room', externalId="%s" % room.room.key, \
                                             locationX="%s" % building.building.coordinate_x, \
                                             locationY="%s" % building.building.coordinate_y, \
                                             roomNumber="%s" % room.room.code, \
                                             roomClassification="%s" % room.room.room_type.type, \
                                             capacity="%s" % room.room.capacity, instructional="True")

        # pretty string

        s = etree.tostring(root, pretty_print=True)
        current_date = datetime.datetime.now()
        directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
        outDirectory = root_directory+'/bin/dphs/data_exchange/'+directory_name
        if not os.path.exists(outDirectory):
            os.makedirs(outDirectory)
        outFile = open(outDirectory+'/buildingRoomImport.xml', 'w+')
        outFile.write("%s" % s)
        print "Dosya %s dizini altina kayit edilmistir" % outDirectory

environ['PYOKO_SETTINGS'] = 'ulakbus.settings'
environ['ZENGINE_SETTINGS'] = 'ulakbus.settings'

if __name__ == '__main__':
    ManagementCommands()
