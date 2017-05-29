# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext_lazy as __
from datetime import datetime
import hashlib


class FirmaKayitForm(JsonForm):
    """
    Firma ve firma yetkilisi bilgilerinin girileceği form.
    
    """

    class Meta:
        exclude = ['durum', 'Yetkililer']
        title = __(u'Firma Bilgileri')
        help_text = __(u'Lütfen kayıt işlemi için firma ve yetkili bilgilerinizi giriniz.')

    isim = fields.String(__(u"Yetkili Adı"), required=True)
    soyad = fields.String(__(u"Yetkili Soyadı"), required=True)
    k_adi = fields.String(__(u"Yetkili Kullanıcı Adı"), required=True)
    yetkili_e_posta = fields.String(__(u"Yetkili E-Posta"), required=True)
    kaydi_bitir = fields.Button(__(u"Kaydı Bitir"))


class IslemMesajiForm(JsonForm):
    """
    Firma kayıt başvurusu sonrası gösterilecek form.

    """

    class Meta:
        title = __(u'Firma Kaydı İşlem Mesajı')

    tamam = fields.Button(__(u'Tamam'))

    
class BapFirmaKayit(CrudView):
    """
    Firmaların firma bilgileri ve yetkili bilgisini girerek teklif verebilmek 
    için sisteme kayıt olma isteği yapmasını sağlayan iş akışı.
    
    """

    class Meta:
        model = 'BAPFirma'

    def kayit_formu_olustur(self):
        """
        Firma ve firma yetkilisi bilgilerinin girileceği form oluşturulur.        
        
        """
        self.form_out(FirmaKayitForm(self.object, current=self.current))

    def kaydi_bitir(self):
        """
        Formdan gelen bilgilerle firma nesnesi kaydedilir. Durumu, değerlendirme sürecinde anlamına
        gelen 1 yapılır. Yetkili bilgilerinden kullanıcı nesnesi oluşturulur ve firmanın Yetkililer
        list node'una eklenir. Kullanıcı parolasına geçici olarak anlık hashlenmiş string atanır.
        Firmanın onaylanması durumunda, yeni parola üretilerek, geçici parola değiştirilir ve 
        yetkili kişiyle yeni üretilen parola paylaşılarak giriş yapması sağlanır. 

        """
        temp_password = hashlib.sha1(str(datetime.now())).hexdigest()
        form = self.input['form']
        user = User(name=form['isim'], surname=form['soyad'], username=form['k_adi'],
                    e_mail=form['e_posta'], password=temp_password)
        user.blocking_save()
        self.set_form_data_to_object()
        self.object.Yetkililer(yetkili=user)
        self.object.durum = 1
        self.object.blocking_save()

    def islem_mesaji_goster(self):
        """
        Kayıt başvurusunun alındığına dair işlem sonrası mesaj üretilir ve gösterilir. 

        """
        firma_adi = self.input['form']['ad']
        form = IslemMesajiForm(current=self.current)
        form.help_text = __(
            u"%s adlı firmanız için kayıt başvurunuz alınmıştır. Koordinasyon birimi "
            u"değerlendirmesinden sonra başvuru sonucunuz hakkında bilgilendirileceksiniz."
            % firma_adi)
        self.form_out(form)
