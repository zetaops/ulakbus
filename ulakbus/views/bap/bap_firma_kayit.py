# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.exceptions import ObjectDoesNotExist

from ulakbus.models import User, Permission, BAPFirma
from zengine.models import BPMNWorkflow, WFInstance, TaskInvitation
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from datetime import datetime, timedelta
import hashlib
from ulakbus.lib.common import get_temp_password, e_mail_star_formatter
from zengine.lib.catalog_data import catalog_data_manager

vergi_no_msg = "Sistemimizde, girmiş olduğunuz '{}' vergi numarası ile '{}' vergi dairesine ait " \
               "firma kaydı bulunmaktadır. Bu kaydın size ait olduğunu düşünüyorsanız 'Giriş " \
               "Bilgilerimi Hatırlat' diyerek sistemde kayıtlı firma e-postanıza firma ile " \
               "ilgili giriş bilgilerinizi alabilirsiniz. Forma yanlış giriş yapmış iseniz " \
               "'Kayıt Ekranına Geri Dön' seçeneği ile kayıt bilgilerinizi kontrol ederek " \
               "başvurunuzu tekrarlayabilirsiniz."

mevcut_bilgi_msg = "Sistemimizde, girmiş olduğunuz '{}' {} ait kayıt bulunmaktadır. " \
                   "Lütfen bilgilerinizi kontrol ederek tekrar deneyiniz."

hatirlatma_msg = "İyi günler,\n\n{} adlı firmanız için sistem giriş bilgileri hatırlatma " \
                 "isteğinde bulunulmuştur. Yapılan istek ile ilginiz yoksa bu mesajı görmezden " \
                 "geliniz. Tekrarlanması durumunda lütfen bizi haberdar ediniz.\nAşağıdaki " \
                 "yetkili bilgileri sistemimizde firmanıza ait kullanıcı bilgileridir. " \
                 "Parolanızı unuttuysanız kullanıcı adı ile giriş ekranında Parolamı Unuttum " \
                 "seçeneğini kullanarak parolanızı sıfırlayabilirsiniz.\n\n"


class FirmaKayitForm(JsonForm):
    """
    Firma ve firma yetkilisi bilgilerinin girileceği form.

    """

    class Meta:
        exclude = ['durum', 'Yetkililer']
        title = __(u'Firma Bilgileri')
        help_text = __(u"Lütfen kayıt işlemi için firma ve yetkili bilgilerinizi giriniz. "
                       u"Yetkili bilgilerini, değerlendirme sonucunda firmanızın onay alması "
                       u"halinde, giriş yapmanız için oluşturacağımız kullanıcı bilgisi için "
                       u"kullanacağız. Bu yüzden yetkili bilgileri kısmını, firmanızın yetkilisi "
                       u"olan kişi olarak düşünerek doldurunuz.")
        always_blank = False

    isim = fields.String(__(u"Yetkili Adı"), required=True)
    soyad = fields.String(__(u"Yetkili Soyadı"), required=True)
    k_adi = fields.String(__(u"Yetkili Kullanıcı Adı"), required=True)
    yetkili_e_posta = fields.String(__(u"Yetkili E-Posta"), required=True)
    kaydi_bitir = fields.Button(__(u"Kaydı Bitir"))


class VergiBilgileriUyariForm(JsonForm):
    """
    Forma girilen vergi numarası ve vergi dairesinin sistemde bulunması durumunda 
    gösterilecek uyarı formu. 
    
    """

    class Meta:
        title = __(u'Vergi Bilgileri Uyarısı')

    geri_don = fields.Button(__(u"Kayıt Ekranına Geri Dön"), cmd='geri_don')
    hatirlat = fields.Button(__(u"Giriş Bilgilerimi Hatırlat"), cmd='hatirlat')


