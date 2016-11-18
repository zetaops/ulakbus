# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import sys
from zengine.management_commands import *

from ..models import Donem, Unit, Sube, Ders, Program, OgrenciProgram, OgrenciDersi, Okutman, Takvim, \
    Building, Room, OgElemaniZamanPlani, ZamanCetveli, DerslikZamanPlani, HAFTA,\
    SinavEtkinligi, OgretimYili
from ulakbus.models import DersEtkinligi, SinavEtkinligi
from common import get_akademik_takvim, SOLVER_MAX_ID, SLOT_SURESI, saat2slot,\
    timedelta2slot, datetime2timestamp
from datetime import datetime, date, timedelta, time
import streamingxmlwriter
import io
import random


def _year():
    return date.today().year


class UnitimeEntityXMLExport(Command):
    EXPORT_DIR = 'bin/dphs/data_exchange/'
    FILE_NAME = ''
    DOC_TYPE = ''
    CMD_NAME = ''
    HELP = ''
    PARAMS = []

    # CPSolver için ID oluştururken pyoko keyleri ile solver idlerini eşleştirmek için kullanılan sözlük
    _SOLVER_IDS = {}

    def _key2id(self, key):
        """Çakışmaları önleyerek pyoko key'lerinden solver id'leri oluşturur."""
        if key in self._SOLVER_IDS:
            return self._SOLVER_IDS[key]
        unitime_key = hash(key) % SOLVER_MAX_ID
        # Çakışmalar çözülene kadar id değerini değiştir
        while unitime_key in self._SOLVER_IDS.values():
            unitime_key += 1
        self._SOLVER_IDS[key] = unitime_key
        return unitime_key

    def _room_id(self, room):
        id_ = room.unitime_key
        if id_ is None:
            id_ = self._key2id(room.key)
            room.unitime_key = id_
            room.save()
        else:
            # Daha sonraki çakışmaları önlemek için, görülen key'i kaydet
            self._SOLVER_IDS[room.key] = id_
        return id_

    def pre_run(self):
        """Export alınmadan önce çağırılır.

        Export'a başlamadan önce yapılması gereken hazırlıklar için
        subclass'lar bu methodu overwrite edebilir.
        """
        pass

    def run(self):
        self.pre_run()
        out_dir = self.create_dir()
        out_file = os.path.join(out_dir, self.FILE_NAME)
        with io.open(out_file, 'wb') as write_stream:
            with streamingxmlwriter.from_stream(write_stream) as writer:
                self.prepare_data(writer)
        print("Veriler %s dizini altinda %s adlı dosyaya kayit edilmiştir" % (out_dir, self.FILE_NAME))

    def write(self, writer):
        """Export alınırken, xml'in basılması için çağırılır.

        Subclass'lar, bu methodu overwrite ederek export etmek istedikleri veriyi burada yazmalıdır.

        Args:
            writer: streamingxmlwriter kütüphanesinden bir writer.
        """
        pass

    def create_dir(self):
        export_directory = self.EXPORT_DIR
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


