# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.services.zato_wrapper import ZatoService
from ulakbus.models import Role, AbstractRole
from zengine.models import WFInstance
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.settings import MAIL_ADDRESS, DATE_DEFAULT_FORMAT
from ulakbus.lib.common import get_file_url, get_temp_password
from collections import OrderedDict


class BasvuruDegerlendirForm(JsonForm):
    """
    Başvuruların değerlendirildiği form.

    """
    belge_indir = fields.Button(__(u"Faaliyet Belgesi İndir"), cmd='indir')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class KararOnaylamaForm(JsonForm):
    """
    Karar Onaylama ekranı formu.
    
    """
    onayla = fields.Button(__(u"Onayla"), cmd='onayla')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class RedGerekceForm(JsonForm):
    """
    Başvuru reddi gerekçesi formu.

    """
    gerekce = fields.Text(__(u"Red Gerekçesi"), required=True)
    gonder = fields.Button(__(u"Gerekçe Gönder"), cmd='gonder')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don', form_validation=False)


class KararVerForm(JsonForm):
    """
    Karar Verme ekranı formu.

    """
    onayla = fields.Button(__(u"Onayla"), cmd='onayla')
    red = fields.Button(__(u"Red"), cmd='red')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class BapFirmaBasvuruDegerlendirme(CrudView):
    """
    Koordinasyon biriminin, firma başvurularını değerlendirmesini sağlayan iş akışı.

    """

    class Meta:
        model = 'BAPFirma'

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.ListForm.add = None
        self.model_class.Meta.verbose_name_plural = __(u"Firma Başvuru Değerlendirmeleri")

    def incele(self):
        """
        Firma kayıt başvurusu incelenir.

        """
        yetkili = self.object.Yetkililer[0].yetkili
        firma_bilgileri = OrderedDict([
            ('Firma Adı', self.object.ad),
            ('Telefon', self.object.telefon),
            ('E-Posta', str(self.object.e_posta)),
            ('Vergi No', self.object.vergi_no),
            ('Vergi Dairesi', self.object.get_vergi_dairesi_display()),
            ('Faaliyet Belgesi Veriliş Tarihi',
             self.object.faaliyet_belgesi_verilis_tarihi.strftime(DATE_DEFAULT_FORMAT)),
            ('Firma Yetkilisi Adı', yetkili.name),
            ('Firma Yetkilisi Soyadı', yetkili.surname),
            ('Firma Yetkilisi E-Posta', yetkili.e_mail),
        ])
        self.output['object'] = firma_bilgileri

        form = BasvuruDegerlendirForm(current=self.current)
        form.title = _(u"%s Firması Kayıt Başvurusu Değerlendirme") % self.object.ad
        self.form_out(form)

    def belge_indir(self):
        """
        Firma faaliyet belgesi indirilir.

        """
        self.set_client_cmd('download')
        self.current.output['download_url'] = get_file_url(self.object.faaliyet_belgesi)

    def karar_ver(self):
        """
        Koordinasyon birimi başvuru hakkında karar verir.

        """
        self.current.task_data["firma_key"] = self.object.key
        self.current.task_data["firma_ad"] = self.object.ad
        form = KararVerForm(current=self.current)
        form.title = _(u"%s Firması Başvuru Değerlendirme Kararı") % self.object.ad
        form.help_text = _(u"Lütfen %s firması kayıt başvurusu hakkında değerlendirme kararınızı"
                           u" veriniz.") % self.current.task_data["firma_ad"]
        self.form_out(form)

    def kabul_onaylama(self):
        """
        Kararın, firmanın başvurusunun kabulü yönünde olmasının onayı alınır.

        """
        form = KararOnaylamaForm(current=self.current)
        form.title = _(u"%s Firması Başvuru Kabulü") % self.current.task_data["firma_ad"]
        form.help_text = _(u"""%s adlı firmanın kayıt başvurusunu kabul etmek üzeresiniz. Bu işlemi
        onaylıyor musunuz?""") % self.current.task_data["firma_ad"]
        self.form_out(form)

    def red_gerekcesi_yaz(self):
        """
        Karar başvurunun reddi ise, reddedilme gerekçesi yazılması istenir.

        """
        form = RedGerekceForm(current=self.current)
        form.title = _(u"%s Firması Başvuru Reddi Gerekçesi") % self.current.task_data["firma_ad"]
        form.help_text = _(u"""Lütfen %s adlı firmanın kayıt başvurusu reddi hakkında gerekçe
        belirtiniz.""") % self.current.task_data["firma_ad"]
        self.form_out(form)

    def red_onaylama(self):
        """
        Kararın, firmanın başvurusunun reddi yönünde olmasının onayı alınır.

        """
        form = KararOnaylamaForm(current=self.current)
        form.title = _(u"%s Firması Başvuru Reddi") % self.current.task_data["firma_ad"]
        form.help_text = _(u"""%s adlı firmanın kayıt başvurusunu reddetmek üzeresiniz. Bu işlemi
        onaylıyor musunuz?""") % self.current.task_data["firma_ad"]
        self.form_out(form)

    def kullanici_aktiflestir(self):
        """
        Eğer karar firmanın kabulü yönünde ise, firma yetkilisi kullanıcısı aktif hale getirilir.

        """
        kullanici = self.object.Yetkililer[0].yetkili
        kullanici.is_active = True
        kullanici.blocking_save()
        abs_role = AbstractRole.objects.get('FIRMA_YETKILISI')
        role = Role(user=kullanici, abstract_role=abs_role, typ=3)
        role.blocking_save()
        role.add_permission_by_name('bap_firma_teklif', True)

    def onay_e_posta_icerik_hazirla(self):
        """
        Firma yetkilisine gönderilecek onay mesajı içeriği hazırlanır. Firmanın durumu onaylandı 
        anlamına gelen 2 yapılır. Geçici parola üretilerek, firma yetkilisi kullanıcısının parolası 
        geçici parola ile değiştirilir, e-posta içeriğine eklenir. Böylelikle kullanıcı bu parola 
        ile sisteme giriş yapabilir duruma gelecektir.

        """
        self.object.durum = 2
        self.object.blocking_save({'durum': 2})
        kullanici = self.object.Yetkililer[0].yetkili
        gecici_parola = get_temp_password()
        kullanici.password = gecici_parola
        kullanici.blocking_save()
        yetkili_onay_msg = "İyi günler.\n\n%s adlı firmanızın kayıt başvurusu tarafımızdan " \
                           "onaylanmıştır. Aşağıdaki giriş bilgilerini kullanarak sisteme giriş " \
                           "yapabilirsiniz." \
                           "\n\nKullanıcı Adı: '%s'\nParola: '%s'" % \
                           (self.current.task_data["firma_ad"],
                            kullanici.username, gecici_parola)

        self.e_posta_yolla(yetkili_onay_msg, kullanici.e_mail)

        firma_onay_msg = "İyi günler.\n\n%s adlı firmanızın kayıt başvurusu tarafımızdan " \
                         "onaylanmıştır. Sisteme giriş yapabilmeniz için gereken bilgiler " \
                         "firma yetkilisinin e-postasına gönderilmiştir." % self.current.task_data[
                             "firma_ad"]

        self.e_posta_yolla(firma_onay_msg, self.object.e_posta)

    def red_e_posta_icerik_hazirla(self):
        """
        Karar başvurunun reddi yönünde ise, firma başvurusu silinir ve yetkiliye başvuru reddi 
        hakkında gönderilecek e-postanın içeriği hazırlanır. Koordinasyon biriminin başvuruyu
        reddetme gerekçesi de içeriğe eklenir. 

        """
        kullanici = self.object.Yetkililer[0].yetkili
        red_msg = "İyi günler.\n\n%s adlı firmanızın kayıt başvurusu tarafımızdan " \
                  "reddedilmiştir. Reddedilme gerekçesinde belirtilen kriterleri düzeltip " \
                  "sisteme tekrardan kayıt başvurusu yapabilirsiniz.\n\nReddedilme Gerekçesi: " \
                  "%s" % (self.current.task_data["firma_ad"],
                          self.current.task_data['RedGerekceForm']['gerekce'])
        self.e_posta_yolla(red_msg, self.object.e_posta)
        self.e_posta_yolla(red_msg, kullanici.e_mail)
        kullanici.blocking_delete()
        self.object.blocking_delete()
        del self.current.task_data['object_id']

    def e_posta_yolla(self, msg, e_posta):
        """
        Firma yetkilisine karar hakkında e-posta gönderilir.        
        
        """
        posta_gonder = ZatoService(service_name='e-posta-yolla',
                                   payload={"default_e_mail": MAIL_ADDRESS,
                                            "e_posta": e_posta,
                                            "message": msg,
                                            "subject": _(
                                                u"Firma Kayıt Başvurusu Değerlendirme Sonucu")})

        posta_gonder.zato_request()

    def islem_mesaji_olustur(self):
        """
        İşlem bitiminde, işlem mesajı oluşturulur ve gösterilir.        
        
        """
        self.ilgili_daveti_sil()
        self.current.output['msgbox'] = {"type": "info",
                                         "title": _(u"Firma Başvuru Kaydı Değerlendirme"),
                                         "msg": _(u"""%s adlı firmanın kayıt başvurusu hakkındaki
                                            kararınız firma yetkilisine başarıyla iletilmiştir.
                                            """ % self.current.task_data["firma_ad"])}

    def ilgili_daveti_sil(self):
        try:
            instance = WFInstance.objects.get(current_actor=self.current.role,
                                              name=self.current.workflow_name,
                                              wf_object=self.current.task_data["firma_key"])
            davet = instance.task_invitation_set[0].task_invitation
            davet.blocking_delete()
        except:
            pass

    @obj_filter
    def firma_degerlendirme_actions(self, obj, result):
        """
        Firma başvuruları için, karar verme ve inceleme action buttonları oluşturulur.

        """
        result['actions'] = [
            {'name': _(u'Karar Ver'), 'cmd': 'karar_ver', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'İncele'), 'cmd': 'incele', 'mode': 'normal', 'show_as': 'button'}
        ]

    @list_query
    def degerlendirilmemis_firmalari_listele(self, queryset):
        """
        Durumu 1 olan yani değerlendirmeye alınmamış firma kayıt başvuruları listelenir.

        """
        return queryset.filter(durum=1)
