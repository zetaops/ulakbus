# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje

from pyoko import ListNode
from ulakbus.models import BAPButcePlani
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _


class ButceKalemleriForm(JsonForm):
    class Meta:
        inline_edit = ['muhasebe_kod']
        always_blank = False

    class ButceKalemList(ListNode):
        class Meta:
            title = _(u"Bütçe Kalemleri")
        kod_adi = fields.String(_(u"Kod Adı"))
        ad = fields.String(_(u"Ad"))
        muhasebe_kod_genel = fields.Integer(_(u"Öğretim Üyesinin Seçtiği Muhasebe Kodu"),
                                            choices='bap_ogretim_uyesi_gider_kodlari')
        muhasebe_kod = fields.String(_(u"Muhasebe Kodu"),
                                     choices='analitik_butce_dorduncu_duzey_gider_kodlari')
        key = fields.String("Key", hidden=True)

    iptal = fields.Button(_(u"İptal"), cmd='iptal')
    kaydet = fields.Button(_(u"Kaydet ve Listele"), cmd='kaydet')


class ButceKalemleriFormRO(ButceKalemleriForm):
    class Meta:
        inline_edit = []
        always_blank = False

    ButceKalemList = ButceKalemleriForm.ButceKalemList

    iptal = fields.Button(_(u"Listeye Dön"), cmd='geri')
    kaydet = fields.Button(_(u"Bitir"), cmd='bitir')


class BAPButceFisiView(CrudView):
    """
    Koordinasyon biriminin bütçe kalemlerine muhasebe kodlarını girdiği iş akışıdır. Proje
    onaylandıktan sonra koordinasyon biriminin görev yöneticisine bu iş akışı düşer, iş akışı görev
     yöneticisinden başlatılır. Tamamlandığında da görev yöneticisinden silinir.
    """
    def butce_kalemlerini_goruntule(self):
        """
        Bütçe kalemleri; isimleri, öğretim üyesinin girdiği genel muhasebe türleri ve muhasebe
        kodları ile listelenir. Koordinasyon birimi bu liste üzerinde muhasebe kodlarını seçerler.
         Kaydet ve listele butonu ile muhasebe kodları kaydedilerek read-only bir şekilde
         listenir. İptal butonu iş akışından çıkılmasını sağlar, ancak iş akışı tamamlanmadığı için
         görev yöneticisinden silinmez. Tıklandığında kaldığı yerden devam eder.
        """
        proje_id = self.current.task_data.get('bap_proje_id', False) or self.input.get(
            'bap_proje_id')
        self.current.task_data['bap_proje_id'] = proje_id
        butce_kalemleri = BAPButcePlani.objects.all(ilgili_proje_id=proje_id)
        form = ButceKalemleriForm(current=self.current, title=BAPProje.objects.get(proje_id).ad)
        for bk in butce_kalemleri:
            form.ButceKalemList(
                kod_adi=bk.kod_adi,
                ad=bk.ad,
                muhasebe_kod_genel=bk.muhasebe_kod_genel,
                muhasebe_kod=bk.muhasebe_kod,
                key=bk.key
            )
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False
        self.form_out(form)

    def butce_kalemlerini_kaydet(self):
        """
        Listedeki bütçe kalemlerini submit edildiği şekilde kaydeder.
        """
        butce_kalemleri = self.input['form']['ButceKalemList']
        for bk in butce_kalemleri:
            butce_plani = BAPButcePlani.objects.get(bk['key'])
            if butce_plani.muhasebe_kod != bk['muhasebe_kod']:
                butce_plani.muhasebe_kod = bk['muhasebe_kod']
                butce_plani.blocking_save()
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        proje.durum = 7
        proje.blocking_save()

    def yonlendir(self):
        """
        Anasayfaya yönlendirir ve iş akışını bir sonraki adıma taşır.
        """
        self.current.output['cmd'] = 'reload'

    def uyari_mesaji_goster(self):
        """
         Bütçe kalemlerinin read-only olarak gösterildiği adımdır. Değişiklik yapılmak istenirse
         listeye dön butonu ile listeye dönülür, istenmezse Bitir butonu ile iş akışı sonlanır.
        """
        self.current.task_data['ButceKalemleriFormRO'] = self.current.task_data['ButceKalemleriForm']
        proje_id = self.current.task_data['bap_proje_id']
        form = ButceKalemleriFormRO(current=self.current, title=BAPProje.objects.get(proje_id).ad)
        form.help_text = _(u"Bütçe kalemlerinin muhasebe kodlarını aşağıdaki gibi kaydettiniz. "
                           u"Düzenleme yapmak için 'Listeye Dön' işlemi tamamlamak için 'Bitir' "
                           u"butonlarını kullanabilirsiniz.")
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False
        self.form_out(form)
