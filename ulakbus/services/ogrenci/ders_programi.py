# -*- coding: utf-8 -*-
# from zato.server.service import Service
from ulakbus.lib.unitime import ExportCourseTimetable
from ulakbus.models import User
import xml.etree.ElementTree as ET
import subprocess
import os
from ulakbus.lib.common import ders_programi_doldurma
import shutil
import httplib
from ulakbus.services.ulakbus_service import UlakbusService


class DersProgramiStartSolver(UlakbusService):
    """Ders programı planlamasını arka planda başlatır."""

    HAS_CHANNEL = True

    def handle(self):
        solver_service = DersProgramiExecuteSolver().name
        self.invoke_async(solver_service, payload=self.request.payload)
        self.response.status_code = httplib.OK
        self.response.payload = {'status': 'ok', 'result': 'Ders planlaması başlatıldı'}


class DersProgramiExecuteSolver(UlakbusService):
    """Bir bölüm için ders programı hesaplaması yapar.

    Bu servisi çalıştırmak için ders programı hesaplanacak olan bölümün
    yöksis numarası, ve ders planı hesaplamasını başlatan kullanıcının key'i
     verilmelidir. Örneğin:

    >>> requests.post('http://example.com/dersler', json={'bolum': 124150, 'kullanici': 'Lpdk2348cTfWeTTXY22asd', 'url': ''})

    Servis, ders programını hesaplayarak sonucunu kaydedecektir. İşlem
    bittiğinde, servis durumunu bildiren bir sonuç verir. Örneğin başarılı
    olması durumunda gelecek sonuç:

        {'status': 'ok', 'result': 'Tüm dersler yerleştirildi'}

    Başarısız bir sonuç örneği:

        {'status': 'fail', 'result': 'Solver çalıştırılırken hata oluştu'}

    Eğer servis HTTP üzerinden kullanılıyorsa HTTP durum kodlarına da bakılabilir.

    Servis tamamlandıktan sonra, işlemi başlatan kullanıcıyı notification göndererek uyaracaktır.
    Kullanıcıya gönderilecek olan mesajı değiştirmek için, servise gönderilen istekte 'baslik' ve 'mesaj'
    alanları kullanılabilir.
    """

    HAS_CHANNEL = False

    _SOLVER_DIR = '/opt/zato/solver'

    def handle(self):
        bolum_yoksis_no = int(self.request.payload['bolum'])
        kullanici_key = self.request.payload['kullanici']
        url = self.request.payload['url']
        export_dir = os.path.join(self._SOLVER_DIR, str(bolum_yoksis_no))
        try:
            status, result = self._handle(bolum_yoksis_no, kullanici_key, url, export_dir)
        except Exception as e:
            shutil.rmtree(export_dir)
            raise e

        # İşlem sonucunu hem HTTP durumu olarak, hem de yanıtın içine yaz
        self.response.status_code = status
        status_msg = 'ok' if status == httplib.OK else 'fail'
        self.response.payload = {'status': status_msg, 'result': result}

    def _handle(self, bolum_yoksis_no, kullanici_key, url, export_dir):
        if not os.path.isdir(self._SOLVER_DIR):
            os.mkdir(self._SOLVER_DIR)

        if os.path.isdir(export_dir):
            return httplib.CONFLICT, '%i yöksis no\'lu bölüm için çalışan bir solver var' % bolum_yoksis_no

        # Derslerin export'unu al
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
        # Solver'ın çıktısını inceleyerek olası hata mesajlarını yakala,
        # solver'ın çözümü yazdığı yeri bul
        for line in p.stdout:
            if 'test failed' in line.lower():
                return httplib.INTERNAL_SERVER_ERROR, 'XML exportları hatalı'
            elif line.startswith("Output folder:"):
                output_folder = line.split(":")[1][1:].strip()

        if output_folder == '':
            return httplib.INTERNAL_SERVER_ERROR, 'Solver çalıştırılırken hata oluştu'

        # Sonuçları oku
        root = ET.parse(os.path.join(output_folder, 'solution.xml')).getroot()
        ders_programi_doldurma(root)
        shutil.rmtree(export_dir)

        # Çözümü isteyen kullanıcıyı bilgilendir
        kullanici = User.objects.get(key=kullanici_key)
        baslik = self.request.payload.get('baslik', 'Ders planlaması tamamlandı')
        mesaj = self.request.payload.get('mesaj', 'Ders planlaması işlemi tamamlandı.')
        kullanici.send_notification(baslik, mesaj, url=url)
        return httplib.OK, mesaj
