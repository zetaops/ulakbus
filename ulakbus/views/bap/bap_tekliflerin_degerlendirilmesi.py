# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import BAPTeklif, BAPFirma, BAPButcePlani, BAPTeklifFiyatIsleme
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.lib.s3_file_manager import S3FileManager
from pyoko.exceptions import ObjectDoesNotExist
from datetime import datetime


class KazananFirmalarForm(JsonForm):
    """
    
    """

    class Meta:
        inline_edit = ['firma']
        always_blank = False

    class KazananFirmalar(ListNode):
        class Meta:
            title = "Kazanan Firmalar"

        kalem = fields.String(__(u"Bütçe Kalemi Adı"))
        adet = fields.Integer(__(u"Adet"))
        firma = fields.String(__(u"Kazanan Firma"))
        key = fields.String('Key', hidden=True)

    kaydet = fields.Button(__(u"Kaydet"), cmd='kaydet')
    geri = fields.Button(__(u"Teklif Görüntüleme Ekranına Geri Dön"), cmd='geri_don')


class KazananFirmalarGosterForm(KazananFirmalarForm):
    class Meta:
        inline_edit = []
        always_blank = False

    KazananFirmalar = KazananFirmalarForm.KazananFirmalar
    kaydet = fields.Button(__(u"Onayla"), cmd='onayla')
    geri = fields.Button(__(u"Kazanan Belirleme Ekranına Geri Dön"), cmd='geri_don')


