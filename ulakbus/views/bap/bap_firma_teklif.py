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


class FirmaTeklifForm(JsonForm):
    """
    Teklifin yapıldığı ve düzenlendiği form.
    
    """

    class Meta:
        include = ['Belgeler']

    kaydet = fields.Button(__(u"Teklifi Kaydet"), cmd='kaydet')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class MevcutTeklifForm(JsonForm):
    """
    Firmaya ait yapılmış, değerlendirme halindeki tekliflerin gösterildiği form.
        
    """

    class Meta:
        title = _(u"Firmanın Mevcut Teklifleri")
        help_text = __(u'Firmanın değerlendirme sürecinde bulunan teklifleri gösterilir.')

    geri_don = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class SonuclanmisTeklifForm(JsonForm):
    """
    Firmaya ait sonuçlanmış tekliflerin gösterildiği form.

    """

    class Meta:
        title = _(u'Firmanın Sonuçlanmış Teklifleri')

    geri_don = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class BapFirmaTeklif(CrudView):
    """
    Firmaların, teklife açık bütçe kalemlerine teklif vermesini sağlayan iş akışı.
    
    """

    class Meta:
        model = 'BAPButcePlani'

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.ListForm.add = fields.Button(__(u"Mevcut Tekliflerim"), cmd='mevcut')
        self.ListForm.sonuclanan = fields.Button(__(u"Sonuçlanmış Tekliflerim"), cmd='sonuclanan')
        self.model_class.Meta.verbose_name_plural = __(u"Teklife Açık Bütçe Kalemleri")
        self.firma = self.current.user.bap_firma_set[0].bap_firma

    def ayni_butce_kalemi_teklif_kontrol(self):
        """
        Bir firma tarafından, bir bütçe kalemine teklif yapılmışsa, 
        aynı bütçe kalemine yeni bir teklif yapılmasını kontrol eder.
                
        """
        teklif_sayisi = BAPTeklif.objects.filter(butce=self.object, firma=self.firma).count()
        self.current.task_data['ayni_teklif'] = True if teklif_sayisi else False

    def ayni_teklif_var_mesaji(self):
        """
        Bir bütçe kalemine, firma tarafından yapılmış teklif varken, yeni 
        bir teklif yapılmaya çalışıldığında uyarı mesajı gösterilir. 

        """
        self.current.output['msgbox'] = {"type": "warning",
                                         "title": __(u'Mevcut Teklif Uyarısı'),
                                         "msg": __(u"""%s adlı bütçe kalemine ait başvuru sürecinde
                                         olan teklifiniz bulunmaktadır. Mevcut Tekliflerim'den 
                                         ilgili teklife ulaşabilir, değişiklikler yapabilirsiniz.
                                         """ % self.object.ad)}

    def istenen_teklifler_kontrol(self):
        """
        İstenen şekilde (mevcut ya da sonuçlanan) herhangi 
        bir teklifin olup olmadığını kontrol eder. 

        """
        query = {'durum__in': [2, 3]} if self.cmd == 'sonuclanan' else {'durum': 1}
        teklif_sayisi = BAPTeklif.objects.filter(firma=self.firma, **query).count()
        self.current.task_data['istenen_teklifler'] = True if teklif_sayisi else False

    def istenen_teklif_yok_mesaji(self):
        """
        İstenen teklif (mevcut ya da sonuçlanan) yokken, tekliflerin 
        görüntülenmesi istenirse uyarı mesajı üretilir ve gösterilir.

        """
        durum = 'sonuçlanmış' if self.cmd == 'sonuclanan' else 'başvuru sürecinde bulunan'
        self.current.output['msgbox'] = {"type": "warning",
                                         "title": __(u'Firma Teklifleri'),
                                         "msg": __(
                                             u"Sistemde kayıtlı %s teklifiniz bulunmamaktadır."
                                             % durum)}

    def mevcut_teklifleri_goster(self):
        """
        Firmaya ait değerlendirme halinde olan güncel teklifler gösterilir.

        """
        teklifler = BAPTeklif.objects.filter(firma=self.firma, durum=1).order_by()
        self.output['objects'] = [[_(u'Bütçe Kalemi')]]
        for teklif in teklifler:
            butce = teklif.butce.ad
            list_item = {
                "fields": [butce],
                "actions": [
                    {'name': _(u'Belgeleri İndir'), 'cmd': 'belge_indir', 'show_as': 'button',
                     'object_key': 'data_key'},
                    {'name': _(u'Belgeleri Düzenle'), 'cmd': 'belge_duzenle', 'show_as': 'button',
                     'object_key': 'data_key'}
                ],
                'key': teklif.key}
            self.output['objects'].append(list_item)
        self.form_out(MevcutTeklifForm(current=self.current))

    def sonuclanan_teklifleri_goster(self):
        """
        Firmaya ait sonuçlanmış(red ya da kabul) teklifler gösterilir.
        
        """
        self.current.output["meta"]["allow_actions"] = False
        teklifler = BAPTeklif.objects.filter(firma=self.firma, durum__in=[2, 3]).order_by()
        self.output['objects'] = [[_(u'Bütçe Kalemi'), _(u'Sonuçlanma Tarihi'), _(u'Durum')]]
        for teklif in teklifler:
            butce = teklif.butce.ad
            tarih = teklif.sonuclanma_tarihi.strftime(DATE_DEFAULT_FORMAT)
            durum = teklif.get_durum_display()
            list_item = {
                "fields": [butce, tarih, durum],
                "actions": ''}
            self.output['objects'].append(list_item)
        self.form_out(SonuclanmisTeklifForm(current=self.current))

    def teklif_belgeleri_indir(self):
        """
        Seçilen teklife ait teklif belgeler zip dosyası olarak indirilir.
                
        """
        s3 = S3FileManager()
        teklif = BAPTeklif.objects.get(self.current.input['data_key'])
        keys = [belge.belge for belge in teklif.Belgeler]
        zip_name = "%s-teklif-belgeler" % teklif.__unicode__()
        zip_url = s3.download_files_as_zip(keys, zip_name)
        self.set_client_cmd('download')
        self.current.output['download_url'] = zip_url

    def teklif_belgeleri_duzenle(self):
        """
        Seçilen teklife ait teklif belgeleri düzenlenir. Mevcut 
        belgeler silinebilir, yeni belgeler yüklenebilir. 

        """
        self.current.task_data['data_key'] = self.current.input['data_key']
        teklif = BAPTeklif.objects.get(self.current.task_data['data_key'])
        self.form_out(
            FirmaTeklifForm(teklif, current=self.current, title=__(u"Teklif Belgeleri Düzenleme")))

    def teklif_duzenle_kaydet(self):
        """
        Teklif belgeleri düzenlendikten sonra Belgeler kısmı formdan 
        gelen belgelere göre tekrardan düzenlenir ve kaydedilir.        

        """
        teklif = BAPTeklif.objects.get(self.current.task_data['data_key'])
        # Formdan değişiklik yapılmış, en son istenen belgeler alınır.
        form_belgeler = [(belge['belge'], belge['aciklama']) for belge in
                         self.input['form']['Belgeler']]

        mevcut = {}
        yeni = []
        for belge, aciklama in form_belgeler:
            # dict ise yeni eklenmiş belgedir.
            if isinstance(belge, dict):
                yeni.append((belge, aciklama))
            else:
                # kayıtlı, var olan belgedir.
                mevcut[belge] = aciklama

        # Veritabanına kayıtlı belgeler içinde dolaşılır,
        # formda bulunmayan belgeler veritabanından silinir.
        # Formda bulunan ama açıklaması değişmiş belgelerin açıklamaları güncellenir.
        for belge in teklif.Belgeler:
            if belge.belge not in mevcut:
                belge.remove()
            elif belge.aciklama != mevcut[belge.belge]:
                belge.aciklama = mevcut[belge.belge]

        # Yeni belgeler açıklamalarıyla beraber veritabına kaydedilir.
        [teklif.Belgeler(belge=belge, aciklama=aciklama) for belge, aciklama in yeni]
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
                                                   u" yüklenmiştir. Mevcut Tekliflerim altından"
                                                   u" teklif belgelerinize ulaşabilir ve "
                                                   u"belgelerinizde değişiklikler yapabilirsiniz.")}

    def teklif_ver(self):
        """
        Teklifin yapıldığı, belgelerin eklenebildiği ekran oluşturulur.         

        """
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
        result['actions'] = [
            {'name': _(u'Teklifte Bulun'), 'cmd': 'teklif_ver', 'mode': 'normal',
             'show_as': 'button'},
        ]

    @list_query
    def teklife_acik_butce_kalemleri_listele(self, queryset):
        """
        Durumu 1 olan yani, teklife açık olan bütçe kalemleri listelenir.
                
        """
        return queryset.filter(teklif_durum=1)
