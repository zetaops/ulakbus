# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User, IntegrityError
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
        help_text = __(u"""Lütfen kayıt işlemi için firma ve yetkili bilgilerinizi giriniz. 
        Yetkili bilgilerini, değerlendirme sonucunda firmanızın onay alması halinde, giriş yapmanız 
        için oluşturacağımız kullanıcı bilgisi için kullanacağız. Bu yüzden yetkili bilgileri 
        kısmını, firmanızın yetkilisi olan kişi olarak düşünerek doldurunuz.""")
        always_blank = False

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

    def kullanici_uygunlugu_kontrol(self):
        """
        Yetkili bilgilerinden kullanıcı nesnesi oluşturulur ve kaydedilmeye çalışılır. Eğer formdan
        gelen kullanıcı adı bilgisi veya e-posta bilgisi veritabanında bulunuyorsa kaydetme işlemi
        gerçekleşmez. Eğer gelen bilgiler kurallara uygunsa geçici yaratılan bir şifreyle kullanıcı
        kaydedilir.

        Returns:
            user(obj): formdan gelen datalarla kaydedilen user nesnesi
            False or True: eğer kaydetme işlemi olmuş ise True hata oluşmuşsa False döndürülür

        """
        temp_password = hashlib.sha1(str(datetime.now())).hexdigest()
        form = self.input['form']
        user = User(name=form['isim'], surname=form['soyad'], username=form['k_adi'],
                    e_mail=form['yetkili_e_posta'], password=temp_password)

        self.current.task_data['uygunluk'] = True
        try:
            self.current.task_data['user_key'] = user.save().key
        except IntegrityError as e:
            error, field_name = ('kullanıcı adı', 'k_adi') if 'username' in e.message else (
                'e-posta', 'yetkili_e_posta')
            self.current.task_data['FirmaKayitForm'][field_name] = None
            self.current.task_data['error'] = error
            self.current.task_data['uygunluk'] = False

    def kaydi_bitir(self):
        """
        Formdan gelen bilgilerle firma nesnesi kaydedilir. Durumu, değerlendirme sürecinde anlamına
        gelen 1 yapılır. 

        """
        user = User.objects.get(self.current.task_data['user_key'])
        self.set_form_data_to_object()
        self.object.Yetkililer(yetkili=user)
        self.object.durum = 1
        self.object.blocking_save()

    def islem_mesaji_goster(self):
        """
        Kayıt başvurusunun alındığına dair işlem sonrası mesaj üretilir ve gösterilir. 

        """
        form = IslemMesajiForm(current=self.current)
        form.help_text = __(
            u"%s adlı firmanız için kayıt başvurunuz alınmıştır. Koordinasyon birimi "
            u"değerlendirmesinden sonra başvuru sonucunuz hakkında bilgilendirileceksiniz."
            % self.input['form']['ad'])
        self.form_out(form)

    def hata_mesaji_olustur(self):
        """
        Formda girilen kullanıcı adı ya da e-posta adresinin unique 
        olmaması halinde uyarı mesajı üretilir. 

        """
        error = self.current.task_data['error']
        self.current.output['msgbox'] = {"type": "warning",
                                         "title": __(u'Mevcut Bilgi Uyarısı'),
                                         "msg": __(u"""Girmiş olduğunuz yetkili %s bilgisi, 
                                         sistemimizde bulunmaktadır. Lütfen başka bir %s ile 
                                         değiştirerek tekrar deneyiniz.""" % (error, error))}
