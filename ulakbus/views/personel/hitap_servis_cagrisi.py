# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.modelmeta import model_registry
from ulakbus.lib.cache import HitapPersonelGirisBilgileri
from zengine.lib.translation import gettext as _
from zengine.forms import fields, JsonForm
from zengine.views.crud import CrudView, view_method
from zengine import signals
from ulakbus.services.zato_wrapper import TcknService, HitapService
from pyoko.lib.utils import un_camel
import json


class HitapGirisBilgileriForm(JsonForm):
    """
    Hitap giriş bilgilerinin girilebileceği form
    
    """

    class Meta:
        title = _(u"Hitap Servisi Giriş Bilgileri")
        help_text = _(u"Bu iş akışı hitap servisine bağlanmayı gerektirmektedir. Lütfen Hitap "
                      u"kullanıcı adı ve parola bilgilerinizi giriniz. Girdiğiniz bilgiler "
                      u"sistemimizde iki saat tutulduktan sonra silinecektir. Böylelikle iki saat "
                      u"içerisinde yapacağınız HİTAP işlemlerinde sizden şifre istenmeyecektir.")

    hitap_k_adi = fields.String(_(u"Hitap kullanıcı adınızı giriniz."))
    hitap_parola = fields.String(_(u"Hitap parolanızı giriniz."), type="password")
    ilerle = fields.Button(_(u"İlerle"))


