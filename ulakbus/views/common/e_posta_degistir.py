# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.views.crud import CrudView
from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.services.zato_wrapper import E_PostaYolla
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.views.common.profil_sayfasi_goruntuleme import mesaj_goster
from ulakbus.lib.common import aktivasyon_kodu_uret
from ulakbus.lib.common import EPostaDogrulama
import re

e_posta_kalibi = re.compile('[^@]+@[^@]+\.[^@]+')


class EPostaForm(JsonForm):
    birincil_e_posta = fields.String(__(u"Birincil e-postanız"))


class EPostaDegistir(CrudView):
    """
    Kullanıcıların birincil e-posta adreslerini değiştirebilmelerini sağlar,
    bu değişim yapılırken kullanıcıdan yeni belirlediği e-posta adresini doğrulaması
    istenir.
    """

    def yeni_e_posta_girisi(self):
        """
        Kullanıcının birincil e_posta değişikliğini yapabileceği ekran oluşturulur ve birincil olarak belirlemek
        istediği e_posta adresini girmesi istenir. Bu işlem sonunda girdiği adrese doğrulama linki gönderilecektir.

        """
        try:
            if self.current.task_data['msg']:
                mesaj_goster(self, _(u'Geçersiz E-Posta Adresi'))
        except KeyError:
            pass

        self.current.task_data['deneme_sayisi'] = 3
        _form = EPostaForm(current=self.current, title=_(u'Yeni E-Posta Girişi'))
        _form.help_text = _(u"""Birincil olarak belirlemek istediğiniz e-posta adresinize
                          doğrulama linki gönderilecektir.""")
        _form.birincil_e_posta = self.current.user.e_mail
        _form.e_posta = fields.String(_(u"Birincil olarak belirlemek istediğiniz e-posta adresinizi yazınız."))
        _form.degistir = fields.Button(_(u"Doğrulama Linki Yolla"))
        self.form_out(_form)

    def e_posta_bilgisi_kontrol(self):
        """
        Girilen e-posta adresinin doğruluğu belirlenen kalıpla kontrol edilir.
        """
        self.current.task_data['uygunluk'] = True
        self.current.task_data["e_posta"] = self.input['form']['e_posta']
        if not e_posta_kalibi.search(self.current.task_data["e_posta"]):
            self.current.task_data['uygunluk'] = False
            self.current.task_data['msg'] = _(u"""Girmiş olduğunuz e-posta adresi geçersizdir.
                                            Lütfen düzelterek tekrar deneyiniz.""")

    def e_posta_bilgisini_kaydet(self):
        """
        Doğrulama linki gönderilecek e_posta adresi, oluşturulan aktivasyon kodu ile cache'e kaydedilir.
        Gönderilecek e-postanın içeriği ve linki wf ismi ve aktivasyon kodu ile hazırlanır.
        """

        self.current.task_data["aktivasyon"] = aktivasyon_kodu_uret()
        EPostaDogrulama(self.current.task_data["aktivasyon"]).set(self.current.task_data["e_posta"], 7200)
        self.current.task_data["message"] = 'http://dev.zetaops.io/#/%s/dogrulama=%s' \
                                            % (self.current.task_data['wf_name'],
                                               self.current.task_data["aktivasyon"])

    def aktivasyon_maili_yolla(self):
        """
        Hashlenmiş 40 karakterli bir aktivasyon kodu üretilir ve cache'e atılır. Zato servisi ile
        kullanıcının yeni olarak belirlediği e_posta adresine doğrulama linki gönderilir.

        """

        posta_gonder = E_PostaYolla(service_payload={
            "e_posta": self.current.task_data["e_posta"],
            "message": self.current.task_data["message"]})

        posta_gonder.zato_request()

    def link_gonderimi_bilgilendir(self):
        """
        Doğrulama linki yollandığında kullanıcı linkin yollandığına dair bilgilendirilir.

        """
        self.current.task_data['msg'] = _(u"""'%s' adresinize doğrulama linki gönderilmiştir.
        Lütfen e-posta'nızdaki bağlantı linkine tıklayarak e-posta adresinin size ait
        olduğunu doğrulayınız. """) % (self.current.task_data['e_posta'])

        mesaj_goster(self, 'E-Posta Doğrulama', 'info')
