# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje, User
from zengine.forms import JsonForm
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import fields

from pyoko import field


class ProjeDegerlendirmeForm(JsonForm):
    class Meta:
        title = _(u"Bilimsel Araştırma Projesi (BAP) Proje Başvuru Değerlendirme Formu")
        always_blank = False

        grouping = [
            {
                "layout": "6",
                "groups": [
                    {

                        "items": ['arastirma_kapsam_tutar', 'arastirma_kapsam_tutar_gerekce',
                                  'literatur_ozeti', 'literatur_ozeti_gerekce', 'ozgun_deger',
                                  'ozgun_deger_gerekce', 'yontem_amac_tutar',
                                  'yontem_amac_tutar_gerekce', 'yontem_uygulanabilirlik',
                                  'yontem_uygulanabilirlik_gerekce']

                    }
                ]
            },
            {
                "layout": "6",
                "groups": [
                    {

                        "items": ['katki_beklenti', 'katki_beklenti_gerekce',
                                  'bilim_endustri_katki', 'bilim_endustri_katki_gerekce',
                                  'arastirmaci_bilgi_yeterlilik',
                                  'arastirmaci_bilgi_yeterlilik_gerekce',
                                  'butce_gorus_oneri', 'basari_olcut_gercek',
                                  'basari_olcut_gercek_gerekce', 'proje_gorus_oneri']
                    }
                ]
            },
            {
                "layout": "12",
                "groups": [
                    {

                        "items": ['proje_degerlendirme_sonucu']
                    }
                ]
            }
        ]

    arastirma_kapsam_tutar = field.Integer(_(u"ARAŞTIRMA KAPSAMININ PROJE AMACI İLE TUTARLILIĞI"),
                                           choices='bap_proje_degerlendirme_secenekler',
                                           default=1)
    arastirma_kapsam_tutar_gerekce = field.Text(_(u"Gerekçe-Açıklama"), required=False)

    literatur_ozeti = field.Integer(
        _(u"VERİLEN LİTERATÜR ÖZETİNİN PROJEYE UYGUNLUĞU VE YETERLİLİĞİ"),
        choices='bap_proje_degerlendirme_secenekler', default=1)

    literatur_ozeti_gerekce = field.Text(_(u"Gerekçe-Açıklama"), required=False)

    ozgun_deger = field.Integer(_(u"PROJENİN ÖZGÜN DEĞERİ"),
                                choices='bap_proje_degerlendirme_secenekler', default=1)

    ozgun_deger_gerekce = field.Text(_(u"Gerekçe-Açıklama"), required=False)

    yontem_amac_tutar = field.Integer(_(u"ÖNERİLEN YÖNTEMİN PROJE AMACI İLE TUTARLILIĞI"),
                                      choices='bap_proje_degerlendirme_secenekler', default=1)

    yontem_amac_tutar_gerekce = field.Text(_(u"Gerekçe-Açıklama"), required=False)

    yontem_uygulanabilirlik = field.Integer(_(u"ÖNERİLEN YÖNTEMİN UYGULANABİLİRLİĞİ"),
                                            choices='bap_proje_degerlendirme_secenekler', default=1)

    yontem_uygulanabilirlik_gerekce = field.Text(_(u"Gerekçe-Açıklama"), required=False)

    basari_olcut_gercek = field.Integer(_(u"BAŞARI ÖLÇÜTLERİNİN GERÇEKÇİLİĞİ"),
                                        choices='bap_proje_degerlendirme_secenekler', default=1)

    basari_olcut_gercek_gerekce = field.Text(_(u"Gerekçe-Açıklama"), required=False)

    katki_beklenti = field.Integer(_(u"PROJE İLE SAĞLANACAK KATKILARA İLİŞKİN BEKLENTİLER"),
                                   choices='bap_proje_degerlendirme_secenekler', default=1)

    katki_beklenti_gerekce = field.Text(_(u"Gerekçe-Açıklama"), required=False)

    bilim_endustri_katki = field.Integer(
        _(u"ARAŞTIRMA SONUÇLARININ BİLİME VE/VEYA ÜLKE ENDÜSTRİSİNE KATKISI"),
        choices='bap_proje_degerlendirme_secenekler', default=1)

    bilim_endustri_katki_gerekce = field.Text(_(u"Gerekçe-Açıklama"), required=False)

    arastirmaci_bilgi_yeterlilik = field.Integer(
        _(u"ARAŞTIRMACILARIN BİLGİ VE DENEYİM BİRİKİMİNİN YETERLİLİĞİ"),
        choices='bap_proje_degerlendirme_secenekler', default=1)

    arastirmaci_bilgi_yeterlilik_gerekce = field.Text(_(u"Gerekçe-Açıklama"), required=False)

    butce_gorus_oneri = field.Text(
        _(u"PROJENİN BÜTÇESİ VE UYGUNLUĞUNA İLİŞKİN GÖRÜŞ VE ÖNERİLERİNİZ"))

    proje_gorus_oneri = field.Text(
        _(u"PROJE İLE İLGİLİ UYARI VE ÖNERİLERİNİZ"))

    proje_degerlendirme_sonucu = field.Integer(
        _(u"DEĞERLENDİRME SONUCUNUZ"), choices='bap_proje_degerlendirme_sonuc', default=1)

    incelemeye_don = fields.Button(_(u"İncelemeye Dön"), cmd='incelemeye_don',
                                   form_validation=False)
    degerlendirme_kaydet = fields.Button(_(u"Değerlendirme Kaydet"), cmd='kaydet')



