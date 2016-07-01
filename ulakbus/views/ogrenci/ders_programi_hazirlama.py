# from ulakbus.lib.unitime import ExportAllDataSet
from ulakbus.models import DersEtkinligi
import xml.etree.ElementTree as ET
import subprocess, os
from ulakbus.lib.common import ders_programi_doldurma

data_set = ExportAllDataSet()
data_set.EXPORT_DIR = '/opt/zato/solver'
data_set.run()

bolum = 124150
export_file = str(bolum)
subprocess.call(["sudo","su","-","zato"])
os.chdir("/")
os.chdir("%s") % data_set.EXPORT_DIR
subprocess.check_call(["sudo", "java", "-Xmx1g" , "-jar" ,"coursett-1.2.jar", "default.cfg", "%s" %export_file, "." ,">" ,"data.txt"])

if 'Test Failed' in open('data.txt').read():
    print "import hatali"

else:
    searchfile = open("data.txt", "r")
    for line in searchfile:
        if "Output folder:" in line:
            folder_dir = line[16:31]
            break

    searchfile.close()
    os.chdir("%s" %folder_dir)
    # path = os.path.join('%s','solution.xml') %folder_dir
    root = ET.parse('solution_xml').getroot()  #'/160630_12050'

    ders_programi_doldurma(root)
    cozulmeyenler = []
    for ders in DersEtkinligi.objects.filter():
        if ders.solved == False:
            cozulmeyenler.append(ders.unitime_id)

    if len(cozulmeyenler)>0:
        print 'hatali'
    else:
        print 'hatasiz'