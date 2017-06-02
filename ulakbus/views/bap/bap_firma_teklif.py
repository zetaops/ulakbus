# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPTeklif
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.lib.s3_file_manager import S3FileManager
from ulakbus.settings import DATE_DEFAULT_FORMAT
from datetime import datetime


class FirmaTeklifForm(JsonForm):
    """
    Teklifin yapıldığı ve düzenlendiği form.
    
    """

    class Meta:
        include = ['Belgeler']

    kaydet = fields.Button(__(u"Teklifi Kaydet"), cmd='kaydet')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class TeklifleriGosterForm(JsonForm):
    """
    Firmaya ait sonuçlanmış tekliflerin gösterildiği form.

    """

    class Meta:
        title = _(u'Firmanın Teklifleri')
        help_text = _(u"Firmanın sonuçlanmış veya değerlendirme sürecinde bulunan"
                      u" tüm teklifleri gösterilir.")

    geri_don = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class BapFirmaTeklif(CrudView):
    """
    Firmaların, teklife açık bütçe kalemlerine teklif vermesini sağlayan iş akışı.
    
    """

    class Meta:
        model = 'BAPButcePlani'

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.ListForm.add = fields.Button(__(u"Tekliflerimi Göster"), cmd='tekliflerim')
        self.model_class.Meta.verbose_name_plural = __(u"Teklife Açık Bütçe Kalemleri")
        self.firma = self.current.user.bap_firma_set[0].bap_firma

    def teklifler_kontrol(self):
        """
        Değerlendirme sürecinde ya da sonuçlanmış herhangi 
        bir teklifin olup olmadığını kontrol eder. 

        """
        teklif_sayisi = BAPTeklif.objects.filter(firma=self.firma).count()
        self.current.task_data['tekliflerim'] = True if teklif_sayisi else False

    def teklif_yok_mesaji(self):
        """
        Değerlendirme sürecinde ya da sonuçlanmış teklif yokken, tekliflerin 
        görüntülenmesi istenirse uyarı mesajı üretilir ve gösterilir.

        """
        self.current.output['msgbox'] = {"type": "warning",
                                         "title": __(u'Firma Teklifleri'),
                                         "msg": __(
                                             u"Sistemde kayıtlı sonuçlanmış ya da değerlendirme"
                                             u" sürecinde bulunan teklifiniz bulunmamaktadır.")}

    def teklifleri_goster(self):
        """
        Değerlendirme sürecinde ya da sonuçlanmış teklifler gösterilir.
        
        """
        teklifler = BAPTeklif.objects.filter(firma=self.firma).order_by()
        self.output['objects'] = [[_(u'Bütçe Kalemi'), _(u'Sonuçlanma Tarihi'), _(u'Durum')]]
        for teklif in teklifler:
            butce = teklif.butce.ad
            tarih = teklif.sonuclanma_tarihi.strftime(
                DATE_DEFAULT_FORMAT) if teklif.sonuclanma_tarihi else ""
            durum = teklif.get_durum_display()
            list_item = {
                "fields": [butce, tarih, durum],
                "actions": [
                    {'name': _(u'Teklif Belgeleri İndir'), 'cmd': 'belge_indir',
                     'show_as': 'button',
                     'object_key': 'data_key'}
                ],
                'key': teklif.key}
            self.output['objects'].append(list_item)
        self.form_out(TeklifleriGosterForm(current=self.current))

    def teklif_belgeleri_indir(self):
        """
        Seçilen teklife ait teklif belgeler zip dosyası olarak indirilir.
                
        """
        s3 = S3FileManager()
        if 'data_key' in self.current.input:
            teklif = BAPTeklif.objects.get(self.current.input['data_key'])
        else:
            teklif = BAPTeklif.objects.get(firma=self.firma, butce=self.object)
        keys = [belge.belge for belge in teklif.Belgeler]
        zip_name = "%s-teklif-belgeler" % teklif.__unicode__()
        zip_url = s3.download_files_as_zip(keys, zip_name)
        self.set_client_cmd('download')
        self.current.output['download_url'] = zip_url

    def teklif_belgeleri_duzenle(self):
        """
        Seçilen teklife ait teklif belgeleri düzenlenir. Mevcut 
        belgeler düzenlenebilir, silinebilir, yeni belgeler yüklenebilir. 

        """
        self.current.task_data['new'] = False
        teklif = BAPTeklif.objects.get(firma=self.firma, butce=self.object)
        self.form_out(
            FirmaTeklifForm(teklif, current=self.current, title=__(u"Teklif Belgeleri Düzenleme")))

    def teklif_duzenle_kaydet(self):
        """
        Teklif belgeleri düzenlendikten sonra Belgeler kısmı formdan 
        gelen belgelere göre tekrardan düzenlenir ve kaydedilir.        

        """
        teklif = BAPTeklif.objects.get(firma=self.firma, butce=self.object)
        form_belgeler = self.input['form']['Belgeler']

        # yeni kayıtlar
        for belge in form_belgeler:
            if 'file_content' in belge['belge']:
                teklif.Belgeler(belge=belge['belge'], aciklama=belge['aciklama'])
                form_belgeler.remove(belge)

        # mevcutlar
        belgeler_kv = {belge['belge']: belge['aciklama'] for belge in form_belgeler}

        # mevcutta olmayanları sil, olanların açıklaması değişmişse güncelle
        for belge in teklif.Belgeler:
            if not isinstance(belge.belge, dict):
                if belge.belge not in belgeler_kv:
                    belge.remove()
                elif belge.aciklama != belgeler_kv[belge.belge]:
                    belge.aciklama = belgeler_kv[belge.belge]

        teklif.son_degisiklik_tarihi = datetime.now()
        teklif.blocking_save()
        self.task_data_file_guncelle(teklif)

    def islem_sonrasi_mesaj(self):
        """
        Teklif yeni kaydedildikten sonra ve düzenlemeden 
        sonra işlem mesajı üretilir ve gösterilir.
         
        """
        self.current.output['msgbox'] = {"type": "info",
                                         "title": __(u'Firma Teklifleri'),
                                         "msg": __(u"Teklif belgeleriniz sisteme başarıyla"
                                                   u" yüklenmiştir. Teklif Belgeleri Düzenle ile"
                                                   u" teklif belgelerinize ulaşabilir ve "
                                                   u"belgelerinizde değişiklikler yapabilirsiniz.")}

    def teklif_ver(self):
        """
        Teklifin yapıldığı, belgelerin eklenebildiği ekran oluşturulur.         

        """
        self.current.task_data['new'] = True
        form = FirmaTeklifForm(BAPTeklif(), current=self.current, title=__(u"Bütçe Kalemi Teklifi"))
        form.help_text = __(
            u"Lütfen %s adlı bütçe kalemine yaptığınız teklife "
            u"ilişkin belgeleri sisteme yükleyiniz.") % self.object.ad
        self.form_out(form)

    def teklif_belge_kontrol(self):
        """
        Teklife ilişkin herhangi bir belgenin eklenip eklenmediği kontrol edilir.        

        """
        self.current.task_data['belge'] = True if len(self.input['form']['Belgeler']) else False

    def belge_eksikligi_mesaj(self):
        """
        Teklife ilişkin bir belge eklenmemişse uyarı mesajı üretilir ve gösterilir.      

        """
        self.current.output['msgbox'] = {"type": "warning",
                                         "title": __(u'Belge Eksikliği'),
                                         "msg": __(u"""Teklifinize ilişkin belge ya da belgeleri 
                                         yüklemeniz gerekmektedir. Lütfen kontrol edip tekrar 
                                         deneyiniz.""")}

    def teklif_kaydet(self):
        """
        Teklif veritabanına kaydedilir ve durumu değerlendirme 
        sürecinde anlamına gelen 1 yapılır.

        """
        teklif = BAPTeklif(butce=self.object, firma=self.firma)
        form_belgeler = [(belge['belge'], belge['aciklama']) for belge in
                         self.input['form']['Belgeler']]
        [teklif.Belgeler(belge=belge, aciklama=aciklama) for belge, aciklama in form_belgeler]
        teklif.durum = 1
        teklif.ilk_teklif_tarihi = datetime.now()
        teklif.son_degisiklik_tarihi = datetime.now()
        teklif.blocking_save()
        self.task_data_file_guncelle(teklif)

    def task_data_file_guncelle(self, teklif):
        """
        Task data içerisinde base64 şeklinde dosya ismi ve dosya içeriği tutulan 
        dosyanın, kaydedildikten sonra form datası, dosyanın ismi ile güncellenir.
        
        Args:
            teklif(obj): BAPTeklif nesnesi 

        """
        teklif.reload()
        belge_form = [{'belge': b.belge, 'aciklama': b.aciklama} for b in teklif.Belgeler]
        self.current.task_data['FirmaTeklifForm']['Belgeler'] = belge_form

    @obj_filter
    def firma_kayit_actions(self, obj, result):
        teklif_sayisi = BAPTeklif.objects.filter(firma=self.firma, butce=obj).count()
        butonlar = [(_(u'Teklif Belgeleri Düzenle'), 'duzenle'),
                    (_(u'Teklif Belgeleri İndir'), 'indir')] if teklif_sayisi else [
            (_(u'Teklifte Bulun'), 'teklif_ver')]

        result['actions'] = [{'name': name, 'cmd': cmd, 'mode': 'normal',
                              'show_as': 'button'} for name, cmd in butonlar]

    @list_query
    def teklife_acik_butce_kalemleri_listele(self, queryset):
        """
        Durumu 1 olan yani, teklife açık olan bütçe kalemleri listelenir.
                
        """
        return queryset.filter(teklif_durum=1)
