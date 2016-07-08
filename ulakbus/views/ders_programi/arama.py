# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from ulakbus.models import Room, Okutman, DersEtkinligi
from pyoko.exceptions import ObjectDoesNotExist

ARAMA_TURU = [
    (1, 'Derslik'),
    (2, 'Ogretim Elemani')
]


class AramaForm(JsonForm):

    class Meta:
        title = 'Ogretim Elemani veya Derslik Ara'

    arama_sec = fields.String('Arama Secenegi', choices=ARAMA_TURU, default=1)
    arama_text = fields.String(" ")
    arama_button = fields.Button('Ara')


class DerslikOgElemaniArama(CrudView):

    def derslik_og_elemani_ara(self):

        self.form_out(AramaForm(self.object, current=self.current))

    def arama_kontrol(self):
        text = str(self.input['form']['arama_text'])
        try:
            if self.input['form']['arama_sec'] == 1:
                room = Room.objects.get(code=text)
                ders_etkinligi = DersEtkinligi.objects.filter(room=room)
            else:
                ad = text.split()[0]
                soyad = text.split()[1]
                ogretim_elemani = Okutman.objects.get(ad=ad, soyad=soyad)
                ders_etkinligi = DersEtkinligi.objects.filter(okutman=ogretim_elemani)

            if len(ders_etkinligi) > 1:
                self.current.task_data['cmd'] = 'coklu'
            elif len(ders_etkinligi) == 1:
                self.current.task_data['cmd'] = 'tekli'
            else:
                raise

        except ObjectDoesNotExist:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Kayıt Bulunamadi',
                "msg": 'Ilgili kayit bulunamadi.'

            }

    def coklu_sonuc(self):
        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Coklu Kayıt',
            "msg": '10 tane kayit bulundu.'

        }

    def tek_sonuc(self):
        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Tekli Kayıt',
            "msg": '1 tane kayit bulundu.'
        }
