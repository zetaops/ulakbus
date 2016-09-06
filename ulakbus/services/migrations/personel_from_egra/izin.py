# -*-  coding: utf-8 -*-
import os
from convert import converter, convert_unit
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models.personel import Izin, Personel
from orcl import Orcl
from helper import merge_attr
from datetime import datetime

DB_USER = os.getenv("DB_USER", None)
DB_PASS = os.getenv("DB_PASS", None)
DB_HOST = os.getenv("DB_HOST", None)

orcl = Orcl(DB_USER, DB_PASS, DB_HOST)
orcl.get_cursor()

orcl.cursor.execute("SELECT i.* FROM SUPEBS.IZIN i")

insert = 0
fail = 0
dosya = open("izin_failed.txt","a")

for row in orcl.rows_as_dicts():
	data, err = converter("IZINLER", row)
	izin = Izin()
	merge_attr(izin, data)
	try:
		baslangic_tarih = row["BASTAR"]
		bitis_tarih= row["BITTAR"]
		onay_tarih = row["ONAYTAR"]
		if baslangic_tarih != None:
			izin.baslangic = baslangic_tarih.strftime("%d.%m.%Y")
		if bitis_tarih != None:
			izin.bitis = bitis_tarih.strftime("%d.%m.%Y")
		if onay_tarih != None:
			izin.onay = onay_tarih.strftime("%d.%m.%Y")
		personel = Personel.objects.get(tckn=row["VATANDASLIKNO"])
		izin.personel = personel
		if row["VEKALET_SICILNO"] != None:
			vekil = Personel.objects.get(kurum_sicil_no_int=row["VEKALET_SICILNO"])
			izin.vekil = vekil
		izin.save()
		insert += 1
		print "%i eklendi"%row["IZIN_ID"]
	except:
		fail += 1
		dosya.write("%i\n"%row["IZIN_ID"])
		print "%i eklenemedi"%row["IZIN_ID"]
		continue

dosya.close()

print "%i kayıt kopyalandı"%insert
print "%i kayıt kopyalanamadı"%fail