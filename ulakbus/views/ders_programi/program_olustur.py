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
from ulakbus.services.zato_wrapper import SinavProgramiOlustur
from ulakbus.models import Room, Okutman, DersEtkinligi, Donem, DerslikZamanPlani, SinavEtkinligi, Sube
from zengine.lib.translation import gettext_lazy as __, gettext as _, format_time, format_datetime
from datetime import time

ARAMA_TURU = [
    (1, 'Derslik'),
    (2, 'Öğretim Elemanı')
]

MESSAGE = {"kayit_var": {"type": 'info',
                         "title": __(u'Yayınlanmış Program Var!'),
                         "msg": __(u'Yayınlanan programınız bulunmaktadır. Tekrardan program oluşturamazsınız.')},
           "hatasiz_sonuc": {"type": 'info',
                             "title": __(u'Yayınlanmamış Program Var!'),
                             "msg": __(u'Yayınlanmayan programınızı inceleyip yayınlayabilirsiniz.')},
           "hatali_sonuc": {"type": 'warning',
                            "title": __(u'Hatalı Sonuçlar Var!'),
                            "msg": __(u'Oluşturulan programda hatalı sonuçlar bulunmaktadır. Lütfen tekrardan'
                                      u'verileri düzenleyip çalıştırınız.')},
           "basarili": {"type": 'info',
                        "title": __(u'Program Başarıyla Oluşturuldu!'),
                        "msg": __(u'Yayınlanmayan programınızı inceleyip yayınlayabilirsiniz.')},
           "yayinlandi": {"type": 'info',
                          "title": __(u'Program Yayınlandı!'),
                          "msg": __(u'Oluşturulan Program Başarıyla Yayınlandı')}}


class AramaForm(JsonForm):
    class Meta:
        title = __(u'Öğretim Elemanı veya Derslik Ara')

    arama_sec = fields.String(__(u'Arama Seçeneği'), choices=ARAMA_TURU, default=1)
    arama_text = fields.String(__(u" "), required=False)
    arama_button = fields.Button(__(u'Ara'))
    vazgec_button = fields.Button(__(u'Geri'), cmd='vazgec')


