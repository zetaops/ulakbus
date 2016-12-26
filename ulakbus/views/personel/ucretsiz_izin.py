# -*-  coding: utf-8 -*-

from zengine.views.crud import CrudView, obj_filter
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.lib.translation import gettext as _, gettext_lazy
from ulakbus.models.personel import Personel, UcretsizIzin
from ulakbus.models.hitap.hitap import HizmetKayitlari
from datetime import timedelta, date


class UcretsizIzinIslemleri(CrudView):
    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'UcretsizIzin'
        exclude = ['donus_tarihi', 'donus_tip']

        # ozel bir eylem listesi hazirlayacagiz. bu sebeple listeyi bosaltiyoruz.
        # kayit tipine bagli olarak ekleyecegimiz eylemleri .append() ile ekleyecegiz
        object_actions = [
            #     # {'fields': [0, ], 'cmd': 'show', 'mode': 'normal', 'show_as': 'link'},
        ]

    class ListForm(JsonForm):
        btn = fields.Button(gettext_lazy(u"Ücretsiz İzine Ayır"), next="izine_ayir", cmd="save")  # default

    class IzinForm(JsonForm):
        class Meta:
            include = ['tip', 'baslangic', 'bitis', 'onay_tarihi', 'personel']
            title = gettext_lazy(u"İzine Ayır")

        kaydet = fields.Button(gettext_lazy(u"Kaydet"), next="izine_ayir", cmd="izine_ayir")

    class DonusForm(JsonForm):
        class Meta:
            include = ['donus_tarihi', 'donus_tip']

        kaydet = fields.Button(gettext_lazy(u"Kaydet"), next="izin_donus", cmd="izin_donus")

    def goster(self):
        if 'id' in self.input:
            personel = Personel.objects.get(self.input['id'])

            ucretsiz_izinler = UcretsizIzin.objects.filter(personel=personel)
            ucretsiz_izinde = False

            for izin in ucretsiz_izinler:
                if izin.donus_tarihi == None or izin.donus_tarihi == "":
                    ucretsiz_izinde = True
                    self.current.task_data['izin_id'] = izin.key
                    break

            if ucretsiz_izinde:
                self.ListForm.btn = fields.Button(_(u"Ücretsiz İzin Dönüşü"), cmd="izin_donus",
                                                object_id=self.current.task_data['izin_id'])
            else:
                self.ListForm.btn = fields.Button(_(u"Ücretsiz İzine Ayır"), cmd="izine_ayir")
        else:
            pass

        self.list()

    def izine_ayir(self):
        self.form_out(self.IzinForm(self.object, current=self.current))

    def izin_donusu(self):
        self.object = UcretsizIzin.objects.get(self.current.task_data['izin_id'])
        self.form_out(self.DonusForm(self.object, current=self.current))

    def kontrol(self):
        self.set_form_data_to_object()
        if self.current.task_data['cmd'] == 'izine_ayir':
            if self.object.baslangic > self.object.bitis:
                self.current.task_data['cmd'] = 'izne_ayir'
            else:
                hitap_kaydi = HizmetKayitlari()
                personel = self.object.personel
                hitap_kaydi.personel = personel
                hitap_kaydi.tckn = personel.tckn
                hitap_kaydi.bitis_tarihi = self.object.baslangic
                hitap_kaydi.gorev = ".."
                hitap_kaydi.hizmet_sinifi = personel.hizmet_sinifi
                hitap_kaydi.unvan_kod = personel.kadro.unvan

                ## TODO: Sebep Kodları fixtures eklenecek
                hitap_kaydi.sebep_kod = 269
                hitap_kaydi.kurum_onay_tarihi = self.object.onay_tarihi
                hitap_kaydi.sync = 2
                hitap_kaydi.save()
                self.current.task_data['cmd'] = 'basarili'
                self.save()
        else:  ## cmd="izin_donus"
            hitap_kaydi = HizmetKayitlari()
            personel = self.object.personel
            hitap_kaydi.personel = personel
            hitap_kaydi.tckn = personel.tckn
            hitap_kaydi.baslama_tarihi = self.object.donus_tarihi
            hitap_kaydi.gorev = ".."
            hitap_kaydi.hizmet_sinifi = personel.hizmet_sinifi
            hitap_kaydi.unvan_kod = personel.kadro.unvan

            ## TODO: Sebep Kodları fixtures eklenecek, form içerisinden seçilecek
            hitap_kaydi.sebep_kod = 269
            hitap_kaydi.kurum_onay_tarihi = self.object.onay_tarihi
            hitap_kaydi.sync = 2
            hitap_kaydi.save()
            self.current.task_data['cmd'] = 'basarili'
            self.save()

    @obj_filter
    def donus_yapilmis_mi(self, izin, result):
        """
        Ücretsiz İzin Dönüşü yapılmış mı kontrol edilecek
        Eğer izin dönüşü yapılmışsa Sil olmayacak

        :param obj: Kadro instance
        :param result: liste ogesi satiri
        :return: liste ogesi
        """
        if izin.donus_tarihi == None or izin.donus_tarihi == "":
            result['actions'].append(
                    {'name': _(u'Sil'), 'cmd': 'delete', 'show_as': 'button'})
        return result