class ExportCourseTimetable(UnitimeEntityXMLExport):
    CMD_NAME = 'export_course_timetable'
    HELP = 'Generates all data set Unitime XML import file'
    PARAMS = [{'name': 'bolum', 'type': int, 'required': True,
               'help': 'Bolum olarak yoksis numarasi girilmelidir. Ornek: --bolum 124150'},
                {'name': 'batch_size', 'type': int, 'default': 1000,
               'help': 'Retrieve this amount of records from Solr in one time, defaults to 1000'}]
    FILE_NAME = 'course.xml'
    DOC_TYPE = ''

    # Ders programı modellerindeki günleri, solver'ın günleri ile eşleştiren sözlük
    _GUNLER = {1: '1000000', 2: '0100000', 3: '0010000', 4: '0001000',
               5: '0000100', 6: '0000010', 7: '0000001'}
    # Dersliklerin zaman planlarını hesaplarken kullanılacak minimum zaman, slot sayısı olarak.
    # Bu süreden daha küçük zaman dilimleri planları çıkarırken dikkate alınmayacaktır
    _ODA_ZAMAN_SLOT = 6
    # Room sharing pattern'larında oda kullanımını gösteren semboller
    _ODA_KAPALI = '0'  # Oda herkese kapalı
    _ODA_ACIK = '1'  # Oda herkese açık
    # Bölümlerin value'ları olarak kullanılacak olan karakterler,
    # 'A' ... 'Z' ve 'a' ... 'z' arasındaki tüm ascii karakterlerini içerir
    _BOLUM_KARAKTER = [chr(c) for c in range(65, 91) + range(97, 122)]

    def pre_run(self):
        self.FILE_NAME = '%i.xml' % self.manager.args.bolum

    def prepare_data(self, writer):
        bolum = Unit.objects.get(yoksis_no=self.manager.args.bolum)
        with writer.element('timetable', {
            'version': '2.4',
            'initiative': '%s' % self.uni,
            'term': '%i%s' % (_year(), self.term.ad),
            'created': '%s' % str(date.today()),
            'nrDays': '7',
            'slotsPerDay': '%i' % saat2slot(24)}):
            self.export_rooms(writer)
            self.export_classes(writer, bolum)

    def export_rooms(self, writer):
        with writer.element('rooms'):
            buildings = list(Building.objects.filter())
            for building in buildings:
                rooms = list(Room.objects.filter(building=building))
                for room in rooms:
                    id = self._room_id(room)
                    room_coordinates = '%s,%s' % (room.building.coordinate_x, room.building.coordinate_y)
                    with writer.element('room', {'id': '%i' % id,
                                                 'constraint': 'true',
                                                 'capacity': '%s' % room.capacity,
                                                 'location': room_coordinates,
                                                 }):
                        if room.RoomDepartments:
                            with writer.element('sharing'):
                                bolum_values = {}  # Pattern oluştururken bölümleri valuelar ile eşleştirmek için
                                for j, department in enumerate(room.RoomDepartments):
                                    value = self._BOLUM_KARAKTER[j]
                                    id_ = '%i' % department.unit.yoksis_no
                                    bolum_values[id_] = value
                                    writer.text_element('department', attrs={'value': value, 'id': id_})
                                with writer.element('pattern', {'unit': '%i' % self._ODA_ZAMAN_SLOT}):
                                    writer.characters(self._derslik_zaman_plani(room, bolum_values))
                                writer.text_element('freeForAll', attrs={'value': self._ODA_ACIK})
                                writer.text_element('notAvailable', attrs={'value': self._ODA_KAPALI})

    def _derslik_zaman_plani(self, derslik, bolum_values):
        """Dersliğin zaman planını, solver'a verilecek bir pattern olarak çıkartır.

        Args:
            derslik (Room): Zaman planı çıkarılacak derslik
            bolum_values: Bölüm yoksis no'larını, pattern'da kullanılacak value'lar
                ile eşleştiren sözlük

        Returns:
            str: Solver'a verilecek room sharing pattern'i
        """
        # Haftada ilk gerçekleşenden son gerçekleşene doğru sıralı zaman planları
        zaman_planlari = sorted(DerslikZamanPlani.objects.filter(derslik=derslik),
                                key=lambda p: (p.gun, p.baslangic_saat, p.baslangic_dakika))
        hs, hs_adi = HAFTA[-1]
        hafta_sonu = datetime.min + timedelta(days=hs)
        zaman = datetime.min
        zaman_adimlari = timedelta(minutes=self._ODA_ZAMAN_SLOT*SLOT_SURESI)
        plan = zaman_planlari.pop(0)
        pattern = []
        while zaman < hafta_sonu:
            while self._zaman_araliginda(zaman, plan) > 0:
                try:
                    plan = zaman_planlari.pop(0)
                except IndexError: # Eğer işlenmemiş plan kalmadıysa
                    break
            if self._zaman_araliginda(zaman, plan) == 0:
                if plan.derslik_durum == 1:  # Herkese açık
                    pattern.append(self._ODA_ACIK)
                elif plan.derslik_durum == 2:  # Bölüme ait
                    pattern.append(bolum_values[str(plan.unit.yoksis_no)])
                else:  # Herkese kapalı
                    pattern.append(self._ODA_KAPALI)
            else:
                # Eğer bu zaman için zaman planı girilmediyse odayı herkese kapalı say
                pattern.append(self._ODA_KAPALI)
            zaman = zaman + zaman_adimlari
        return ''.join(pattern)

    @staticmethod
    def _zaman_araliginda(zaman, plan):
        """Verilen zamanın, zaman planının içinde olup olmadığını kontrol eder.

        Args:
            zaman (datetime):
            plan (DerslikZamanPlani):

        Returns:
            int: Eğer zaman, planın içerisinde ise 0, plandan önce ise negatif, plandan
                sonra ise de pozitif bir sayı.
        """
        plan_baslangic = datetime.min + timedelta(days=plan.gun - 1,
                                                  hours=int(plan.baslangic_saat),
                                                  minutes=int(plan.baslangic_dakika))
        plan_bitis = datetime.min + timedelta(days=plan.gun - 1,
                                              hours=int(plan.bitis_saat),
                                              minutes=int(plan.bitis_dakika))
        if zaman < plan_baslangic: return -1
        if plan_bitis <= zaman: return 1
        # Aralıktaysa
        return 0

    def export_classes(self, writer, bolum):
        # Aynı programın aynı dönemindeki ders etkinlikleri arasındaki çakışmaları minimuma indir
        program_sinirlama = {}
        # Aynı şubenin ders etkinliklerine aynı öğrenciler girecektir
        sube_sinirlama = {}
        with writer.element('classes'):
            programlar = list(Program.objects.filter(bolum=bolum))
            for program in programlar:
                donemler_dersler = {}
                for ders in list(Ders.objects.filter(program=program)):
                    donem = ders.program_donemi
                    try:
                        donemler_dersler[donem].append(ders)
                    except KeyError:
                        donemler_dersler[donem] = [ders]
                for donem, donem_dersler in donemler_dersler.items():
                    program_sinirlama[(program.key, donem)] = []
                    for ders in donem_dersler:
                        self._export_ders(writer, bolum, ders, program_sinirlama, sube_sinirlama)
        self._sinirlandirmalar(writer, program_sinirlama, sube_sinirlama)
        writer.text_element('students')

    def _export_ders(self, writer, bolum, ders, program_sinirlama, sube_sinirlama):
        subeler = list(Sube.objects.filter(ders=ders))
        # Önceki exportlardan kalmış olabilecek kayıtları, yenileriyle
        # karışmaması için temizle
        for sube in subeler:
            etkinlikler = DersEtkinligi.objects.filter(bolum=bolum, published=False,
                                                       donem=self.term, sube=sube)
            if etkinlikler.count() > 0:
                etkinlikler.delete()

        derslik_turleri = ders.DerslikTurleri
        ders_turu = [True,False]
        for sube in subeler:
            sube_sinirlama[sube.key] = []
            for i, tur in enumerate(derslik_turleri):
                uygun_derslikler = list(Room.objects.filter(room_type=tur.sinif_turu()))
                sube_subpart_id = '%i' % self._key2id('%i %s' % (i, sube.key))
                okutman = sube.okutman()
                with writer.element('class', {'id': sube_subpart_id,
                                              'offering': '%i' % self._key2id(ders.key),
                                              'config': '%i' % self._key2id(sube.key),
                                              'subpart': sube_subpart_id,
                                              'classLimit': '%i' % sube.kontenjan,
                                              'scheduler': '%i' % bolum.yoksis_no,
                                              'dates': '1111100111110011111001111100', # haftasonları hariç 1 ay her gün
                                              }):
                    program_sinirlama[(ders.program.key, ders.program_donemi)].append(sube_subpart_id)
                    sube_sinirlama[sube.key].append(sube_subpart_id)
                    # Çıkartılan ders için ders etkinliği kaydı oluştur
                    d = DersEtkinligi()
                    d.solved = False
                    d.unitime_key = sube_subpart_id
                    d.unit_yoksis_no = bolum.yoksis_no
                    d.room_type = tur.sinif_turu()
                    d.okutman = okutman
                    d.sube = sube
                    d.donem = self.term
                    d.bolum = bolum
                    d.published = False
                    d.sure = tur.ders_saati
                    d.ek_ders = random.choice(ders_turu)
                    d.save()
                    # Derse uygun derslikleri çıkar
                    for derslik in uygun_derslikler:
                        writer.text_element('room', attrs={'id': '%i' % derslik.unitime_key, 'pref': '0'})

                    writer.text_element('instructor', attrs={'id': '%i' % self._key2id(okutman.key)})
                    self._zamanlari_cikar(writer, okutman, tur, bolum)

    def _zamanlari_cikar(self, writer, ogretim_elemani, tur, bolum):
        """Okutmanın bölüme ait zaman planına göre zaman seçenekleri çıkar

        Args:
            writer: XML çıktısını yazan obje
            okutman (Okutman): Zaman planları kontrol edilecek eğitim görevlisi
            tur (Ders.DerslikTurleri): Zamanların çıkarıldığı dersin ders etkinliği
            bolum (Unit): Uygun zamanları çıkartan bölüm
        """
        # TODO: Eğer öğretim elemanı birden fazla bölümde ders veriyorsa, diğer bölümlerde ders verdiği ders saatleri burada export edilmemeli
        plan = OgElemaniZamanPlani.objects.get(birim=bolum, okutman=ogretim_elemani)
        # Sadece uygun olan zaman cetvelleri
        cetveller = list(ZamanCetveli.objects.filter(birim=bolum, ogretim_elemani_zaman_plani=plan).exclude(durum=3))
        for cetvel in cetveller:
            dilim = cetvel.zaman_dilimi
            zaman = timedelta(hours=int(dilim.baslama_saat), minutes=int(dilim.baslama_dakika))
            bitis = timedelta(hours=int(dilim.bitis_saat), minutes=int(dilim.bitis_dakika))
            gun = self._GUNLER[cetvel.gun]
            sure = int(tur.ders_saati)
            ders_araligi = timedelta(minutes=int(dilim.ders_araligi))
            # Bitiş zamanı gelene kadar, zamanları ekle
            while zaman < bitis:
                # Pazar günü gece yarısını geçen zaman çıkarırsak solver hata veriyor
                if cetvel.gun == 7 and (zaman + timedelta(hours=sure)) >= timedelta(hours=24): break
                writer.text_element('time', attrs={'days': gun,
                                        'start': '%i' % timedelta2slot(zaman),
                                        'length': '%i' % saat2slot(sure),
                                        'breaktime': '%i' % dilim.ara_suresi,
                                        'pref': '%i' % cetvel.durum
                                        })
                zaman += ders_araligi

    def _sinirlandirmalar(self, writer, program_sinirlama, sube_sinirlama):
        with writer.element('groupConstraints'):
            for (program_key, program_donemi), ders_etkinligi_idleri in program_sinirlama.items():
                with writer.element('constraint', {'type': 'SAME_DAYS', 'pref': 'P',
                                                   'id': '%i' % self._key2id('%i %s' % (program_donemi, program_key)),
                                                   }):
                    for etkinlik_id in ders_etkinligi_idleri:
                        writer.text_element('class', attrs={'id': etkinlik_id})
            # TODO: Aynı şubenin derslerini farklı günlere dağıtılması tercih edilmeli
            for sube_key, ders_etkinligi_idleri in sube_sinirlama.items():
                with writer.element('constraint',
                                    {'id': '%i' % self._key2id(sube_key),
                                     'type': 'SAME_STUDENTS', 'pref': 'R',
                                     }):
                    for etkinlik_id in ders_etkinligi_idleri:
                        writer.text_element('class', attrs={'id': etkinlik_id})


