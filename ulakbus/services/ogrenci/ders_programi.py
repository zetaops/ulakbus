from zato.server.service import Service
from ulakbus.lib.unitime import ExportCourseTimetable
from ulakbus.models.ders_programi_data import DersEtkinligi, Donem, Unit
import xml.etree.ElementTree as ET
import subprocess
import os
from ulakbus.lib.common import ders_programi_doldurma
import time
import signal
import shutil


class ExecuteSolver(Service):
    _SOLVER_DIR = '/opt/zato/solver'

    def handle(self):

        bolum_yoksis_no = int(self.request.payload['bolum'])
        # bolum_yoksis_no = str(self.bolum_yoksis_no)
        # guncel_donem = Donem.objects.get(guncel=True)
        # bolum = Unit.objects.get(yoksis_no = bolum_yoksis_no)
        # secilen_bolum = DersEtkinligi.objects.get(donem=guncel_donem, bolum = bolum)

        if not os.path.isdir(self._SOLVER_DIR):
            os.mkdir(self._SOLVER_DIR)

        # XML export etmeye yarar.
        data_set = ExportCourseTimetable(bolum=bolum_yoksis_no)
        export_dir = os.path.join(self._SOLVER_DIR, str(bolum_yoksis_no))

        if os.path.isdir(export_dir):
            status = 'fail'
            result = 'zaten calisan bir solver var'

        else:
            os.mkdir(export_dir)
            data_set.EXPORT_DIR = export_dir
            data_set.run()

            # export edilen XML dosyasini, solverda calistirir.
            export_file = os.path.join(export_dir, str(bolum_yoksis_no) + '.xml')
            print export_file
            os.chdir(self._SOLVER_DIR)

            p = subprocess.Popen(
                ["java", "-Xmx1g", "-jar", "cpsolver-1.3.79.jar", "great-deluge.cfg", export_file, export_dir],
                stdout=subprocess.PIPE, universal_newlines=True)

            os.chdir(export_dir)
            output_folder = ''
            status = 'ok'
            result = ''
            # c = 0
            # time.sleep()
            # while p.poll() is None:
            # while c < 100:
            # c += 1
            p.wait()
            best_found = False
            for line in p.stdout:
                print line
                if 'test failed' in line.lower():
                    status = 'fail'
                    result = 'XML exportlari hatali'
                if line.startswith("Output folder:"):
                    output_folder = line.split(":")[1][1:].strip()
                if "BEST" in line:
                    best_found = True
            # if not best_found:
            #     break
            # if status == 'fail': break

            # try:
            #     p.send_signal(signal.SIGINT)
            # except OSError:
            #     pass

            # p.wait()
            print output_folder
            if status == 'ok':

                os.chdir(output_folder)
                root = ET.parse('solution.xml').getroot()

                ders_programi_doldurma(root)
                cozulmeyenler = []
                for ders in DersEtkinligi.objects.filter():
                    if not ders.solved:
                        cozulmeyenler.append(ders.unitime_id)

                if len(cozulmeyenler) > 0:
                    print 'hatali'
                    result = 'eksik cozum bulundu'
                else:
                    result = 'butun dersler yerlestirildi'
                    print 'hatasiz'

            shutil.rmtree(export_dir)


        self.response.payload = {"status": status, "result": result}