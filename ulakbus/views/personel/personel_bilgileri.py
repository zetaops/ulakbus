# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Personel
from zengine.views.crud import CrudView

__author__ = 'Ali Riza Keles'

personel_karti = """__Sicil No__: {sicil_no} | __Vatandaşlık No__: {tckn}

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

    class Meta:
        model = 'Personel'

    def goster(self):
        p = self.object
        self.output['object_title'] = "Personel: {0} {1}".format(p.ad, p.soyad)

        kig = p.kurum_ici_gorevlendirme.birim.name if p.kurum_ici_gorevlendirme else ""
        kdg = p.kurum_disi_gorevlendirme.get_ulke_display() if p.kurum_disi_gorevlendirme else ""

        self.output['object'] = {
            "": personel_karti.format(
                sicil_no=p.kurum_sicil_no_int,
                tckn=p.tckn,
                ana_adi=p.ana_adi,
                baba_adi=p.baba_adi,
                dogum_yeri=p.dogum_yeri,
                dogum_tarihi=p.dogum_tarihi.strftime(
                    "%d.%m.%Y") if p.dogum_tarihi is not None else "",
                kadro=p.kadro.birim.name,
                kurum_ici_gorevlendirme=kig,
                kurum_disi_gorevlendirme=kdg,
                oda_telefon=p.oda_tel_no,
                gsm=p.cep_telefonu,
                mail=p.e_posta,
                adres=p.ikamet_adresi
            )
        }
