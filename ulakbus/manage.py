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

        {'name': 'length', 'required': True, 'help': 'Amount of random personel'},

    ]

    def run(self):
        from tests.fake.personel import yeni_personel
        length = int(self.manager.args.length)
        for x in range(0, length):
            yeni_personel()


class GenerateRandomOkutman(Command):
    CMD_NAME = 'random_okutman'
    HELP = 'Generates Random Okutman From Personel Objects'
    PARAMS = [

        {'name': 'length', 'required': True, 'help': 'Amount of random okutman'},

    ]

    def run(self):
        from tests.fake.okutman import yeni_okutman
        length = int(self.manager.args.length)
        for x in range(0, length):
            yeni_okutman()


class GenerateRandomHariciOkutman(Command):
    CMD_NAME = 'random_harici_okutman'
    HELP = 'Generates Random Okutman From Personel Objects'
    PARAMS = [

        {'name': 'length', 'required': True, 'help': 'Amount of random okutman'},

    ]

    def run(self):
        from tests.fake.harici_okutman import yeni_harici_okutman
        length = int(self.manager.args.length)
        for x in range(0, length):
            yeni_harici_okutman()


class GenerateRandomOogrenci(Command):
    CMD_NAME = 'random_ogrenci'
    HELP = 'Generates Random Ogrenci Model Objects'
    PARAMS = [
        {'name': 'length', 'required': True, 'help': 'Amount of random ogrenci'},
    ]

    def run(self):
        from tests.fake.ogrenci import yeni_ogrenci
        length = int(self.manager.args.length)
        for x in range(0, length):
            yeni_ogrenci()


class GenerateProgramList(Command):
    CMD_NAME = 'generate_programs'
    HELP = 'Generates Programs From Unit Model'
    PARAMS = []

    def run(self):
        from tests.fake.program import yeni_program
        yeni_program()


class GenerateDersList(Command):
    CMD_NAME = 'generate_ders'
    HELP = 'Generates fake Ders model objects'
    PARAMS = []

    def run(self):
        from tests.fake.ders import yeni_ders
        yeni_ders()


class ExportRoomsToXml(Command):
    CMD_NAME = 'export_rooms'
    HELP = 'Generates Unitime XML import file for rooms'
    PARAMS = []

    def run(self):
        import os
        import datetime
        from lxml import etree
        from ulakbus.models import Donem, Unit, Campus
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        campuses = Campus.objects.filter()
        doc_type = '<!DOCTYPE buildingsRooms PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/BuildingRoom.dtd">'

        # create XML
        for campus in campuses:
            if campus.building_set:
                root = etree.Element('buildingsRooms', campus="%s" % uni, term="%s" % term.ad, \
                                     year="%s" % term.baslangic_tarihi.year)
                for building in campus.building_set:

                    buildingelement = etree.SubElement(root, 'building', externalId="%s" % building.building.key, \
                                                       abbreviation="%s" % building.building.code, \
                                                       locationX="%s" % building.building.coordinate_x, \
                                                       locationY="%s" % building.building.coordinate_y, \
                                                       name="%s" % building.building.name)
                    if building.building.room_set:

                        for room in building.building.room_set:
                            roomelement = etree.SubElement(buildingelement, 'room', externalId="%s" % room.room.key, \
                                             locationX="%s" % building.building.coordinate_x, \
                                             locationY="%s" % building.building.coordinate_y, \
                                             roomNumber="%s" % room.room.code, \
                                             roomClassification="%s" % room.room.room_type.type, \
                                             capacity="%s" % room.room.capacity, instructional="True")

                            if room.room.RoomDepartments:
                                roommdepartments = etree.SubElement(roomelement, 'roomDepartments')
                                for department in room.room.RoomDepartments:
                                    etree.SubElement(roommdepartments, 'assigned', departmentNumber="%s" % department.unit.yoksis_no, percent="100")

        # pretty string

        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)
        current_date = datetime.datetime.now()
        directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
        export_directory = root_directory + '/bin/dphs/data_exchange/' + directory_name
        if not os.path.exists(export_directory):
            os.makedirs(export_directory)
        out_file = open(export_directory + '/buildingRoomImport.xml', 'w+')
        out_file.write("%s" % s)
        print("Dosya %s dizini altina kayit edilmistir" % export_directory)