class ProgramOlustur(CrudView):

    def calculate(self, obj):
        """

        Args:
            obj: Ders veya Sınav etkinliği modeli

        Returns: model_object.count() >> bölüm ve güncel doneme ait model sayısı,
                 solved_count >> çözülen model sayısı,
                 published_count >> yayınlanan model sayısı

        """
        model_object = obj.objects.filter(bolum=self.current.role.unit, donem=Donem.guncel_donem(self.current))

        solved_count = model_object.filter(solved=True).count()

        published_count = model_object.filter(published=True).count()

        return model_object.count(), solved_count, published_count

    def kontrol(self, obj_count, solved, published):
        """
            Yayınlanan veya çözülmüş ama yayınlanmamış program var mı kontrolü yapılır.
        """
        self.current.task_data['published'] = published
        self.current.task_data['solved'] = solved
        self.current.task_data['obj_count'] = obj_count

    def sinav_kontrol(self):
        se_count, solved_count, published_count = self.calculate(SinavEtkinligi)
        self.kontrol(se_count, solved_count, published_count)

    def ders_kontrol(self):
        de_count, solved_count, published_count = self.calculate(DersEtkinligi)
        self.kontrol(de_count, solved_count, published_count)

    def program_hesaplama_baslat(self):
        _form = JsonForm(title=_(u"Program Oluştur"))
        _form.button = fields.Button(_(u'Başlat'))
        self.form_out(_form)

    def program_hesapla(self, obj):
        """

        Args:
            obj: ZatoService objesi

        Zato service çağırılıp hesaplama başlatılır. Dönen response, hesaplamanın başladığını yada
        başlamadığını bildirir.

        """
        response = obj.zato_request()

        if response:
            msg = {"type": 'info',
                   "title": _(u'Program Oluşturuluyor'),
                   "msg": _(u'Program için yaptığınız taleb başarıyla alınmıştır.')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg
        else:
            msg = {"type": 'warning',
                   "title": _(u'Sistemde Sorun Oluştu'),
                   "msg": _(u'Lütfen tekrardan programı oluşturmayı çalıştırnız!')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg

    def sinav_programi_hesapla(self):
        sp = SinavProgramiOlustur(service_payload={"bolum": self.current.role.unit.yoksis_no,
                                                   "kullanici": self.current.user.key,
                                                   "sinav_turleri": [1],
                                                   "url": self.current.get_wf_link()})
        self.program_hesapla(sp)

    def ders_programi_hesapla(self):
        dp = DersProgramiOlustur(service_payload={"bolum": self.current.role.unit.yoksis_no,
                                                  "kullanici": self.current.user.key,
                                                  "url": self.current.get_wf_link()})

        self.program_hesapla(dp)

    def servis_bilgi_mesaji(self):
        """
            Kullanıcıyı programının başladığı yada başlamadığına dair bilgilendirme mesajı gösterir
        """
        self.current.output['msgbox'] = self.current.task_data['LANE_CHANGE_MSG']

    def sinav_programi_sonucu(self):
        se_count, solved_count, published_count = self.calculate(SinavEtkinligi)
        self.current.task_data['solved_count'] = solved_count
        self.current.task_data['obj_count'] = se_count

    def ders_programi_sonucu(self):
        de_count, solved_count, published_count = self.calculate(DersEtkinligi)
        self.current.task_data['solved_count'] = solved_count
        self.current.task_data['obj_count'] = de_count

    def yayinlanmamis_kayit(self):
        _form = JsonForm(title=_(u"İşleme devam etmek için tıklayınız!"))
        _form.devam = fields.Button(_(u'Devam'))
        self.form_out(_form)
        self.current.output['msgbox'] = MESSAGE['hatasiz_sonuc']

    def hatasiz(self):
        """
            Hatasız oluşan programı inceleyebilir yada yayınlanır.
        """
        _form = JsonForm(title=_(u"Programı İncele Veya Yayınla"))
        _form.incele = fields.Button(_(u"İncele"), cmd='incele')
        _form.yayinla = fields.Button(_(u"Yayınla"), cmd='bitir')
        self.form_out(_form)

    def hatali(self):
        self.current.task_data['LANE_CHANGE_MSG'] = MESSAGE['hatali_sonuc']

    def derslik_ogretim_elemani_ara(self):
        """
            İncelediğiniz programda Öğretim Elemanlarına yada Dersliklere bakılır.
        """
        self.form_out(AramaForm(self.object, current=self.current))

    def arama_secim(self):
        self.current.task_data['arama'] = self.input['form']['arama_sec']

    def derslik_arama(self):
        text = str(self.input['form']['arama_text'])
        rooms = [r for r in Room.objects.search_on('code',
                                                   contains=text,
                                                   unit=self.current.role.unit)
                 if self.input['wf'] == 'ders_programi_hazirla'
                 or self.input['wf'] == 'sinav_programi_hazirla']

        if len(rooms) > 1:
            self.current.task_data['arama_text'] = text
            self.current.task_data['sonuc'] = 2
        elif len(rooms) == 1:
            self.current.task_data['data_key'] = rooms[0].key
            self.current.task_data['sonuc'] = 1
        else:
            self.current.task_data['sonuc'] = 0

    def ogretim_elemani_arama(self):
        text = str(self.input['form']['arama_text'])
        okutmanlar = [ok for ok in Okutman.objects.search_on('ad', 'soyad',
                                                             startswith=text.split()[0],
                                                             endswith=text.split()[-1],
                                                             unit=self.current.role.unit)
                      if self.input['wf'] == 'ders_programi_hazirla'
                      or self.input['wf'] == 'sinav_programi_hazirla']

        if len(okutmanlar) > 1:
            self.current.task_data['arama_text'] = text
            self.current.task_data['sonuc'] = 2
        elif len(okutmanlar) == 1:
            self.current.task_data['data_key'] = okutmanlar[0].key
            self.current.task_data['sonuc'] = 1
        else:
            self.current.task_data['sonuc'] = 0

    def coklu_sonuc(self):
        text = str(self.current.task_data['arama_text'])
        if self.current.task_data['arama'] == 2:
            self.output['objects'] = [[_(u'Ad'), _(u'Soyad')]]
            derslik = False
            datas = [ok for ok in Okutman.objects.search_on('ad', 'soyad',
                                                            startswith=text.split()[0],
                                                            endswith=text.split()[-1],
                                                            unit=self.current.role.unit) if ok.ders_etkinligi_set]
        else:
            derslik = True
            self.output['objects'] = [[_(u'Code'), _(u'Name')]]
            datas = [r for r in Room.objects.search_on('code', contains=text,
                                                       unit=self.current.role.unit) if r.ders_etkinligi_set]
        for data in datas:
            data_list = OrderedDict({})
            if not derslik:
                data_list[_(u'Ad')] = data.ad
                data_list[_(u'Soyad')] = data.soyad
            else:
                data_list[_(u'Code')] = data.code
                data_list[_(u'Name')] = data.name
            item = {
                'type': "table-multiRow",
                'fields': data_list,
                'actions': [
                    {'name': _(u'Goster'), 'cmd': 'tek_sonuc', 'show_as': 'button',
                     'object_key': 'data_key'}
                ],
                'key': data.key
            }
            self.output['objects'].append(item)

    def ders_detay_goster(self):
        if 'data_key' in self.current.input:
            obj_key = self.current.input['data_key']
        else:
            obj_key = self.current.task_data['data_key']
        if self.current.task_data['arama'] == 1:
            data_etkinlik = DersEtkinligi.objects.filter(room_id=obj_key)
            obj = Room.objects.get(obj_key)

        else:
            data_etkinlik = DersEtkinligi.objects.filter(okutman_id=obj_key)
            obj = Okutman.objects.get(obj_key)

        days = [_(u"Pazartesi"), _(u"Salı"), _(u"Çarşamba"), _(u"Perşembe"), _(u"Cuma"), _(u"Cumartesi"), _(u"Pazar")]
        self.output['objects'] = [days]

        def etkinlik(de):
            """
            Ders etkinligi formatlar ve dondurur.

            :param de: ders etkinligi
            :return: ders adi ve zamani
            """
            aralik = "{baslangic} - {bitis}".format(
                                        baslangic=format_time(time(int(de.baslangic_saat), int(de.baslangic_dakika))),
                                        bitis=format_time(time(int(de.bitis_saat), int(de.bitis_dakika))))

            return "\n\n**%s**\n%s\n\n" % (aralik, de.ders.ad)

        data_list = []
        for day in days:
            data_list.append(
                ''.join(["%s" % etkinlik(de) for de in data_etkinlik.filter(gun=days.index(day) + 1)]))

        self.detay_goster(data_list, obj)

    def sinav_detay_goster(self):
        obj_key = self.current.task_data['data_key']
        if self.input['form']['arama_sec'] == 1:
            sinav_etkinligi = SinavEtkinligi.objects.raw("sinav_yerleri.room_id:" + obj_key)
            obj = Room.objects.get(obj_key)

        else:
            sinav_etkinligi = map(lambda s: SinavEtkinligi.objects.get(sube=s), Sube.objects.filter(
                                                            okutman_id=obj_key, donem=Donem.guncel_donem(self.current)))
            obj = Okutman.objects.get(obj_key)

        days = [_(u"Pazartesi"), _(u"Salı"), _(u"Çarşamba"), _(u"Perşembe"), _(u"Cuma"), _(u"Cumartesi"), _(u"Pazar")]

        self.output['objects'] = [days]

        def etkinlik(de):
            """
            Ders etkinligi formatlar ve dondurur.

            :param de: ders etkinligi
            :return: ders adi ve zamani
            """
            aralik = format_datetime(de.tarih)
            return "\n\n**%s**\n%s\n\n" % (aralik, de.ders.ad)

        data_list = []
        for i, day in enumerate(days):
            data_list.append(
                ''.join(["%s" % etkinlik(de) for de in filter(lambda d: d.tarih.isoweekday() == i + 1,
                                                              sinav_etkinligi)]))
        self.detay_goster(data_list, obj)

    def detay_goster(self, data_list, obj):
        item = {
            "title": "%s - Detaylı Zaman Tablosu" % str(obj.__unicode__()),
            'type': "table-multiRow",
            'fields': data_list,
            "actions": False,
        }
        self.output['objects'].append(item)
        _json = JsonForm(title=obj.__unicode__() +_(u" Detaylı Zaman Tablosu"))
        _json.tamamla = fields.Button(_(u"Bitir"))
        if not self.current.task_data['sonuc'] == 1:
            _json.geri = fields.Button(_(u"Geri"), cmd='geri_coklu')
        self.form_out(_json)

    def sonuc_bulunamadi(self):
        msg = {
            'type': 'warning', "title": _(u'Kayıt Bulunamadı'),
            "msg": _(u'İlgili kayıt bulunamadı.')
        }
        self.current.output['msgbox'] = msg
        _form = JsonForm(title=_(u' '))
        _form.devam = fields.Button(_(u'Bitir'))
        self.form_out(_form)

    def kayit_var(self):
        self.current.output['msgbox'] = MESSAGE['kayit_var']

    def sinav_yayinla(self):
        se = SinavEtkinligi.objects.filter(bolum=self.current.role.unit, donem=Donem.guncel_donem(self.current))
        for s in se:
            s.published = True
            s.save()

    def ders_yayinla(self):
        de = DersEtkinligi.objects.filter(bolum=self.current.role.unit, donem=Donem.guncel_donem(self.current))
        for d in de:
            d.published = True
            d.save()

    def bilgilendirme(self):
        self.current.output['msgbox'] = MESSAGE['yayinlandi']
