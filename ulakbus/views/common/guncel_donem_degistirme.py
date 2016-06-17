# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models import Donem
from zengine.forms import JsonForm
from zengine.views.crud import CrudView
from zengine.forms import fields


class GuncelDonemDegistirme(CrudView):
    """
    Güncel Dönem Değiştirme iş akışı 3 adımdan oluşur.

    Güncel Dönem Seç:
    SelectBox içinde gelen dönemler bir güncel dönem olarak seçilir.

    Güncel Dönem Kaydet:
    Seçilen güncel dönem kaydedilir.

    Bilgi Ver:
    İşlemin başarılı olduğuna dair bilgilendirme mesajı verilir.

    """

    class Meta:
        model = 'Donem'

    def guncel_donem_sec(self):
        """
        SelectBox içinde gelen dönemler bir güncel dönem olarak seçilir.
        SelectBox içindeki dönemler, güncel dönemden önceki 2 dönem, güncel
        dönemden sonraki iki dönem  ve güncel dönem sıralanır.

        """
        # TODO : Güncel dönem seçili olarak verilecek.
        _form = JsonForm(title='Güncel Dönem Seçiniz', current=self.current)
        guncel_donem = Donem.guncel_donem()
        donemler = []
        try:
            ilk_onceki_donem = guncel_donem.onceki_donem()
            donemler.append((ilk_onceki_donem.key, ilk_onceki_donem.__unicode__()))
            ikinci_onceki_donem = ilk_onceki_donem.onceki_donem()
            donemler.append((ilk_onceki_donem.key, ikinci_onceki_donem.__unicode__()))
        except ObjectDoesNotExist:
            pass
        try:
            ilk_sonraki_donem = guncel_donem.sonraki_donem()
            donemler.append((ilk_sonraki_donem.key, ilk_sonraki_donem.__unicode__()))
            ikinci_sonraki_donem = ilk_sonraki_donem.sonraki_donem()
            donemler.append((ikinci_sonraki_donem.key, ikinci_sonraki_donem.__unicode__()))
        except ObjectDoesNotExist:
            pass
        donemler.append((guncel_donem.key, guncel_donem.__unicode__()))
        _form.guncel_donem = fields.Integer(choices=donemler)
        _form.kaydet = fields.Button('Kaydet')
        self.form_out(_form)

    def guncel_donem_kaydet(self):
        """
        Seçilen güncel dönem kaydedilir.

        """

        self.current.task_data['donem_key'] = self.current.input['form']['guncel_donem']
        donem = Donem.objects.get(self.current.task_data['donem_key'])
        guncel_donem = Donem.guncel_donem()
        guncel_donem.guncel = False
        guncel_donem.save()
        donem.guncel = True
        donem.save()

    def bilgi_ver(self):
        """
        İşlemin başarılı olduğuna dair bilgilendirme mesajı verilir.

        """

        donem = Donem.objects.get(self.current.task_data['donem_key'])
        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Güncel Dönem Değiştirme',
            "msg": '{0} dönemi güncel dönem olarak atanmıştır'.format(donem)}