class ExportSessionsToXml(Command):
    CMD_NAME = 'export_sessions'
    HELP = 'Generates Unitime XML import file for academic sessions'
    PARAMS = []

    def run(self):
        import os
        import datetime
        from lxml import etree
        from ulakbus.models import Donem, Unit, Campus
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        campuses = Campus.objects.filter()
        sessions = Donem.objects.filter()
        doc_type = '<!DOCTYPE session PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Session.dtd">'

        # create XML
        for campus in campuses:
            if campus:

                root = etree.Element('session', campus="%s" % uni, term="%s" % term.ad, \
                                     year="%s" % term.baslangic_tarihi.year, dateFormat="M/d/y")
                for session in sessions:
                    start_date = session.baslangic_tarihi.strftime("%m/%d/%Y")
                    end_date = session.bitis_tarihi.strftime("%m/%d/%Y")
                    etree.SubElement(root, 'sessionDates', beginDate="%s" % start_date, endDate="%s" % end_date, \
                                     classesEnd="%s" % end_date, examBegin="%s" % start_date, \
                                     eventBegin="%s" % start_date, eventEnd="%s" % end_date)
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)
        current_date = datetime.datetime.now()
        directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
        export_directory = root_directory + '/bin/dphs/data_exchange/' + directory_name
        if not os.path.exists(export_directory):
            os.makedirs(export_directory)
        out_file = open(export_directory + '/sessionImport.xml', 'w+')
        out_file.write("%s" % s)
        print("Dosya %s dizini altina kayit edilmistir" % export_directory)


class ExportDepartmentsToXML(Command):
    CMD_NAME = 'export_departments'
    HELP = 'Generates Unitime XML import file for academic departments'
    PARAMS = []

    def run(self):
        import os
        import datetime
        from lxml import etree
        from ulakbus.models import Donem, Unit, Campus
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        units = Unit.objects.filter(unit_type='Bölüm')
        campuses = Campus.objects.filter()
        sessions = Donem.objects.filter()
        doc_type = '<!DOCTYPE departments PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Department.dtd">'

        # create XML
        for campus in campuses:
            if campus:
                root = etree.Element('departments', campus="%s" % uni, term="%s" % term.ad, \
                                     year="%s" % term.baslangic_tarihi.year)
            for unit in units:
                etree.SubElement(root, 'department', externalId="%s" % unit.key, \
                                 abbreviation="%s" % unit.yoksis_no, name="%s" % unit.name, \
                                 deptCode="%s" % unit.yoksis_no, allowEvents="true")
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)
        current_date = datetime.datetime.now()
        directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
        export_directory = root_directory + '/bin/dphs/data_exchange/' + directory_name
        if not os.path.exists(export_directory):
            os.makedirs(export_directory)
        out_file = open(export_directory + '/departmentImport.xml', 'w+')
        out_file.write("%s" % s)
        print("Dosya %s dizini altina kayit edilmistir" % export_directory)


class ExportAcademicSubjectsToXML(Command):
    CMD_NAME = 'export_academic_subjects'
    HELP = 'Generates Unitime XML import file for academic subjects'
    PARAMS = []

    def run(self):
        import os
        import datetime
        from lxml import etree
        from ulakbus.models import Donem, Campus, Program, Unit
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        units = Unit.objects.filter(unit_type='Bölüm')
        campuses = Campus.objects.filter()
        sessions = Donem.objects.filter()
        doc_type = '<!DOCTYPE subjectAreas PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/SubjectArea.dtd">'

        # create XML
        for campus in campuses:
            if campus:
                root = etree.Element('subjectAreas', campus="%s" % uni, term="%s" % term.ad,
                                     year="%s" % term.baslangic_tarihi.year)
            for unit in units:
                subunits = Unit.objects.filter(parent_unit_no=unit.yoksis_no)
                for subunit in subunits:
                    etree.SubElement(root, 'subjectArea', externalId="%s" % subunit.key,
                                    abbreviation="%s" % subunit.yoksis_no, title="%s" % subunit.name,
                                    department="%s" % subunit.parent_unit_no)
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)
        current_date = datetime.datetime.now()
        directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
        export_directory = root_directory + '/bin/dphs/data_exchange/' + directory_name
        if not os.path.exists(export_directory):
            os.makedirs(export_directory)
        out_file = open(export_directory + '/subjectAreaImport.xml', 'w+')
        out_file.write("%s" % s)
        print("Dosya %s dizini altina kayit edilmistir" % export_directory)


