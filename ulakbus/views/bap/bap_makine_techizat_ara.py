# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Demirbas

from ulakbus.models import Unit
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _
from ulakbus.settings import DATE_DEFAULT_FORMAT
from ulakbus.lib.view_helpers import prepare_choices_for_model


class MakineTechizatAraForm(JsonForm):
    class Meta:
        title = _(u"Teçhizat Arama")

    ad = fields.String(_(u"Mal/Malzeme"), required=True)
    birim = fields.String(_(u"Birim"), required=False)

    ara = fields.Button(_(u"Ara"), cmd='ara')
    iptal = fields.Button(_(u"İptal"), cmd='iptal', form_validation=False)


class BAPMakineTechizatAra(CrudView):
    """
    BAP Makine, Techizatlari aramalarinin yapildigi anonim is akisidir. Ogretim uyesi proje
    basvurusunda da bu is akisini kullanir.
    """
    class Meta:
        model = 'Demirbas'

    def kontrol(self):
        """
        Makine, teçhizat ara iş akışına nereden(proje başvurusu ya da bap anasayfa) gelindiğini
         kontrol eden adımdır.
        """
        self.current.task_data['proje_basvuru'] = self.current.task_data.get('proje_basvuru', False)

    def onay_metni_goster(self):
        """
        Proje başvurusunda, aranan demirbaşla ilgili gerçekleştirilen işlemin bir satın alma
        olmadığı konusunda öğretim üyesine gerekli bilgiyi veren ve anlaşıldı onayını alan adımdır.
        """
        form = JsonForm(title=_(u"Makine, Teçhizat Ekle"))
        form.help_text = _(u"Burası demirbaş satın alma ekranı değildir, sorgulama ekranıdır. "
                           u"Burada yer alan demirbaşlar yanlarında belirtilen birim ve kişilerin "
                           u"sorumluluğundadır. Kullanım izinleri bu birimlerden alınmalıdır. "
                           u"Koordinatörlüğümüzün bu demirbaşlar üzerinde hiçbir tasarrufu "
                           u"bulunmamaktadır.  Projenizde kullanmayı düşündüğünüz demirbaşları "
                           u"ilgili birim yetkilisi ile görüşüp, kullanım onayı aldıktan sonra "
                           u"başvurunuza dahil ediniz.")
        form.anladim = fields.Button(_(u"Anladım, Devam"), cmd='devam')
        form.geri = fields.Button(_(u"Geri"), cmd='geri')
        self.form_out(form)

    def ara_listele(self):
        """
        Makine, teçhizatların aranıp listelendiği iş akışı adımıdır.
        """
        form = MakineTechizatAraForm(current=self.current)
        form.set_choices_of('birim',choices = prepare_choices_for_model(Unit, unit_type="Bölüm"))

        # Arama sonuclari task_data'dan alınır.
        arama_sonuclari = self.current.task_data.pop('arama_sonuclari', False)
        if arama_sonuclari:
            self.output['objects'] = [
                [_(u'Kayıt Tarihi'), _(u'Sorumlu'), _(u'Techizat'), _(u'Birim')]]
            for tech in arama_sonuclari:
                demirbas = Demirbas.objects.get(tech)
                kayit_tarihi = demirbas.teslim_alinma_tarihi.strftime(DATE_DEFAULT_FORMAT)
                proje = demirbas.sorumlu.__unicode__()
                techizat = demirbas.ad
                birim = demirbas.birim.__unicode__()
                list_item = {
                    "fields": [kayit_tarihi, proje, techizat, birim],
                    "actions": [
                        {'name': _(u'Görüntüle'), 'cmd': 'goruntule', 'mode': 'normal',
                         'show_as': 'button'},
                    ],
                    "key": demirbas.key,
                }
                # Proje başvurusundan gelindiyse araştırma olanak listesine ekle butonu işlemlere
                # eklenir.
                if self.current.task_data['proje_basvuru']:
                    list_item['actions'].append(
                        {'name': _(u'Araştırma Olanakları Listesine Ekle'), 'cmd': 'listeye_ekle',
                         'mode': 'normal', 'show_as': 'button'},
                    )
                self.output['objects'].append(list_item)
        elif arama_sonuclari is not False:
            self.current.output['msgbox'] = {
                'type': 'warning',
                'title': _(u"Sonuç bulunamadı."),
                "msg": _(u"Filtrelerinize uygun sonuç bulunamadı.")}
        self.current.output["meta"]["allow_search"] = False
        self.form_out(form)

    def arama_sonuc_dondur(self):
        """
        Girilen filtreleri modele uygulayarak, dönen sonuçları keyleri ile task_data'ya yazan
        adımdır.
        """
        ad = self.input['form']['ad']
        birim_id = self.input['form']['birim']
        qs = Demirbas.objects
        qs = qs.all(birim_id=birim_id) if birim_id else qs
        self.current.task_data['arama_sonuclari'] = qs.search_on(
            'ad', 'teknik_ozellikler', 'etiketler', contains=ad).values_list('key')

    def listeye_ekle(self):
        """
        Seçilen demirbaşı araştırma olanakları listesine ekleyen adımdır.
        """
        self.current.task_data['cmd'] = 'ekle'
        self.current.task_data['demirbas'] = self.current.task_data.pop('object_id')

    def goruntule(self):
        """
        Seçilen demirbaşın ayrıntılı görüntülendiği adımdır.
        """
        self.object = Demirbas.objects.get(self.current.task_data.pop('object_id'))
        self.show()
        form = JsonForm(title=self.object.__unicode__())
        form.arama_ekranina_don = fields.Button(_(u"Arama Ekranına Dön"))
        self.form_out(form)




