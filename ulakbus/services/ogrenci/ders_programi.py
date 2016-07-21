# -*- coding: utf-8 -*-
from zato.server.service import Service
from ulakbus.lib.unitime import ExportCourseTimetable
from ulakbus.models.ders_programi_data import DersEtkinligi, Donem, Unit
import xml.etree.ElementTree as ET
import subprocess
import os
from ulakbus.lib.common import ders_programi_doldurma
import shutil
import httplib


class ExecuteSolver(Service):
    _SOLVER_DIR = '/opt/zato/solver'

    def handle(self):
        bolum_yoksis_no = int(self.request.payload['bolum'])
        export_dir = os.path.join(self._SOLVER_DIR, str(bolum_yoksis_no))
        try:
            status, result = self._handle(bolum_yoksis_no, export_dir)
        except Exception as e:
            shutil.rmtree(export_dir)
            raise e

        self.response.status_code = status
        status_msg = 'ok' if status == httplib.OK else 'fail'
        self.response.payload = {'status': status_msg, 'result': result}

    def _handle(self, bolum_yoksis_no, export_dir):
        if not os.path.isdir(self._SOLVER_DIR):
            os.mkdir(self._SOLVER_DIR)

        if os.path.isdir(export_dir):
            return httplib.CONFLICT, '%i yöksis no\'lu bölüm için çalışan bir solver var' % bolum_yoksis_no

        # XML export etmeye yarar.
        data_set = ExportCourseTimetable(bolum=bolum_yoksis_no)
        os.mkdir(export_dir)
        data_set.EXPORT_DIR = export_dir
        data_set.run()

        # export edilen XML dosyasini, solverda calistirir.
        export_file = os.path.join(export_dir, '%i.xml' % bolum_yoksis_no)
        os.chdir(self._SOLVER_DIR)

        p = subprocess.Popen(
            ["java", "-Xmx1g", "-jar", "cpsolver-1.3.79.jar", "great-deluge.cfg", export_file, export_dir],
            stdout=subprocess.PIPE, universal_newlines=True)

        os.chdir(export_dir)
        output_folder = ''
        p.wait()
        for line in p.stdout:
            if 'test failed' in line.lower():
                return httplib.INTERNAL_SERVER_ERROR, 'XML exportları hatalı'
            elif line.startswith("Output folder:"):
                output_folder = line.split(":")[1][1:].strip()

        if output_folder == '':
            return httplib.INTERNAL_SERVER_ERROR, 'Solver çalıştırılırken hata oluştu'

        root = ET.parse(os.path.join(output_folder, 'solution.xml')).getroot()
        ders_programi_doldurma(root)

        donem = Donem.guncel_donem()
        bolum = Unit.objects.get(yoksis_no=bolum_yoksis_no)
        cozulemeyenler = DersEtkinligi.objects\
            .filter(donem=donem, bolum=bolum)\
            .exclude(solved=True)

        shutil.rmtree(export_dir)
        if len(cozulemeyenler) > 0:
            return httplib.OK, 'Eksik çözüm bulundu'
        return httplib.OK, 'Tüm dersler yerleştirildi'