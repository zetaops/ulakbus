# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models import Donem
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView


class GuncelDonemDegistirme(CrudView):
    class Meta:
        model = 'Donem'

    def guncel_donem_sec(self):
        _form = JsonForm(current=self.current, title='Güncel Dönem Seçiniz.')
        # _choices = prepare_choices_for_model
        en_son_kaydedilen_bahar_donemi = Donem.en_son_kaydedilen_bahar_donemi()
        en_son_kaydedilen_guz_donemi = Donem.en_son_kaydedilen_guz_donemi()
        try:
            guncel_donem = Donem.guncel_donem()
            _choices = (
                (en_son_kaydedilen_bahar_donemi.key, en_son_kaydedilen_bahar_donemi.__unicode__()),
                (en_son_kaydedilen_guz_donemi.key, en_son_kaydedilen_guz_donemi.__unicode__()))
            if (guncel_donem.key, guncel_donem.__unicode__()) in _choices:
                _form.guncel_donem = fields.Integer(choices=_choices)

            else:
                _choices = (
                    (en_son_kaydedilen_bahar_donemi.key, en_son_kaydedilen_bahar_donemi.__unicode__()),
                    (en_son_kaydedilen_guz_donemi.key, en_son_kaydedilen_guz_donemi.__unicode__()),
                    (guncel_donem.key, guncel_donem.__unicode__()))
                _form.guncel_donem = fields.Integer(choices=_choices)
        except ObjectDoesNotExist:
            _choices = (
                (en_son_kaydedilen_bahar_donemi.key, en_son_kaydedilen_bahar_donemi.__unicode__()),
                (en_son_kaydedilen_guz_donemi.key, en_son_kaydedilen_guz_donemi.__unicode__()))
            _form.guncel_donem = fields.Integer(choices=_choices)
        _form.kayde = fields.Button('Kaydet')
        self.form_out(_form)

    def guncel_donem_kaydet(self):
        self.current.task_data['donem_key'] = self.current.input['form']['guncel_donem']
        donem = Donem.objects.get(self.current.task_data['donem_key'])
        try:
            guncel_donem = Donem.guncel_donem()
            guncel_donem.guncel = False
            guncel_donem.save()
        except ObjectDoesNotExist:
            donem.guncel = True
            donem.save()

    def bilgi_ver(self):
        donem = Donem.objects.get(self.current.task_data['donem_key'])
        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Güncel Dönem Değiştirme',
            "msg": '{0} dönemi güncel dönem olarak atanmıştır'.format(donem)}
