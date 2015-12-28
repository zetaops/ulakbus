# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import random
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.base import SimpleView, BaseView
from zengine.views.crud import CrudView


class TCKNForm(JsonForm):
    class Meta:
        title = 'Yeni Personel'

    tcno = fields.String("TC No")
    goto_hata = fields.Button("Ekleme")
    ekle = fields.Button("Ekle")


class YeniPersonelEkle(BaseView):
    def __init__(self, current=None):
        current.output['forms'] = TCKNForm().serialize()
        current.output['client_cmd'] = ['form']


def get_personel_from_hitap(current):
    tcno = current.input['form']['tcno']
    current.task_data['hitap_tamam'] = current.input['form'].get('goto_hata') != 1
    current.task_data['tcno'] = tcno
    current.set_message(title='%s TC no için Hitap servisi başlatıldı' % tcno,
                        msg='', typ=1, url="/wftoken/%s" % current.token)


def get_by_tckn(current):
    current.task_data['aks_tamam'] = True


def get_from_mernis(current):
    # %60 ihtimalle yeni atama ekranina gidecek, %40  hata verecek...
    # current.task_data['mernis_tamam'] = random.choice((1, 2, 3, 4, 5)) in (1, 2, 3)
    current.task_data['mernis_tamam'] = True
    current.set_message(title='%s için Mernis\'e erişilemedi' % current.task_data['tcno'],
                        msg='', typ=1, url="/wftoken/%s" % current.token)


class AtamaYap(CrudView):

    class Meta:
        model = 'Kadro'

    class ObjectForm(JsonForm):
        save_list = fields.Button("Kaydet", cmd="save::list", flow="goto_service")
        save_edit = fields.Button("Kaydet ve Devam Et", cmd="save::devam_et", flow="goto_service")


class HataIncele(JsonForm):
    class Meta:
        title = 'İşlem Başarısız Oldu'
        help_text = "Dasd askdhjkasbdajs gasjkhdgasjkhg ajhdgas askjdhaskjhasj dhas dhaskjdhas" \
                    "aklsjsd haskljdhasklj dhaskldh akdhaksj dajskh dgasjkhdg ajshgdasj dgas" \
                    "aslkd haskldhaskdhaskldhaskl dhaklsd"

    restart = fields.Button("Tekrar Dene", flow="hata_to_tcno")
    cancel = fields.Button("İşlemi İptal Et", flow="iptal_hata")


# class Iptal(JsonForm):
#     class Meta:
#         title = 'İptal'
#         help_text = "Başarıyla iptal edildi"

def delete_draft(current):
    current.output['msgbox'] = {'type': 'info', "title": 'İptal', "msg": 'Başarıyla iptal edildi'}


class review_service_errors(SimpleView):
    def show_view(self):
        self.output['forms'] = HataIncele(current=self.current).serialize()


def yeni_ekle_kontrol(current):
    current.output['object'] = {'bumudur': 'budur'}
    current.output['client_cmd'] = ['show']
