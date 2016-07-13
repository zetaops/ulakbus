# -*-  coding: utf-8 -*-
from zato.server.service import Service
from ulakbus.lib.unitime import ExportAllDataSet
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

        # işlem yapılacak olan bölümün yöksis numarası
        bolum_yoksis_no = str(self.request.payload['bolum'])

        # XML exportlarını almak için instance yaratılır.
        data_set = ExportAllDataSet(bolum=bolum_yoksis_no)
        # XML exportlarının çıkartılacağı yerin pathi
        export_dir = os.path.join(self._SOLVER_DIR, bolum_yoksis_no)

        # eğer solver çalışır durumdaysa (bölüm yoksis numarası ile oluşturulmuş
        # bir directrory varsa error döndürülür.)
        if os.path.isdir(export_dir):
            status = 'fail'
            result = 'zaten calisan bir solver var'
        # çalışan bir solver yoksa, bölümün yöksis numarasından bir directory yaratılır.

        else:
            os.mkdir(export_dir)

            # XML exportlarının çıkartılacağı yerin path'i verilir.
            data_set.EXPORT_DIR = export_dir
            # XML exportları çıkartılır.
            data_set.run()

            # export edilen XML dosyasini, solverda calistirir.
            export_file = os.path.join(export_dir, str(bolum_yoksis_no) + '.xml')
            os.chdir(self._SOLVER_DIR)

            # export edilen XMl solverda çalıştırılır.
            p = subprocess.Popen(
                ["java", "-Xmx1g", "-jar", "cpsolver-1.3.79.jar", "great-deluge.cfg", export_file, export_dir],
                stdout=subprocess.PIPE, universal_newlines=True)

            # os.chdir(export_dir)
            output_folder = ''
            status = 'ok'
            result = ''
            c = 0
            # while p.poll() is None:
            while c < 1000000:
                c += 1

                best_found = False
                for line in p.stdout:
                    # eğer solver outputunda hata varsa (XML exportları hatalı) error döndürülür.
                    if 'test failed' in line.lower():
                        status = 'error'
                        result = 'XML exportlari hatali'
                    # hata yoksa, outputtan solution.xml çıktısının hangi foldera konulduğu bilgisi bulunur.
                    if line.startswith("Output folder:"):
                        output_folder = line.split(":")[1][1:].strip()
                    if "BEST" in line:
                        best_found = True
                if not best_found:
                    break
                if status == 'error': break

            try:
                # istenilen sonuç bulunduğunda ınterrupt yollanarak solver durdurulur.
                p.send_signal(signal.SIGINT)
            except OSError:
                pass

            # çalışan program durana kadar bekler.
            p.wait()
            print output_folder
            if status == 'ok':

                # output'un çıktığı yere gidilir.
                os.chdir(output_folder)
                # solution.xml parse edilir.
                root = ET.parse('solution.xml').getroot()

                """
                solution'ın bize bulduğu çözüme göre oda, okutman, şube gibi DersEtkinliği modelinde
                bulunan gerekli field lar doldurulur.
                """
                ders_programi_doldurma(root)
                cozulmeyenler = []

                """
                DersEtkinliği modelinde 'solved' fieldı default olarak False'dur.
                Dönen çözümde eğer solver bir çözüm üretebilmişse solved field'ı True olarak
                işaretlenir. Solutıon bulunduktan sonra eğer hala yerleştirilemeyen objectler varsa
                eksik çözüm bulunmuş demektir, eğer hepsi True ise eksiksiz olarak yerleştirilmiştir.
                """
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

