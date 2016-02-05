# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import os
from zengine.management_commands import *
from lxml import etree
from ulakbus.lib.directory import create_unitime_export_directory
from ulakbus.models import Donem, Ogrenci, Unit, Sube, Ders, Program, OgrenciProgram, OgrenciDersi

class ExportRoomsToXml(Command):
    CMD_NAME = 'export_rooms'
    HELP = 'Generates Unitime XML import file for rooms'
    PARAMS = []

    def run(self):

        from ulakbus.models import Donem, Unit, Campus
        root_directory = os.path.dirname(os.path.abspath(__file__))
        term = Donem.objects.filter(guncel=True)[0]
        uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        campuses = Campus.objects.filter()
        doc_type = '<!DOCTYPE buildingsRooms PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/BuildingRoom.dtd">'

        # create XML
        for campus in campuses:
            if campus.building_set:
                root = etree.Element('buildingsRooms', campus="%s" % uni, term="%s" % term.ad,
                                     year="%s" % term.baslangic_tarihi.year)
                for building in campus.building_set:

                    buildingelement = etree.SubElement(root, 'building',
                                                       externalId="%s" % building.building.key,
                                                       abbreviation="%s" % building.building.code,
                                                       locationX="%s" % building.building.coordinate_x,
                                                       locationY="%s" % building.building.coordinate_y,
                                                       name="%s" % building.building.name)
                    if building.building.room_set:

                        for room in building.building.room_set:
                            roomelement = etree.SubElement(buildingelement, 'room',
                                                           externalId="%s" % room.room.key,
                                                           locationX="%s" % building.building.coordinate_x,
                                                           locationY="%s" % building.building.coordinate_y,
                                                           roomNumber="%s" % room.room.code,
                                                           roomClassification="%s" % room.room.room_type.type,
                                                           capacity="%s" % room.room.capacity,
                                                           instructional="True")

                            if room.room.RoomDepartments:
                                roommdepartments = etree.SubElement(roomelement, 'roomDepartments')
                                for department in room.room.RoomDepartments:
                                    etree.SubElement(roommdepartments, 'assigned',
                                                     departmentNumber="%s" % department.unit.yoksis_no,
                                                     percent="100")

        # pretty string

        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                           doctype="%s" % doc_type)
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

                root = etree.Element('session', campus="%s" % uni, term="%s" % term.ad,
                                     year="%s" % term.baslangic_tarihi.year, dateFormat="M/d/y")
                for session in sessions:
                    start_date = session.baslangic_tarihi.strftime("%m/%d/%Y")
                    end_date = session.bitis_tarihi.strftime("%m/%d/%Y")
                    etree.SubElement(root, 'sessionDates', beginDate="%s" % start_date,
                                     endDate="%s" % end_date,
                                     classesEnd="%s" % end_date, examBegin="%s" % start_date,
                                     eventBegin="%s" % start_date, eventEnd="%s" % end_date)
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                           doctype="%s" % doc_type)
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
                root = etree.Element('departments', campus="%s" % uni, term="%s" % term.ad,
                                     year="%s" % term.baslangic_tarihi.year)
            for unit in units:
                etree.SubElement(root, 'department', externalId="%s" % unit.key,
                                 abbreviation="%s" % unit.yoksis_no, name="%s" % unit.name,
                                 deptCode="%s" % unit.yoksis_no, allowEvents="true")
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                           doctype="%s" % doc_type)
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
                                     abbreviation="%s" % subunit.yoksis_no,
                                     title="%s" % subunit.name,
                                     department="%s" % subunit.parent_unit_no)
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                           doctype="%s" % doc_type)
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
                root = etree.Element('staff', campus="%s" % uni, term="%s" % term.ad,
                                     year="%s" % term.baslangic_tarihi.year)
            for staffmember in stafflist:
                unvan = self.acadTitle(title=staffmember.unvan)
                staff_dep = staffmember.birim_no
                if staffmember.birim_no:
                    staff_dep = Unit.objects.filter(yoksis_no=staffmember.birim_no)[0].parent_unit_no

                etree.SubElement(root, 'staffMember', externalId="%s" % staffmember.key, \
                                 firstName="%s" % staffmember.ad, lastName="%s" % staffmember.soyad, \
                                 department="%s" % staff_dep, acadTitle="%s" % unvan[0], \
                                 positionType="%s" % unvan[1])
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                           doctype="%s" % doc_type)
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

        root = etree.Element('students', campus="%s" % uni, term="%s" % term.ad,
                             year="%s" % term.baslangic_tarihi.year)
        # FIX for default row size in pyoko filter
        for i in range(rounds):
            for student in Ogrenci.objects.set_params(rows=1000, start=i * batch_size).filter():
                # for student in students:
                etree.SubElement(root, 'student', externalId="%s" % student.key,
                                 firstName="%s" % student.ad,
                                 lastName="%s" % student.soyad,
                                 email="%s" % student.e_posta)
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                           doctype="%s" % doc_type)

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
                derselement = etree.SubElement(root, 'course', externalId="%s" % ders.key,
                                               courseNumber="%s" % ders.kod,
                                               subject="%s" % ders.program.yoksis_no,
                                               title="%s" % ders.ad)
                etree.SubElement(derselement, 'courseCredit', creditType="collegiate",
                                 creditUnitType="semesterHours",
                                 creditFormat="fixedUnit", fixedCredit="%s" % ders.yerel_kredisi)
        # pretty string
        s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                           doctype="%s" % doc_type)

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

        export_directory = create_unitime_export_directory()
        academic_area_doc_type = '<!DOCTYPE academicAreas PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/AcademicArea.dtd">'
        academic_classification_doc_type = '<!DOCTYPE academicClassifications PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/AcademicClassification.dtd">'
        pos_major_doc_type = '<!DOCTYPE posMajors PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/PosMajor.dtd">'
        doc_type = '<!DOCTYPE curricula PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Curricula_3_2.dtd">'

        try:

            term = Donem.objects.filter(guncel=True)[0]
            uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
            program_list = Program.objects.filter()

            """
            academicAreas Import File

            """



            academic_area_root = etree.Element('academicAreas', campus="%s" % uni, term="%s" % term.ad,
                                               year="%s" % term.baslangic_tarihi.year)
            etree.SubElement(academic_area_root, 'academicArea', abbreviation='A', externalId='A',
                             title="%s" % uni + ' - ' + term.ad)

            academic_area_string = etree.tostring(academic_area_root, pretty_print=True,
                                                  xml_declaration=True,
                                                  encoding='UTF-8',
                                                  doctype="%s" % academic_area_doc_type)
            out_file = open(export_directory + '/academicAreaImport.xml', 'w+')
            out_file.write("%s" % academic_area_string)

            print("Academic Area Import dosyası %s dizini altina kayit edilmistir" % export_directory)

            """
            academicClassifications Import File

            """

            academic_classification_root = etree.Element('academicClassifications', campus="%s" % uni,
                                                         term="%s" % term.ad,
                                                         year="%s" % term.baslangic_tarihi.year)
            etree.SubElement(academic_classification_root, 'academicClassification', externalId="01",
                             code="01", name="01")
            academic_classification_string = etree.tostring(academic_classification_root,
                                                            pretty_print=True,
                                                            xml_declaration=True, encoding='UTF-8',
                                                            doctype="%s" % academic_classification_doc_type)
            out_file = open(export_directory + '/academicClassificationImport.xml', 'w+')
            out_file.write("%s" % academic_classification_string)

            print("Academic Classification Import dosyası %s dizini altina kayit edilmistir" % export_directory)

            """
            posMajors Import File

            """

            pos_major_root = etree.Element('posMajors', campus="%s" % uni, term="%s" % term.ad,
                                           year="%s" % term.baslangic_tarihi.year)
            etree.SubElement(pos_major_root, 'posMajor', externalId="M1", code="M1",
                             name="%s Major 1" % term.baslangic_tarihi.year, academicArea="A")
            pos_major_string = etree.tostring(pos_major_root, pretty_print=True, xml_declaration=True,
                                              encoding='UTF-8',
                                              doctype="%s" % academic_classification_doc_type)
            out_file = open(export_directory + '/posMajorImport.xml', 'w+')
            out_file.write("%s" % pos_major_string)

            print("Pos Major Import dosyası %s dizini altina kayit edilmistir" % export_directory)

            """
            curricula Import File

            """

            root = etree.Element('curricula', campus="%s" % uni, term="%s" % term.ad,
                                 year="%s" % term.baslangic_tarihi.year)
            for program in program_list:
                ders_list = Ders.objects.filter(program=program).count()
                if ders_list:
                    parent_yoksis_no = Unit.objects.filter(yoksis_no=program.yoksis_no)[0].parent_unit_no
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
            s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                               doctype="%s" % doc_type)

            if len(s):
                out_file = open(export_directory + '/curricula.xml', 'w+')
                out_file.write("%s" % s)
                print("Dosya %s dizini altina kayit edilmistir" % export_directory)

            else:
                print("Bir Hata Oluştu ve XML Dosyası Yaratılamadı")

        except Exception as e:
            print(e.message)



