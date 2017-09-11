# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import OrderedDict
from ulakbus.models import BAPProje
from ulakbus.views.bap.bap_proje_degerlendirme import ProjeDegerlendirmeForm
from zengine.forms import JsonForm
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.lib.catalog_data import catalog_data_manager
from zengine.forms import fields
from pyoko.fields import Integer


class ProjeDegerlendirmeGoruntuleForm(JsonForm):
    """
    Proje degerlendirmelerinin goruntulendigi formdur.
    """

    class Meta:
        title = __(u"Proje Degerlendirmeleri")

    geri = fields.Button(__(u"Geri Dön"), cmd='geri')


class ProjeDegerlendirmeDetayGoruntuleForm(JsonForm):
    """
    Proje degerlendirme detaylarının goruntulendigi formdur.
    """

    class Meta:
        title = __(u"Proje Degerlendirmeleri")

    geri = fields.Button(__(u"Geri Dön"))


class ProjeDegerlendirmeGoruntule(CrudView):
    """
    Koordinasyon biriminin proje degerlendirmelerini goruntuleyegi is akisidir.
    """

    def degerlendirmeleri_goruntule(self):
        """
        Koordinasyon biriminin proje degerlendirme sonuclarini goruntuleyebildigi adimdir.
         Eger projeler degerlendirilmisse detay goruntuleme secenegi aktif olur.
         Degerlendirilmemisse o anki durum gösterilir. Detay gosterilmez.
        """
        if 'object_id' in self.input:
            self.current.task_data['bap_proje_id'] = self.input['object_id']
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.current.output["meta"]["allow_search"] = False
        self.output['objects'] = [
            [_(u'Hakem'), _(u'Değerlendirme Durumu'), _(u'Değerlendirme Sonucu')]
        ]
        cd_durum = catalog_data_manager.get_all_as_dict('bap_proje_hakem_degerlendirme_durum')
        cd_sonuc = catalog_data_manager.get_all_as_dict('bap_proje_degerlendirme_sonuc')
        for degerlendirme in proje.ProjeDegerlendirmeleri:
            hakem = degerlendirme.hakem().okutman().__unicode__()
            durum = cd_durum[degerlendirme.hakem_degerlendirme_durumu]
            sonuc = cd_sonuc.get(degerlendirme.degerlendirme_sonucu, 'Henüz değerlendirme yapmadı')

            list_item = {
                "fields": [hakem, durum, sonuc],
                "actions": [],
            }
            if degerlendirme.hakem_degerlendirme_durumu == 5:
                list_item["actions"].append(
                    {
                        'name': _(u'Detay'),
                        'cmd': 'detay',
                        'mode': 'normal',
                        'show_as': 'button'
                    })
                list_item['key'] = degerlendirme.hakem().okutman().key
            self.output['objects'].append(list_item)
        self.form_out(ProjeDegerlendirmeGoruntuleForm())

    def detay_goruntule(self):
        """
        Koordinasyon biriminin proje degerlendirme detaylarini goruntuledigi adimdir.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        hakem_id = self.input['object_id']
        f = ProjeDegerlendirmeForm()
        cd_degerlendirme = catalog_data_manager.get_all_as_dict('bap_proje_degerlendirme_secenekler')
        cd_sonuc = catalog_data_manager.get_all_as_dict('bap_proje_degerlendirme_sonuc')
        obj = OrderedDict()
        for degerlendirme in proje.ProjeDegerlendirmeleri:
            if hakem_id == degerlendirme.hakem().okutman().key:
                self.output['object_title'] = _(u"""%s Projesine %s Adlı Hakemin Değerlendirme
                Detayı""" % (proje, degerlendirme.hakem().okutman()))
                for key, value in f._fields.items():
                    if key not in ['degerlendirme_kaydet', 'incelemeye_don',
                                   'proje_degerlendirme_sonucu'] and not key.endswith("_gerekce"):
                        obj[value.title] = _(u"""Değerlendirme: %s\nAçıklama: %s""" % (
                            cd_degerlendirme[degerlendirme.form_data[key]],
                            degerlendirme.form_data["%s_gerekce" % key])) if \
                            type(value) == Integer else degerlendirme.form_data[key]
                obj[f._fields['proje_degerlendirme_sonucu'].title] = cd_sonuc[
                    degerlendirme.form_data['proje_degerlendirme_sonucu']]
        del self.current.task_data['object_id']
        self.output['object'] = obj
        self.form_out(ProjeDegerlendirmeDetayGoruntuleForm())
