# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from collections import OrderedDict

from ulakbus.models import SinavEtkinligi, Donem, Okutman, Room, Sube
from ulakbus.services.zato_wrapper import SinavProgramiOlustur
from ulakbus.views.ders_programi.ders_programi import AramaForm
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, get_day_names, format_datetime


class SinavProgramiYap(CrudView):
    def sinav_etkinligi_sayisi(self):
        sinav_etkinligi_count = SinavEtkinligi.objects.filter(bolum=self.current.role.unit,
                                                              donem=Donem.guncel_donem()).count()

        solved_count = SinavEtkinligi.objects.filter(bolum=self.current.role.unit,
                                                     donem=Donem.guncel_donem(),
                                                     solved=True).count()

        published_count = SinavEtkinligi.objects.filter(bolum=self.current.role.unit, published=True,
                                                        donem=Donem.guncel_donem()).count()

        return sinav_etkinligi_count, solved_count, published_count

    def kontrol(self):
        sinav_etkinligi_count, solved_count, published_count = self.sinav_etkinligi_sayisi()

        if published_count > 0:
            self.current.task_data['cmd'] = 'kayit_var'
            msg = {"type": 'info',
                   "title": _(u'Yayınlanmış Sınav Programı Var!'),
                   "msg": _(u'Yayınlanan sınav programınız bulunmaktadır. Tekrardan sınav programı oluşturamazsınız.')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg

        elif solved_count == sinav_etkinligi_count and solved_count > 0:
            self.current.task_data['cmd'] = 'hatasiz_sonuc'
            msg = {"type": 'info',
                   "title": _(u'Yayınlanmamış Sınav Programı Var!'),
                   "msg": _(u'Yayınlanmayan sınav programını inceleyip yayınlayabilirsiniz.')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg

        elif solved_count != sinav_etkinligi_count and solved_count > 0:
            msg = {"type": 'warning',
                   "title": _(u'Hatalı Sonuçlar Var!'),
                   "msg": _(u'Oluşturulan sınav programınızda hatalı sonuçlar bulunmaktadır.'
                            u'Lütfen tekrardan sınav programı oluşturunuz.')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg

    def sinav_programi_hesaplama_baslat(self):
        if 'LANE_CHANGE_MSG' in self.current.task_data:
            if self.current.task_data['LANE_CHANGE_MSG']['title'] == _(u'Hatalı Sonuçlar Var!'):
                self.current.output['msgbox'] = self.current.task_data['LANE_CHANGE_MSG']
        _form = JsonForm(title=_(u"Sınav Programı Oluştur"))
        _form.button = fields.Button(_(u'Başlat'))
        self.form_out(_form)

    def sinav_programi_hesapla(self):
        # bolum = self.current.role.unit.yoksis_no
        sp = SinavProgramiOlustur(service_payload={"bolum": self.current.role.unit.yoksis_no,
                                                   "kullanici": self.current.user.key,
                                                   "sinav_turleri": [1],
                                                   "url": self.current.get_wf_link()})
        response = sp.zato_request()

        if response:
            msg = {"type": 'info',
                   "title": _(u'Sınav Programı Oluşturuluyor'),
                   "msg": _(u'Sınav programı için yaptığınız taleb başarıyla alınmıştır.')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg
        else:
            msg = {"type": 'warning',
                   "title": _(u'Sistemde Sorun Oluştu'),
                   "msg": _(u'Lütfen tekrardan sınav programı oluşturmayı çalıştırnız!')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg

    def servis_bilgi_mesaji(self):

        if self.current.task_data['LANE_CHANGE_MSG']['title'] == _(u'Sınav Programı Oluşturuluyor'):
            self.current.output['msgbox'] = self.current.task_data['LANE_CHANGE_MSG']
        else:
            self.current.output['msgbox'] = self.current.task_data['LANE_CHANGE_MSG']

    def sinav_programi_sonucu(self):
        sinav_etkinligi_count, solved_count, published_count = self.sinav_etkinligi_sayisi()
        if solved_count != sinav_etkinligi_count:
            msg = {"type": 'warning',
                   "title": _(u'Hatalı Sonuçlar Var!'),
                   "msg": _(u'Oluşturulan sınav programınızda hatalı sonuçlar bulunmaktadır.'
                            u'Lütfen tekrardan sınav programı oluşturunuz.')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg

            self.current.task_data['cmd'] = 'hata'
        else:
            msg = {"type": 'info',
                   "title": _(u'Sınav Programı Başarıyla Oluşturuldu!'),
                   "msg": _(u'Yayınlanmayan sınav programını inceleyip yayınlayabilirsiniz.')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg

    def hatasiz(self):
        _form = JsonForm(title=_(U"Derslik veya Öğretim Elemanı İncele"))
        _form.incele = fields.Button(_(u"İncele"), cmd='incele')
        _form.yayinla = fields.Button(_(u"Yayınla"), cmd='bitir')
        self.form_out(_form)
        self.current.output['msgbox'] = self.current.task_data['LANE_CHANGE_MSG']

    def derslik_ogretim_elemani_ara(self):

        self.form_out(AramaForm(self.object, current=self.current))

    def arama(self):
        text = str(self.input['form']['arama_text'])
        try:
            if self.input['form']['arama_sec'] == 1:
                room_search = [r for r in Room.objects.filter(code=text) if
                               self.current.role.unit in r.RoomDepartments]
                if room_search:
                    self.current.task_data['data_key'] = room_search[0].key
                    self.current.task_data['cmd'] = 'tekli'
                else:
                    raise
            else:
                ad = text.split()[0]
                soyad = text.split()[1]
                okutman_search = Okutman.objects.filter(birim_no=self.current.role.unit.yoksis_no, ad=ad, soyad=soyad)
                if len(okutman_search) > 1:
                    self.current.search = okutman_search
                    self.current.task_data['cmd'] = 'coklu'
                elif len(okutman_search) == 1:
                    self.current.task_data['data_key'] = okutman_search[0].key
                    self.current.task_data['cmd'] = 'tekli'
                else:
                    raise
        except:
            msg = {
                'type': 'warning', "title": _(u'Kayıt Bulunamadı'),
                "msg": _(u'İlgili kayıt bulunamadı.')
            }
            self.current.task_data["LANE_CHANGE_MSG"] = msg

    def coklu_sonuc(self):

        self.output['objects'] = [[_(U'Ad'), _(u'Soyad')]]
        for data in self.current.search:
            data_list = OrderedDict({})
            data_list[_(u'Ad')] = data.ad
            data_list[_(u'Soyad')] = data.soyad
            item = {
                'type': "table-multiRow",
                'fields': data_list,
                'actions': [
                    {'name': _(u'Göster'), 'cmd': 'tek_sonuc', 'show_as': 'button',
                     'object_key': 'ogretim_elemani'}
                ],
                'key': data.key
            }
            self.output['objects'].append(item)

    def detay_goster(self):

        if "LANE_CHANGE_MSG" in self.current.task_data and \
                        'title' in self.current.task_data["LANE_CHANGE_MSG"] and \
                        self.current.task_data["LANE_CHANGE_MSG"]['title'] == _(u"Kayıt Bulunamadı"):

            self.current.output['msgbox'] = self.current.task_data["LANE_CHANGE_MSG"]
            self.current.task_data["LANE_CHANGE_MSG"] = ''
        else:
            obj_key = self.current.task_data['data_key']
            if self.input['form']['arama_sec'] == 1:
                ders_etkinligi = SinavEtkinligi.objects.raw("sinav_yerleri.room_id:" + obj_key)
                obj = Room.objects.get(obj_key)

            else:
                ders_etkinligi = map(lambda s: SinavEtkinligi.objects.get(sube=s), Sube.objects.filter(
                                                                okutman_id=obj_key, donem=Donem.guncel_donem()))
                obj = Okutman.objects.get(obj_key)

            days = list(get_day_names())

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
                                                                  ders_etkinligi)]))

            item = {
                "title": _(u"%s - Detaylı Zaman Tablosu") % obj.__unicode__(),
                'type': "table-multiRow",
                'fields': data_list,
                "actions": False,
            }
            self.output['objects'].append(item)
        _json = JsonForm(title=_(u"Detaylı Zaman Tablosu"))
        _json.tamamla = fields.Button(_(u"Bitir"))
        self.form_out(_json)

    def hatali(self):
        msg = {"type": 'info',
               "title": _(u'Yayınlanmamış Sınav Programı Var!'),
               "msg": _(u'Yayınlanmayan sınav programını inceleyip yayınlayabilirsiniz.')}
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def yayinla(self):
        des = SinavEtkinligi.objects.filter(bolum=self.current.role.unit, donem=Donem.guncel_donem())
        try:
            for de in des:
                de.published = True
                de.save()
            msg = {"type": 'info',
                   "title": _(u'Sınav Programı Yayınlandı!'),
                   "msg": _(u'Oluşturulan Sınav Programı Başarıyla Yayınlandı')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg
        except:
            msg = {"type": 'warning',
                   "title": _(u'!!HATA!!'),
                   "msg": _(u'Sınav Programı yayınlanırken hata oluştu lütfen tekrar yayınlayın.')}
            self.current.task_data['LANE_CHANGE_MSG'] = msg

    def bilgilendirme(self):
        self.current.output['msgbox'] = self.current.task_data['LANE_CHANGE_MSG']