class ExportStudentCourseDemandsToXML(Command):
    CMD_NAME = 'export_student_course_demands'
    HELP = 'Generates Unitime XML import file for student course demands'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]

    def run(self):

        export_directory = create_unitime_export_directory()
        doc_type = '<!DOCTYPE lastLikeCourseDemand PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/StudentCourse.dtd">'

        try:

            term = Donem.objects.filter(guncel=True)[0]
            uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
            program_list = Program.objects.filter()

            '''
            lastLikeCourseDemand Import File
            '''

            root = etree.Element('lastLikeCourseDemand', campus="%s" % uni, term="%s" % term.ad,
                                 year="%s" % term.baslangic_tarihi.year)

            batch_size = int(self.manager.args.batch_size)
            count = Ogrenci.objects.count()
            rounds = int(count / batch_size) + 1

            for i in range(rounds):
                for student in Ogrenci.objects.set_params(rows=1000, start=i * batch_size).filter():
                    student_department_list = OgrenciProgram.objects.filter(ogrenci=student)
                    if (student_department_list):
                        student_element = etree.SubElement(root, "student", externalId="%s" % student.key)
                        for department in student_department_list:
                            for ogrenci_ders in OgrenciDersi.objects.filter(ogrenci_program=department):
                                if (ogrenci_ders):
                                    ders = ogrenci_ders.ders.ders
                                    etree.SubElement(student_element, 'studentCourse', externalId="%s" % ders.key,
                                                     courseNumber="%s" % ders.kod,
                                                     subject="%s" % ders.program.yoksis_no)
            # pretty string
            s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)
            if len(s):

                out_file = open(export_directory + '/studentCrsDemandImport.xml', 'w+')
                out_file.write("%s" % s)
                print("Dosya %s dizini altina kayit edilmistir" % export_directory)

            else:
                print("Bir Hata Oluştu ve XML Dosyası Yaratılamadı")

        except Exception as e:
            print(e.message)