class TeklifGorForm(JsonForm):
    """
    Teklifin yapıldığı ve düzenlendiği form.

    """
    degerlendir = fields.Button(__(u"Teklifleri Değerlendir"), cmd='degerlendir')
    toplu_indir = fields.Button(__(u"Bütün Teklif Dosyalarını İndir"), cmd='toplu_indir')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class KararVerForm(JsonForm):
    """
    
    """
    belirle = fields.Button(__(u"Kazanan Firmaları Belirle"), cmd='belirle')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class TeklifIsleForm(JsonForm):
    """

    """

    class Meta:
        inline_edit = ['birim_fiyat', 'toplam_fiyat']

    class TeklifIsle(ListNode):
        class Meta:
            title = __(u"Teklif Fiyat İşlemeleri")

        kalem = fields.String(__(u"Bütçe Kalemi Adı"))
        adet = fields.Integer(__(u"Adet"))
        birim_fiyat = fields.Float(__(u" Birim Fiyat"))
        toplam_fiyat = fields.Float(__(u"Toplam Fiyat"))
        key = fields.String('Key', hidden=True)

    kaydet = fields.Button(__(u"Kaydet"), cmd='kaydet')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class TeklifDegerlendirme(CrudView):
    """
    Firmaların, teklife açık bütçe kalemlerine teklif vermesini sağlayan iş akışı.

    """

    class Meta:
        model = 'BAPSatinAlma'

    def _list(self):
        """
        Koordinasyon birimi görevlisinin kendi üstünde bulunan, teklif süresi dolmuş ve 
        değerlendirilmemiş satın alma duyurularını listeler.
        
        """
        form = JsonForm(title=__(u"Teklife Kapanmış Bütçe Kalemi Satın Almaları"))
        self.list(custom_form=form)

    def teklifleri_gor(self):
        """
        Seçilen satın alma duyurusuna teklif yapmış firmalar listelenir.
        
        """
        self.output['objects'] = [[_(u'Firma Adı')]]
        for teklif in BAPTeklif.objects.filter(satin_alma=self.object):
            name, cmd = (_(u'Teklif Fiyatları Düzenle'), 'duzenle') if teklif.fiyat_islemesi else (
                _(u'Teklif Fiyatları İşle'), 'isle')
            firma_ad = teklif.firma.ad
            list_item = {
                "fields": [firma_ad],
                "actions": [
                    {'name': _(u'Teklif Belgesi İndir'), 'cmd': 'indir', 'show_as': 'button',
                     'object_key': 'data_key'},
                    {'name': name, 'cmd': cmd, 'show_as': 'button', 'object_key': 'data_key'}
                ],
                'key': teklif.key}

            self.output['objects'].append(list_item)

        title = "{} Adlı Satın Alma Duyurusu Teklifleri".format(self.object.ad)
        help_text = "{} adlı satın alma duyurusuna yapılmış teklifler gösterilir."
        form = TeklifGorForm(title=title)
        form.help_text = help_text.format(self.object.ad)
        self.form_out(form)

    def belge_indir(self):
        kwargs = {'firma_key': self.input['data_key']} if 'data_key' in self.input else {}
        teklifler = self.belge_keyleri_bul(**kwargs)
        keys = [belge for teklif in teklifler for belge in teklif.Belgeler]
        s3 = S3FileManager()
        s3.download_files_as_zip(keys, self.object.ad)

    def belge_keyleri_bul(self, firma_key):
        query = {'satin_alma_id': self.object.id}
        if firma_key:
            query['firma_id'] = firma_key

        return BAPTeklif.objects.filter(**query)

    def teklifleri_isle_duzenle(self):

        self.current.output["meta"]["allow_add_listnode"] = False
        self.current.output["meta"]["allow_actions"] = False
        self.current.task_data['teklif_id'] = self.input['data_key']
        firma = BAPTeklif.objects.get(self.input['data_key']).firma
        self.current.task_data['firma_id'] = firma.key
        form = TeklifIsleForm(current=self.current)
        form.title = __(
            u"{} Firması {} Satın Alma Duyurusu Fiyat İşlemeleri".format(firma.ad, self.object.ad))
        form.help_text = __(u"Firmanın teklifte bulunduğu bütçe kalemleri için gereken yerleri "
                            u"doldurunuz. Teklif verilmeyen kalemlerin alanlarını boş bırakınız.")
        for kalem in self.object.ButceKalemleri:
            kalem = kalem.butce
            kwargs = {'kalem': kalem.ad, 'adet': kalem.adet, 'key': kalem.key, 'birim_fiyat': None,
                      'toplam_fiyat': None}
            if self.cmd == 'duzenle':
                try:
                    fiyat_isleme = BAPTeklifFiyatIsleme.objects.get(firma=firma, kalem=kalem)
                    kwargs.update({'birim_fiyat': fiyat_isleme.birim_fiyat,
                                   'toplam_fiyat': fiyat_isleme.toplam_fiyat})
                except ObjectDoesNotExist:
                    pass

            form.TeklifIsle(**kwargs)

        self.form_out(form)

    def teklif_islemeleri_kaydet(self):
        teklif = BAPTeklif.objects.get(self.current.task_data['teklif_id'])
        teklif.fiyat_islemesi = True
        firma = BAPFirma.objects.get(self.current.task_data.pop('firma_id'))
        for obj in self.input['form']['TeklifIsle']:
            kalem = BAPButcePlani.objects.get(obj['key'])
            kwargs = {'firma': firma, 'kalem': kalem, 'satin_alma': self.object}

            if not obj['birim_fiyat'] or not obj['toplam_fiyat']:
                BAPTeklifFiyatIsleme.objects.filter(**kwargs).delete()
                continue

            isleme, new = BAPTeklifFiyatIsleme.objects.get_or_create(**kwargs)
            kwargs = {'birim_fiyat': float(obj['birim_fiyat']),
                      'toplam_fiyat': float(obj['toplam_fiyat'])}
            isleme(**kwargs).save()
        teklif.save()

    def islem_mesaji_olustur(self):
        islem_mesaji = _(u"Teklif Fiyatları İşleme işleminiz başarıyla kaydedilmiştir. Düzenleme "
                         u"butonuna basarak girmiş olduğunuz bilgileri düzenleyebilirsiniz.")
        self.current.output['msgbox'] = {'type': 'info',
                                         "title": _(u"İşlem Mesajı"),
                                         "msg": islem_mesaji}

    def degerlendirme_kontrol(self):
        teklifler = BAPTeklif.objects.filter(satin_alma=self.object, fiyat_islemesi=False)
        self.current.task_data['degerlendirme_kontrol'] = False if teklifler else True

    def degerlendirme_hata_mesaji_olustur(self):
        hata_mesaji = _(u"'{}' adlı satın almaya ait teklif fiyatları işlemediğiniz firmalar "
                        u"bulunmaktadır. Karar vermeden önce lütfen teklif veren tüm firmaların "
                        u"tekliflerini işleyiniz.".format(self.object.ad))
        self.current.output['msgbox'] = {'type': 'warning',
                                         "title": _(u"Hata Mesajı"),
                                         "msg": hata_mesaji}

    def teklifleri_degerlendir(self):
        self.current.output["meta"]["allow_actions"] = False
        form = KararVerForm(current=self.current)
        form.title = __(u"'{}' Satın Alma Duyurusuna Verilen Teklifler".format(self.object.ad))

        self.output['objects'] = [[_(u'Kalem Adı'), _(u'Adet')]]
        firmalar = [teklif.firma for teklif in BAPTeklif.objects.filter(satin_alma=self.object)]
        self.current.task_data['firma_adlari'] = {firma.key: firma.ad for firma in firmalar}
        self.output['objects'][0].extend([firma.ad for firma in firmalar])

        for kalem in self.object.ButceKalemleri:
            kalem = kalem.butce
            list_item = {
                "fields": [kalem.ad,
                           str(kalem.adet)],
                "actions": '',
            }
            for firma in firmalar:
                fiyat = None
                try:
                    fiyat = BAPTeklifFiyatIsleme.objects.get(kalem=kalem, firma=firma)
                except ObjectDoesNotExist:
                    pass
                toplam_fiyat = str(fiyat.toplam_fiyat) if fiyat else '-'

                list_item['fields'].append(toplam_fiyat)

            self.output['objects'].append(list_item)
        self.form_out(form)

    def kazanan_firmalari_belirle(self):
        self.current.output["meta"]["allow_add_listnode"] = False
        self.current.output["meta"]["allow_actions"] = False
        form = KazananFirmalarForm(current=self.current)
        form.title = __(u"'{}' İçin Kazanan Firmaların Belirlenmesi".format(self.object.ad))
        form.help_text = __(u"Lütfen listelenmiş bütçe kalemleri için kazanan firmayı seçiniz. "
                            u"Kazanan bir firma bulunmuyor ise boş bırakınız.")
        form.KazananFirmalar._fields['firma'].choices = self.current.task_data[
            'firma_adlari'].items()

        for kalem in self.object.ButceKalemleri:
            kalem = kalem.butce
            form.KazananFirmalar(kalem=kalem.ad, adet=kalem.adet, key=kalem.key)

        self.form_out(form)

    def onaylama_ekrani_goster(self):
        self.current.output["meta"]["allow_add_listnode"] = False
        self.current.output["meta"]["allow_actions"] = False
        help_text = '{} satın alma duyurusunda bulunan bütçe kalemleri için belirlediğiniz ' \
                    'kazanan firmalar aşağıda listelenmiştir. Değişiklik yapmak için bir önceki ' \
                    'ekrana dönebilir, kaydetmek için Onayla butonuna basarak ilerleyebilirsiniz.'

        self.current.task_data['KazananFirmalarGosterForm'] = self.current.task_data[
            'KazananFirmalarForm']

        form = KazananFirmalarGosterForm(current=self.current,
                                         title='Kazanan Firmaların Onayı'
                                         )
        form.help_text = help_text.format(self.object.ad)

        self.form_out(form)

    def kazanan_firma_kaydet(self):
        form = self.input['form']['KazananFirmalar']
        for obj in form:
            if obj['firma']:
                kalem = BAPButcePlani.objects.get(obj['key'])
                kalem.kazanan_firma_id = str(obj['firma'])
                kalem.save()

    def islem_mesaji_goster(self):
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'İşlem Bilgilendirme'),
            "msg": _(u'{} adlı satın alma duyurusu için teklifler değerlendirildi ve kazanan '
                     u'firma ya da firmalar belirlendi.')}

    @obj_filter
    def teklife_kapanmis_satin_alma_actions(self, obj, result):
        result['actions'] = [
            {'name': _(u'Teklifleri Gör'), 'cmd': 'gor', 'mode': 'normal', 'show_as': 'button'},
        ]

    @list_query
    def teklife_kapanmis_satin_almalari_listele(self, queryset):
        """
        Durumu 1 olan yani, teklife açık olan satın alma duyuruları listelenir.

        """
        now = datetime.now()
        # return queryset.filter(teklife_kapanma_tarihi__lt=now, teklif_durum__lte=2)
        return queryset.filter()