class HitapServisCagrisi(CrudView):
    """
    CrudHitap İş Akışı

    CrudHitap, standart CrudView'a ait save, delete gibi metotların
    Hitap senkronizasyonunu ilgilendiren işlevsellikler ile
    genişletilerek elde edilmiştir.

    Bu iş akışı için senkronizasyon şu şekilde çalışmaktadır:

        - Yerel kayıtlarda yapılan her değişiklik anında Hitap
          ile eşlenecektir.

        - Silinen kayıtlar, ancak Hitap'tan silinme onayı geldikten
          sonra silinecektir. İlgili kayıt öncelikle ``silinecek``
          şeklinde işaretlenir. Hitap'tan silme işlemi ile ilgili olumlu
          sonuç geldikten sonra silinme işlemi gerçekleşir. Kayit
          senkronize olarak işaretlenir.

        - Yeni eklenen kayıtlar, gönderilecek şeklinde işaretlenir.
          Hitap'a gonderilir. Hitap'tan dönen kayıt no ile ilgili
          kayda eklenir ve senkronize şeklinde işaretlenir.

        - Güncellenen kayıtlar ise, güncelleniyor şeklinde işaretlenir.
          Guncellenen kayıt Hitap'a gönderilir. Hitap yeni bir kayıt no
          üretir ve eski kaydı siler. Bu işlem soncunda Hitap yeni bir
          ``kayıt no`` gönderir. Yereldeki kayıt yeni ``kayıt no`` ile
          güncellenir ve senkronize olarak işaretlenir.

    Buna gore ``sync`` field şu değerlerde bulunabilir:

        * 1: Kayıt Hitap ile senkronize
        * 2: Yerel kayıt güncellendi, Hitap güncellenecek
        * 3: Yerel kayıt silindi, Hitap kaydı silinecek
        * 4: Yeni bir yerel kayıt oluşturuldu, Hitap'a gönderilecek.
        
    
    Hitap servisleri task data içerisinde bulunan hitap_islemleri datasına göre çalışmaktadır.
     
        - sync: True ise hitap_sync servisi çalışır.
        
        - save: ['key_list'], key_list içerisinde gelen key ler için save servisi çalıştırılır.
        - delete: ['key_list'], key_list içerisinde gelen key ler için sil servisi çalıştırılır.
        - tekil_sync: key, yollanan key ile bulunan nesne, tekil olarak hitap ile sync edilir.

    """

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        if 'model' in self.current.task_data['hitap_islemleri']:
            self.model_class = model_registry.get_model(self.current.task_data['model_name'])
            del self.current.task_data['hitap_islemleri']['model']
        if 'object_id' in self.current.task_data:
            del self.current.task_data['object_id']

        self.meta = {'user': self.current.user_id,
                     'role': self.current.role_id,
                     'wf_name': self.current.workflow_name,
                     # 'model_name': self.model.__name__,
                     'personel': self.current.task_data['personel_id']
                     }

        self.index_fields = [('user', 'bin'),
                             ('role', 'bin'),
                             ('wf_name', 'bin'),
                             ('model_name', 'bin'),
                             ('personel', 'bin')]

    def hitap_bilgileri_cache_kontrol(self):
        """
        Cache'de personelin hitapa giriş bilgilerinin olup olmadığı kontrol edilir. Eğer varsa
        tekrardan giriş bilgileri istenmez ve iş akışı boyunca kullanılabilmesi için task_data'nın
        içine koyulur.

        """
        td = self.current.task_data
        self.current.task_data['personel_key'] = "RngBQlVfKwyFHcqcmXRvlxipK6x"
        # personel_key = self.current.user.personel.key
        giris_bilgileri = HitapPersonelGirisBilgileri(self.current.task_data['personel_key']).get()
        td['cache_varmi'] = bool(giris_bilgileri)

        if td['cache_varmi'] and 'giris_bilgileri' not in td:
            td['giris_bilgileri'] = giris_bilgileri

        td['sync'] = td['hitap_islemleri'].get('sync', False)

    def hitap_bilgileri_isteme(self):
        """
        Giriş bilgileri cache'de bulunamadıysa, personelden giriş bilgileri istenir.

        """
        self.form_out(HitapGirisBilgileriForm(current=self.current))

    def hitap_giris_bilgileri_kontrol(self):
        """
        Personelin girmiş olduğu giriş bilgilerinin doğruluğu servis çağrısıyla kontrol edilir.
        
        """
        # Giriş bilgileriyle servis call yapılıp giriş bilgileri kontrol edilecek.
        # Kontroller geçici olarak test için yapılmıştır.
        username = self.input['form']['hitap_k_adi']
        password = self.input['form']['hitap_parola']
        self.current.task_data['hitap_bilgi_kontrol'] = (username == 'hitap' and password == '123')

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
        self.current.task_data['giris_bilgileri'] = {'k_adi': self.input['form']['hitap_k_adi'],
                                                     'parola': self.input['form']['hitap_parola']}
        HitapPersonelGirisBilgileri(self.current.task_data['personel_key']).set(
            self.current.task_data['giris_bilgileri'], 7200)

    def hitap_call(self):
        """
        tekil_sync, save ve delete methodlarını gerekli parametreleri ile çalıştırır.        

        """
        for method_name, value in self.current.task_data['hitap_islemleri'].items():
            getattr(self, method_name)(value)
        del self.current.task_data['hitap_islemleri']

    def hitap_tekil_sync(self, key):
        """        
        Yerelde kayıtlı tekil bir nesne Hitap'ta bulunan hali ile güncellenir. 
        Hitap'ta bulunamazsa yerelden de silinir.

        """

        obj = self.model_class.objects.get(key)
        service_name = "{}-getir".format(un_camel(self.model_class.__name__, dash='-'))
        service = TcknService(service_name=service_name,
                              payload={"tckn": str(obj.tckn),
                                       "kullanici_ad": "",
                                       "kullanici_sifre": ""})

        result = service.zato_request()
        hitap_data = filter(lambda x: x['kayit_no'] == obj.kayit_no, json.loads(result))[0]
        if not hitap_data:
            obj.sync = 3
            obj.blocking_delete()
        else:
            for hk, hv in hitap_data.items():
                setattr(obj, hk, hv)
            obj.sync = 1
            obj.blocking_save({'sync': 1})

    def hitap_save(self, key_list):
        """Crud Hitap Kaydet

        Nesneyi kaydeder. Eğer kayıt yeni ise ``sync`` alanını 4,
        mevcut kayıt güncellemesi ise 2 olarak işaretler.

        Hemen ardından zato servisi ile değişikliği bildirir.

        """
        for key in key_list:
            obj = self.model_class.objects.get(key)
            action = 'ekle' if obj.sync == 4 else 'guncelle'
            service_name = "{}-{}".format(un_camel(self.model_class.__name__, dash='-'), action)
            service = HitapService(service_name=service_name,
                                   payload=obj,
                                   auth={"kullanici_ad": "",
                                         "kullanici_sifre": ""})
            try:
                result = service.zato_request()
                obj.kayit_no = result['kayitNo']
                obj.sync = 1
                obj.blocking_save()
            except:
                pass

    def hitap_delete(self, key_list):
        """Crud Hitap Sil

        Nesneyi kaydeder. ``sync`` alanını 3 olarak işaretler.

        Hemen ardından zato servisi ile değişikliği bildirir.

        """

        # signals.crud_pre_delete.send(self, current=self.current, object=self.object)

        for key in key_list:
            obj = self.model_class.objects.get(key)
            # object_data = obj._data
            # obj.sync = 3

            service_name = "{}-sil".format(un_camel(self.model_class.__name__, dash='-'))
            service = HitapService(service_name=service_name,
                                   payload={"tckn": obj.tckn,
                                            "kayit_no": obj.kayit_no},
                                   auth={"kullanici_ad": "",
                                         "kullanici_sifre": ""})
            try:
                service.zato_request()
                obj.sync = 1
                obj.blocking_delete()
                # signals.crud_post_delete.send(self, current=self.current, object_data=object_data)
            except:
                pass

    def hitap_sync(self):
        """Crud Hitap Sync

        Personele ait kayitlari hitap ile sync eder. Zamanlanmis sync islemini
        manuel olarak calistirir.

        """

        # Sync işleminden önce ekleme veya güncelleme işlemlerinden biri yapıldıysa
        # self.current.task_data nın içinde en son işlem yapılan objenin keyi bulunuyor
        # eğer bu obje hitap ile sync işleminde silinirse 404 hatasına sebep oluyor.
        # bu sorunu cozmek için aşağıdaki yöntem uygulanmıştır.

        service_name = "{}-sync".format(un_camel(self.model_class.__name__, dash='-'))
        service = TcknService(service_name=service_name,
                              payload={"tckn": str(self.current.task_data['personel_tckn']),
                                       "meta": {'user': self.current.user_id,
                                                'role': self.current.role_id,
                                                'wf_name': self.current.workflow_name,
                                                'model_name': self.model_class.__name__,
                                                'personel': self.current.task_data['personel_id']},
                                       "index_fields": [('user', 'bin'), ('role', 'bin'),
                                                        ('wf_name', 'bin'), ('model_name', 'bin'),
                                                        ('personel', 'bin')],
                                       "kullanici_ad": "",
                                       "kullanici_sifre": ""})
        service.zato_request()