class ExportStudentCoursesToXML(Command):
    CMD_NAME = 'export_student_courses'
    HELP = 'Generates Unitime XML import file for student courses'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]

    def run(self):

        export_directory = create_unitime_export_directory()
        doc_type = '<!DOCTYPE studentEnrollments PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/StudentEnrollment.dtd">'

        try:

            term = Donem.objects.filter(guncel=True)[0]
            uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
            program_list = Program.objects.filter()

            '''
            studentEnrollments Import File
            '''

            root = etree.Element('studentEnrollments', campus="%s" % uni, term="%s" % term.ad,
                                 year="%s" % term.baslangic_tarihi.year)

            batch_size = int(self.manager.args.batch_size)
            count = Ogrenci.objects.count()
            rounds = int(count / batch_size) + 1

            for i in range(rounds):
                for student in Ogrenci.objects.set_params(rows=1000, start=i * batch_size).filter():
                    student_department_list = OgrenciProgram.objects.filter(ogrenci=student)
                    if (student_department_list):
                        student_element = etree.SubElement(root, "student", externalId="%s" % student.key,
                                                           firstName="%s" % student.ad, lastName="%s" % student.soyad,
                                                           email="%s" % student.e_posta)
                        for department in student_department_list:
                            for ogrenci_ders in OgrenciDersi.objects.filter(ogrenci_program=department):
                                if (ogrenci_ders):
                                    ders = ogrenci_ders.ders.ders
                                    etree.SubElement(student_element, 'class', externalId="%s" % ders.key,
                                                     courseNbr="%s" % ders.kod,
                                                     subject="%s" % ders.program.yoksis_no, type="Lec", suffix="1")
            # pretty string
            s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', doctype="%s" % doc_type)

            if len(s):

                out_file = open(export_directory + '/studentEnrollments.xml', 'w+')
                out_file.write("%s" % s)
                print("Dosya %s dizini altina kayit edilmistir" % export_directory)
            else:
                print("Bir Hata Oluştu ve XML Dosyası Yaratılamadı")

        except Exception as e:
            print (e.message)

