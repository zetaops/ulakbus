# -*-  coding: utf-8 -*-

from zengine.views.crud import CrudView, obj_filter
from pyoko import form

from zengine.lib.forms import JsonForm
from ulakbus.models.personel import Personel
from ulakbus.models.hitap import HizmetKayitlari,HizmetBirlestirme
from datetime import timedelta,date

class IzinIslemleri(CrudView):

    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'Izin'

        # ozel bir eylem listesi hazirlayacagiz. bu sebeple listeyi bosaltiyoruz.
        # kayit tipine bagli olarak ekleyecegimiz eylemleri .append() ile ekleyecegiz
        # object_actions = [
        #     # {'fields': [0, ], 'cmd': 'show', 'mode': 'normal', 'show_as': 'link'},
        # ]

    # class ObjectForm(JsonForm):
    #     class Meta:
    #         # durum alanini formdan cikar. kadrolar sadece sakli olarak kaydedilebilir.
    #         exclude = ['personel', 'vekil', ]
    #
    #     save_edit = form.Button("Kaydet", cmd="save")

    #
    # ObjectForm birden cok view da farklilasiyorsa metod icinde bu sekilde kullanilmali.
    #
    # def kadro_ekle_form(self):
    #     self.object_form.exclude = ['durum',]
    #     self.form()
    #

    # def izin_kaydet(self):
    #     # formdan gelen datayi, instance a gecir.
    #     self.set_form_data_to_object()
    #     print self.object
    #
    #     # Kadroyu kaydet
    #     self.object.save()
    #
    #     # isakisini bastan baslat
    #     self.reset()

    def goster(self):
        self.list()
        personel = Personel.objects.get(self.input['personel_id'])
        izin_gun = self.hizmet_izin_yil_hesapla(personel)

        # Personelin izin gün sayısı 365 günden azsa eklemeyi kaldır.
        # Personel pasifse eklemeyi kaldır.
        if izin_gun<365 or not self.personel_aktif:
            del self.output['forms']['schema']['properties']['add']

        ## ToDo: Personel bilgileri tabloda gösterilecek
        self.output['object'] = {
                               "type": "table",
                               "fields": [
                                {
                                 "name": izin_gun,
                                 "surname": "Aktif" if self.personel_aktif else "Pasif"
                                },{
                                 "name": "ali riza",
                                 "surname": "keles"
                                }
                               ]
                              }

    def emekli_sandigi_hesapla(self,personel):
        personel_hizmetler = HizmetKayitlari.objects.filter(tckn=personel.tckn)

        baslangic_liste = set()
        bitis_liste = set()

        for hizmet in personel_hizmetler:
            baslangic_liste.add(hizmet.baslama_tarihi)
            bitis_liste.add(hizmet.bitis_tarihi)

        baslangic_liste.remove(date( 1900, 1, 1))
        bitis_liste.remove(date(1900, 1, 1))

        baslangic_liste = sorted(baslangic_liste)
        bitis_liste = sorted(bitis_liste)

        ZERO = timedelta(0)
        toplam_sure = ZERO
        son_baslama = None

        for baslangic in baslangic_liste:
            if son_baslama == None:
                son_baslama = baslangic
            elif len(bitis_liste)>0 and baslangic >= bitis_liste[0]:
                toplam_sure += bitis_liste[0] - son_baslama
                son_baslama = baslangic
                bitis_liste.remove(bitis_liste[0])

        if son_baslama == None:
            personel_aktif = False
        elif len(bitis_liste)>0:
            personel_aktif = False
            toplam_sure += bitis_liste[0] - son_baslama
        else:
            personel_aktif = True
            toplam_sure += date.today() - son_baslama

        print str(int(toplam_sure.days / 360)) + " Yıl, " + str(int(toplam_sure.days % 360)) + " Gün"
        return toplam_sure.days,personel_aktif

    def sgk_hesapla(self,personel):
        personel_birlestirmeler = HizmetBirlestirme.objects.filter(tckn=personel.tckn)
        toplam_gun = 0

        for hizmet in personel_birlestirmeler:
            toplam_gun += hizmet.sure

        return toplam_gun

    def hizmet_izin_yil_hesapla(self,personel):
        emekli_sandigi_gun,aktif = self.emekli_sandigi_hesapla(personel)
        sgk_gun = self.sgk_hesapla(personel)
        self.personel_aktif = aktif
        return emekli_sandigi_gun + sgk_gun

    def kullanilan_izin_hesapla(self):
        query = self._apply_list_queries(self.object.objects.filter())
        izinler = list()
        # for izin in query:
        #     if izin. izinler