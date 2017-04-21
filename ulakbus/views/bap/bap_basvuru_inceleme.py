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
    proje_hakkinda = fields.Button(_(u"Proje Hakkında"), cmd='proje_hakkinda')
    butce_islemleri = fields.Button(_(u"Bütçe İşlemleri"), cmd='butce_islemleri')
    proje_calisanlari = fields.Button(_(u"Proje Çalışanları"), cmd='proje_calisanlari')
    is_plani = fields.Button(_(u"İş Planı"), cmd='is_plani')
    geri_don = fields.Button(_(u"Listeleme Ekranına Geri Dön"), cmd='iptal')
    karar_ver = fields.Button(_(u"Karar Ver"), cmd='karar_ver')


class BasvuruInceleme(CrudView):
    class Meta:
        model = "BAPProje"

    detaylar = {
        'proje_hakkinda': (['proje_no', 'ad', 'sure', 'anahtar_kelimeler', 'konu_ve_kapsam',
                            'literatur_ozeti', 'ozgun_deger', 'hedef_ve_amac', 'yontem',
                            'basari_olcutleri', 'b_plani', 'ArastirmaOlanaklari'],
                           'Proje Hakkında'),
        'proje_calisanlari': (
            ['ProjeCalisanlari', 'UniversiteDisiUzmanlar'], 'Proje Çalışanları'),
        'butce_islemleri': (['teklif_edilen_butce', 'kabul_edilen_butce'], 'Bütçe İşlemleri'),
        'is_plani': (['teklif_edilen_baslama_tarihi'], 'İş Planı')
    }
    default_key = 'proje_hakkinda'

    def sayfa_datalari_olustur(self):
        obj_form = JsonForm(self.object, current=self.current, models=False)._serialize(
            readable=True)

        detaylar = self.detaylar
        detay_goster_data = {k: {} for k, v in detaylar.items()}

        for obj in obj_form:
            field_tur = None
            for tur, detay_fields in detaylar.items():
                if obj['name'] in detay_fields[0]:
                    field_tur = tur
                    break
            if not field_tur:
                continue
            else:
                if obj['type'] == 'ListNode':
                    key = six.text_type(getattr(self.object, obj['name']).Meta.verbose_name)
                    for i, val in enumerate(obj['value']):
                        degerler = []
                        for d in obj['schema']:
                            if val[d['name']] is not None:
                                if d['name'].endswith('_id'):
                                    a = '%s: %s' % (d['title'], val[d['name']]['unicode'])
                                else:
                                    a = '%s: %s' % (d['title'], val[d['name']])

                            else:
                                a = '%s: %s' % (d['title'], ' ')
                            degerler.append(a)

                        degerler = ' || '.join(degerler)
                        detay_goster_data[field_tur]['%s %s' % (key, i + 1)] = degerler

                else:
                    key = six.text_type(obj['title'])
                    detay_goster_data[field_tur][key] = str(obj['value'])

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
