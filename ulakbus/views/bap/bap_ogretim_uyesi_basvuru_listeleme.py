# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView, list_query, obj_filter
from zengine.lib.translation import gettext as _


class TalepSecForm(JsonForm):
    class Meta:
        title = _(u"Talep Seçimi")

    talepler = fields.Integer(_(u"Talep"), required=True)
    sec = fields.Button(_(u"Seç"))
    iptal = fields.Button(_(u"İptal"), cmd='iptal')


class OgretimUyesiBasvuruListelemeView(CrudView):
    """
    Öğretim Üyesinin kendi BAP Proje başvurularını görüntüleyeceği iş akışıdır.
    """

    class Meta:
        allow_search = True
        model = 'BAPProje'

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.ListForm.add = None

    def goruntule(self):
        """
        Talepler harici is akisi task dataya konulur. BAP proje id task dataya konulur.

        """
        td = self.current.task_data
        td['bap_proje_id'] = td.get('bap_proje_id', td.pop('object_id', ''))
        td['external_wf'] = self.current.input['cmd']

    def basvuru_listele(self):
        """
        Öğretim üyesinin hali hazırdaki başvurularının listelendiği adımdır.
        """
        self.list(list_fields=['ad', 'durum'])

    def talep_sec(self):
        """
        Öğretim üyesinin proje üzerinde Ek Bütçe Talebi, Fasıl Aktarım Talebi, Ek Süre Talebi, Satın
        Alma Talebi, Yürütücü Değişikliği Talebi ve Proje İptal Talebi seçenekleri arasından
        birini seçerek talep gerçekleştireceği adımdır.
        """
        form = TalepSecForm()
        talep_list = [
            (1, _(u"Ek Bütçe Talebi")),
            (2, _(u"Fasıl Aktarımı Talebi")),
            (3, _(u"Ek Süre Talebi")),
            (4, _(u"Satın Alma Talebi")),
            (5, _(u"Yürütücü Değişikliği Talebi")),
            (6, _(u"Proje İptal Talebi")),
        ]
        proje = BAPProje.objects.get(self.current.task_data['object_id'])
        if proje.durum == 7:
            talep_list.append((4, _(u"Satın Alma Talebi")))
        form.set_choices_of('talepler', talep_list)
        form.set_default_of('talepler', 1)
        self.form_out(form)

    def secim_to_wf(self):
        """
        Seçilen talebi external olarak çalıştırmak üzere, external workflow placeholder adımına
        gönderecek adımdır.
        """
        self.current.task_data['bap_proje_id'] = self.current.task_data.pop('object_id')
        ex_dict = {
            1: 'bap_ek_butce_talep',
            2: 'bap_fasil_aktarim_talep',
            3: 'bap_ek_sure_talep',
            4: 'bap_satin_alma_talep',
            5: 'bap_yurutucu_degisikligi_talebi',
            6: 'bap_proje_iptal_talep',
        }
        secim = self.input['form'].get('talepler') or self.input['form'].get('raporlar')
        self.current.task_data['external_wf'] = ex_dict[secim]

    @obj_filter
    def basvuru_islemleri(self, obj, result, **kwargs):
        """
        Default action buttonlar, öğretim üyesinin projedeki eylemlerine göre düzenlenmiştir.
        """
        # todo externaL_wf'ler tamamlandıkça actionlara eklenecek
        result['actions'] = [
            {'name': _(u'Görüntüle'), 'cmd': 'bap_ogrbasvuru_goruntule', 'mode': 'normal',
             'show_as': 'button'},
        ]
        if obj.durum == 5:
            result['actions'].append(
                {'name': _(u'Rapor Ekle'), 'cmd': 'bap_proje_raporu', 'mode': 'normal',
                 'show_as': 'button'})
            if obj.talep_uygunlugu:
                result['actions'].append(
                    {'name': _(u'Talepler'), 'cmd': 'talepler', 'mode': 'normal',
                     'show_as': 'button'})

    @list_query
    def list_by_personel_id(self, queryset):
        """
        Öğretim üyesinin kendi projeleri filtrelenmiştir.
        """
        return queryset.filter(yurutucu=self.current.user.personel.okutman)
