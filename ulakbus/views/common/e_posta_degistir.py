# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from ulakbus.lib.views import UlakbusView
from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.services.zato_wrapper import E_PostaYolla
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.lib.common import aktivasyon_kodu_uret
from ulakbus.lib.common import EPostaDogrulama
from ulakbus.lib.common import e_posta_uygunlugu
from ulakbus.settings import DEMO_URL, MAIL_ADDRESS


class EPostaForm(JsonForm):
    birincil_e_posta = fields.String(__(u"Birincil e-postanız"))


class EPostaDegistir(UlakbusView):
    """
    Kullanıcıların birincil e-posta adreslerini değiştirebilmelerini sağlar,
    bu değişim yapılırken kullanıcıdan yeni belirlediği e-posta adresini doğrulaması
    istenir.
    """

    def yeni_e_posta_girisi(self):
        """
        Kullanıcının birincil e_posta değişikliğini yapabileceği ekran oluşturulur
        ve birincil olarak belirlemek istediği e_posta adresini girmesi istenir.
        Bu işlem sonunda girdiği adrese doğrulama linki gönderilecektir.

        """
        if self.current.task_data.get('msg', None):
            self.mesaj_kutusu_goster(_(u'Geçersiz E-Posta Adresi'))

        self.current.task_data['deneme_sayisi'] = 3
        _form = EPostaForm(current=self.current, title=_(u'Yeni E-Posta Girişi'))
        _form.help_text = _(u"""Birincil olarak belirlemek istediğiniz e-posta adresinize
                          doğrulama linki gönderilecektir.""")
        _form.birincil_e_posta = self.current.user.e_mail
        _form.e_posta = fields.String(
            _(u"Birincil olarak belirlemek istediğiniz e-posta adresinizi yazınız."))
        _form.degistir = fields.Button(_(u"Doğrulama Linki Yolla"))
        self.form_out(_form)

    def e_posta_bilgisi_kontrol(self):
        """
        Girilen e-posta adresinin doğruluğu belirlenen kalıpla kontrol edilir.
        """
        self.current.task_data["e_posta"] = self.input['form']['e_posta']
        self.current.task_data['uygunluk'] = e_posta_uygunlugu(self.current.task_data["e_posta"])
        self.current.task_data['msg'] = _(u"""Girmiş olduğunuz e-posta adresi geçersizdir.
                                        Lütfen düzelterek tekrar deneyiniz.""")

    def e_posta_bilgisi_cache_koy_e_posta_hazirla(self):
        """
        Doğrulama linki gönderilecek e_posta adresi, oluşturulan aktivasyon kodu
        ile cache'e kaydedilir. Gönderilecek e-postanın içeriği ve linki wf ismi
        ve aktivasyon kodu ile hazırlanır.
        """
        self.current.task_data['msg'] = None
        self.current.task_data["aktivasyon"] = aktivasyon_kodu_uret()
        EPostaDogrulama(self.current.task_data["aktivasyon"]).set(self.current.task_data["e_posta"],
                                                                  7200)
        self.current.task_data["message"] = "E-Posta adresinizi doğrulamak için aşağıdaki linke" \
                                            " tıklayınız:\n\n %s/#/%s/dogrulama=%s" % (
        DEMO_URL, self.current.task_data['wf_name'], self.current.task_data["aktivasyon"])
        self.current.task_data['subject'] = 'Ulakbüs Aktivasyon Maili'

    def aktivasyon_maili_yolla(self):
        """
        Hashlenmiş 40 karakterli bir aktivasyon kodu üretilir ve cache'e atılır. Zato servisi ile
        kullanıcının yeni olarak belirlediği e_posta adresine doğrulama linki gönderilir.

        """

        posta_gonder = E_PostaYolla(service_payload={
            "default_e_mail": MAIL_ADDRESS,
            "e_posta": self.current.task_data["e_posta"],
            "message": self.current.task_data["message"],
            "subject": self.current.task_data["subject"]})

        posta_gonder.zato_request()

    def link_gonderimi_bilgilendir(self):
        """
        Doğrulama linki yollandığında kullanıcı linkin yollandığına dair bilgilendirilir.

        """
        self.current.task_data['msg'] = _(u"""'%s' adresinize doğrulama linki gönderilmiştir.
        Lütfen e-posta'nızdaki bağlantı linkine tıklayarak e-posta adresinin size ait
        olduğunu doğrulayınız. """) % (self.current.task_data['e_posta'])

        self.mesaj_kutusu_goster('E-Posta Doğrulama', 'info')
