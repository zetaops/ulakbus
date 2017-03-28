# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Demirbas, DemirbasRezervasyon
from zengine.forms import JsonForm
from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import fields
from ulakbus.settings import DATE_DEFAULT_FORMAT
from datetime import datetime


__author__ = 'Anil Can Aydin'


class RezervasyonForm(JsonForm):
    class Meta:
        title = __(u'Rezervasyon Bilgileri')

    rezerve_eden = fields.String(__(u"Rezerve Eden Personel"))
    rezervasyon_baslama_tarihi = fields.Date(_(u"Rezervasyon Başlama Tarihi"))
    rezervasyon_bitis_tarihi = fields.Date(_(u"Rezervasyon Başlama Tarihi"))

    kontrol_kayit = fields.Button(__(u"Kontrol Et ve Kaydet"), cmd="kaydet_ve_kontrol")


class DemirbasView(CrudView):

    def __init__(self, current):
        CrudView.__init__(self, current)
        if self.cmd != 'confirm_deletion' and self.cmd != 'delete' \
                and 'object_id' in self.current.task_data:
            del self.current.task_data['object_id']

    class Meta:
        allow_search = True
        model = "Demirbas"
        object_actions = []

    def goruntule(self):

        if 'basari_mesaji' in self.current.task_data:
            self.current.output['msgbox'] = {"type": _(u"info"),
                                             "title": _(u"İşlem Başarılı"),
                                             "msg": self.current.task_data['basari_mesaji']}
            del self.current.task_data['basari_mesaji']
            self.show()
            form = JsonForm()
            form.geri = fields.Button(__(u"Listeye Dön"), cmd='listele')
            form.rezervasyon = fields.Button(__(u"Rezervasyon Yap"), cmd='rezervasyon')
            self.form_out(form)
        else:
            self.show()
            form = JsonForm()
            form.geri = fields.Button(__(u"Listeye Dön"), cmd='listele')
            form.rezervasyon = fields.Button(__(u"Rezervasyon Yap"), cmd='rezervasyon')
            self.form_out(form)



    @obj_filter
    def demirbas_islem(self, obj, result):
        result['actions'].extend([
            {'name': _(u'Sil'), 'cmd': 'confirm_deletion', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Görüntüle'), 'cmd': 'goster', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'},
        ])


class RezervasyonView(CrudView):

    class Meta:
        model = 'RezerveBilgileri'

    def rezervasyon_yap(self):

        if 'object_key' in self.input:
            obj_key = self.input['object_key']
            self.current.task_data['obj_key'] = obj_key
        else:
            obj_key = self.current.task_data['obj_key']

        demirbas = Demirbas.objects.get(obj_key)
        onceki_rezervasyonlar = []
        if DemirbasRezervasyon.objects.filter(rezerve_edilen_demirbas=demirbas).count() == 0:
            onceki_rezervasyonlar.append(__(u"Bu demirbaşa ait rezervasyon bulunmamaktadır."))
        else:
            for rez in DemirbasRezervasyon.objects.filter(rezerve_edilen_demirbas=demirbas):
                onceki_rezervasyonlar.append("(" +\
                    str(rez.rezervasyon_baslama_tarihi) + " - " + \
                    str(rez.rezervasyon_bitis_tarihi) + ")")
        if 'hata_mesaji' in self.current.task_data:
            mesaj = __(u"Önceki Rezervasyonlar: ") + " " + ", ".join(onceki_rezervasyonlar)
            self.current.output['msgbox'] = {"type": _(u"error"),
                                             "title": _(u"Hatalı İşlem"),
                                             "msg": self.current.task_data['hata_mesaji']+ mesaj}
            del self.current.task_data['hata_mesaji']
        else:
            if len(onceki_rezervasyonlar) > 1:
                mesaj = ", ".join(onceki_rezervasyonlar)
            else:
                mesaj = onceki_rezervasyonlar[0]
            self.current.output['msgbox'] = {"type": _(u"info"),
                                         "title": _(u"Önceki Rezervasyonlar"),
                                         "msg": mesaj}
        form = RezervasyonForm(title=__(u"Rezervasyon bilgilerini giriniz"))
        self.form_out(form)

    def rezervasyon_kontrol(self):

        demirbas = Demirbas.objects.get(self.current.task_data['obj_key'])

        baslama_tarihi = datetime.strptime(self.input['form']['rezervasyon_baslama_tarihi'],
                                           DATE_DEFAULT_FORMAT)
        bitis_tarihi = datetime.strptime(self.input['form']['rezervasyon_bitis_tarihi'],
                                         DATE_DEFAULT_FORMAT)

        illegal_rezervasyon = DemirbasRezervasyon.objects.filter(
            rezervasyon_baslama_tarihi__lte=bitis_tarihi,
            rezervasyon_bitis_tarihi__gte=baslama_tarihi,
            rezerve_edilen_demirbas=demirbas
        )

        if illegal_rezervasyon:
            self.current.task_data['hata_mesaji'] = "Belirtilen tarihler rezervasyon için uygun " \
                                                    "değil. "
        else:
            self.current.task_data['basari_mesaji'] = "%s - %s tarihleri arasındaki " \
                                                      "rezervasyonununuz başarılı bir şekilde " \
                                                      "kaydedilmiştir." % (
                self.input['form']['rezervasyon_baslama_tarihi'],
                self.input['form']['rezervasyon_bitis_tarihi'])
            self.current.task_data['form_data'] = self.input['form']
            self.current.task_data['cmd'] = 'rezervasyon_kaydet'

    def rezervasyon_kaydet(self):
        data = self.current.task_data['form_data']

        DemirbasRezervasyon(
            rezervasyon_baslama_tarihi=datetime.strptime(data['rezervasyon_baslama_tarihi'],
                                                         DATE_DEFAULT_FORMAT),
            rezervasyon_bitis_tarihi=datetime.strptime(data['rezervasyon_bitis_tarihi'],
                                                       DATE_DEFAULT_FORMAT),
            rezerve_edilen_demirbas=Demirbas.objects.get(self.current.task_data['obj_key']),
            rezerve_eden=data['rezerve_eden']
        ).blocking_save()

        self.current.task_data['object_id'] = self.current.task_data['obj_key']















