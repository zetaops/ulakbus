# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Personel
from zengine.views.crud import CrudView

__author__ = 'Ali Riza Keles'

personel = """__Sicil No__: KON123 | __Vatandaşlık No__: {tckn}

### Kimlik Bilgileri

__Anne Adı__: {ana_adi}

__Baba Adı__: {baba_adi}

__Doğum Yeri__:  {dogum_yeri}

__Doğum Tarihi__: {dogum_tarihi}


### Atama ve Görev Bilgileri

__Kadro__: Tekniker, Ahmet Keleşoğlu Fakültesi

__Görevlendirme__: Yok


### İletişim Bilgileri

__Telefon__: 0555 555 55 55

__GSM__: 0555 555 55 55

__Email__: eposta@afasdfads.com

__Address__: Xyz Caddesi ABC Sok. No:5


"""


class PersonelBilgileri(CrudView):

    def __init__(self, current=None):
        super(PersonelBilgileri, self).__init__(current)
        if 'id' in self.current.input.keys():
            self.current.task_data['personel_id'] = self.current.input['id']

        self.object = Personel.objects.get(self.current.task_data['personel_id'])

    class Meta:
        model = 'Personel'

    def goster(self):
        p = self.object
        self.output['object_title'] = "Personel: {0} {1}".format(p.ad, p.soyad)
        self.output['object'] = {
            "": personel.format(**p.clean_value())
        }