class HatirlatmaOnayForm(JsonForm):
    """
    Hatırlatma e-postası gönderilmeden önce onay alınmasında kullanılan form.

    """

    class Meta:
        title = __(u"Giriş Bilgileri Hatırlatma E-Postası Onayı")

    geri_don = fields.Button(__(u"Kayıt Ekranına Geri Dön"), cmd='geri_don')
    onayla = fields.Button(__(u"Onayla"), cmd='onayla')


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

    def kayit_uygunlugu_kontrol(self):
        """
        Formda girilen vergi numarası, vergi dairesi, e-posta, kullanıcı adı gibi bilgilerin 
        sistemde bulunup bulunmaması kontrolleri yapılır.
        
        """
        data = self.current.task_data
        form = self.input['form']
        data['uygunluk'], data['hata_msg'], data['field'] = self.uygunluk_kontrolleri(form)

    def uyari_mesaji_hazirla(self):
        """
        Uyarı verilen form alanı için uyarı mesajı hazırlanır. Form ekranına geri dönüldüğünde 
        uyarı mesajı gösterilir.
        
        """
        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'Mevcut Bilgi Uyarısı'),
            "msg": _(u'{}'.format(self.current.task_data['hata_msg']))}

    def ilgili_form_alanini_temizle(self):
        """
        Form ekranına geri dönüşte, uyarı verilen form alanının boş gelmesini sağlar. 
        
        """
        for field in self.current.task_data['field']:
            self.current.task_data['FirmaKayitForm'][field] = None

    def vergi_bilgileri_uyari_formu_goster(self):
        """
        Formda girilen vergi numarası ve vergi dairesinin sistemde bulunması durumunda 
        uyarı formu gösterilir. 
        
        """
        form = VergiBilgileriUyariForm(current=self.current)
        form.help_text = _(u"{}".format(self.current.task_data['hata_msg']))
        self.form_out(form)

    def hatirlatma_e_postasi_onayi(self):
        """
        Firma sisteme daha önceden kayıt yaptırmış ise, giriş bilgilerimi hatırlat seçeneğini 
        seçebilir. Bu durumda hatırlatma e-postası gönderimi öncesi onay alınır. 
        
        """
        firma = BAPFirma.objects.get(self.current.task_data['firma_key'])
        self.current.task_data['e_posta'] = firma.e_posta
        self.current.task_data['format_e_posta'] = e_mail_star_formatter(firma.e_posta)

        form = HatirlatmaOnayForm(current=self.current)
        form.help_text = _(u"'{}' firma e-posta adresine, yetkili giriş bilgilerini "
                           u"hatırlatma e-postası yollanacaktır. Bu işlemi onaylıyor "
                           u"musunuz?".format(self.current.task_data['format_e_posta']))

        # markdowndan dolayi * \* ile yerdeğiştirildi.
        form.help_text = form.help_text.replace('*', '\*')

        self.form_out(form)

    def hatirlatma_e_postasi_hazirla(self):
        """
        Veritabanında kayıtlı firmanın e-posta adresine gönderilecek hatırlatma e-postası 
        hazırlanır.
         
        """
        firma = BAPFirma.objects.get(self.current.task_data['firma_key'])
        firma_msg = hatirlatma_msg.format(firma.ad)

        yetkili_bilgisi = "Yetkililer:\n\n"
        for yetkili in firma.Yetkililer:
            kullanici = yetkili.yetkili
            yetkili_bilgisi += "Kullanıcı Adı: {}\nE-Posta: {}\n\n".format(kullanici.username,
                                                                           kullanici.e_mail)

        self.current.task_data["message"] = "{}{}".format(firma_msg, yetkili_bilgisi)
        self.current.task_data['subject'] = 'Ulakbüs BAP Giriş Bilgileri Hatırlatma'

    def e_posta_gonderimi_bilgilendir(self):
        """
        Hatırlatma e-postası gönderimi hakkında bilgilendirme mesajı gösterilir.
        
        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Giriş Bilgileri Hatırlatma E-Posta Gönderimi'),
            "msg": _(u'{} e-posta adresine firmanıza kayıtlı yetkili giriş bilgileri başarıyla '
                     u'gönderilmiştir. Lütfen kontrol ediniz.'
                     .format(self.current.task_data['format_e_posta']))}

    def kaydi_bitir(self):
        """
        Formdan gelen bilgilerle firma nesnesi kaydedilir. Durumu, değerlendirme sürecinde anlamına
        gelen 1 yapılır. 
    
        """
        form = self.input['form']
        temp_password = hashlib.sha1(get_temp_password()).hexdigest()
        user = User(name=form['isim'], surname=form['soyad'], username=form['k_adi'],
                    e_mail=form['yetkili_e_posta'], password=temp_password, is_active=False)
        user.blocking_save()
        self.set_form_data_to_object()
        self.object.Yetkililer(yetkili=user)
        self.object.durum = 1
        self.object.save()
        self.current.task_data['firma_key'] = self.object.key

    def davet_gonder(self):
        """
        Firmanın kayıt başvurusunun değerlendirilmesi için koordinasyon birimine davet gönderilir.
    
        """
        wf = BPMNWorkflow.objects.get(name='bap_firma_basvuru_degerlendirme')
        perm = Permission.objects.get('bap_firma_basvuru_degerlendirme')
        sistem_user = User.objects.get(username='sistem_bilgilendirme')
        today = datetime.today()
        for role in perm.get_permitted_roles():
            wfi = WFInstance(
                wf=wf,
                current_actor=role,
                task=None,
                name=wf.name,
                wf_object=self.current.task_data['firma_key']
            )
            wfi.data = dict()
            wfi.data['flow'] = None
            wfi.pool = {}
            wfi.blocking_save()
            role.send_notification(title=_(u"Firma Kayıt Başvurusu"),
                                   message=_(u"%s adlı firma, kayıt başvurusunda bulunmuştur. "
                                             u"Görev yöneticinizden firmaların kayıt başvurularına "
                                             u"ulaşabilir, değerlendirebilirsiniz." %
                                             self.input['form']['ad']),
                                   typ=1,
                                   sender=sistem_user
                                   )
            inv = TaskInvitation(
                instance=wfi,
                role=role,
                wf_name=wfi.wf.name,
                progress=30,
                start_date=today,
                finish_date=today + timedelta(15)
            )
            inv.title = wfi.wf.title
            inv.save()

    def islem_mesaji_goster(self):
        """
        Kayıt başvurusunun alındığına dair işlem sonrası mesaj üretilir ve gösterilir. 
    
        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Firma Kaydı Başarılı'),
            "msg": _(u"""Koordinasyon birimi %s adlı firmanız için yaptığınız kayıt başvurusu hakkında 
            bilgilendirilmiştir. Başvurunuz değerlendirildikten sonra sonucu hakkında
            bilgilendirileceksiniz.""" % self.input['form']['ad'])}

    def uygunluk_kontrolleri(self, form):
        """
        Firma kaydında girilen bilgiler kontrol edilir. Örneğin, formda girilen vergi numarası ve 
        vergi dairesine ait veritabanında kayıt bulunması ya da girilen firma e-postasının 
        sistemde bulunması gibi durumlar kontrol edilir. Bu durumlara özel uyarı mesajları üretilir.
    
    
        Args:
            form(form): Firma kayıt başvurusu formu. 
    
        Returns:
            bool, hata mesajı, hatanın bulunduğu form field listesi
    
        """
        vergi_daireleri = catalog_data_manager.get_all_as_dict('vergi_daireleri')
        vergi_dairesi = vergi_daireleri[form['vergi_dairesi']]

        giris_bilgileri = {
            'vergi_no': (BAPFirma,
                         {'vergi_no': form['vergi_no'], 'vergi_dairesi': form['vergi_dairesi']},
                         vergi_dairesi, 'vergi_dairesi'),
            'e_posta': (BAPFirma, {'e_posta': form['e_posta']}, 'firma e-postasına', ''),
            'k_adi': (User, {'username': form['k_adi']}, 'yetkili kullanıcı adına', ''),
            'yetkili_e_posta': (User, {'e_mail': form['yetkili_e_posta']}, 'yetkili e-postasına', '')}

        for key, bilgiler in giris_bilgileri.items():
            model, query, msg, additional = bilgiler
            try:
                obj = model.objects.get(**query)
                error_msg = vergi_no_msg if key == 'vergi_no' else mevcut_bilgi_msg
                field_list = [key, additional] if key == 'vergi_no' else [key]
                self.current.task_data['vergi_no_hatasi'] = (key == 'vergi_no')
                if self.current.task_data['vergi_no_hatasi']:
                    self.current.task_data['firma_key'] = obj.key
                return False, error_msg.format(form[key], msg), field_list
            except ObjectDoesNotExist:
                pass
        return True, '', ''
