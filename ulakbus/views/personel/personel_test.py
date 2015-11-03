# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.model import field
from zengine.lib.forms import JsonForm
from zengine.views.base import SimpleView


class TCKNForm(JsonForm):
    class Meta:
        title = 'Yeni Personel'

    tcno = field.String("TC No")
    cmd = field.String("Ekle", type="button")


class YeniPersonelEkle(SimpleView):
    def show_view(self):
        self.current.output['forms'] = TCKNForm().serialize()


def get_personel_from_hitap(current):
    tcno = current.input['form']['tcno']
    current.task_data['hitap_tamam'] = True
    current.task_data['tcno'] = tcno
    current.set_message(title='%s TC no için Hitap servisi başlatıldı' % tcno,
                        msg='', typ=1, url="/wftoken/%s" % current.token)


def get_from_mernis(current):
    current.task_data['mernis_tamam'] = False
    current.set_message(title='%s için Mernis\'e erişilemedi' % current.task_data['tcno'],
                        msg='', typ=1, url="/wftoken/%s" % current.token)


class HataIncele(JsonForm):
    class Meta:
        title = 'İşlem Başarısız Oldu'
        help_text = "Dasd askdhjkasbdajs gasjkhdgasjkhg ajhdgas askjdhaskjhasj dhas dhaskjdhas" \
                    "aklsjsd haskljdhasklj dhaskldh akdhaksj dajskh dgasjkhdg ajshgdasj dgas" \
                    "aslkd haskldhaskdhaskldhaskl dhaklsd"

    restart = field.String("Tekrar Dene", type="button")
    cancel = field.String("İşlemi İptal Et", type="button")


def review_service_errors(current):
    if 'restart' in current.input['form']:
        current.task_data['hata_to_tcno'] = True
    else:
        current.output['forms'] = HataIncele().serialize()
