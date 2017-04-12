# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import OrderedDict

from pyoko.lib.utils import un_camel
from ulakbus.lib.cache import HitapPersonelGirisBilgileri
from ulakbus.models import Personel
from zengine.views.crud import CrudView, list_query, obj_filter
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy
import six
from ulakbus.lib.hitap import hitap_save, hitap_delete
import datetime


class ListFormHitap(JsonForm):
    """
    Hitapa Gönder eklenmis list view formu.
    """
    gonder = fields.Button(gettext_lazy(u"Hitap'a Gönder"), cmd="gonder")


class HitapIslemleri(CrudView):
    def __init__(self, current=None):
        super(HitapIslemleri, self).__init__(current)
        self.ListForm = ListFormHitap
        self.model = self.model_class
        if 'id' in self.input:
            self.current.task_data['personel_id'] = self.input['id']
            self.current.task_data['personel_tckn'] = Personel.objects.get(self.input['id']).tckn
        self.personel_id = self.current.task_data['personel_id']

        self.meta = {'user': self.current.user_id,
                     'role': self.current.role_id,
                     'wf_name': self.current.workflow_name}

        self.index_fields = [('user', 'bin'), ('role', 'bin'), ('wf_name', 'bin')]

    def hitap_bilgileri_cache_kontrol(self):
        """
        Cache'de personelin hitapa giriş bilgilerinin olup olmadığı kontrol edilir. Eğer varsa
        tekrardan giriş bilgileri istenmez ve iş akışı boyunca kullanılabilmesi için task_data'nın
        içine koyulur.

        """
        self.current.task_data['cache_kontrol'] = False
        giris_bilgileri = HitapPersonelGirisBilgileri(self.current.task_data['personel_id']).get()
        if giris_bilgileri:
            self.current.task_data['cache_kontrol'] = True
            if 'giris_bilgileri' not in self.current.task_data:
                self.current.task_data['giris_bilgileri'] = giris_bilgileri

    def hitap_bilgileri_isteme(self):
        """
        Giriş bilgileri cache'de bulunamadıysa, personelden giriş bilgileri istenir.

        """
        form = JsonForm(title=_(u"Hitap Servisi Giriş Bilgileri"))
        form.help_text = _(u"Bu iş akışı hitap servisine bağlanmayı gerektirmektedir. Lütfen "
                           u"Hitap kullanıcı adı ve parola bilgilerinizi giriniz. Girdiğiniz bilgiler"
                           u" sistemimizde iki saat tutulduktan sonra silinecektir. Böylelikle iki "
                           u"saat içerisinde yapacağınız HİTAP işlemlerinde sizden şifre istenmeyecektir.")

        form.hitap_k_adi = fields.String(_(u"Hitap kullanıcı adınızı giriniz."))
        form.hitap_parola = fields.String(_(u"Hitap parolanızı giriniz."), type="password")
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def hitap_giris_bilgileri_kontrol(self):
        """
        Personelin girmiş olduğu giriş bilgilerinin doğruluğu servis çağrısıyla kontrol edilir.
        """
        # Giriş bilgileriyle servis call yapılıp giriş bilgileri kontrol edilecek.
        # Kontroller geçici olarak test için yapılmıştır.
        self.current.task_data['hitap_bilgi_kontrol'] = False
        username = self.input['form']['hitap_k_adi']
        password = self.input['form']['hitap_parola']
        if username == 'temp_uname' and password == 'temp_pass':
            self.current.task_data['hitap_bilgi_kontrol'] = True

    def hitap_giris_bilgileri_hata_mesaji_uret(self):
        """
        Bilgiler yanlış girilmişse hata mesajı üretilir, kullanıcıdan tekrar giriş yapması istenir.
        """
        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'Hatalı Hitap Giriş Bilgileri'),
            "msg": _(u'Hitap giriş bilgileriniz hatalıdır. Lütfen kontrol ederek tekrar deneyiniz.')
        }

    def hitap_bilgileri_cache_kaydet(self):
        """
        Bilgiler doğru ise iki saatlik süre boyunca cache'e koyulur. İş akışı boyunca kullanılması
        için ayrıca task_data'nın içine de koyulur.
        """
        k_adi = self.input['form']['hitap_k_adi']
        parola = self.input['form']['hitap_parola']
        giris_bilgileri = {'k_adi': k_adi, 'parola': parola}
        HitapPersonelGirisBilgileri(self.personel_id).set(giris_bilgileri, 7200)
        self.current.task_data['giris_bilgileri'] = giris_bilgileri

    def islem_secim(self):
        """
        Hitap ile senkronize etme ve hitapa değişiklik gönderme ekranlarından birisinin seçilmesi
        beklenir.
        """
        # Tab'li yapı implementasyonu yapılacaktır.
        form = JsonForm(title=_(u"İşlem Seçeneği"))
        form.degisiklik = fields.Button(_(u"Değişiklik Ekranı"), cmd='degisiklik')
        form.hitap_bilgileri = fields.Button(_(u"Hitap Bilgileri"), cmd='hitap_bilgileri')
        self.form_out(form)

    def kaydet(self):
        """
        Gelen nesnenin kayit_no field'ı boş ise hitapa hiç gitmemiş demektir ve yeni bir kayıttır.
        Değişiklikler kaydedilir ve sync field'ı yeni kayıt anlamına gelen 2 yapılır. kayit_no
        fieldı mevcut ise hitapta va demektir, değişiklikler kaydedilir ve sync'i güncellenecek
        anlamına gelen 4 yapılır.
        """
        # self.set_form_data_to_object()
        self.object.sync = 4 if self.object.kayit_no else 2
        self.object.save(meta=self.meta, index_fields=self.index_fields)

    def sil(self):
        """
        Silinmek istenen kayıt yeni kayıt ise direk silinir, mevcut bir kayıt ise sync'i silinecek
        kayıt anlamına gelen 3 yapılır.
        """
        if not self.object.kayit_no:
            self.object.delete(meta=self.meta, index_fields=self.index_fields)
        else:
            self.object.sync = 3
            self.object.save(meta=self.meta, index_fields=self.index_fields)
        self.set_client_cmd('reload')

    def hitaptaki_kaydi_getir(self):
        # Tekil hitaptaki kaydı getirip yereldeki datayı onunla değiştirecek servis yapılacaktır.
        pass

    def hitapa_gonder(self):
        """


        """

        service_name = un_camel(self.model_class.__name__, dash='-')
        # p = Personel.objects.get(self.personel_id)
        # self.model_class(personel=p,sync =3,kayit_no='21',tckn = self.current.task_data['personel_tckn']).blocking_save()

        kaydedilecekler = self.model.objects.filter(personel_id=self.personel_id, sync__in=[2, 4])
        silinecekler = self.model.objects.filter(personel_id=self.personel_id, sync=3)
        for kayit in kaydedilecekler:
            kayit.tckn = str(self.current.task_data['personel_tckn'])
            kayit.save()
            hitap_save(kayit, service_name,self.meta,self.index_fields)
        for kayit in silinecekler:
            kayit.tckn = str(self.current.task_data['personel_tckn'])
            kayit.save()
            hitap_delete(kayit, service_name,self.meta,self.index_fields)

    def hitap_bilgileri_goster(self):
        """
        Yerelde bulunan en son senkronize edilmiş bilgiler gösterilir. Hitap ile senkronize et
        butonuna basıldığında senkronize servis çağrısı gerçekleşir.
        """
        self.list()
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_search"] = False
        model_adi = six.text_type(self.model.Meta.verbose_name)
        form = JsonForm(title=_(u"Hitap %s Bilgileri") % model_adi)
        try:
            son_senkronize_tarihi = self.list_by_personel_id(self.model.objects)[
                0].son_senkronize_tarihi
            form.help_text = _(u"Son Senkronize Tarihi: %s" % son_senkronize_tarihi)
        except:
            form.help_text = _(u"Veritabanında HİTAP ile senkronize kayıt bulunmamaktadır.")

        form.senkronize = fields.Button(_(u"Hitap İle Senkronize Et"), cmd='sync')
        self.form_out(form)

    def islem_mesaji_olustur(self):
        """
        Senkronizasyon işlemi gerçekleştikten sonra başarılı işlem mesajı oluşturulur.
        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'İşlem Başarılı'),
            "msg": _(u'Kayıtlar Hitap ile başarıyla senkronize edildi.')
        }

    @obj_filter
    def hitap_islemleri(self, obj, result):
        result['actions'] = [
            {'name': _(u'Kaydet'), 'cmd': 'save', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Sil'), 'cmd': 'delete', 'mode': 'normal', 'show_as': 'button'},
        ]

    @list_query
    def list_by_personel_id(self, queryset):
        return queryset.filter(personel_id=self.personel_id, sync=1)
