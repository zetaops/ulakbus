# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Personel
from zengine.views.crud import CrudView

__author__ = 'Ali Riza Keles'

personel = """__Sicil No__: {sicil_no} | __Vatandaşlık No__: {tckn}

### Kimlik Bilgileri

__Anne Adı__: {ana_adi}

__Baba Adı__: {baba_adi}

__Doğum Yeri__:  {dogum_yeri}

__Doğum Tarihi__: {dogum_tarihi}


### Atama ve Görev Bilgileri

__Kadro__: {kadro}

__Kurum İçi Görevlendirme__: {kurum_ici_gorevlendirme}

__Kurum Dışı Görevlendirme__: {kurum_disi_gorevlendirme}


### İletişim Bilgileri

__Oda Telefonu__: {oda_telefon}

__GSM__: {gsm}

__Email__: {mail}

__Address__: {adres}


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

        """
            Migration sırasında Doğum Tarihi bilgisi boş gelebilmektedir. Boş gelen verinin
            programı kırmaması için kontrolü yapılmaktadır.
        """

        dogum_tarihi = ""
        if (p.dogum_tarihi != None) and (p.dogum_tarihi != ""):
            dogum_tarihi = "%i.%i.%i"%(
                p.dogum_tarihi.day,
                p.dogum_tarihi.month,
                p.dogum_tarihi.year
            )

        kurum_ici_gorevlendirme = ""
        if p.kurum_ici_gorevlendirme.count() > 0:
            kurum_ici_gorevlendirme = p.kurum_ici_gorevlendirme[0].birim.name

        kurum_disi_gorevlendirme = ""
        if p.kurum_disi_gorevlendirme.count() > 0:
            kurum_disi_gorevlendirme = p.kurum_disi_gorevlendirme[0].get_ulke_display()

        self.output['object'] = {
            "": personel.format(
                sicil_no = p.kurum_sicil_no_int,
                tckn = p.tckn,
                ana_adi = p.ana_adi,
                baba_adi = p.baba_adi,
                dogum_yeri = p.dogum_yeri,
                dogum_tarihi = dogum_tarihi,
                kadro = p.kadro.birim.name,
                kurum_ici_gorevlendirme = kurum_ici_gorevlendirme,
                kurum_disi_gorevlendirme = kurum_disi_gorevlendirme,
                oda_telefon = p.oda_tel_no,
                gsm = p.cep_telefonu,
                mail = p.e_posta,
                adres = p.ikamet_adresi
            )
        }