class ExportStaffToXML(Command):
    CMD_NAME = 'export_staff'
    HELP = 'Generates Unitime XML import file for staff'
    PARAMS = []

    def run(self):
        import os
        import datetime
        from lxml import etree
        from ulakbus.models import Donem, Unit, Campus, Okutman
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        units = Unit.objects.filter()
        campuses = Campus.objects.filter()
        sessions = Donem.objects.filter()
        stafflist = Okutman.objects.filter()
        doc_type = '<!DOCTYPE staff PUBLIC "-//UniTime//UniTime Staff Import DTD/EN" "http://www.unitime.org/interface/Staff.dtd">'

        for campus in campuses:
            if campus:
                root = etree.Element('staff', campus="%s" % uni, term="%s" % term.ad, \
                                     year="%s" % term.baslangic_tarihi.year)
            for staffmember in stafflist:
                unvan = self.acadTitle(title=staffmember.unvan)

                etree.SubElement(root, 'staffMember', externalId="%s" % staffmember.key, \
                                 firstName="%s" % staffmember.ad, lastName="%s" % staffmember.soyad, \
                                 department="%s" % staffmember.birim_no, acadTitle="%s" % unvan[0], \
                                 positionType="%s" % unvan[1])
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)
        current_date = datetime.datetime.now()
        directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
        export_directory = root_directory + '/bin/dphs/data_exchange/' + directory_name
        if not os.path.exists(export_directory):
            os.makedirs(export_directory)
        out_file = open(export_directory + '/staffImport.xml', 'w+')
        out_file.write("%s" % s)
        print("Dosya %s dizini altina kayit edilmistir" % export_directory)

    @staticmethod
    def acadTitle(title):
        if title == 1:
            return ["Professor", "Prof"]
        elif title == 2:
            return ["Associate Professor", "Ass. Prof"]
        elif title == 3:
            return ["Research Assistant", "Res. Assist."]
        elif title == 4:
            return ["Lecturer", "Lect."]
        else:
            return ["", ""]


class ExportStudentInfoToXML(Command):
    CMD_NAME = 'export_student_info'
    HELP = 'Generates Unitime XML import file for student info'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]

    def run(self):
        import os
        import datetime
        from lxml import etree
        from ulakbus.models import Donem, Ogrenci, Unit
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        doc_type = '<!DOCTYPE students PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Student.dtd">'

        # FIX for default row size in pyoko filter
        batch_size = int(self.manager.args.batch_size)
        count = Ogrenci.objects.count()
        rounds = int(count / batch_size) + 1

        root = etree.Element('students', campus="%s" % uni, term="%s" % term.ad, year="%s" % term.baslangic_tarihi.year)
        # FIX for default row size in pyoko filter
        for i in range(rounds):
            for student in Ogrenci.objects.set_params(rows=1000, start=i * batch_size).filter():
                # for student in students:
                etree.SubElement(root, 'student', externalId="%s" % student.key, firstName="%s" % student.ad,
                                 lastName="%s" % student.soyad,
                                 email="%s" % student.e_posta)
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)

        if len(s):

            current_date = datetime.datetime.now()
            directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
            export_directory = root_directory + '/bin/dphs/data_exchange/' + directory_name
            if not os.path.exists(export_directory):
                os.makedirs(export_directory)
            out_file = open(export_directory + '/studentInfoImport.xml', 'w+')
            out_file.write("%s" % s)
            print("Dosya %s dizini altina kayit edilmistir" % export_directory)

        else:
            print("Bir Hata Oluştu ve XML Dosyası Yaratılamadı")


class ExportCourseCatalogToXML(Command):
    CMD_NAME = 'export_course_catalog'
    HELP = 'Generates Unitime XML import file for course catalog'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]

    def run(self):
        import os
        import datetime
        from lxml import etree
        from ulakbus.models import Donem, Ogrenci, Unit, Ders
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        doc_type = '<!DOCTYPE courseCatalog PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/CourseCatalog.dtd">'

        batch_size = int(self.manager.args.batch_size)
        count = Ders.objects.count()
        rounds = int(count / batch_size) + 1

        root = etree.Element('courseCatalog', campus="%s" % uni, term="%s" % term.ad,
                             year="%s" % term.baslangic_tarihi.year)
        # FIX for default row size in pyoko filter
        for i in range(rounds):
            for ders in Ders.objects.set_params(rows=1000, start=i * batch_size).filter():
                # for student in students:
                derselement = etree.SubElement(root, 'course', externalId="%s" % ders.key, courseNumber="%s" % ders.kod,
                                               subject="%s" % ders.program.yoksis_no,
                                               title="%s" % ders.ad)
                etree.SubElement(derselement, 'courseCredit', creditType="collegiate", creditUnitType="semesterHours",
                                 creditFormat="fixedUnit", fixedCredit="%s" % ders.yerel_kredisi)
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)

        if len(s):

            current_date = datetime.datetime.now()
            directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
            export_directory = root_directory + '/bin/dphs/data_exchange/' + directory_name
            if not os.path.exists(export_directory):
                os.makedirs(export_directory)
            out_file = open(export_directory + '/courseCatalogImport.xml', 'w+')
            out_file.write("%s" % s)
            print("Dosya %s dizini altina kayit edilmistir" % export_directory)

        else:
            print("Bir Hata Oluştu ve XML Dosyası Yaratılamadı")


