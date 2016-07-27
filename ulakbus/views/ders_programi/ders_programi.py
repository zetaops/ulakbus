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
from ulakbus.services.zato_wrapper import DersProgramiOlustur
from ulakbus.models import Room, Okutman, DersEtkinligi, Donem

ARAMA_TURU = [
    (1, 'Derslik'),
    (2, 'Öğretim Elemanı')
]


class AramaForm(JsonForm):

    class Meta:
        title = 'Öğretim Elemanı veya Derslik Ara'

    arama_sec = fields.String('Arama Seçeneği', choices=ARAMA_TURU, default=1)
    arama_text = fields.String(" ")
    arama_button = fields.Button('Ara')


class DersProgramiYap(CrudView):

    def kontrol(self):
        ders_etkinligi_count = DersEtkinligi.objects.filter(bolum=self.current.role.unit,
                                                            donem=Donem.guncel_donem()).count()

        solved_count = DersEtkinligi.objects.filter(bolum=self.current.role.unit,
                                                    donem=Donem.guncel_donem(),
                                                    solved=True).count()

        published_count = DersEtkinligi.objects.filter(bolum=self.current.role.unit, published=True,
                                                       donem=Donem.guncel_donem()).count()

        if published_count > 0:
            self.current.task_data['cmd'] = 'kayit_var'

        elif solved_count == ders_etkinligi_count and solved_count > 0:
            self.current.task_data['cmd'] = 'hatasiz_sonuc'
            msg = {"type": 'info',
                   "title": 'Yayınlanmamış Ders Programı Var!',
                   "msg":  'Yayınlanmayan ders programını inceleyip yayınlayabilirsiniz.'}
            # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır
            self.current.task_data['LANE_CHANGE_MSG'] = msg
        elif solved_count != ders_etkinligi_count and solved_count > 0:
            msg = {"type": 'warning',
                   "title": 'Hatalı Sonuçlar Var!',
                   "msg":  'Oluşturulan ders programınızda hatalı sonuçlar bulunmaktadır.'
                            'Lütfen tekrardan ders programı oluşturunuz.'}
            # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır
            self.current.task_data['LANE_CHANGE_MSG'] = msg

    def ders_programi_hesaplama_baslat(self):
        if 'LANE_CHANGE_MSG' in self.current.task_data:
            if self.current.task_data['LANE_CHANGE_MSG']['title'] == 'Hatalı Sonuçlar Var!':
                self.current.output['msgbox'] = self.current.task_data['LANE_CHANGE_MSG']
        _form = JsonForm(title="Ders Programı Oluştur")
        _form.button = fields.Button('Başlat')
        self.form_out(_form)

    def ders_programi_hesapla(self):
        dp = DersProgramiOlustur(service_payload={"bolum": self.current.role.unit.yoksis_no,
                                                  "kullanici": self.current.user.key,
                                                  "url": self.current.get_wf_link()})
        response = dp.zato_request()

        if response:
            msg = {"type": 'info',
                   "title": 'Ders Programı Oluşturuluyor',
                   "msg": 'Ders programı için yaptığınız taleb başarıyla alınmıştır.'}
            self.current.task_data['LANE_CHANGE_MSG'] = msg
        else:
            msg = {"type": 'warning',
                   "title": 'Sistemde Sorun Oluştu',
                   "msg": 'Lütfen tekrardan ders programı oluşturmayı çalıştırnız!'}
            self.current.task_data['LANE_CHANGE_MSG'] = msg

    def servis_bilgi_mesaji(self):

        if self.current.task_data['LANE_CHANGE_MSG']['title'] == 'Ders Programı Oluşturuluyor':
            self.current.output['msgbox'] = self.current.task_data['LANE_CHANGE_MSG']

        _form = JsonForm(title="Devam")
        _form.devam = fields.Button("Devam")
        self.form_out(_form)

    def ders_programi_sonucu(self):
        self.current.task_data['cmd'] = 'hata_yok'

    def hatasiz(self):
        _form = JsonForm(title="Devam")
        _form.devam = fields.Button("Devam", cmd='incele')
        self.form_out(_form)
        self.current.output['msgbox'] = self.current.task_data['LANE_CHANGE_MSG']

    def derslik_og_elemani_ara(self):

        self.form_out(AramaForm(self.object, current=self.current))

    def arama(self):
        text = str(self.input['form']['arama_text'])
        try:
            if self.input['form']['arama_sec'] == 1:
                room_search = Room.objects.get(code=text)
                if room_search:
                    self.current.ders_etkinligi = sorted(DersEtkinligi.objects.filter(room=room_search),
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

    def detay_goster(self):
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

    def yayinla(self):
        pass

    def bilgilendirme(self):
        pass


class OgretimElemaniDersProgrami(CrudView):

    def kontrol(self):
        okutman = Okutman.objects.get(personel=self.current.user.personel)
        ders_etkinligi = sorted(DersEtkinligi.objects.filter(okutman=okutman), key=lambda d: (d.gun, d.baslangic_saat))
        for de in ders_etkinligi:
            if not de.published or de.published is False:
                self.current.task_data['cmd'] = 'yok'
                break

    def ders_programini_goster(self):
        okutman = Okutman.objects.get(personel=self.current.user.personel)
        ders_etkinligi = sorted(DersEtkinligi.objects.filter(okutman=okutman), key=lambda d: (d.gun, d.baslangic_saat))

        dersler = list()

        for de in ders_etkinligi:
            ders = dict()
            ders['ad'] = de.sube.ders.ad
            ders['gun'] = de.gun
            ders[
                'saat_araligi'] = de.baslangic_saat + ':' + de.baslangic_dakika + '-' + de.bitis_saat + ':' + de.bitis_dakika
            dersler.append(ders)
        item = {'read_only': True,
                'name': self.current.user.name,
                'gunler': ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"],
                'dersler': dersler}

        self.output['ders_programi'] = item

    def ders_programi_bulunamadi(self):
        msg = {"type": "warning",
               "title": 'Ders Programı Bulunamadı',
               "msg": "Ders Programı Henüz Oluşturulmadı."}

        self.current.output['msgbox'] = msg
