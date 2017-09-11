# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
""" Bap Proje Raporu Modülü

 Bu modül Ulakbüs uygulaması için bap proje raporunun öğretim üyesi tarafından yüklenmesi ve
 koordinasyon birimi tarafından rapora ait kararın verilmesi işlemlerini içerir.

"""
from ulakbus.models import BAPGundem, BAPRapor, BAPProje
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _
from ulakbus.lib.common import get_file_url
import json


class RaporTurForm(JsonForm):
    """
    Projeye ait hangi rapor türünün girileceğinin belirlenmesi işlemini içerir.

    """

    class Meta:
        include = ['tur']
        title = _(u'Lütfen Rapor Türü Seçiniz.')
        always_blank = False

    sec = fields.Button(_(u"Seç"))


class RaporYukleForm(JsonForm):
    """
    Proje raporunun öğretim üyesi tarafından yüklenilmesi işlemini içerir.

    """

    class Meta:
        include = ['belge']
        title = _(u'Lütfen Raporu Ekleyiniz.')

    kaydet = fields.Button(_(u"Kaydet"))


class RevizyonMesaji(JsonForm):
    """
    Revizyon mesajının girilmesi işlemini içerir.

    """
    mesaj = fields.Text(_(u'Revizyon Mesajı'))
    gonder = fields.Button(_(u'Gönder'))


