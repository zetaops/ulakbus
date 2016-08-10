# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import Sube, Sinav, OgrenciDersi, Ogrenci, DegerlendirmeNot
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView


class OgrenciSecimForm(forms.JsonForm):
    """
    Öğrenci Not Duzenleme sınıfı için form olarak kullanılacaktır.

    """
    class Meta:
        inline_edit = ['secim']

    class Ogrenciler(ListNode):
        ogrenci_key = fields.String('ogrenci_key', hidden=True)
        secim = fields.Boolean(type="checkbox")
        ad_soyad = fields.String('Ad Soyad')


class SubeSecimForm(forms.JsonForm):
    """
    Öğrenci Not Duzenleme sınıfı için form olarak kullanılacaktır.

    """
    class Meta:
        title = 'Şube Seçim'
    sube = fields.String('Şube Seçiniz', type='typeahead')
    ileri = fields.Button('İleri')


class NotDuzenlemeForm(forms.JsonForm):
    """

    Öğrenci Not Duzenleme sınıfı için form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alanlara sahiptir.

    """

    class Meta:
        include = ['puan']

    kaydet = fields.Button('Kaydet')


def sube_arama(current):
    """
    custom search için kullanılan viewdir.

    """

    subeler = []
    query = current.input.get('query')
    for sube in Sube.objects.search_on(*['ders_adi'], contains=query):
        subeler.append((sube.key, sube.ders_adi))

    current.output['objects'] = subeler


class OgrenciNotDuzenleme(CrudView):
    """Öğrenci İşleri Not Düzenleme İş Akışı

    Öğrenci İşleri Not Düzenleme  iş akışı 8 adımdan ve 2 laneden oluşmaktadır. İlk lane öğrenci işleri
    tarafından, ikinci lane ise öğretim üyesi tarafından işletilir.

    İlk lane aşağıdaki beş adımdan oluşur.
       * Fakülte Yönetim Karar No Gir
       * Şube Seç
       * Sınav Seç
       * Öğrenci Seç
       * Öğrenci Seçim Kaydet

    İkinci lane 3 adımdan oluşur.

       * Not Düzenle
       * Not Kaydet
       * Bilgi ver

    """

    class Meta:
        model = 'DegerlendirmeNot'

    def fakulte_yonetim_karar_no_gir(self):
        """
        Fakülte Yönetim Kurulu tarafından belirlenen karar no girilir.

        """

        # TODO: Fakülte yönetim kurulunun kararı loglanacak.
        _form = forms.JsonForm(current=self.current,
                               title='Fakülte Yönetim Kurulunun Karar Numarasını Giriniz.')
        _form.karar = fields.Integer('Karar No', index=True)
        _form.kaydet = fields.Button('Kaydet')
        self.form_out(_form)

    def sube_sec(self):
        """
        Şube seçilir.

        """

        _form = SubeSecimForm(current=self.current)
        self.form_out(_form)
        self.sube_secim_form_inline_edit()
        self.current.output["meta"]["allow_actions"] = True

    def sinav_sec(self):
        """
        Sınav seçilir.

        """

        self.current.task_data['sube'] = self.current.input['form']['sube']
        sinavlar = [(sinav.key, sinav.__unicode__()) for sinav in Sinav.objects.filter(sube_id=self.current.task_data['sube'])]
        _form = forms.JsonForm(current=self.current, title='Sınav Seçiniz')
        _form.sinav = fields.Integer('Sınavlar', choices=tuple(sinavlar))
        _form.ileri = fields.Button('İleri')
        self.form_out(_form)

    def ogrenci_sec(self):
        """
        Notu değiştirelecek öğrenciler seçilir.

        """
        self.current.task_data['sinav_key'] = self.current.input['form']['sinav']
        ogrenci_dersi_lst = OgrenciDersi.objects.filter(sube_id=self.current.task_data['sube'])
        _form = OgrenciSecimForm(current=self.current, title='Öğrenci Seçiniz')
        for ogrenci_dersi in ogrenci_dersi_lst:
            _form.Ogrenciler(ogrenci_key=ogrenci_dersi.ogrenci.key,
                             ad_soyad='%s %s' % (ogrenci_dersi.ogrenci.ad, ogrenci_dersi.ogrenci.soyad))
        _form.ileri = fields.Button('İleri')
        self.form_out(_form)
        self.current.output['meta']['allow_actions'] = False

    def ogrenci_secim_kaydet(self):
        """
        Ekrana bilgi mesajı basılır ve seçilen öğrenciler task data içinde bir sonraki adımda kullanılmak
        üzere tutulur.

        """
        self.current.task_data['ogrenciler'] = [ogr for ogr in self.current.input['form']['Ogrenciler'] if ogr['secim']]
        msg = {"title": 'Not Düzenleme İşlemi',
               "body": 'Not düzenleme işlemi için sınav, öğrenci, şube seçimi başarıyla tamamlanmıştır.'}

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def not_duzenle(self):
        """
        Öğrencilere ait notlar düzenlenir.

        """
        _ogrenci = self.current.task_data['ogrenciler'].pop()
        ogrenci_object = Ogrenci.objects.get(_ogrenci['ogrenci_key'])
        _sinav = Sinav.objects.get(self.current.task_data['sinav_key'])
        degerlendirme_not = DegerlendirmeNot.objects.get(sinav_id=self.current.task_data['sinav_key'],
                                                         ogrenci_id=_ogrenci['ogrenci_key'])
        _form = NotDuzenlemeForm(degerlendirme_not, current=self.current, title='Not Düzenleme Ekranı')
        _form.help_text = '%s adlı öğrencininin %s adlı sınava ait puanı' % (ogrenci_object, _sinav)
        self.form_out(_form)

    def bilgi_ver(self):
        """
        İşlemin başarıyla tamamlandığına dair bilgi mesajı basılır.

        """
        self.current.output['msgbox'] = {'type': 'info', "title": 'Not Düzenleme',
                                         "msg": 'Öğrencilere ait notlar başarıyla düzenlendi'}

    def sube_secim_form_inline_edit(self):
        self.output['forms']['schema']['properties']['sube']['widget'] = 'custom'
        self.output['forms']['schema']['properties']['sube']['view'] = 'sube_arama'
        self.output['forms']['schema']['properties']['sube']['wf'] = "ogrenci_not_duzenleme"