# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.lib.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from ulakbus.models import OgrenciProgram, Ogrenci
from zengine.notifications import Notify


class KayitSil(CrudView):
    class Meta:
        model = 'OgrenciProgram'

    def ayrilma_nedeni_sec(self):
        self.current.task_data['ogrenci_id'] = self.current.input['id']
        _form = JsonForm(current=self.current, title='Öğrencinin Ayrılma Nedenini Seçiniz')
        _form.ayrilma_nedeni = fields.Integer(choices=self.object.get_choices_for('ayrilma_nedeni'))
        _form.aciklama = fields.Text("Açıklama Yazınız", required=True)
        _form.sec = fields.Button("Seç")
        self.form_out(_form)

    def ogrenci_program_sec(self):
        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        programlar = OgrenciProgram.objects.filter(ogrenci=ogrenci)
        for program in programlar:
            program.ayrilma_nedeni = self.current.input['form']['ayrilma_nedeni']
            # todo: elle vermek yerine daha iyi bir yol dusunelim
            program.ogrencilik_statusu = 21
            program.save()

    def bilgi_ver(self):
        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci)
        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Kayıt Silme',
            "msg": 'Öğrencinin kaydı %s nedeniyle silinmiştir.' % self.current.input['form']['aciklama']
        }
        title = 'Kayıt Silme'
        msg = '%s adlı öğrencinin kaydı %s nedeniyle silinmiştir.' % (ogrenci, self.current.input['form']['aciklama'])

        def notify(danisman):
            Notify(danisman.user.key).set_message(msg=msg, title=title, typ=Notify.TaskInfo)

        notify(ogrenci_program.danisman)
        notify(ogrenci)