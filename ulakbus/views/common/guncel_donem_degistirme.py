# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.lib.view_helpers import convert_model_object_titlemap_item
from ulakbus.models import Donem, OgretimYili
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy


def donemler():
    """
    Dönem seçim formunu dinamik olarak dolduran method.
    Güncel dönemden önceki ve sonraki 2 şer adet dönemle birlikte bir seçim
    listesi oluşturur.
    """
    ds = []  # return list
    td = []  # tum donemler, onceki guncel ve sonrakilerden liste
    gd = Donem.guncel_donem()
    td.extend(gd.onceki_donemler(2))
    td.append(gd)
    td.extend(gd.sonraki_donemler(2))
    for donem in td:
        ds.append(convert_model_object_titlemap_item(donem))
    return ds


class DonemSecForm(JsonForm):
    guncel_donem = fields.Integer(gettext_lazy(u"Dönem Seçiniz"), choices=donemler)
    kaydet = fields.Button(gettext_lazy(u'Kaydet'))


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

        _form = DonemSecForm(title=_(u'Güncel Dönem Seçiniz'), current=self.current)

        # formun güncel dönemi seçili hale getirilir.
        _form.guncel_donem = Donem.guncel_donem().key

        self.form_out(_form)

    def guncel_donem_kaydet(self):
        """
        Seçilen güncel dönem kaydedilir.

        """

        self.current.task_data['donem_key'] = self.current.input['form']['guncel_donem']
        donem = Donem.objects.get(self.current.task_data['donem_key'])
        try:
            ogretim_yili = OgretimYili.objects.get(yil=int(donem.baslangic_tarihi.year))
        except ObjectDoesNotExist:
            ogretim_yili = OgretimYili(yil=int(donem.baslangic_tarihi.year))
            ogretim_yili.save()

        donem.ogretim_yili = ogretim_yili
        donem.guncel = True
        meta = {'user_id': self.current.user_id,
                'role_id': self.current.role_id,
                'wf_name': self.current.workflow_name,
                'task_name': self.current.task_name}
        index_fields = [('user_id', 'bin'), ('wf_name', 'bin')]
        donem.save(meta=meta, index_fields=index_fields)

    def bilgi_ver(self):
        """
        İşlemin başarılı olduğuna dair bilgilendirme mesajı verilir.

        """

        donem = Donem.objects.get(self.current.task_data['donem_key'])
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Güncel Dönem Değiştirme'),
            "msg": _(u'{donem} dönemi güncel dönem olarak atanmıştır').format(donem=donem)}