class BapProjeRaporu(CrudView):
    class Meta:
        model = "BAPRapor"

    def rapor_turu_sec(self):
        """
        Seçili olan projenin rapor türünün seçilmesi işlemlerini gerçekleştirir.

        """
        form = RaporTurForm(self.object, current=self.current)
        self.form_out(form)

    def rapor_yukle(self):
        """
        Proje raporunun yükleme ekranı öğretim üyesine gösterilir.

        """
        form = RaporYukleForm(self.object, current=self.current, title="Rapor Yükleme Formu")
        self.form_out(form)

    def rapor_kaydet(self):
        """
        Seçili olan rapor dosyasının veritabanına kaydedilmesi işlemini gerçekleştirir.

        """
        belge = self.input["form"]["belge"]
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        rapor = BAPRapor(proje=proje, belge=belge, durum=1,
                         tur=self.current.task_data['RaporTurForm']['tur'])
        rapor.blocking_save()
        self.current.task_data['rapor'] = {"key": rapor.key,
                                           "ad": self.current.user.name,
                                           "soyad": self.current.user.surname,
                                           "proje": rapor.proje.ad}

    def rapor_gonder_onay(self):
        """
        Seçili olan rapor dosyasının koordinasyon birimine gönderilmesi için öğretim üyesinden onay istenir.

        """
        form = JsonForm(title="Rapor Gönderme Form")
        form.help_text = "Raporunuz başarılı bir şekilde yüklendi. Raporunuzu koordinasyon birimine gönderebilirsiniz."
        form.gonder = fields.Button(_(u'Koordinasyon Birimine Gönder'), cmd="gonder")
        form.geri_don = fields.Button(_(u'Geri Dön'))
        self.form_out(form)

    def rapor_gonder(self):
        """
        Öğretim üyesine raporun koordinasyon birimine gönderildiğine dair bir mesaj gösterir.

        """
        msg = {"title": _(u'Proje Raporu Gönderildi!'),
               "body": _(u'Proje raporunuz koordinasyon birimine başarıyla iletilmiştir. '
                         u'Değerlendirme sürecinde size bilgi verilecektir.')}
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def rapor_goruntule(self):
        """
        Öğretim üyesinin yüklediği raporun koordinasyon birimi tarafından görüntülenmesi işlemini gerçekleştirir.

        """
        ad = self.current.task_data['rapor']['ad']
        soyad = self.current.task_data['rapor']['soyad']
        proje = self.current.task_data['rapor']['proje']
        form = JsonForm(title="Proje Rapor Görüntüleme")
        form.help_text = "%s %s ögretim üyesine ait %s projesinin bilgileri aşağıda yer almaktadır. " \
                         " İndirip inceleyebilirsiniz ya da rapora ait karar işlemlerini gerçekleştirebilirsiniz." \
                         % (ad, soyad, proje)
        form.indir = fields.Button(_(u'İndir'), cmd="indir")
        form.karar = fields.Button(_(u'Karar'), cmd="karar")
        self.form_out(form)

    def rapor_indir(self):
        """
        Koordinasyon birimi tarafından proje raporunun indirilmesi işlemini gerçekleştirir.

        """
        rapor = BAPRapor.objects.get(self.current.task_data['rapor']['key'])
        self.set_client_cmd('download')
        self.current.output['download_url'] = get_file_url(rapor.belge)

    def rapor_karar(self):
        """
        Proje raporu koordinasyon birimine gösterilir. Bap Koordinasyon birimi rapor için
        onaylama,revizyon ve reddetme işlemlerini gerçekleştirir.

        """
        ad = self.current.task_data['rapor']['ad']
        soyad = self.current.task_data['rapor']['soyad']
        proje = self.current.task_data['rapor']['proje']
        form = JsonForm(title="Proje Raporu Karar Formu")
        form.help_text = "%s %s öğretim üyesine ait %s projesinin bilgileri aşağıda yer almaktadır." \
                         " Onaylama,reddetme ya da revizyona alma işlemlerini gerçekleştirebilirsiniz." \
                         % (ad, soyad, proje)
        form.onayla = fields.Button(_(u'Onayla'), cmd="onayla")
        form.red = fields.Button(_(u'Red'), cmd="red")
        form.revizyon = fields.Button(_(u'Revizyon'), cmd="revizyon")
        self.form_out(form)

    def gundeme_al(self):
        """
        Koordinasyon birimi tarafından onaylanan projenin gündeme alınması işlemini gerçekleştirir.
        Rapor nesnesini başarılı durumuna getirme işlemini gerçekleştirir.

        """
        rapor = BAPRapor.objects.get(self.current.task_data['rapor']['key'])
        rapor.durum = 2
        rapor.save()
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        gundem_tipi = 6 if self.current.task_data['RaporTurForm']['tur'] == 1 else 5
        gundem = BAPGundem(gundem_tipi=gundem_tipi,
                           proje=proje,
                           gundem_ekstra_bilgiler=json.dumps({'rapor': rapor.key}))
        gundem.save()
        self.current.user.send_notification(title=_(u"Proje Rapor Yanıtı"),
                                            message=_(u"""%s projenize ait raporunuz koordinasyon birimi
                                                      tarafından kabul edildi.""")
                                                    % (self.current.task_data['rapor']['proje']),
                                            typ=1,
                                            sender=self.current.user)

    def gundeme_al_bilgi(self):
        """
        Proje raporunun gündeme alındığına dair bilgilendirme mesajını koordinasyon birimine gösterir.

        """
        rapor = BAPRapor.objects.get(self.current.task_data['rapor']['key'])
        form = JsonForm(title="Rapor Gündem Bilgi Mesajı")
        form.help_text = "%s adlı rapor başarılı bir şekilde gündeme alınmıştır." % (rapor)
        form.yonlendir = fields.Button(_(u'Anasayfaya Git'))
        self.form_out(form)

    def red_mesaji_gonder(self):
        """
        Koordinasyon birimi tarafından reddedilen rapora dair öğretim üyesine mesaj gönderir.
        Rapor nesnesini başarısız durumuna getirme işlemini gerçekleştirir.

        """
        rapor = BAPRapor.objects.get(self.current.task_data['rapor']['key'])
        rapor.durum = 3
        rapor.save()
        rapor = BAPRapor.objects.get(self.current.task_data['rapor']['key'])
        self.current.user.send_notification(title=_(u"Proje Rapor Yanıtı"),
                                            message=_(u"""%s adlı raporunuz koordinasyon birimi tarafından
                                            reddedildi.""") % (rapor),
                                            typ=1,
                                            sender=self.current.user)

    def red_mesaji_bilgi(self):
        """
        Proje raporunun reddetme işleminin yapıldığına dair bilgilendirme mesajını koordinasyon birimine gösterir.

        """
        rapor = BAPRapor.objects.get(self.current.task_data['rapor']['key'])
        form = JsonForm(title="Rapor Reddetme İşlemi Bilgi Mesajı")
        form.help_text = "%s adlı raporun reddetme işlemi başarılı bir şekilde gerçekleştirilmiştir." % (
            rapor)
        form.yonlendir = fields.Button(_(u'Anasayfaya Git'))
        self.form_out(form)

    def revizyon_mesaji_giris(self):
        """
        Revizyona alınacak olan raporun revizyon nedeninin koordinasyon birimi tarafından girilmesi
        işlemini gerçekleştirir.

        """
        form = RevizyonMesaji(title="Revizyon Mesajı Giriş")
        self.form_out(form)

    def revizyon_mesaji_al(self):
        """
        Revizyon mesajının öğretim üyesine gönderildiğine dair bilgi mesajını koordinasyon birimine gösterir.

        """
        self.current.task_data['mesaj'] = self.current.input["form"]["mesaj"]
        msg = {"title": _(u'Revizyon Mesajı Gönderildi!'),
               "body": _(u'Revizyon mesajınız öğretim üyesine başarıyla iletilmiştir.')}
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def bilgi_mesaji_goster(self):
        """
        Revizyona alınan raporun bilgi mesajının öğretim üyesine gösterilmesi işlemini gerçekleştirir.

        """
        rapor = BAPRapor.objects.get(self.current.task_data['rapor']['key'])
        form = JsonForm(title="Rapor Revizyon Bilgi Mesajı")
        form.help_text = "%s adlı raporunuz koordinasyon birimi tarafından revizyona alındı. Koordinasyon " \
                         "birimine ait revizyon mesajı aşağıda yer almaktadır. \n\nBap Koordinasyon " \
                         "Birimi :  %s" % (rapor, self.current.task_data['mesaj'])
        form.tamam = fields.Button(_(u'Tamam'))
        self.form_out(form)

    def yonlendir(self):
        """
        Anasayfaya yönlendirme işlemi

        """
        self.current.output['cmd'] = 'reload'
