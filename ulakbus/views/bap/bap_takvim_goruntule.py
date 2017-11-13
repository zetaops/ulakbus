# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models.bap.bap import BAPTakvim
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.utils import gettext_lazy as __
from ulakbus.settings import DATE_DEFAULT_FORMAT


class ListeleForm(JsonForm):
    """
    Tarih ve açıklamaların listelendiği form

    """

    class Meta:
        title = __(u"Akademik Takvim")

    ana_sayfa = fields.Button(__(u"Ana Menüye Dön"), cmd='ana_sayfa')


class TakvimListele(CrudView):
    class Meta:
        model = 'BAPTakvim'

    def takvim_listele(self):
        self.current.output["meta"]["allow_actions"] = False
        self.output['objects'] = [[__(u'Açıklama'), __(u'Tarih')]]
        for takvim in BAPTakvim.objects.filter():
            for tarih in sorted(takvim.OnemliTarihler, key=lambda x: x.baslangic_tarihi,
                                reverse=True):
                baslangic_tarihi = tarih.baslangic_tarihi.strftime(
                    DATE_DEFAULT_FORMAT) if tarih.baslangic_tarihi else ''
                bitis_tarihi = tarih.bitis_tarihi.strftime(
                    DATE_DEFAULT_FORMAT) if tarih.bitis_tarihi else ''
                aciklama = tarih.get_aciklama_display()

                list_item = {
                    "fields": [aciklama, (baslangic_tarihi + "-" + bitis_tarihi)],
                    "actions": '',
                }
                self.output['objects'].append(list_item)
        self.form_out(ListeleForm())

    def yonlendir(self):
        """
        Anasayfaya Yonlendirme İşlemi
        """
        self.current.output['cmd'] = 'reload'
