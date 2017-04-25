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
    """
    Koordinasyon biriminin projeyi incelerken kategoriler arasında geçiş yapabileceği ve
    inceleme sonrası karar vermesini sağlayan form.

    """

    proje_hakkinda = fields.Button(_(u"Proje Hakkında"), cmd='proje_hakkinda')
    butce_islemleri = fields.Button(_(u"Bütçe İşlemleri"), cmd='butce_islemleri')
    proje_calisanlari = fields.Button(_(u"Proje Çalışanları"), cmd='proje_calisanlari')
    is_plani = fields.Button(_(u"İş Planı"), cmd='is_plani')
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

        self.default_kategori = 'proje_hakkinda'

    def kategori_datalari_olustur(self):
        """
        Proje bilgilerini kategori kategori ayırır ve dict'e koyar. Gösterime hazır hale getirir.

        """

        obj_form = JsonForm(self.object, current=self.current, models=False)._serialize(
            readable=True)

        detay_goster_data = {k: {} for k, v in self.detaylar.items()}

        for obj_field in obj_form:
            kategori = self.kategori_bul(obj_field['name'])
            if kategori:
                if obj_field['type'] == 'ListNode':
                    if obj_field['value'] is not None:
                        key = six.text_type(
                            getattr(self.object, obj_field['name']).Meta.verbose_name)
                        detay_goster_data = list_node_to_str(detay_goster_data, kategori, key,
                                                             obj_field)

                else:
                    key = six.text_type(obj_field['title'])
                    detay_goster_data[kategori][key] = str(obj_field['value']) if obj_field[
                                                                                      'value'] is not None else ''

        detay_goster_data['proje_calisanlari'][
            'Yürütücü Personel'] = self.object.yurutucu.__unicode__()

        for k, v in detay_goster_data.items():
            self.current.task_data[k] = v, self.detaylar[k][1]

    def istenen_datalari_hazirla(self):
        """
        Gösterilmesi istenen kategorinin adını task_data nın içerisine kategori keyi ile koyar.

        """

        kategori = self.cmd if self.cmd in self.detaylar.keys() else self.default_kategori
        self.current.task_data['kategori'] = kategori

    def istenen_datalari_goster(self):
        """
        Önceden hazırlanmış datalardan istenen kategoriye ait olanları gösterir.

        """

        key = self.current.task_data['kategori']
        gosterilecek_degerler, form_title = self.current.task_data[key]
        form = ProjeIncelemeForm(title=__(form_title))
        self.form_out(form)
        self.output['object'] = gosterilecek_degerler

    def kategori_bul(self, field_name):
        """
        Verilen field name'in hangi kategoriye ait olduğunu döndürür. Eğer belirtilmemişse
        False döner.

        Args:
            field_name(str): Nesnenin fieldının adı. 'ad', 'soyad' gibi.

        Returns: kategori adı 'proje_hakkinda', 'butce_islemleri' gibi ya da False


        """

        for kategori, kategori_fields in self.detaylar.items():
            if field_name in kategori_fields[0]:
                return kategori
        return False


def list_node_to_str(detay_goster_data, kategori, key, obj_field):
    """
    Nesnenin list node fieldının içinde bulunan her bir fieldı key, value şeklinde string haline
    çevirir ve ilgili kategoriye koyar.

    Args:
        detay_goster_data:
        kategori:
        key:
        obj:

    Returns:

    """

    for i, val in enumerate(obj_field['value']):
        degerler = []
        for d in obj_field['schema']:
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
