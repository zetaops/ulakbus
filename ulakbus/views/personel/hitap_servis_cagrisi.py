# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.modelmeta import model_registry

from ulakbus.lib.cache import HitapPersonelGirisBilgileri
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _


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
    def __init__(self, current=None):
        CrudView.__init__(self, current)
        if 'model_name' in self.current.task_data:
            self.model_class = model_registry.get_model(self.current.task_data['model_name'])
            del self.current.task_data['model_name']

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
