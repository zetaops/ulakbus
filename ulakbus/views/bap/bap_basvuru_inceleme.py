# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPIsPaketi
from ulakbus.models import BAPButcePlani
from ulakbus.models import six
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.settings import DATE_DEFAULT_FORMAT


class ProjeIncelemeForm(JsonForm):
    """
    Koordinasyon biriminin projeyi incelerken kategoriler arasında geçiş yapabileceği ve
    inceleme sonrası karar vermesini sağlayan form.

    """

    proje_hakkinda = fields.Button(_(u"Proje Hakkında"), cmd='proje_hakkinda')
    butce_plani = fields.Button(_(u"Bütçe Planı"), cmd='butce_plani')
    proje_calisanlari = fields.Button(_(u"Proje Çalışanları"), cmd='proje_calisanlari')
    is_plani = fields.Button(_(u"İş Planı"), cmd='is_plani')
    iptal = fields.Button(_(u"Daha Sonra Karar Ver"), cmd='iptal', style="btn-info")
    karar_ver = fields.Button(_(u"Karar Ver"), cmd='karar_ver', style="btn-info")


class IsPlaniAyrintilariForm(JsonForm):
    """
    İş paketlerinin içinde bulunan işlerin ayrıntılı gösterilmesine yarayan form.

    """
    tamam = fields.Button(_(u"Tamam"), cmd='is_plani')


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
        }

        self.default_kategori = 'proje_hakkinda'
        self.current.output["meta"]["allow_search"] = False

    def kategori_datalari_olustur(self):
        """
        Proje bilgilerini, proje hakkında ve çalışanları olarak iki kategoriye ayırır ve dict'e
        koyar. Gösterime hazır hale getirir.

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
                        detay_dict = list_node_to_str(key, obj_field)
                        for k, v in detay_dict.items():
                            detay_goster_data[kategori][k] = v

                else:
                    key = six.text_type(obj_field['title'])
                    detay_goster_data[kategori][key] = str(obj_field['value']) if obj_field[
                                                                        'value'] is not None else ''

        detay_goster_data['proje_calisanlari'][
            'Yürütücü Personel'] = self.object.yurutucu.__unicode__()

        for k, v in detay_goster_data.items():
            self.current.task_data[k] = v, self.detaylar[k][1]

    def butce_is_plani_goster(self):
        """
        Projenin Bütçe Planı ve İş Planı kısımlarının gösterildiği yerdir.

        """
        title = 'İş Planı' if self.cmd == 'is_plani' else 'Bütçe Planı'
        plan = '%s_goster' % self.cmd
        getattr(self, plan)()
        self.form_out(ProjeIncelemeForm(title=__(title)))

    def proje_hakkinda_calisanlar_goster(self):
        """
        Proje Hakkında ve Proje Çalışanları kısımlarının gösterildiği yerdir. Önceden hazırlanmış
        datadan proje hakkında ya da çalışanlar'dan hangisi istenmiş ise o gösterilir.

        """

        kategori = self.cmd if self.cmd in self.detaylar.keys() else self.default_kategori
        gosterilecek_degerler, title = self.current.task_data[kategori]
        self.output['object'] = gosterilecek_degerler
        self.form_out(ProjeIncelemeForm(title=__(title)))

    def kategori_bul(self, field_name):
        """
        Verilen field name'in hangi kategoriye ait olduğunu döndürür. Eğer belirtilmemişse
        False döner.

        Args:
            field_name(str): Nesnenin fieldının adı. 'ad', 'soyad' gibi.

        Returns: kategori adı 'proje_hakkinda', 'proje_calisanlari' gibi ya da False

        """

        for kategori, kategori_fields in self.detaylar.items():
            if field_name in kategori_fields[0]:
                return kategori
        return False

    def is_plani_goster(self):
        """
        Projenin iş paketlerini gösterir.

        """
        self.output['objects'] = [[_(u'Paket Adı'), _(u'Başlangıç Tarihi'), _(u'Bitiş Tarihi')]]

        for plan in BAPIsPaketi.objects.filter(proje=self.object):
            ad = plan.ad
            bas_tarih = plan.baslama_tarihi.strftime(
                DATE_DEFAULT_FORMAT) if plan.baslama_tarihi else ''

            bit_tarih = plan.bitis_tarihi.strftime(DATE_DEFAULT_FORMAT) if plan.bitis_tarihi else ''

            list_item = {
                "fields": [ad, str(bas_tarih), str(bit_tarih)],
                "actions": [
                    {'name': _(u'Ayrıntı Göster'), 'cmd': 'ayrinti', 'show_as': 'button',
                     'object_key': 'data_key'}
                ],
                'key': plan.key}

            self.output['objects'].append(list_item)

    def is_plani_ayrintili_goster(self):
        """
        Projenin iş paketleri içerisinden seçilen o iş paketini oluşturan işlerin ayrıntıları
        gösterilir.

        """
        self.output['objects'] = [[_(u'İş Adı'), _(u'Başlangıç Tarihi'), _(u'Bitiş Tarihi')]]
        self.current.output["meta"]["allow_actions"] = False
        is_paketi = BAPIsPaketi.objects.get(self.current.input['data_key'])
        self.form_out(IsPlaniAyrintilariForm(title='%s İş Planı Ayrıntıları' % is_paketi.ad))
        for bap_is in is_paketi.Isler:
            ayrinti_is = bap_is.isler
            ad = ayrinti_is.ad
            bas_tarih = ayrinti_is.baslama_tarihi.strftime(
                DATE_DEFAULT_FORMAT) if ayrinti_is.baslama_tarihi else ''

            bit_tarih = ayrinti_is.bitis_tarihi.strftime(
                DATE_DEFAULT_FORMAT) if ayrinti_is.bitis_tarihi else ''
            list_item = {
                "fields": [ad, str(bas_tarih), str(bit_tarih)],
                "actions": '',
            }

            self.output['objects'].append(list_item)

    def butce_plani_goster(self):
        """
        Projenin bütçe planını gösterir.

        """
        self.current.output["meta"]["allow_actions"] = False
        self.output['objects'] = [
            [_('Muhasebe Kodu'), _(u'Kod Adı'), _(u'Kalem Adı'), _(u'Birim Fiyatı'),
             _(u'Adet'), _('Toplam Fiyat'), _('Gerekçe')]]

        for plan in BAPButcePlani.objects.filter(proje=self.object):
            muhasebe_kodu = plan.muhasebe_kod
            kod_adi = plan.kod_adi
            ad = plan.ad
            birim_fiyat = str(plan.birim_fiyat)
            adet = str(plan.adet)
            toplam_fiyat = str(plan.toplam_fiyat)
            gerekce = plan.gerekce

            list_item = {
                "fields": [muhasebe_kodu, kod_adi, ad, birim_fiyat, adet, toplam_fiyat, gerekce],
                "actions": "",
            }
            self.output['objects'].append(list_item)


def list_node_to_str(key, obj_field):
    """
    Nesnenin list node fieldının içinde bulunan her bir fieldı key, value şeklinde string haline
    çevirir ve ilgili kategoriye koyar.

    Args:
        key(str): list node fieldının adı.
        obj_field(dict): list node fieldının json hali.

    Returns:
        list_node_dict(dict)

    """

    list_node_dict = {}
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

        list_node_dict['%s %s' % (key, i + 1)] = degerler

    return list_node_dict
