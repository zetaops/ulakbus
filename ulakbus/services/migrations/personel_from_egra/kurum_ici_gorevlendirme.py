# -*-  coding: utf-8 -*-
import os
from convert import converter, convert_unit
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models.personel import UcretsizIzin, Personel
from orcl import Orcl
from helper import merge_attr
from datetime import datetime
from ulakbus.models.auth import AbstractRole

#DB_USER = os.getenv("DB_USER", None)
#DB_PASS = os.getenv("DB_PASS", None)
#DB_HOST = os.getenv("DB_HOST", None)

#orcl = Orcl(DB_USER, DB_PASS, DB_HOST)
#orcl.get_cursor()

#orcl.cursor.execute("SELECT g.* FROM SUPEBS.KURUMICIGOREV g")

#insert = 0
#fail = 0
#dosya = open("failed/kurum_ici_gorevlendirme_failed.txt","a")

#for row in orcl.rows_as_dicts():
#	data, err = converter("KURUMICIGOREV", row)

abs_role = AbstractRole.objects.filter()

for row in abs_role:
	print row.name