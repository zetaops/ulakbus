# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.forms import JsonForm
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import fields

from pyoko import field


class ProjeDegerlendirmeForm(JsonForm):
    class Meta:
        title = _(u"Bilimsel Araştırma Projesi (BAP) Proje Başvuru Değerlendirme Formu")
        # always_blank = False

        grouping = [
            {
                "layout": "6",
                "groups": [
                    {

                        "items": ['arastirma_kapsam_tutar', 'arastirma_kapsam_tutar_gerekce',
                                  'literatur_ozeti', 'literatur_ozeti_gerekce', 'ozgun_deger',
                                  'ozgun_deger_gerekce', 'yontem_amac_tutar',
                                  'yontem_amac_tutar_gerekce', 'yontem_uygulanabilirlik',
                                  'yontem_uygulanabilirlik_gerekce']

                    }
                ]
            },
            {
                "layout": "6",
                "groups": [
                    {

                        "items": ['katki_beklenti', 'katki_beklenti_gerekce',
                                  'bilim_endustri_katki', 'bilim_endustri_katki_gerekce',
                                  'arastirmaci_bilgi_yeterlilik',
                                  'arastirmaci_bilgi_yeterlilik_gerekce',
                                  'butce_gorus_oneri', 'basari_olcut_gercek',
                                  'basari_olcut_gercek_gerekce', 'proje_gorus_oneri']
                    }
                ]
            },
            {
                "layout": "12",
                "groups": [
                    {

                        "items": ['proje_degerlendirme_sonucu']
                    }
                ]
            }
        ]

    arastirma_kapsam_tutar = field.Integer(_(u"ARAŞTIRMA KAPSAMININ PROJE AMACI İLE TUTARLILIĞI"),
                                           choices='bap_proje_degerlendirme_secenekler',
                                           default=1)
    arastirma_kapsam_tutar_gerekce = field.Text(_(u"Gerekçe-Açıklama"))

    literatur_ozeti = field.Integer(
        _(u"VERİLEN LİTERATÜR ÖZETİNİN PROJEYE UYGUNLUĞU VE YETERLİLİĞİ"),
        choices='bap_proje_degerlendirme_secenekler', default=1)

    literatur_ozeti_gerekce = field.Text(_(u"Gerekçe-Açıklama"))

    ozgun_deger = field.Integer(_(u"PROJENİN ÖZGÜN DEĞERİ"),
                                choices='bap_proje_degerlendirme_secenekler', default=1)

    ozgun_deger_gerekce = field.Text(_(u"Gerekçe-Açıklama"))

    yontem_amac_tutar = field.Integer(_(u"ÖNERİLEN YÖNTEMİN PROJE AMACI İLE TUTARLILIĞI"),
                                      choices='bap_proje_degerlendirme_secenekler', default=1)

    yontem_amac_tutar_gerekce = field.Text(_(u"Gerekçe-Açıklama"))

    yontem_uygulanabilirlik = field.Integer(_(u"ÖNERİLEN YÖNTEMİN UYGULANABİLİRLİĞİ"),
                                            choices='bap_proje_degerlendirme_secenekler', default=1)

    yontem_uygulanabilirlik_gerekce = field.Text(_(u"Gerekçe-Açıklama"))

    basari_olcut_gercek = field.Integer(_(u"BAŞARI ÖLÇÜTLERİNİN GERÇEKÇİLİĞİ"),
                                        choices='bap_proje_degerlendirme_secenekler', default=1)

    basari_olcut_gercek_gerekce = field.Text(_(u"Gerekçe-Açıklama"))

    katki_beklenti = field.Integer(_(u"PROJE İLE SAĞLANACAK KATKILARA İLİŞKİN BEKLENTİLER"),
                                        choices='bap_proje_degerlendirme_secenekler', default=1)

    katki_beklenti_gerekce = field.Text(_(u"Gerekçe-Açıklama"))

    bilim_endustri_katki = field.Integer(
        _(u"ARAŞTIRMA SONUÇLARININ BİLİME VE/VEYA ÜLKE ENDÜSTRİSİNE KATKISI"),
        choices='bap_proje_degerlendirme_secenekler', default=1)

    bilim_endustri_katki_gerekce = field.Text(_(u"Gerekçe-Açıklama"))

    arastirmaci_bilgi_yeterlilik = field.Integer(
        _(u"ARAŞTIRMACILARIN BİLGİ VE DENEYİM BİRİKİMİNİN YETERLİLİĞİ"),
        choices='bap_proje_degerlendirme_secenekler', default=1)

    arastirmaci_bilgi_yeterlilik_gerekce = field.Text(_(u"Gerekçe-Açıklama"))

    butce_gorus_oneri = field.Text(
        _(u"PROJENİN BÜTÇESİ VE UYGUNLUĞUNA İLİŞKİN GÖRÜŞ VE ÖNERİLERİNİZ"))

    proje_gorus_oneri = field.Text(
        _(u"PROJE İLE İLGİLİ UYARI VE ÖNERİLERİNİZ"))

    proje_degerlendirme_sonucu = field.Integer(
        _(u"DEĞERLENDİRME SONUCUNUZ"), choices='bap_proje_degerlendirme_sonuc', default=1)

    iptal = fields.Button(_(u"İptal"), cmd='iptal')
    tamam = fields.Button(_(u"Değerlendirme Kaydet"), cmd='kaydet')



class ProjeDegerlendirme(CrudView):
    """
        Proje hakemlerinin projeyi degerlendirirken kullanacagi is akisidir.
    """
    def __init__(self, current):
        CrudView.__init__(self, current)
        self.current.task_data['bap_proje_id'] = 'RLWk2BU0HjX1XGiU8YXJ0UhslNt'

    def deneme(self):
        self.current.task_data['bap_proje_id'] = 'RLWk2BU0HjX1XGiU8YXJ0UhslNt'

    def proje_degerlendir(self):
        form = ProjeDegerlendirmeForm()
        self.form_out(form)

    def degerlendirme_kaydet(self):
        pass