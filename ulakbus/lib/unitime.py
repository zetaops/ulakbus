# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import os
import sys
from zengine.management_commands import *
from lxml import etree
from ulakbus.models import Donem, Ogrenci, Unit, Sube, Ders, Program, OgrenciProgram, OgrenciDersi, Okutman, Campus
import datetime


class UnitimeEntityXMLExport(Command):
    EXPORT_DIR = 'bin/dphs/data_exchange/'
    FILE_NAME = ''
    DOC_TYPE = ''
    CMD_NAME = ''
    HELP = ''
    PARAMS = []

    def write_file(self, data):
        out_dir = self.create_dir()
        out_file = open(out_dir + '/' + self.FILE_NAME, 'w+')
        out_file.write("%s" % data)
        print(
            "Veriler %s dizini altinda %s adlı dosyaya kayit edilmiştir" % (
                out_dir, self.FILE_NAME))

    def run(self):
        data = self.prepare_data()
        if len(data) > 0:
            self.write_file(data)
        else:
            print("Aktarilacak veri bulunamadi!.")

    def prepare_data(self):
        return ''

    def create_dir(self):
        current_date = datetime.datetime.now()
        export_directory = self.EXPORT_DIR + current_date.strftime('%d_%m_%Y_%H')
        if not os.path.exists(export_directory):
            os.makedirs(export_directory)
        return export_directory

    @property
    def uni(self):
        try:
            return Unit.objects.filter(parent_unit_no=0)[0].yoksis_no
        except:
            print("Universite tanimlanmamis")
            sys.exit(1)

    @property
    def term(self):
        try:
            return Donem.objects.filter(guncel=True)[0]
        except:
            print("Guncel donem tanimlanmamis")
            sys.exit(1)

    @property
    def campuses(self):
        c = Campus.objects.filter()
        if len(c) > 0:
            return c
        else:
            print("Kampus Bulunamadi")
            sys.exit(1)

    @property
    def sessions(self):
        s = Donem.objects.filter()
        if len(s) > 0:
            return s
        else:
            print("Donem Bulunamadi")
            sys.exit(1)

    @property
    def bolumler(self):
        b = Unit.objects.filter(unit_type='Bölüm')
        if len(b) > 0:
            return b
        else:
            print("Bolum Bulunamadi")
            sys.exit(1)