class ExportStudentEnrollmentsToXML(Command):
    CMD_NAME = 'export_student_enrollments'
    HELP = 'Generates Unitime XML import file for student enrollments'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]

    def run(self):


        export_directory = create_unitime_export_directory()
        student_enrollments_doc_type = '<!DOCTYPE studentEnrollments PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/StudentEnrollment.dtd">'

        batch_size = int(self.manager.args.batch_size)
        count = Ogrenci.objects.count()
        rounds = int(count / batch_size) + 1

        """
        StudentEnrollments Import File

        """

        try:
            term = Donem.objects.filter(guncel=True)[0]
            uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
            root = etree.Element('studentEnrollments', campus="%s" % uni, term="%s" % term.ad,
                                 year="%s" % term.baslangic_tarihi.year)
            for i in range(rounds):
                for student in Ogrenci.objects.set_params(rows=1000, start=i * batch_size).filter():
                    student_element = etree.SubElement(root, 'student',
                                                       externalId="%s" % student.key,
                                                       firstName="%s" % student.ad,
                                                       lastName="%s" % student.soyad,
                                                       email="%s" % student.e_posta)
                    student_program_list = OgrenciProgram.objects.filter(ogrenci=student)
                    for program in student_program_list:
                        for ders in OgrenciDersi.objects.filter(ogrenci_program=program):
                            lecture = ders.ders
                            etree.SubElement(student_element, 'class', courseId="%s" % lecture.key,
                                             courseNumber="%s" % lecture.ders.kod,
                                             subject="%s" % lecture.ders.program.yoksis_no,
                                             type="Lec")

            # pretty string
            s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                               doctype="%s" % student_enrollments_doc_type)

            if len(s):
                out_file = open(export_directory + '/StudentEnrollments.xml', 'w+')
                out_file.write("%s" % s)
                print("Dosya %s dizini altina kayit edilmistir" % export_directory)
            else:
                print("Bir Hata Oluştu ve XML Dosyası Yaratılamadı")
        except Exception as e:
            print(e.message)


class ExportClassesToXML(Command):
    CMD_NAME = 'export_classes'
    HELP = 'Generates Unitime XML import file for timetable'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]

    def run(self):

        export_directory = create_unitime_export_directory()
        student_enrollments_doc_type = '<!DOCTYPE timetable PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/CourseTimetable.dtd">'

        """
        courseTimetableImport Import File

        """

        try:
            term = Donem.objects.filter(guncel=True)[0]
            uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
            batch_size = int(self.manager.args.batch_size)
            count = Sube.objects.filter(donem=term).count()
            rounds = int(count / batch_size) + 1
            root = etree.Element('timetable', campus="%s" % uni, term="%s" % term.ad,
                                 year="%s" % term.baslangic_tarihi.year, action="insert",
                                 instructors="false",
                                 notes="false", prefer="id", timeFormat="HHmm",
                                 dateFormat="yyyy/M/d")

            for i in range(rounds):
                for sube in Sube.objects.set_params(rows=1000, start=i * batch_size).filter(
                        donem=term):
                    lecture = sube.ders
                    etree.SubElement(root, 'class', name="%s" % sube.ad,
                                     courseNbr="%s" % lecture.kod,
                                     subject="%s" % lecture.program.yoksis_no,
                                     type="Lec")
            # pretty string
            s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                               doctype="%s" % student_enrollments_doc_type)

            if len(s):
                out_file = open(export_directory + '/courseTimetableImport.xml', 'w+')
                out_file.write("%s" % s)
                print("Dosya %s dizini altina kayit edilmistir" % export_directory)
            else:
                print("Bir Hata Oluştu ve XML Dosyası Yaratılamadı")
        except Exception as e:
            print(e.message)


class ExportCorseOfferingsToXML(Command):
    CMD_NAME = 'export_course_offerings'
    HELP = 'Generates Unitime XML import file for timetable'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]

    def run(self):

        export_directory = create_unitime_export_directory()
        course_offerings_doc_type = '<!DOCTYPE offerings PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/CourseOfferingExport.dtd">'

        """
        offerings Import File

        """

        try:

            term = Donem.objects.filter(guncel=True)[0]
            uni = Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
            batch_size = int(self.manager.args.batch_size)
            count = Sube.objects.filter(donem=term).count()
            rounds = int(count / batch_size) + 1
            root = etree.Element('offerings', campus="%s" % uni, term="%s" % term.ad,
                                 year="%s" % term.baslangic_tarihi.year, action="insert",
                                 incremental="true",
                                 timeFormat="HHmm", dateFormat="yyyy/M/d")
            for i in range(rounds):

                for sube in Sube.objects.set_params(rows=1000, start=i * batch_size).filter(donem=term):
                    lecture = sube.ders
                    offering_elem = etree.SubElement(root, 'offering', id="%s" % sube.ad, offered="true")
                    course_elem = etree.SubElement(offering_elem, 'course', courseNbr="%s" % lecture.kod,
                                                   subject="%s" % lecture.program.yoksis_no,
                                                   controlling="true")
                    etree.SubElement(course_elem, 'class', name="%s" % sube.ad, suffix="1", imit="%s" % sube.kontenjan,
                                     type="Rec")

            # pretty string
            s = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                               doctype="%s" % course_offerings_doc_type)
            if len(s):

                out_file = open(export_directory + '/courseOfferingsImport.xml', 'w+')
                out_file.write("%s" % s)
                print("Dosya %s dizini altina kayit edilmistir" % export_directory)

            else:
                print("Bir Hata Oluştu ve XML Dosyası Yaratılamadı")

        except Exception as e:

            print(e.message)
