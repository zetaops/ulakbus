# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from collections import OrderedDict
from ulakbus.models import Room, Okutman, DersEtkinligi

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


class DersProgramiYap(CrudView):

    def kontrol(self):
        pass

    def ders_programi_yolla(self):
        _form = JsonForm(title="Ders Programi Olustur")
        _form.button = fields.Button('Gonder')
        self.form_out(_form)

    def zato_service_cagir(self):
        pass

    def ders_programi_olusturuluyor(self):
        msg = {"title": 'Ders Programi Olusturuluyor',
               "body": 'Ders programi için yaptığınız taleb başarıyla alınmıştır.'}
        self.current.task_data['LANE_CHANGE_MSG'] = msg
        _form = JsonForm(title="Devam")
        _form.devam = fields.Button("Devam")
        self.form_out(_form)

    def ders_programi_tamamlandi(self):
        self.current.task_data['cmd'] = 'hata_yok'

    def hatasiz(self):
        msg = {"title": 'Ders Programi Olusturuldu',
               "body": 'Ders programi hatasiz bir sekilde olusturuldu.'}

        self.current.task_data['LANE_CHANGE_MSG'] = msg
        _form = JsonForm(title="Devam")
        _form.devam = fields.Button("Devam", cmd='incele')
        self.form_out(_form)

    def derslik_og_elemani_ara(self):
        # sample:
        self.form_out(AramaForm(self.object, current=self.current))

    def arama_kontrol(self):
        text = str(self.input['form']['arama_text'])
        try:
            if self.input['form']['arama_sec'] == 1:
                room_search = Room.objects.filter(code=text)
                if len(room_search) > 1:
                    self.current.search = room_search
                    self.current.task_data['cmd'] = 'coklu'
                elif len(room_search) == 1:
                    self.current.ders_etkinligi = sorted(DersEtkinligi.objects.filter(room=room_search[0]),
                                                         key=lambda d: (d.gun, d.baslangic_saat, d.baslangic_dakika))
                    self.current.task_data['cmd'] = 'tekli'
                else:
                    raise
            else:
                ad = text.split()[0]
                soyad = text.split()[1]
                okutman_search = Okutman.objects.filter(ad=ad, soyad=soyad)
                if len(okutman_search) > 1:
                    self.current.search = okutman_search
                    self.current.task_data['cmd'] = 'coklu'
                elif len(okutman_search) == 1:
                    self.current.ders_etkinligi = sorted(DersEtkinligi.objects.filter(okutman=okutman_search[0]),
                                                         key=lambda d: (d.gun, d.baslangic_saat, d.baslangic_dakika))
                    self.current.task_data['cmd'] = 'tekli'
                else:
                    raise
        except:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Kayıt Bulunamadi',
                "msg": 'Ilgili kayit bulunamadi.'
            }

    def coklu_sonuc(self):

        self.output['objects'] = [['Ad', 'Soyad']]
        for data in self.current.search:
            data_list = OrderedDict({})
            data_list['Ad'] = data.ad
            data_list['Soyad'] = data.soyad
            item = {
                'type': "table-multiRow",
                'fields': data_list,
                'actions': [
                    {'name': 'Goster', 'cmd': 'tek_sonuc', 'show_as': 'button', 'object_key': 'ogretim_elemani'}
                ],
                'key': data.key
            }
            self.output['objects'].append(item)

    def tek_sonuc(self):
        """
        .. code-block:: python
            # response:
            {
             'ders_programi': {
                 'name': string,     # code
                 'gunler': [string, string,...],     # days,
                 'dersler': [{
                     'ad': string,  # lesson name
                     'gun': string,  # day,
                     'saat_araligi': string,  # '10.30-12.00',
                     'atama': string,      # code or name
                     }]}
        """

        dersler = list()

        for de in self.current.ders_etkinligi:
            if self.input['form']['arama_sec'] == 1:
                atama = de.okutman.ad + ' ' + de.okutman.soyad
                self.current.name = de.room.code
            else:
                atama = de.room.code
                self.current.name = de.okutman.ad + ' ' + de.okutman.soyad
            ders = dict()
            ders['ad'] = de.sube.ders.ad
            ders['gun'] = de.gun
            ders['saat_araligi'] = de.baslangic_saat+':'+de.baslangic_dakika+'-'+de.bitis_saat+':'+de.bitis_dakika
            ders['atama'] = atama
            dersler.append(ders)
        item = {'name': self.current.name,
                'gunler': ["Pazartesi", "Sali", "Carsamba", "Persembe", "Cuma", "Cumartesi", "Pazar"],
                'dersler': dersler}
        self.output['ders_programi'] = item

    def hatali(self):
        pass

    def derslik_ogretim_elemani_kontrol(self):
        pass

    def yolla(self):
        pass

    def bilgilendirme(self):
        pass