class ProjeDegerlendirme(CrudView):
    """
        Proje hakemlerinin projeyi degerlendirirken kullanacagi is akisidir.
    """
    class Meta:
        model = "BAPProje"

    def proje_degerlendirme_karari_sor(self):
        """
            Hakemlik daveti gönderilen hakem adayına proje hakemlik daveti kararını soran
             adımdır. Hakem adayı proje özetini görüntüleyebilir, hakemlik davetini kabul ya da
             reddedebilir.
        """
        form = JsonForm(title=_(u"""%s Tarafından Gönderilen Hakemlik Daveti""" %
                                User.objects.get(self.current.task_data['davet_gonderen'])))
        form.help_text = _(u"""Proje özetini inceleyebilir, hakemlik davetini kabul edebilir ya da
        geri çevirebilirsiniz.""")
        form.ozet_incele = fields.Button(_(u"Proje Özeti İncele"), cmd='ozet_incele')
        form.davet_red = fields.Button(_(u"Hakemlik Davetini Reddet"), cmd='davet_red')
        form.davet_kabul = fields.Button(_(u"Hakemlik Davetini Kabul Et"), cmd='davet_kabul')
        self.form_out(form)

    def proje_ozet_goruntule(self):
        """
            Hakem adayına proje özetinin gösterildiği adımdır.
        """
        self.object = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.show()
        form = JsonForm()
        form.geri = fields.Button(_(u"Geri"))
        self.form_out(form)

    def red_bildirimi(self):
        """
            Hakem adayı hakemlik davetini reddederse, projenin ProjeDegerlendirmeleri ListNode'unda
              hakem adayına karşılık gelen alanın degerlendirme durumu 'Hakemlik Daveti Reddedildi'
              (4) olarak kaydedilir. Daveti gönderen kullanıcıya davetin reddedildiği bildirilir.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        for degerlendirme in proje.ProjeDegerlendirmeleri:
            if degerlendirme.hakem().okutman().user().key == self.current.user_id:
                degerlendirme.hakem_degerlendirme_durumu = 4
        proje.blocking_save()
        role = User.objects.get(self.current.task_data['davet_gonderen']).role_set[0].role
        role.send_notification(title=_(u"Proje Hakemlik Daveti Yanıtı"),
                               message=_(u"""%s adlı projeyi değerlendirmek üzere %s adlı hakem
                               adayına gönderdiğiniz davet reddedilmiştir. Proje listeleme adımından
                               hakemlik daveti butonuna tıklayarak yeniden davet gönderebilirsiniz.
                               """ % (proje.ad, self.current.user)),
                               typ=1,
                               sender=self.current.user
                               )

    def kabul_durum_degistir(self):
        """
            Hakem adayı hakemlik davetini kabul ederse, projenin ProjeDegerlendirmeleri
            ListNode'unda hakem adayına karşılık gelen alanın degerlendirme durumu 'Hakemlik Daveti
            Kabul Edildi' (3) olarak kaydedilir. Daveti gönderen kullanıcıya davetin kabul edildiği
            bildirilir.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        for degerlendirme in proje.ProjeDegerlendirmeleri:
            if degerlendirme.hakem().okutman().user().key == self.current.user_id:
                degerlendirme.hakem_degerlendirme_durumu = 3
        proje.blocking_save()
        role = User.objects.get(self.current.task_data['davet_gonderen']).role_set[0].role
        role.send_notification(title=_(u"Proje Hakemlik Daveti Yanıtı"),
                               message=_(u"""%s adlı projeyi değerlendirmek üzere %s adlı hakem
                                       adayına gönderdiğiniz davet kabul edilmiştir. Değerlendirme
                                       tamamlandığında tarafınıza bildirim yapılacaktır.
                                       """ % (proje.ad, self.current.user)),
                               typ=1,
                               sender=self.current.user
                               )

    def yonlendir(self):
        self.current.output['cmd'] = 'reload'

    def proje_degerlendir(self):
        """
            Hakem adayının projeyi değerlendireceği formu gösterir. Form doldurulup submit
            edildiğinde bir sonraki adımda kayıt gerçekleştirilir. Eğer hakem adayı proje inceleme
            adımına dönüp tekrar form adımına gelirse, form bıraktığı şekilde yeniden gösterilir.
        """
        form = ProjeDegerlendirmeForm(current=self.current)
        self.form_out(form)

    def degerlendirme_kaydet(self):
        """
            Hakem adayının doldurduğu formu, aynı hakem adayının değerlendirmesi olarak projeye
             kaydeder.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form = self.input['form']
        if 'incelemeye_don' in form and 'degerlendirme_kaydet' in form:
            del form['incelemeye_don']
            del form['degerlendirme_kaydet']
        for degerlendirme in proje.ProjeDegerlendirmeleri:
            if degerlendirme.hakem().okutman().user().key == self.current.user_id:
                degerlendirme.hakem_degerlendirme_durumu = 5
                degerlendirme.degerlendirme_sonucu = form['proje_degerlendirme_sonucu']
                if form['proje_degerlendirme_sonucu'] == 1:
                    deger_durum = _(u"Olumlu/Proje Desteklenmelidir")
                else:
                    deger_durum = _(u"Olumsuz/Proje Desteklenmemelidir")
                self.current.task_data['deger_durum'] = deger_durum
                degerlendirme.form_data = form
        proje.blocking_save()

    def degerlendirildi_bildirimi(self):
        """
            Hakem adayı değerlendirmesi kaydedildikten sonra koordinasyon birimine proje
             değerlendirildi bildirimi gönderilir. Değerlendirme sonucu da bildirim içinde
             gösterilir.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        role = User.objects.get(self.current.task_data['davet_gonderen']).role_set[0].role
        deger_durum = self.current.task_data['deger_durum']
        role.send_notification(title=_(u"Proje Değerlendirme Sonucu"),
                               message=_(u"""%s adlı proje %s adlı hakem adayı tarafından
                               değerlendirilmiştir. Projenin değerlendirme sonucu '%s' olarak
                               belirtilmiştir.""" % (proje.ad, self.current.user, deger_durum)),
                               typ=1,
                               sender=self.current.user
                               )

    def red_mesaji_goster(self):
        """
            Hakem adayına proje davetini reddettiğine dair mesaj gösterir. Tamam butonuna
            basıldıktan sonra iş akışı tamamlanır ve anasayfaya yöndlendirilir.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        user = User.objects.get(self.current.task_data['davet_gonderen'])
        form = JsonForm(title=_(u"%s Adlı Proje Hakem Daveti Yanıtı" % proje.__unicode__()))
        form.help_text = _(u"""%s adlı proje için gelen hakemlik davetini reddettiniz. %s bu hususta
        bilgilendirildi.""" % (proje.__unicode__(), user))
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def degerlendirildi_mesaji_goster(self):
        """
            Hakem adayına projeyi başarıyla değerlendirdiğine dair mesaj gösterir. Tamam butonuna
            basıldıktan sonra iş akışı tamamlanır ve anasayfaya yöndlendirilir.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        user = User.objects.get(self.current.task_data['davet_gonderen'])
        form = JsonForm(title=_(u"%s Adlı Proje Değerlendirme Sonucu" % proje.__unicode__()))
        form.help_text = _(u"""%s adlı proje değerlendirmeniz başarıyla kaydedildi. %s bu hususta
                bilgilendirildi.""" % (proje.__unicode__(), user))
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def bitir(self):
        self.current.output['cmd'] = 'reload'

