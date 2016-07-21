# -*- coding: utf-8 -*
from zato.server.service import Service
from ulakbus.lib.unitime import ExportExamTimetable
from ulakbus.lib.common import sinav_etkinlikleri_oku
from ulakbus.models import SinavEtkinligi, Donem, Unit
from xml.etree import ElementTree
import subprocess
import shutil
import os


class ExecuteExamSolver(Service):
    _SOLVER_DIR = '/opt/zato/solver'

    def handle(self):
        status, result = self._handle()
        self.response.payload = {'status': status, 'result': result}

    def _handle(self):
        bolum_yoksis_no = str(self.request.payload['bolum'])
        sinav_turleri = str(self.request.payload['sinav_turleri'])

        if not os.path.isdir(self._SOLVER_DIR):
            os.mkdir(self._SOLVER_DIR)


        exporter = ExportExamTimetable(bolum=bolum_yoksis_no, sinav_turleri=sinav_turleri)
        export_dir = os.path.join(self._SOLVER_DIR, bolum_yoksis_no)

        if os.path.isdir(export_dir):
            return 'fail', '%s yöksis no\'lu bölüm için çalışan bir solver var' % bolum_yoksis_no

        # Sınavların export'unu al
        os.mkdir(export_dir)
        exporter.EXPORT_DIR = export_dir
        exporter.FILE_NAME = '%s.xml' % bolum_yoksis_no
        exporter.run()
        if not os.path.isfile(os.path.join(export_dir, exporter.FILE_NAME)):
            return 'fail', '%s yöksis no\'lu bölüm için export alınamamış'

        # Alınan export'u solver'a çözdür
        os.chdir(self._SOLVER_DIR)
        prefix_file = os.path.join(export_dir, bolum_yoksis_no)
        export_file = '%s.xml' % prefix_file
        output_file = '%s.OUTPUT.xml' % prefix_file
        p = subprocess.Popen(
            ['java', '-Xmx1g', '-cp', 'cpsolver-1.3.79.jar', 'org.cpsolver.exam.Test', 'exam-base.cfg',
             export_file, output_file],
        )
        p.wait()

        # Sonuçları oku
        root = ElementTree.parse(output_file).getroot()
        sinav_etkinlikleri_oku(root)
        shutil.rmtree(export_dir)
        # Sonuçları kontrol et
        guncel_donem = Donem.guncel_donem()
        bolum = Unit.objects.get(yoksis_no=bolum_yoksis_no)
        cozulmemis_sinavlar = SinavEtkinligi.objects.filter(donem=guncel_donem,
                                                            solved=True,
                                                            bolum=bolum)
        if len(cozulmemis_sinavlar) > 0:
            return 'ok', 'Eksik çözüm bulundu'
        return 'ok', 'Tüm sınavlar yerleştirildi'