class ExportRooms(UnitimeEntityXMLExport):
    CMD_NAME = 'export_rooms'
    HELP = 'Generates Unitime XML import file for rooms'
    PARAMS = []
    FILE_NAME = 'buildingRoomImport.xml'
    DOC_TYPE = '<!DOCTYPE buildingsRooms PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/BuildingRoom.dtd">'

    def prepare_data(self):
        # create XML
        root = ''
        for campus in self.campuses:
            if campus.building_set:
                root = etree.Element('buildingsRooms', campus="%s" % self.uni,
                                     term="%s" % self.term.ad,
                                     year="%s" % self.term.baslangic_tarihi.year)
                for building in campus.building_set:

                    buildingelement = etree.SubElement(
                            root, 'building',
                            externalId="%s" % building.building.key,
                            abbreviation="%s" % building.building.code,
                            locationX="%s" % building.building.coordinate_x,
                            locationY="%s" % building.building.coordinate_y,
                            name="%s" % building.building.name)
                    if building.building.room_set:

                        for room in building.building.room_set:
                            roomelement = etree.SubElement(
                                    buildingelement, 'room',
                                    externalId="%s" % room.room.key,
                                    locationX="%s" % building.building.coordinate_x,
                                    locationY="%s" % building.building.coordinate_y,
                                    roomNumber="%s" % room.room.code,
                                    roomClassification="%s" % room.room.room_type.type,
                                    capacity="%s" % room.room.capacity,
                                    instructional="True")

                            if room.room.RoomDepartments:
                                roommdepartments = etree.SubElement(roomelement,
                                                                    'roomDepartments')
                                for department in room.room.RoomDepartments:
                                    etree.SubElement(
                                            roommdepartments, 'assigned',
                                            departmentNumber="%s" % department.unit.yoksis_no,
                                            percent="100")

        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportSessionsToXml(UnitimeEntityXMLExport):
    CMD_NAME = 'export_sessions'
    HELP = 'Generates Unitime XML import file for academic sessions'
    PARAMS = []
    FILE_NAME = 'sessionImport.xml'
    DOC_TYPE = '<!DOCTYPE session PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Session.dtd">'

    def prepare_data(self):
        root = ''
        # create XML
        for campus in self.campuses:

            root = etree.Element('session', campus="%s" % self.uni, term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year, dateFormat="M/d/y")
            for session in self.sessions:
                start_date = session.baslangic_tarihi.strftime("%m/%d/%Y")
                end_date = session.bitis_tarihi.strftime("%m/%d/%Y")
                etree.SubElement(root, 'sessionDates', beginDate="%s" % start_date,
                                 endDate="%s" % end_date,
                                 classesEnd="%s" % end_date, examBegin="%s" % start_date,
                                 eventBegin="%s" % start_date, eventEnd="%s" % end_date)
        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportDepartmentsToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_departments'
    HELP = 'Generates Unitime XML import file for academic departments'
    PARAMS = []
    FILE_NAME = 'departmentImport.xml'
    DOC_TYPE = '<!DOCTYPE departments PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Department.dtd">'

    def prepare_data(self):

        # create XML
        for campus in self.campuses:

            root = etree.Element('departments', campus="%s" % self.uni, term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year)
            for unit in self.bolumler:
                etree.SubElement(root, 'department', externalId="%s" % unit.key,
                                 abbreviation="%s" % unit.yoksis_no, name="%s" % unit.name,
                                 deptCode="%s" % unit.yoksis_no, allowEvents="true")
        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportAcademicSubjectsToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_academic_subjects'
    HELP = 'Generates Unitime XML import file for academic subjects'
    PARAMS = []
    FILE_NAME = 'subjectAreaImport.xml'
    DOC_TYPE = '<!DOCTYPE subjectAreas PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/SubjectArea.dtd">'

    def prepare_data(self):

        # create XML
        for campus in self.campuses:

            root = etree.Element('subjectAreas', campus="%s" % self.uni, term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year)
            for unit in self.bolumler:
                try:
                    subunits = Unit.objects.filter(parent_unit_no=unit.yoksis_no)
                    for subunit in subunits:
                        etree.SubElement(root, 'subjectArea', externalId="%s" % subunit.key,
                                         abbreviation="%s" % subunit.yoksis_no,
                                         title="%s" % subunit.name,
                                         department="%s" % subunit.parent_unit_no)
                except:
                    pass

        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportStaffToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_staff'
    HELP = 'Generates Unitime XML import file for staff'
    PARAMS = []
    FILE_NAME = 'staffImport.xml'
    DOC_TYPE = '<!DOCTYPE staff PUBLIC "-//UniTime//UniTime Staff Import DTD/EN" "http://www.unitime.org/interface/Staff.dtd">'

    def prepare_data(self):
        stafflist = Okutman.objects.filter()
        if len(stafflist) > 0:
            for campus in self.campuses:
                root = etree.Element('staff', campus="%s" % self.uni, term="%s" % self.term.ad,
                                     year="%s" % self.term.baslangic_tarihi.year)
                for staffmember in stafflist:
                    unvan = self.acadTitle(title=staffmember.unvan)
                    staff_dep = staffmember.birim_no
                    if staffmember.birim_no:
                        try:
                            staff_dep = Unit.objects.filter(yoksis_no=staffmember.birim_no)[
                                0].parent_unit_no
                            etree.SubElement(root, 'staffMember', externalId="%s" % staffmember.key,
                                             firstName="%s" % staffmember.ad,
                                             lastName="%s" % staffmember.soyad,
                                             department="%s" % staff_dep, acadTitle="%s" % unvan[0],
                                             positionType="%s" % unvan[1])
                        except:
                            pass
            # pretty string
            return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                  doctype="%s" % self.DOC_TYPE)
        else:
            print("Okutman Bulunamadi")

    @staticmethod
    def acadTitle(title):
        if title == 1:
            return ["Professor", "PROF"]
        elif title == 2:
            return ["Associate Professor", "ASSOC_PROF"]
        elif title == 3:
            return ["Research Assistant", "INSTRUCTOR"]
        elif title == 4:
            return ["Lecturer", "INSTRUCTOR"]
        else:
            return ["", ""]


class ExportStudentInfoToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_student_info'
    HELP = 'Generates Unitime XML import file for student info'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]
    FILE_NAME = 'studentInfoImport.xml'
    DOC_TYPE = '<!DOCTYPE students PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Student.dtd">'

    def prepare_data(self):
        # FIX for default row size in pyoko filter
        batch_size = int(self.manager.args.batch_size)
        count = Ogrenci.objects.count()
        rounds = int(count / batch_size) + 1

        root = etree.Element('students', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year)
        # FIX for default row size in pyoko filter
        for i in range(rounds):
            for student in Ogrenci.objects.set_params(rows=1000, start=i * batch_size).filter():
                etree.SubElement(root, 'student', externalId="%s" % student.key,
                                 firstName="%s" % student.ad,
                                 lastName="%s" % student.soyad,
                                 email="%s" % student.e_posta)
        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportCourseCatalogToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_course_catalog'
    HELP = 'Generates Unitime XML import file for course catalog'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]
    FILE_NAME = 'courseCatalogImport.xml'
    DOC_TYPE = '<!DOCTYPE courseCatalog PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/CourseCatalog.dtd">'

    def prepare_data(self):
        # FIX for default row size in pyoko filter
        batch_size = int(self.manager.args.batch_size)
        count = Ders.objects.count()
        rounds = int(count / batch_size) + 1

        root = etree.Element('courseCatalog', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year)
        # FIX for default row size in pyoko filter
        for i in range(rounds):
            for ders in Ders.objects.set_params(rows=1000, start=i * batch_size).filter():
                derselement = etree.SubElement(root, 'course', externalId="%s" % ders.key,
                                               courseNumber="%s" % ders.kod,
                                               subject="%s" % ders.program.yoksis_no,
                                               title="%s" % ders.ad)
                etree.SubElement(derselement, 'courseCredit', creditType="collegiate",
                                 creditUnitType="semesterHours",
                                 creditFormat="fixedUnit",
                                 fixedCredit="%s" % ders.yerel_kredisi)
        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportCurriculaToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_curricula'
    HELP = 'Generates Unitime XML import file for curricula'
    PARAMS = []
    FILE_NAME = 'curricula.xml'
    DOC_TYPE = '<!DOCTYPE curricula PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Curricula_3_2.dtd">'

    def prepare_data(self):

        program_list = Program.objects.filter()

        if len(program_list) > 0:

            """
            curricula Import File

            """

            root = etree.Element('curricula', campus="%s" % self.uni, term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year)
            for program in program_list:
                ders_list = Ders.objects.filter(program=program).count()
                try:
                    parent_yoksis_no = Unit.objects.filter(yoksis_no=program.yoksis_no)[
                        0].parent_unit_no
                    curriculum = etree.SubElement(root, 'curriculum')
                    etree.SubElement(curriculum, 'academicArea', abbreviation='A')
                    etree.SubElement(curriculum, 'department', code="%s" % parent_yoksis_no)
                    etree.SubElement(curriculum, 'major', code="M1")
                    classification = etree.SubElement(curriculum, 'classification', name="01",
                                                      enrollment='2')
                    etree.SubElement(classification, 'academicClassification', code="01")
                    for program_ders in Ders.objects.filter(program=program):
                        etree.SubElement(classification, 'course', subject="%s" % program.yoksis_no,
                                         courseNbr="%s" % program_ders.kod)
                except:
                    pass

            # pretty string
            return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                  doctype="%s" % self.DOC_TYPE)
        else:
            print("Program Bulunmadi")


class ExportAcademicAreaToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_academic_area'
    HELP = 'Generates Unitime XML import file for Academic Areas'
    PARAMS = []
    FILE_NAME = 'academicAreaImport.xml'
    DOC_TYPE = '<!DOCTYPE academicAreas PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/AcademicArea.dtd">'

    def prepare_data(self):
        """
        academicAreas Import File

        """

        root = etree.Element('academicAreas', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year)
        etree.SubElement(root, 'academicArea', abbreviation='A', externalId='A',
                         title="%s" % self.uni + ' - ' + self.term.ad)

        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportAcademicClassificationsToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_academic_class'
    HELP = 'Generates Unitime XML import file for Academic Classifications'
    PARAMS = []
    FILE_NAME = 'academicClassificationImport.xml'
    DOC_TYPE = '<!DOCTYPE academicClassifications PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/AcademicClassification.dtd">'

    def prepare_data(self):
        """
        academicClassifications Import File

        """

        root = etree.Element('academicClassifications', campus="%s" % self.uni,
                             term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year)
        etree.SubElement(root, 'academicClassification',
                         externalId="01",
                         code="01", name="01")
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportPosMajorsToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_posmajors'
    HELP = 'Generates Unitime XML import file for Pos Majors'
    PARAMS = []
    FILE_NAME = 'posMajorImport.xml'
    DOC_TYPE = '<!DOCTYPE posMajors PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/PosMajor.dtd">'

    def prepare_data(self):
        """
        posMajors Import File

        """

        root = etree.Element('posMajors', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year)
        etree.SubElement(root, 'posMajor', externalId="M1", code="M1",
                         name="%s Major 1" % self.term.baslangic_tarihi.year,
                         academicArea="A")
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportStudentCourseDemandsToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_student_course_demands'
    HELP = 'Generates Unitime XML import file for student course demands'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]
    FILE_NAME = 'studentCrsDemandImport.xml'
    DOC_TYPE = '<!DOCTYPE lastLikeCourseDemand PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/StudentCourse.dtd">'

    def prepare_data(self):

        program_list = Program.objects.filter()

        if len(program_list) > 0:
            '''
            lastLikeCourseDemand Import File
            '''
            root = etree.Element('lastLikeCourseDemand', campus="%s" % self.uni,
                                 term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year)

            batch_size = int(self.manager.args.batch_size)
            count = Ogrenci.objects.count()
            rounds = int(count / batch_size) + 1

            for i in range(rounds):
                for student in Ogrenci.objects.set_params(rows=1000, start=i * batch_size).filter():
                    student_department_list = OgrenciProgram.objects.filter(ogrenci=student)
                    if (student_department_list):
                        student_element = etree.SubElement(root, "student",
                                                           externalId="%s" % student.key)
                        for department in student_department_list:
                            try:
                                for ogrenci_ders in OgrenciDersi.objects.filter(
                                        ogrenci_program=department):
                                    ders = ogrenci_ders.ders
                                    etree.SubElement(student_element, 'studentCourse',
                                                     externalId="%s" % ders.key,
                                                     courseNumber="%s" % ders.kod,
                                                     subject="%s" % ders.program.yoksis_no)
                            except:
                                pass
            # pretty string
            return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                  doctype="%s" % self.DOC_TYPE)
        else:
            print("Program Bulunamadi")


class ExportStudentCoursesToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_student_courses'
    HELP = 'Generates Unitime XML import file for student courses'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]
    FILE_NAME = 'studentEnrollments.xml'
    DOC_TYPE = '<!DOCTYPE studentEnrollments PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/StudentEnrollment.dtd">'

    def prepare_data(self):
        program_list = Program.objects.filter()

        if len(program_list) > 0:

            '''
            studentEnrollments Import File
            '''

            root = etree.Element('studentEnrollments', campus="%s" % self.uni,
                                 term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year)

            batch_size = int(self.manager.args.batch_size)
            count = Ogrenci.objects.count()
            rounds = int(count / batch_size) + 1

            for i in range(rounds):
                for student in Ogrenci.objects.set_params(rows=1000, start=i * batch_size).filter():
                    student_department_list = OgrenciProgram.objects.filter(ogrenci=student)
                    if len(student_department_list) > 0:
                        student_element = etree.SubElement(root, "student",
                                                           externalId="%s" % student.key,
                                                           firstName="%s" % student.ad,
                                                           lastName="%s" % student.soyad,
                                                           email="%s" % student.e_posta)
                        for department in student_department_list:
                            try:
                                for ogrenci_ders in OgrenciDersi.objects.filter(
                                        ogrenci_program=department):
                                    if (ogrenci_ders):
                                        ders = ogrenci_ders.ders
                                        etree.SubElement(student_element, 'class',
                                                         externalId="%s" % ders.key,
                                                         courseNbr="%s" % ders.kod,
                                                         subject="%s" % ders.program.yoksis_no,
                                                         type="Lec", suffix="1")
                            except:
                                pass
            # pretty string
            return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                  doctype="%s" % self.DOC_TYPE)
        else:
            print("Program Bulunamadi")


class ExportClassesToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_classes'
    HELP = 'Generates Unitime XML import file for timetable'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]
    FILE_NAME = 'courseTimetableImport.xml'
    DOC_TYPE = '<!DOCTYPE timetable PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/CourseTimetable.dtd">'

    def prepare_data(self):

        """
        courseTimetableImport Import File

        """

        batch_size = int(self.manager.args.batch_size)
        count = Sube.objects.filter(donem=self.term).count()
        rounds = int(count / batch_size) + 1
        root = etree.Element('timetable', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year, action="insert",
                             instructors="false",
                             notes="false", prefer="id", timeFormat="HHmm",
                             dateFormat="yyyy/M/d")

        for i in range(rounds):
            for sube in Sube.objects.set_params(rows=1000, start=i * batch_size).filter(
                    donem=self.term):
                lecture = sube.ders
                etree.SubElement(root, 'class', name="%s" % sube.ad,
                                 courseNbr="%s" % lecture.kod,
                                 subject="%s" % lecture.program.yoksis_no,
                                 type="Lec")
        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportCorseOfferingsToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_course_offerings'
    HELP = 'Generates Unitime XML import file for timetable'
    PARAMS = [

        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'},

    ]
    FILE_NAME = 'courseOfferingsImport.xml'
    DOC_TYPE = '<!DOCTYPE offerings PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/CourseOfferingExport.dtd">'

    def prepare_data(self):

        """
        offerings Import File

        """

        batch_size = int(self.manager.args.batch_size)
        count = Sube.objects.filter(donem=self.term).count()
        rounds = int(count / batch_size) + 1
        root = etree.Element('offerings', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year, action="insert",
                             incremental="true",
                             timeFormat="HHmm", dateFormat="yyyy/M/d")

        for i in range(rounds):
            for sube in Sube.objects.set_params(rows=1000, start=i * batch_size).filter(
                    donem=self.term):

                try:
                    lecture = sube.ders
                    offering_elem = etree.SubElement(root, 'offering', id="%s" % sube.ad,
                                                     offered="true")
                    course_elem = etree.SubElement(offering_elem, 'course',
                                                   courseNbr="%s" % lecture.kod,
                                                   subject="%s" % lecture.program.yoksis_no,
                                                   controlling="true")
                    etree.SubElement(course_elem, 'class', name="%s" % sube.ad, suffix="1",
                                     limit="%s" % sube.kontenjan,
                                     type="Rec")
                except:
                    pass

        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportAllUnitimeXMLs(Command):
    CMD_NAME = 'export_all_unitime_xmls'
    HELP = 'Tum unitime xml dosyalarini tek bir dizine aktarir.'

    def run(self):
        ExportSessionsToXml().run()
        ExportRooms().run()
        ExportDepartmentsToXML().run()
        ExportAcademicSubjectsToXML().run()
        ExportStaffToXML().run()
        ExportStudentInfoToXML().run()
        ExportCourseCatalogToXML().run()
        ExportCorseOfferingsToXML().run()
        ExportStudentCoursesToXML().run()
        ExportStudentCourseDemandsToXML().run()
        ExportClassesToXML().run()
        ExportAcademicAreaToXML().run()
        ExportAcademicClassificationsToXML().run()
        ExportPosMajorsToXML().run()
        ExportCurriculaToXML().run()
