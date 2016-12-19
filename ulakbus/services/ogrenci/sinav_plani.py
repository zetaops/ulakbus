# -*- coding: utf-8 -*
from ulakbus.lib.unitime import ExportExamTimetable
from ulakbus.lib.common import sinav_etkinlikleri_oku
from ulakbus.models import User
from xml.etree import ElementTree
import subprocess
import shutil
import os
import httplib
from ulakbus.services.ulakbus_service import UlakbusService


class SinavPlaniStartExamSolver(UlakbusService):
    """Sınav programı planlamasını arka planda başlatır."""

    HAS_CHANNEL = True

    def handle(self):
        solver_service = SinavPlaniExecuteExamSolver().name
        # Bize verilen payload'u Exam Solver servisine aktararak çalıştırıyoruz
        self.invoke_async(solver_service, payload=self.request.payload)
        self.response.status_code = httplib.OK
        self.response.payload = {'status': 'ok', 'result': 'Sınav planlaması başlatıldı'}


class SinavPlaniExecuteExamSolver(UlakbusService):
    """Bir bölüm için sınav planı hesaplaması yapar.

    Bu servisi çalıştırmak için sınav planı hesaplanacak olan bölümün
    yöksis numarası, hesaplamaya dahil edilecek sınavların türlerinin
    listesi, ve sınav planı hesaplamasını başlatan kullanıcının key'i
    verilmelidir. Örneğin:

    >>> requests.post('http://example.com/sinavlar', json={'bolum': 124150, 'sinav_turleri': [1], 'kullanici': 'Lpdk2348cTfWeTTXY22asd', 'url': ''})

    Servis, sınav programını hesaplayarak sonucunu kaydedecektir. İşlem
    bittiğinde, servis durumunu bildiren bir sonuç verir. Örneğin başarılı
    olması durumunda gelecek sonuç:

        {'status': 'ok', 'result': 'Planlama tamamlandı'}

    Başarısız bir sonuç örneği:

        {'status': 'fail', 'result': '00000 yöksis no\'lu bölüm için çalışan bir solver var'}

    Eğer servis HTTP üzerinden kullanılıyorsa HTTP durum kodlarına da bakılabilir.

    Servis tamamlandıktan sonra, işlemi başlatan kullanıcıyı notification göndererek uyaracaktır.
    Kullanıcıya gönderilecek olan mesajı değiştirmek için, servise gönderilen istekte 'baslik' ve 'mesaj'
    alanları kullanılabilir.
    """
    HAS_CHANNEL = False

    _SOLVER_DIR = '/opt/zato/solver'

    def handle(self):
        bolum_yoksis_no = int(self.request.payload['bolum'])
        sinav_turleri = self.request.payload['sinav_turleri']
        kullanici_key = self.request.payload['kullanici']
        url = self.request.payload['url']
        export_dir = os.path.join(self._SOLVER_DIR, '%i' % bolum_yoksis_no)
        
        status, result = self._handle(bolum_yoksis_no, sinav_turleri, kullanici_key, url, export_dir)


        # İşlem sonucunu hem HTTP durumu olarak, hem de yanıtın içine yaz
        self.response.status_code = status
        status_msg = 'ok' if status == httplib.OK else 'fail'
        self.response.payload = {'status': status_msg, 'result': result}

    def _handle(self, bolum_yoksis_no, sinav_turleri, kullanici_key, url, export_dir):
        if not os.path.isdir(self._SOLVER_DIR):
            os.mkdir(self._SOLVER_DIR)

        exporter = ExportExamTimetable(bolum=bolum_yoksis_no,
                                       sinav_turleri=','.join(map(str, sinav_turleri)))

        if os.path.isdir(export_dir):
            return httplib.CONFLICT, '%i yöksis no\'lu bölüm için çalışan bir solver var' % bolum_yoksis_no

        # Sınavların export'unu al
        os.mkdir(export_dir)
        exporter.EXPORT_DIR = export_dir
        exporter.FILE_NAME = '%i.xml' % bolum_yoksis_no
        exporter.run()
        if not os.path.isfile(os.path.join(export_dir, exporter.FILE_NAME)):
            return httplib.INTERNAL_SERVER_ERROR, '%i yöksis no\'lu bölüm için export alınamamış' % bolum_yoksis_no

        # Alınan export'u solver'a çözdür
        os.chdir(self._SOLVER_DIR)
        prefix_file = os.path.join(export_dir, '%i' % bolum_yoksis_no)
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

        # Çözümü isteyen kullanıcıyı bilgilendir
        kullanici = User.objects.get(key=kullanici_key)
        baslik = self.request.payload.get('baslik', 'Sınav planlaması tamamlandı')
        mesaj = self.request.payload.get('mesaj', 'Sınav planlaması işlemi tamamlandı.')
        kullanici.send_notification(baslik, mesaj, url=url)
        return httplib.OK, mesaj
