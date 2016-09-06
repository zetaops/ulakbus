# -*-  coding: utf-8 -*-
import os
from convert import converter, convert_unit
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models.personel import UcretsizIzin, Personel
from orcl import Orcl
from helper import merge_attr
from datetime import datetime

DB_USER = os.getenv("DB_USER", None)
DB_PASS = os.getenv("DB_PASS", None)
DB_HOST = os.getenv("DB_HOST", None)

orcl = Orcl(DB_USER, DB_PASS, DB_HOST)
orcl.get_cursor()

orcl.cursor.execute("SELECT u.* FROM SUPEBS.UCRETSIZ u")

insert = 0
fail = 0
dosya = open("failed/ucretsiz_izin_failed.txt","a")

for row in orcl.rows_as_dicts():
	data, err = converter("UCRETSIZIZIN", row)
	izin = UcretsizIzin()
	merge_attr(izin, data)

	try:
		baslangic_tarih = row["BASTAR"]
		bitis_tarih = row["BITTAR"]
		if baslangic_tarih != None:
			izin.baslangic_tarihi = baslangic_tarih.strftime("%d.%m.%Y")
		if bitis_tarih != None:
			izin.bitis_tarihi = bitis_tarih.strftime("%d.%m.%Y")

		personel = Personel.objects.get(tckn=row["VATANDASLIKNO"])
		izin.personel = personel
		izin.save()
		insert += 1
		print "%i/%i kayıt eklendi"%(row["P_HAREKET1"], row["P_HAREKET2"])
	except ObjectDoesNotExist:
		fail += 1
		dosya.write("%i/%i\n"%(row["P_HAREKET1"], row["P_HAREKET2"]))
		# Buradaki %i/%i yine P_HAREKET1 ve P_HAREKET2 alanlarıdır.
		print "%i/%i kayıt eklenemedi"%(row["P_HAREKET1"], row["P_HAREKET2"])
		continue

dosya.close()

print "%i kayıt kopyalandı"%insert
print "%i kayıt kopyalanamadı"%fail