class ExportExamTimetable(UnitimeEntityXMLExport):
    """Solver için sınavları export eder.

    Yöksis numarası verilen bölümün sınavlarını, CPSolver ile çözülebilecek bir sınav
    planlama problem olarak export eder.
    """
    CMD_NAME = 'export_exam_timetable'
    HELP = 'Exports a XML file of the exams, to be solved by CPSolver.'
    PARAMS = [{'name': 'bolum', 'type': int, 'required': True,
               'help': 'Bolum olarak yoksis numarasi girilmelidir. Ornek: --bolum 124150'},
              {'name': 'sinav_turleri', 'type': str, 'required': True,
               'help': 'Çıkartılacak sınav türü. '
                       'Virgüllerle ayırarak birden fazla sınav türü seçilebilir. '
                       'Seçenekler için `sinav_turleri`ne bakın.'}]
    FILE_NAME = 'exam.xml'
    DOC_TYPE = ''
    # Sınavların yerleştirilebilecekleri saat aralıkları
    _SINAV_SURELERI = [
        (time(hour=9),  time(hour=12)),
        (time(hour=12), time(hour=14)),
        (time(hour=14), time(hour=17)),
        (time(hour=17), time(hour=20)),
    ]
    # AKADEMIK_TAKVIM_ETKINLIKLERI arasında sınav tarihlerini gösteren etkinliklerin kodları
    _SINAV_ETKINLIKLERI = (26, 58, 65)
    # Bir şubenin sınavı için kullanılacak maksimum oda sayısı
    _SINAV_MAX_ODA = 2
    # Bir şubenin sınavı, birden fazla odada yapılacaksa, her odada olacak minimum öğrenci sayısı
    _SINAV_MIN_KONTENJAN = 10

    def prepare_data(self, writer):
        bolum = Unit.objects.get(yoksis_no=self.manager.args.bolum)
        sinav_turleri = [int(t) for t in self.manager.args.sinav_turleri.split(',')]
        with writer.element('examtt', {'version': '1.0',
                                       'campus': '1',
                                       'term': 'Term',
                                       'year': '%i' % _year(),
                                       'created': str(date.today()),
                                       }):
            # Sınavların gerçekleşebileceği zamanlar
            with writer.element('periods'):
                zamanlar = self._zamanlar(bolum, writer)
            with writer.element('rooms'):
                odalar = self._odalar(bolum, writer)
            with writer.element('students'):
                ogrenci_dersler = self._ogrenciler(bolum, sinav_turleri, writer)
            with writer.element('exams'):
                self._sinavlar(bolum, sinav_turleri, zamanlar, odalar, ogrenci_dersler, writer)
            with writer.element('instructors'):
                self._sinirlandirmalar(bolum, writer)

    def _zamanlar(self, bolum, writer):
        """Sınavların yapılabilecekleri tarih ve saatleri, sınav planı çıktısına ekler.

        Çıkartılan tarih ve saatler, ``period`` xml elemanının ``time`` alanına bakarak
        bulunabilir. Burada, boşluk ile ayrılmış halde başlangıç ve bitiş zamanları,
        saat dilimi bilgisi içermeyen bir POSIX timestamp'i olarak bulunabilir. Bu
        değerler ``datetime.datetime.utcfromtimestamp`` fonksiyonu ile okunabilir.

        Args:
            bolum (Unit): Sınav planı çıkarılacak bölüm.
            writer: XML çıktısını yazacak olan obje
        Returns:
            dict: Sınav sürelerini, bu süre uzunluğundaki zamanlarla eşleştiren bir sözlük.
        """
        tarihler = self._sinav_tarihleri(bolum)
        zaman = tarihler.baslangic
        i = 0
        zamanlar = {}
        while zaman <= tarihler.bitis:
            for j, (sure_bas, sure_bit) in enumerate(self._SINAV_SURELERI):
                baslangic = zaman.replace(hour=sure_bas.hour, minute=sure_bas.minute)
                bitis = zaman.replace(hour=sure_bit.hour, minute=sure_bit.minute)
                zaman = bitis
                id_ = '%i' % (i * len(self._SINAV_SURELERI) + j)
                length = int((bitis - baslangic).seconds / 60)
                writer.text_element('period', attrs={'id': id_,
                                                     'length': '%i' % length,
                                                     'day': '',
                                                     'time': '%f %f' % (datetime2timestamp(baslangic),
                                                                        datetime2timestamp(bitis)),
                                                     'penalty':'0',
                                                     })
                try:
                    zamanlar[length].append(id_)
                except KeyError:
                    zamanlar[length] = [id_]
            zaman = zaman + timedelta(days=1)
            i += 1
        return zamanlar

    def _sinav_tarihleri(self, bolum):
        """Bu bölüm için geçerli olan sınav tarihlerini bulur.

        Args:
            bolum (Unit):

        Returns:
            Takvim:
        """
        yil = OgretimYili.objects.get(yil=Donem.guncel_donem().baslangic_tarihi.year)
        akademik_takvim = get_akademik_takvim(bolum, yil)
        sinav_takvim = None
        for etkinlik in self._SINAV_ETKINLIKLERI:
            try:
                sinav_takvim = Takvim.objects.get(akademik_takvim=akademik_takvim, etkinlik=etkinlik)
            except ObjectDoesNotExist:
                pass
        if not sinav_takvim:
            raise RuntimeError('Sınav etkinliği bulunamadı')
        if not sinav_takvim.baslangic:
            raise RuntimeError('Sınav etkinliğinin başlangıç tarihi tanımlanmamış')
        if not sinav_takvim.bitis:
            raise RuntimeError('Sınav etkinliğinin bitiş tarihi tanımlanmamış')
        return sinav_takvim

    def _odalar(self, bolum, writer):
        """Sınavların yapılabileceği odaları, sınav planı çıktısına ekler.

        Args:
            bolum (Unit): Sınav planı çıkarılacak bölüm.
            writer: XML çıktısını yazacak obje

        Returns:
            `list` of `Room`: Bu bölümün sınav yapabileceği odaların listesi.
        """
        # Bu bölümün ders verebildiği, ve sınav amaçlı kullanılabilen odalar
        odalar = [r for r in Room.objects if bolum in r.RoomDepartments and r.room_type.exam_available == True]
        for oda in odalar:
            writer.text_element('room', attrs={'id': '%i' % self._room_id(oda),
                                               'size': '%i' % oda.capacity,
                                               'alt': '%i' % oda.capacity,
                                               'coordinates': '%s,%s' % (oda.building.coordinate_x,
                                                                         oda.building.coordinate_y),
                                               })
        return odalar

    def _sinav_id(self, sube, sinav):
        return '%i' % self._key2id('%s %i' % (sube.key, sinav.tur))

    def _sinavlar(self, bolum, sinav_turleri, zamanlar, odalar, ogrenci_dersler, writer):
        """Sınavları, sınav planı çıktısına ekler.

        Args:
            bolum (Unit): Sınav planı çıkarılacak bölüm.
            sinav_turleri (`list` of `int`): Plana dahil edilecek sınav türleri.
            zamanlar (dict): Sınav sürelerini, bu süre uzunluğundaki zamanlarla eşleştiren sözlük.
            odalar (`list` of `Room`): Sınavlar için kullanılabilecek olan odalar.
            writer: XML çıktısını yazacak obje
        """
        # TODO: Eğer odalar paylaşılıyorsa, diğer bölümlerle sınav yerlerinin çakışmaması sağlanmalı
        donem = Donem.guncel_donem()
        # Eski exportlardan kalmış olabilecek kayıtları, yenileri ile karışmaması için temizle
        SinavEtkinligi.objects.filter(donem=donem, bolum=bolum, published=False).delete()
        programlar = list(Program.objects.filter(bolum=bolum))
        for program in programlar:
            dersler = list(Ders.objects.filter(program=program, donem=donem))
            for ders in dersler:
                subeler = list(Sube.objects.filter(ders=ders, donem=donem))
                for s, sinav in enumerate(ders.Degerlendirme):
                    if sinav.tur not in sinav_turleri: continue
                    for sube in subeler:
                        sinav_id = self._sinav_id(sube, sinav)
                        with writer.element('exam', {'id': sinav_id,
                                                 'length': '%i' % sinav.sinav_suresi,
                                                 # Alternative seating özelliği, odaların oturma planları için kullanılabilir
                                                 'alt': "false",
                                                 # Her odadaki minimum öğrenci sayısı
                                                 'minSize': '%i' % self._SINAV_MIN_KONTENJAN,
                                                 # Sınavın en çok kaç odaya bölünebileceği
                                                 'maxRooms': '%i' % self._SINAV_MAX_ODA,
                                                 }):
                            etkinlik = SinavEtkinligi(ders=ders, sube=sube, donem=donem, bolum=bolum,
                                           unitime_key=sinav_id, published=False)
                            for ogrenci_id in ogrenci_dersler[ders.key]:
                                etkinlik.Ogrenciler.add(ogrenci_id=ogrenci_id)
                            etkinlik.save()
                            uygun_zamanlar = filter(lambda z: z[0] >= sinav.sinav_suresi, zamanlar.items())
                            for zaman, zaman_idleri in uygun_zamanlar:
                                # Kısa süreli sınavların uzun zaman dilimlerine ayrılmasını önlemek için
                                # farka bağlı olarak bir penalty ata
                                penalty = round((zaman - sinav.sinav_suresi) / 30)
                                for zaman_id in zaman_idleri:
                                    writer.text_element('period', attrs={'id': zaman_id, 'penalty': '%i' % penalty})
                            for oda in odalar:
                                oda_id = '%i' % self._room_id(oda)
                                writer.text_element('room', attrs={'id': oda_id})

    def _ogrenciler(self, bolum, sinav_turleri, writer):
        """Öğrencileri, ve girecekleri sınavları çıktıya ekler.

        Args:
            bolum (Unit): Sınav planı çıkarılacak bölüm.
            sinav_turleri (`list` of `int`): Plana dahil edilecek sınav türleri.
            writer: XML çıktısını yazacak obje
        """
        donem = Donem.guncel_donem()

        dersler = []
        for program in list(Program.objects.filter(bolum=bolum)):
            for ders in list(Ders.objects.filter(program=program, donem=donem)):
                dersler.append(ders)

        # TODO: Eğer öğrenci birden fazla bölümden ders alıyorsa, diğer bölümlerin sınavlarının olduğu period'lar unavailable işaretlenmeli
        ogrenciler = set()
        for ders in dersler:
            # Bu dönem bu dersi alan, devamsızlıktan kalmamış öğrenciler
            ods = {od.ogrenci for od in
                   OgrenciDersi.objects.filter(ders=ders, donem=donem).exclude(katilim_durumu=False)}
            ogrenciler.update(ods)

        ders_ogrenciler = defaultdict(set)
        for ogrenci in ogrenciler:
            with writer.element('student', {'id': '%i' % self._key2id(ogrenci.key)}):
                # Öğrencinin bu dönem aldığı ve devamsızlıktan kalmadığı dersleri
                dersleri = list(OgrenciDersi.objects.filter(ogrenci=ogrenci, donem=donem).exclude(katilim_durumu=False))
                sinav_idleri = set()
                for ders in dersleri:
                    ders_ogrenciler[ders.ders.key].add(ogrenci.key)
                    for sinav in ders.ders.Degerlendirme:
                        if sinav.tur not in sinav_turleri: continue
                        sinav_idleri.add(self._sinav_id(ders.sube, sinav))
                for id_ in sinav_idleri:
                    writer.text_element('exam', attrs={'id': id_})
        return ders_ogrenciler

    def _sinirlandirmalar(self, bolum, constraints):
        pass
