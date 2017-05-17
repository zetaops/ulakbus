# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Demirbas, DemirbasRezervasyon, Personel
from zengine.forms import JsonForm
from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import fields
from ulakbus.settings import DATE_DEFAULT_FORMAT
from datetime import datetime


__author__ = 'Anil Can Aydin'


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

    def ekle_duzenle(self):
        self.object_form.iptal = fields.Button(__(u"İptal"), cmd='iptal')
        self.add_edit_form()

    def goruntule(self):
        if 'basari_mesaji' in self.current.task_data:
            self.current.output['msgbox'] = {"type": _(u"info"),
                                             "title": _(u"İşlem Başarılı"),
                                             "msg": self.current.task_data['basari_mesaji']}
            del self.current.task_data['basari_mesaji']
        if 'form' in self.input and 'iptal' in self.input['form'] and self.input['form']['iptal'] \
                == 1:
            self.object = Demirbas.objects.get(self.current.task_data['obj_key'])
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
        model = 'DemirbasRezervasyon'

    def anahtar_al(self):
        self.current.task_data['obj_key'] = self.input['object_key']

    def rezervasyon_yap(self):

        obj_key = self.current.task_data['obj_key']
        rezervasyonlar = DemirbasRezervasyon.objects.filter(
            rezerve_edilen_demirbas_id=obj_key)

        onceki_rezervasyonlar = []

        if not rezervasyonlar:
            onceki_rezervasyonlar.append(_(u"Bu demirbaşa ait rezervasyon bulunmamaktadır."))
        else:
            for rez in rezervasyonlar:
                onceki_rezervasyonlar.append("(" + datetime.strftime(rez.rezervasyon_baslama_tarihi,
                                                                     DATE_DEFAULT_FORMAT) +
                                             " - " + datetime.strftime(rez.rezervasyon_bitis_tarihi,
                                                                       DATE_DEFAULT_FORMAT) + ")")

        if 'hata_mesaji' in self.current.task_data and self.current.task_data['hata_mesaji']:
            mesaj_type = "error"
            title = _(u"Hatalı İşlem")
            mesaj = "%s %s %s" % (self.current.task_data['hata_mesaji'],
                                  _(u"Önceki Rezervasyonlar: "),
                                  ", ".join(onceki_rezervasyonlar))
        else:
            mesaj_type = "info"
            title = _(u"Önceki Rezervasyonlar")
            mesaj = ", ".join(onceki_rezervasyonlar)

        self.current.output['msgbox'] = {"type": mesaj_type, "title": title, "msg": mesaj}
        self.form_out(RezervasyonForm(self.object, current=self.current))

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

        if baslama_tarihi > bitis_tarihi:
            self.current.task_data['hata_mesaji'] = "Belirtilen tarihler tutarsız görünüyor. " \
                                                    "Lütfen konrol edip tekrar deneyiniz."
        elif illegal_rezervasyon:
            self.current.task_data['hata_mesaji'] = "Belirtilen tarihler rezervasyon için uygun " \
                                                    "değil. "
        else:
            self.current.task_data['hata_mesaji'] = None
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
            rezerve_eden=Personel.objects.get(data['rezerve_eden_id'])
        ).blocking_save()

    def rezervasyon_kayit_basari(self):
        _data = self.current.task_data['form_data']

        title = _(u"Rezervasyon Kaydı Başarılı")

        help_text = _(u"%s - %s tarihleri arasındaki rezervasyon kaydınız başarıyla tamamlandı. "
                      u"Listeye dönmek için tıklayınız."
                  % (_data['rezervasyon_baslama_tarihi'], _data['rezervasyon_bitis_tarihi']))
        _form = JsonForm(title=title)
        _form.help_text = help_text
        _form.listeye_don = fields.Button(_(u"Listeye Dön"), cmd='listele')

        self.form_out(_form)


class RezervasyonForm(JsonForm):

    class Meta:
        exclude = ['rezerve_edilen_demirbas']
        title = __(u'Rezervasyon Bilgileri')

    kontrol_kayit = fields.Button(__(u"Kontrol Et ve Kaydet"), cmd="kaydet_ve_kontrol")
    iptal = fields.Button(__(u"İptal"), cmd="iptal")
