class ExportCurriculaToXML(Command):
    CMD_NAME = 'export_curricula'
    HELP = 'Generates Unitime XML import file for curricula'
    PARAMS = []

    def run(self):

        import os
        import datetime
        from lxml import etree
        from ulakbus.models import Donem, Ogrenci, Unit, Ders, Program
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        program_list = Program.objects.filter()

        '''
        academicAreas Import File
        '''

        academic_area_doc_type = '<!DOCTYPE academicAreas PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/AcademicArea.dtd">'
        academic_classification_doc_type = '<!DOCTYPE academicClassifications PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/AcademicClassification.dtd">'
        pos_major_doc_type = '<!DOCTYPE posMajors PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/PosMajor.dtd">'
        doc_type = '<!DOCTYPE curricula PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Curricula_3_2.dtd">'

        current_date = datetime.datetime.now()
        directory_name = current_date.strftime('%d_%m_%Y_%H_%M_%S')
        export_directory = root_directory + '/bin/dphs/data_exchange/' + directory_name
        if not os.path.exists(export_directory):
            os.makedirs(export_directory)

        academic_area_root = etree.Element('academicAreas', campus="%s" % uni, term="%s" % term.ad,
                                           year="%s" % term.baslangic_tarihi.year)
        etree.SubElement(academic_area_root, 'academicArea', abbreviation='A', externalId='A', title="%s" % uni+' - '+term.ad)

        academic_area_string = etree.tostring(academic_area_root, pretty_print=True, xml_declaration=True,
                                              encoding='UTF-8', doctype="%s" % academic_area_doc_type)
        out_file = open(export_directory + '/academicAreaImport.xml', 'w+')
        out_file.write("%s" % academic_area_string)
        print("Academic Area Import dosyası %s dizini altina kayit edilmistir" % export_directory)

        '''
        academicClassifications Import File
        '''

        academic_classification_root = etree.Element('academicClassifications', campus="%s" % uni, term="%s" % term.ad,
                                                     year="%s" % term.baslangic_tarihi.year)
        etree.SubElement(academic_classification_root, 'academicClassification', externalId="01", code="01", name="01")
        academic_classification_string = etree.tostring(academic_classification_root, pretty_print=True,
                                                        xml_declaration=True, encoding='UTF-8',
                                                        doctype="%s" % academic_classification_doc_type)
        out_file = open(export_directory + '/academicClassificationImport.xml', 'w+')
        out_file.write("%s" % academic_classification_string)
        print("Academic Classification Import dosyası %s dizini altina kayit edilmistir" % export_directory)


        '''
        posMajors Import File
        '''
        pos_major_root = etree.Element('posMajors', campus="%s" % uni, term="%s" % term.ad,
                                                     year="%s" % term.baslangic_tarihi.year)
        etree.SubElement(pos_major_root, 'posMajor', externalId="M1", code="M1",
                         name="%s Major 1" % term.baslangic_tarihi.year, academicArea="A")
        pos_major_string = etree.tostring(pos_major_root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                                        doctype="%s" % academic_classification_doc_type)
        out_file = open(export_directory + '/posMajorImport.xml', 'w+')
        out_file.write("%s" % pos_major_string)
        print("Pos Major Import dosyası %s dizini altina kayit edilmistir" % export_directory)


        '''
        curricula Import File
        '''

        root = etree.Element('curricula', campus="%s" % uni, term="%s" % term.ad,
                             year="%s" % term.baslangic_tarihi.year)
        # major = etree.SubElement(curriculum, 'major', code='M3')
        for program in program_list:
            ders_list = Ders.objects.filter(program=program).count()
            if ders_list:
                parent_yoksis_no = Unit.objects.filter(yoksis_no=program.yoksis_no)[0].parent_unit_no
                #bolum = Unit.objects.filter(yoksis_no=parent_yoksis_no,unit_type='Bölüm')[0]
                curriculum = etree.SubElement(root, 'curriculum')
                etree.SubElement(curriculum, 'academicArea', abbreviation='A')
                etree.SubElement(curriculum, 'department', code="%s" % parent_yoksis_no)
                etree.SubElement(curriculum, 'major', code="M1")
                classification = etree.SubElement(curriculum, 'classification', name="01", enrollment='2')
                etree.SubElement(classification, 'academicClassification', code="01")
                for program_ders in Ders.objects.filter(program=program):
                    etree.SubElement(classification, 'course', subject="%s" % program.yoksis_no,
                                     courseNbr="%s" % program_ders.kod)
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)

        if len(s):
            out_file = open(export_directory + '/curricula.xml', 'w+')
            out_file.write("%s" % s)
            print("Dosya %s dizini altina kayit edilmistir" % export_directory)

        else:
            print("Bir Hata Oluştu ve XML Dosyası Yaratılamadı")


environ['PYOKO_SETTINGS'] = 'ulakbus.settings'
environ['ZENGINE_SETTINGS'] = 'ulakbus.settings'

if __name__ == '__main__':
    ManagementCommands()
