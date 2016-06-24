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
from ulakbus.models import Donem, Unit, Sube, Ders, Program, OgrenciProgram, OgrenciDersi, Okutman, Takvim, Building, \
    Room
import datetime
from common import get_akademik_takvim


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
            return Unit.objects.get(parent_unit_no=0).yoksis_no
        except:
            print("Universite tanimlanmamis")
            sys.exit(1)

    @property
    def term(self):
        try:
            return Donem.objects.get(guncel=True)
        except:
            print("Guncel donem tanimlanmamis")
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
    """
        yöksis numarası verilen bölümün kullanabileceği odalar, o odaların bulunduğu
        binalar ve eğer varsa o odaları verilen bölüm dışında kullanmaya yetkisi olan diğer
        birimlerin bilgisini export etmeye yarar.

        """
    CMD_NAME = 'export_rooms'
    HELP = 'Generates Unitime XML import file for rooms'
    PARAMS = [{'name': 'batch_size', 'type': int, 'default': 1000,
               'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}]
    FILE_NAME = 'buildingRoomImport.xml'
    DOC_TYPE = '<!DOCTYPE buildingsRooms PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/BuildingRoom.dtd">'

    def prepare_data(self):

        root = etree.Element('buildingsRooms', campus="%s" % self.uni,
                             term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year)

        buildings = Building.objects.filter()

        for building in buildings:
            buildingelement = etree.SubElement(
                root, 'building',
                externalId="%s" % building.key,
                abbreviation="%s" % building.code,
                locationX="%s" % building.coordinate_x,
                locationY="%s" % building.coordinate_y,
                name="%s" % building.name)

            rooms = Room.objects.filter(building=building)

            for room in rooms:
                roomelement = etree.SubElement(
                    buildingelement, 'room',
                    externalId="%s" % room.room.key,
                    locationX="%s" % room.room.building.coordinate_x,
                    locationY="%s" % room.room.building.coordinate_y,
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

        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportSessionsToXml(UnitimeEntityXMLExport):
    """
    İstenen bölümün akademik takvimine ve güncel döneme göre; dönemin başlangıç tarihi,
    dönemin bitiş tarihi, derslerin bitiş tarihi ve yarıyıl sonu sınav tarihlerinin başlangıç tarihi
    bilgisini export etmeye yarar.

    """
    CMD_NAME = 'export_sessions'
    HELP = 'Generates Unitime XML import file for academic sessions'
    PARAMS = [{'name': 'batch_size', 'type': int, 'default': 1000,
               'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}]
    FILE_NAME = 'sessionImport.xml'
    DOC_TYPE = '<!DOCTYPE session PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Session.dtd">'

    def prepare_data(self):
        # create XML

        unit = Unit.objects.get(yoksis_no=self.uni)
        akademik_takvim = get_akademik_takvim(unit)

        if 'Güz' in self.term.ad:

            start_date = Takvim.objects.get(akademik_takvim=akademik_takvim, etkinlik=1).baslangic.strftime("%m/%d/%Y")
            end_date = Takvim.objects.get(akademik_takvim=akademik_takvim, etkinlik=34).bitis.strftime("%m/%d/%Y")
            class_end = Takvim.objects.get(akademik_takvim=akademik_takvim, etkinlik=24).bitis.strftime("%m/%d/%Y")
            exam_begin = Takvim.objects.get(akademik_takvim=akademik_takvim, etkinlik=25).baslangic.strftime("%m/%d/%Y")

        else:

            start_date = Takvim.objects.get(akademik_takvim=akademik_takvim, etkinlik=35).baslangic.strftime("%m/%d/%Y")
            end_date = Takvim.objects.get(akademik_takvim=akademik_takvim, etkinlik=61).bitis.strftime("%m/%d/%Y")
            class_end = Takvim.objects.get(akademik_takvim=akademik_takvim, etkinlik=56).bitis.strftime("%m/%d/%Y")
            exam_begin = Takvim.objects.get(akademik_takvim=akademik_takvim, etkinlik=57).baslangic.strftime("%m/%d/%Y")

        root = etree.Element('session', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year, dateFormat="M/d/y")

        etree.SubElement(root, 'sessionDates', beginDate="%s" % start_date,
                         endDate="%s" % end_date,
                         classesEnd="%s" % class_end, examBegin="%s" % exam_begin,
                         eventBegin="%s" % start_date, eventEnd="%s" % end_date)
        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportDepartmentsToXML(UnitimeEntityXMLExport):
    """
    Okul içerisinde bulunan bütün bölümlerin bilgilerini export etmeye yarar.
    """

    CMD_NAME = 'export_departments'
    HELP = 'Generates Unitime XML import file for academic departments'
    PARAMS = []
    FILE_NAME = 'departmentImport.xml'
    DOC_TYPE = '<!DOCTYPE departments PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Department.dtd">'

    def prepare_data(self):
        # create XML

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
    """
    Okul içerisinde bulunan bütün programların bilgilerini export etmeye yarar.
    """
    CMD_NAME = 'export_academic_subjects'
    HELP = 'Generates Unitime XML import file for academic subjects'
    PARAMS = []
    FILE_NAME = 'subjectAreaImport.xml'
    DOC_TYPE = '<!DOCTYPE subjectAreas PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/SubjectArea.dtd">'

    def prepare_data(self):

        # create XML


        root = etree.Element('subjectAreas', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year)
        for bolum in self.bolumler:
            try:
                programlar = Unit.objects.filter(parent_unit_no=bolum.yoksis_no)
                for program in programlar:
                    etree.SubElement(root, 'subjectArea', externalId="%s" % program.key,
                                     abbreviation="%s" % program.yoksis_no,
                                     title="%s" % program.name,
                                     department="%s" % program.parent_unit_no)
            except:
                pass

        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportStaffToXML(UnitimeEntityXMLExport):
    """
    Okul içerisinde bulunan bütün okutmanların bilgisi, okutmanların unvanı ve bağlı bulundukları
    bölümlerin export edilmesine yarar.
    """
    CMD_NAME = 'export_staff'
    HELP = 'Generates Unitime XML import file for staff'
    PARAMS = []
    FILE_NAME = 'staffImport.xml'
    DOC_TYPE = '<!DOCTYPE staff PUBLIC "-//UniTime//UniTime Staff Import DTD/EN" "http://www.unitime.org/interface/Staff.dtd">'

    def prepare_data(self):
        ogretim_elemanlari = Okutman.objects.filter()
        if len(ogretim_elemanlari) > 0:

            root = etree.Element('staff', campus="%s" % self.uni, term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year)
            for ogretim_elemani in ogretim_elemanlari:
                unvan = self.acadTitle(title=ogretim_elemani.unvan)
                if ogretim_elemani.birim_no:
                    try:
                        staff_dep = Unit.objects.get(yoksis_no=ogretim_elemani.birim_no).parent_unit_no
                        etree.SubElement(root, 'staffMember', externalId="%s" % ogretim_elemani.key,
                                         firstName="%s" % ogretim_elemani.ad,
                                         lastName="%s" % ogretim_elemani.soyad,
                                         department="%s" % staff_dep, acadTitle="%s" % unvan[0],
                                         positionType="%s" % unvan[1])
                    except:
                        pass
            # pretty string
            return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                  doctype="%s" % self.DOC_TYPE)
        else:
            print("Öğretim Elemanı Bulunamadi")

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


class ExportCurriculaToXML(UnitimeEntityXMLExport):
    """
    İstenilen bölümün programlarının güncel dönemde açılan derslerinin export edilmesine yarar.
    """
    CMD_NAME = 'export_curricula'
    HELP = 'Generates Unitime XML import file for curricula'
    PARAMS = [{'name': 'bolum', 'type': int, 'required': True,
               'help': 'Bolum olarak yoksis numarasi girilmelidir. Ornek: --bolum 124150'},
              {'name': 'batch_size', 'type': int, 'default': 1000,
               'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}]
    FILE_NAME = 'curricula.xml'
    DOC_TYPE = '<!DOCTYPE curricula PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Curricula_3_2.dtd">'

    def prepare_data(self):

        bolum = Unit.objects.get(yoksis_no=self.manager.args.bolum)
        programlar = Program.objects.filter(bolum=bolum)

        if len(programlar) > 0:

            root = etree.Element('curricula', campus="%s" % self.uni, term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year)
            for program in programlar:
                try:
                    curriculum = etree.SubElement(root, 'curriculum')
                    etree.SubElement(curriculum, 'academicArea', abbreviation='A')
                    etree.SubElement(curriculum, 'department', code="%s" % bolum.yoksis_no)
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


class ExportCourseOfferingsToXML(UnitimeEntityXMLExport):
    """
    İstenilen bölümün, her bir programının derslerinin bilgisini ve o dersin şube bilgilerini
    export etmeye yarar.


    """
    CMD_NAME = 'export_course_offerings'
    HELP = 'Generates Unitime XML import file for timetable'
    PARAMS = [{'name': 'bolum', 'type': int, 'required': True,
               'help': 'Bolum olarak yoksis numarasi girilmelidir. Ornek: --bolum 124150'},
              {'name': 'batch_size', 'type': int, 'default': 1000,
               'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}]
    FILE_NAME = 'courseOfferingsImport.xml'
    DOC_TYPE = '<!DOCTYPE offerings PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/CourseOfferingExport.dtd">'

    def prepare_data(self):

        """
        offerings Import File

        """
        bolum = Unit.objects.get(yoksis_no=self.manager.args.bolum)
        programlar = Program.objects.filter(bolum=bolum)
        root = etree.Element('offerings', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year, action="insert",
                             incremental="true",
                             timeFormat="HHmm", dateFormat="yyyy/M/d")
        for program in programlar:
            dersler = Ders.objects.filter(program=program)
            for ders in dersler:
                batch_size = int(self.manager.args.batch_size)
                count = Sube.objects.filter(donem=self.term, ders=ders).count()
                rounds = int(count / batch_size) + 1
                for i in range(rounds):
                    for sube in Sube.objects.set_params(rows=1000, start=i * batch_size).filter(
                            donem=self.term, ders=ders):

                        try:
                            offering_elem = etree.SubElement(root, 'offering', id="%s" % sube.ad,
                                                             offered="true")
                            course_elem = etree.SubElement(offering_elem, 'course',
                                                           courseNbr="%s" % ders.kod,
                                                           subject="%s" % ders.program.yoksis_no,
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
        ExportCourseOfferingsToXML().run()
        ExportStudentCoursesToXML().run()
        ExportStudentCourseDemandsToXML().run()
        ExportClassesToXML().run()
        ExportAcademicAreaToXML().run()
        ExportAcademicClassificationsToXML().run()
        ExportPosMajorsToXML().run()
        ExportCurriculaToXML().run()

class ExportClassesToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_classes'
    HELP = 'Generates Unitime XML import file for timetable'
    PARAMS = [{'name': 'bolum', 'type': int, 'required': True,
               'help': 'Bolum olarak yoksis numarasi girilmelidir. Ornek: --bolum 124150'},
              {'name': 'batch_size', 'type': int, 'default': 1000,
               'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}]
    FILE_NAME = 'courseTimetableImport.xml'
    DOC_TYPE = '<!DOCTYPE timetable PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/CourseTimetable.dtd">'

    def prepare_data(self):

        """
        courseTimetableImport Import File

        """

        bolum = Unit.objects.get(yoksis_no=self.manager.args.bolum)
        programlar = Program.objects.filter(bolum=bolum)
        root = etree.Element('timetable', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year, action="insert",
                             instructors="false",
                             notes="false", prefer="id", timeFormat="HHmm",
                             dateFormat="yyyy/M/d")
        for program in programlar:
            dersler = Ders.objects.filter(program=program)
            for ders in dersler:
                batch_size = int(self.manager.args.batch_size)
                count = Sube.objects.filter(donem=self.term, ders=ders).count()
                rounds = int(count / batch_size) + 1

                for i in range(rounds):
                    for sube in Sube.objects.set_params(rows=1000, start=i * batch_size).filter(
                            donem=self.term, ders=ders):
                        etree.SubElement(root, 'class', name="%s" % sube.ad,
                                         courseNbr="%s" % ders.kod,
                                         subject="%s" % ders.program.yoksis_no,
                                         type="Lec")

        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportStudentCoursesToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_student_courses'
    HELP = 'Generates Unitime XML import file for student courses'
    PARAMS = [

        {'name': 'bolum', 'type': int, 'required': True},
        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}

    ]
    FILE_NAME = 'studentEnrollments.xml'
    DOC_TYPE = '<!DOCTYPE studentEnrollments PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/StudentEnrollment.dtd">'

    def prepare_data(self):

        bolum = Unit.objects.get(yoksis_no=self.manager.args.bolum)
        program_list = Program.objects.filter(bolum=bolum)

        if len(program_list) > 0:

            '''
            studentEnrollments Import File
            '''

            root = etree.Element('studentEnrollments', campus="%s" % self.uni,
                                 term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year)

            batch_size = int(self.manager.args.batch_size)
            count = OgrenciProgram.objects.filter(bagli_oldugu_bolum=bolum).count()
            rounds = int(count / batch_size) + 1

            for i in range(rounds):
                for student in OgrenciProgram.objects.set_params(rows=1000, start=i * batch_size).filter(
                        bagli_oldugu_bolum=bolum):
                    student_element = etree.SubElement(root, "student",
                                                       externalId="%s" % student.ogrenci.key,
                                                       firstName="%s" % student.ogrenci.ad,
                                                       lastName="%s" % student.ogrenci.soyad,
                                                       email="%s" % student.ogrenci.e_posta)

                    try:
                        for ogrenci_ders in OgrenciDersi.objects.filter(
                                ogrenci_program=student):
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


class ExportStudentCourseDemandsToXML(UnitimeEntityXMLExport):
    CMD_NAME = 'export_student_course_demands'
    HELP = 'Generates Unitime XML import file for student course demands'
    PARAMS = [

        {'name': 'bolum', 'type': int, 'required': True},
        {'name': 'batch_size', 'type': int, 'default': 1000,
         'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}

    ]
    FILE_NAME = 'studentCrsDemandImport.xml'
    DOC_TYPE = '<!DOCTYPE lastLikeCourseDemand PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/StudentCourse.dtd">'

    def prepare_data(self):

        bolum = Unit.objects.get(yoksis_no=self.manager.args.bolum)
        program_list = Program.objects.filter(bolum=bolum)

        if len(program_list) > 0:
            '''
            lastLikeCourseDemand Import File
            '''
            root = etree.Element('lastLikeCourseDemand', campus="%s" % self.uni,
                                 term="%s" % self.term.ad,
                                 year="%s" % self.term.baslangic_tarihi.year)

            batch_size = int(self.manager.args.batch_size)
            count = OgrenciProgram.objects.filter(bagli_oldugu_bolum=bolum).count()
            rounds = int(count / batch_size) + 1

            for i in range(rounds):
                for student in OgrenciProgram.objects.filter(bagli_oldugu_bolum=bolum):
                    student_element = etree.SubElement(root, "student", externalId="%s" % student.ogrenci.key)
                    try:
                        for ogrenci_ders in OgrenciDersi.objects.filter(
                                ogrenci_program=student):
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


class ExportStudentInfoToXML(UnitimeEntityXMLExport):
    """
    İstenilen bölüme bağlı öğrencilerin bilgilerini export etmeye yarar.
    """
    CMD_NAME = 'export_student_info'
    HELP = 'Generates Unitime XML import file for student info'
    PARAMS = [{'name': 'bolum', 'type': int, 'required': True,
               'help': 'Bolum olarak yoksis numarasi girilmelidir. Ornek: --bolum 124150'},
              {'name': 'batch_size', 'type': int, 'default': 1000,
               'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}]
    FILE_NAME = 'studentInfoImport.xml'
    DOC_TYPE = '<!DOCTYPE students PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/Student.dtd">'

    def prepare_data(self):
        # FIX for default row size in pyoko filter

        bolum = Unit.objects.get(yoksis_no=self.manager.args.bolum)
        batch_size = int(self.manager.args.batch_size)
        count = OgrenciProgram.objects.filter(bagli_oldugu_bolum=bolum).count()
        rounds = int(count / batch_size) + 1

        root = etree.Element('students', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year)
        # FIX for default row size in pyoko filter
        for i in range(rounds):
            for student in OgrenciProgram.objects.set_params(rows=1000, start=i * batch_size).filter(
                    bagli_oldugu_bolum=bolum):
                etree.SubElement(root, 'student', externalId="%s" % student.ogrenci.key,
                                 firstName="%s" % student.ogrenci.ad,
                                 lastName="%s" % student.ogrenci.soyad,
                                 email="%s" % student.ogrenci.e_posta)

        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)


class ExportCourseCatalogToXML(UnitimeEntityXMLExport):
    """
    İstenilen bölümdeki programlara bağlı bütün dersleri export etmeye yarar.
    """
    CMD_NAME = 'export_course_catalog'
    HELP = 'Generates Unitime XML import file for course catalog'
    PARAMS = [{'name': 'bolum', 'type': int, 'required': True,
               'help': 'Bolum olarak yoksis numarasi girilmelidir. Ornek: --bolum 124150'},
              {'name': 'batch_size', 'type': int, 'default': 1000,
               'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}]
    FILE_NAME = 'courseCatalogImport.xml'
    DOC_TYPE = '<!DOCTYPE courseCatalog PUBLIC "-//UniTime//DTD University Course Timetabling/EN" "http://www.unitime.org/interface/CourseCatalog.dtd">'

    def prepare_data(self):
        # FIX for default row size in pyoko filter

        bolum = Unit.objects.get(yoksis_no=self.manager.args.bolum)
        programlar = Program.objects.filter(bolum=bolum)

        root = etree.Element('courseCatalog', campus="%s" % self.uni, term="%s" % self.term.ad,
                             year="%s" % self.term.baslangic_tarihi.year)
        for program in programlar:

            batch_size = int(self.manager.args.batch_size)
            count = Ders.objects.filter(program=program).count()
            rounds = int(count / batch_size) + 1

            for i in range(rounds):
                for ders in Ders.objects.set_params(rows=1000, start=i * batch_size).filter(program=program):
                    derselement = etree.SubElement(root, 'course', externalId="%s" % ders.key,
                                                   courseNumber="%s" % ders.kod,
                                                   subject="%s" % ders.program.yoksis_no,
                                                   title="%s" % ders.ad)
                    etree.SubElement(derselement, 'courseCredit', creditType="collegiate",
                                     creditUnitType="semesterHours",
                                     creditFormat="fixedUnit",
                                     fixedCredit="%s" % ders.yerel_kredisi)

        # FIX for default row size in pyoko filter

        # pretty string
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                              doctype="%s" % self.DOC_TYPE)
