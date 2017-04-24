# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import six
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __


class ProjeIncelemeForm(JsonForm):
    proje_hakkinda = fields.Button(_(u"Proje Hakkında"), cmd='proje_hakkinda', style="btn-success")
    butce_islemleri = fields.Button(_(u"Bütçe İşlemleri"), cmd='butce_islemleri',style="btn-success")
    proje_calisanlari = fields.Button(_(u"Proje Çalışanları"), cmd='proje_calisanlari',
                                      style="btn-success")
    is_plani = fields.Button(_(u"İş Planı"), cmd='is_plani', style="btn-success")
    iptal = fields.Button(_(u"Daha Sonra Karar Ver"), cmd='iptal', style="btn-info")
    karar_ver = fields.Button(_(u"Karar Ver"), cmd='karar_ver', style="btn-info")


class BasvuruInceleme(CrudView):
    class Meta:
        model = "BAPProje"

    def __init__(self, current):
        CrudView.__init__(self, current)
        if not self.object.key:
            self.object = self.model_class.objects.get(self.current.task_data['bap_proje_id'])

        self.detaylar = {
            'proje_hakkinda': (['ad', 'sure', 'anahtar_kelimeler', 'konu_ve_kapsam',
                                'literatur_ozeti', 'ozgun_deger', 'hedef_ve_amac', 'yontem',
                                'basari_olcutleri', 'b_plani', 'ArastirmaOlanaklari'],
                               'Proje Hakkında'),
            'proje_calisanlari': (['ProjeCalisanlari', 'UniversiteDisiUzmanlar'],
                                  'Proje Çalışanları'),
            'butce_islemleri': (['teklif_edilen_butce', 'kabul_edilen_butce'],
                                'Bütçe İşlemleri'),
            'is_plani': (['teklif_edilen_baslama_tarihi'],
                         'İş Planı')
        }

        self.default_key = 'proje_hakkinda'

    def kategori_datalari_olustur(self):
        obj_form = JsonForm(self.object, current=self.current, models=False)._serialize(
            readable=True)

        detay_goster_data = {k: {} for k, v in self.detaylar.items()}

        for obj in obj_form:
            kategori = self.kategori_bul(obj['name'])
            if kategori:
                if obj['type'] == 'ListNode':
                    if obj['value'] is not None:
                        key = six.text_type(getattr(self.object, obj['name']).Meta.verbose_name)
                        detay_goster_data = list_node_to_str(detay_goster_data, kategori, key, obj)

                else:
                    key = six.text_type(obj['title'])
                    detay_goster_data[kategori][key] = str(obj['value']) if obj[
                                                                                'value'] is not None else ''

        detay_goster_data['proje_calisanlari'][
            'Yürütücü Personel'] = self.object.yurutucu.__unicode__()

        for k, v in detay_goster_data.items():
            self.current.task_data[k] = v, self.detaylar[k][1]

    def istenen_datalari_hazirla(self):

        key = self.cmd if self.cmd in self.detaylar.keys() else self.default_key
        self.current.task_data['istenen_key'] = key

    def istenen_datalari_goster(self):
        key = self.current.task_data['istenen_key']
        gosterilecek_degerler, form_title = self.current.task_data[key]
        form = ProjeIncelemeForm(title=__(form_title))
        self.form_out(form)
        self.output['object'] = gosterilecek_degerler

    def kategori_bul(self, field_name):
        for kategori, kategori_fields in self.detaylar.items():
            if field_name in kategori_fields[0]:
                return kategori
        return False


def list_node_to_str(detay_goster_data, kategori, key, obj):
    for i, val in enumerate(obj['value']):
        degerler = []
        for d in obj['schema']:
            if val[d['name']] is not None:
                if d['name'].endswith('_id'):
                    obj_val = '%s: %s' % (d['title'], val[d['name']]['unicode'] if val[d['name']][
                                                                                       'key'] is not None else '')
                else:
                    obj_val = '%s: %s' % (d['title'], val[d['name']])

            else:
                obj_val = '%s: %s' % (d['title'], '')
            degerler.append(obj_val)

        degerler = ' || '.join(degerler)

        detay_goster_data[kategori]['%s %s' % (key, i + 1)] = degerler

    return detay_goster_data
