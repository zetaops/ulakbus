from ulakbus.lib.unitime import ExportAllDataSet
from ulakbus.models.ders_programi_data import DersEtkinligi
import xml.etree.ElementTree as ET
import subprocess, os
from ulakbus.lib.common import ders_programi_doldurma

# XML export etmeye yarar.
data_set = ExportAllDataSet()
data_set.EXPORT_DIR = '/opt/zato/solver'
data_set.run()

# export edilen XML dosyasini, solverda calistirir.
bolum = 124150
export_file = str(bolum) + '.xml'
os.chdir(data_set.EXPORT_DIR)
subprocess.check_call(["sudo", "java", "-Xmx1g" , "-jar" ,"coursett-1.2.jar", "default.cfg", "%s" %export_file, "." ,">" ,"data.txt"])

# solver calistiktan sonra eger outputta 'Test Failed' olmussa, hata var demektir.

if 'Test Failed' in open('data.txt').read():
    print "XML exportlari hatali"

# yoksa bir sonuc bulmus demektir. Olusan ciktiyi txt dosyasina yazarak ve parse ederek,
# olusturulan sonucu hangi klasore koydugunu bulabiliriz.
else:
    folder_dir = ''
    searchfile = open("data.txt", "r")
    for line in searchfile:
        if "Output folder:" in line:
            folder_dir = line[16:31]
            break


# o klasore giderek solution.xml dosyasini parse ederek ders_programi_doldurma methoduna yollariz.
    searchfile.close()
    os.chdir(folder_dir)
    root = ET.parse('solution_xml').getroot()  #'/160630_120504'


# bu method ile olusturulan ders programinin hatasiz ya da ne kadar hatali bir sonuc urettigini bulabiliriz.
    ders_programi_doldurma(root)
    cozulmeyenler = []
    for ders in DersEtkinligi.objects.filter():
        if ders.solved == False:
            cozulmeyenler.append(ders.unitime_id)

    if len(cozulmeyenler)>0:
        print 'hatali'
    else:
        print 'hatasiz'