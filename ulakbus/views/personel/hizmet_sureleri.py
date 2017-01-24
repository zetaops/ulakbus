# -*-  coding: utf-8 -*-

from datetime import timedelta, date, datetime

from ulakbus.models.hitap.hitap import HizmetKayitlari, HizmetBirlestirme
from ulakbus.models.personel import Personel, Izin
from zengine.views.crud import CrudView

personel_hizmet = """__Sicil No__: {sicil_no} | __Vatandaşlık No__: {tckn}

### Fiili Hizmet

__Emekli Sandığı__: {fiili_hizmet_emekli_sandigi}

__Bağkur(Tüm)__: {fiili_hizmet_bagkur_tum}

__Diğer Hizmetler__:  {fiili_hizmet_diger_hizmet}

__Yurtdışı (Tüm)__: {fiili_hizmet_yurtdisi_tum}

__Fiili İtibar__: {fiili_hizmet_fiili_hizmet}

__SSK (Tüm)__: {fiili_hizmet_ssk_tum}

__Askerlik__: {fiili_hizmet_askerlik_hesapla}

__Ücretsiz İzin__: {fiili_hizmet_ucretsiz_izin}

__Fahri Görev__: {fiili_hizmet_fahri_gorev}

__Yurtdışı Eğitim__: {fiili_hizmet_yurtdisi_egitim}



### Kıdem Hizmet

__Emekli Sandığı__: {kidem_hizmet_emekli_sandigi}

__Bağkur(2/3)__: {kidem_hizmet_bagkur_2_3}

__Bağkur(3/4)__: {kidem_hizmet_bagkur_3_4}

__Yurtdışı (2/3)__: {kidem_hizmet_yurtdisi_2_3}

__Yurtdışı (3/4)__: {kidem_hizmet_yurtdisi_3_4}

__Yurtdışı (Tüm)__: {kidem_hizmet_yurtdisi_tum}

__Diğer Hizmetler__:  {kidem_hizmet_diger_hizmet}

__SSK (2/3)__: {kidem_hizmet_ssk_2_3}

__SSK (3/4)__: {kidem_hizmet_ssk_3_4}

__SSK (Kamu)__: {kidem_hizmet_ssk_kamu}

__Askerlik__: {kidem_hizmet_askerlik_hesapla}

__Fahri Görev__: {kidem_hizmet_fahri_gorev}

__Yurtdışı Eğitim__: {kidem_hizmet_yurtdisi_egitim}



### İzin Hizmet

__Emekli Sandığı__: {izin_hizmet_emekli_sandigi}

__Bağkur(2/3)__: {izin_hizmet_bagkur_2_3}

__Bağkur(3/4)__: {izin_hizmet_bagkur_3_4}

__Yurtdışı (2/3)__: {izin_hizmet_yurtdisi_2_3}

__Yurtdışı (3/4)__: {izin_hizmet_yurtdisi_3_4}

__Yurtdışı (Tüm)__: {izin_hizmet_yurtdisi_tum}

__Diğer Hizmetler__:  {izin_hizmet_diger_hizmet}

__SSK (2/3)__: {izin_hizmet_ssk_2_3}

__SSK (3/4)__: {izin_hizmet_ssk_3_4}

__SSK (Kamu)__: {izin_hizmet_ssk_kamu}

__Fahri Görev__: {izin_hizmet_fahri_gorev}

__Yurtdışı Eğitim__: {izin_hizmet_yurtdisi_egitim}

"""


class HizmetSureleriView(CrudView):

    class Meta:
        model = 'Personel'

    def goster(self):
        p = self.object
        self.output['object_title'] = "Personel: {0} {1} Hizmet Süreleri".format(p.ad, p.soyad)

        hs = HizmetSureleri(personel=p)
        fiili_hizmet = hs.fiili_hizmet_ayrinti()
        kidem_hizmet = hs.kidem_hizmet_ayrinti()
        izin_hizmet = hs.izin_hizmet_ayrinti()

        self.output['object'] = {
            "": personel_hizmet.format(
                sicil_no=p.kurum_sicil_no_int,
                tckn=p.tckn,
                fiili_hizmet_emekli_sandigi=fiili_hizmet['emekli_sandigi'],
                fiili_hizmet_bagkur_tum=fiili_hizmet['bagkur_tum'],
                fiili_hizmet_diger_hizmet=fiili_hizmet['diger_hizmet'],
                fiili_hizmet_yurtdisi_tum=fiili_hizmet['yurtdisi_tum'],
                fiili_hizmet_fiili_hizmet=fiili_hizmet['fiili_hizmet'],
                fiili_hizmet_ssk_tum=fiili_hizmet['ssk_tum'],
                fiili_hizmet_askerlik_hesapla=fiili_hizmet['askerlik_hesapla'],
                fiili_hizmet_ucretsiz_izin=fiili_hizmet['ucretsiz_izin'],
                fiili_hizmet_fahri_gorev=fiili_hizmet['fahri_gorev'],
                fiili_hizmet_yurtdisi_egitim=fiili_hizmet['yurtdisi_egitim'],

                kidem_hizmet_emekli_sandigi=kidem_hizmet['emekli_sandigi'],
                kidem_hizmet_bagkur_2_3=kidem_hizmet['bagkur_2_3'],
                kidem_hizmet_bagkur_3_4=kidem_hizmet['bagkur_3_4'],
                kidem_hizmet_yurtdisi_2_3=kidem_hizmet['yurtdisi_2_3'],
                kidem_hizmet_yurtdisi_3_4=kidem_hizmet['yurtdisi_3_4'],
                kidem_hizmet_yurtdisi_tum=kidem_hizmet['yurtdisi_tum'],
                kidem_hizmet_diger_hizmet=kidem_hizmet['diger_hizmet'],
                kidem_hizmet_ssk_2_3=kidem_hizmet['ssk_2_3'],
                kidem_hizmet_ssk_3_4=kidem_hizmet['ssk_3_4'],
                kidem_hizmet_ssk_kamu=kidem_hizmet['ssk_kamu'],
                kidem_hizmet_askerlik_hesapla=kidem_hizmet['askerlik_hesapla'],
                kidem_hizmet_fahri_gorev=kidem_hizmet['fahri_gorev'],
                kidem_hizmet_yurtdisi_egitim=kidem_hizmet['yurtdisi_egitim'],

                izin_hizmet_emekli_sandigi=izin_hizmet['emekli_sandigi'],
                izin_hizmet_bagkur_2_3=izin_hizmet['bagkur_2_3'],
                izin_hizmet_bagkur_3_4=izin_hizmet['bagkur_3_4'],
                izin_hizmet_yurtdisi_2_3=izin_hizmet['yurtdisi_2_3'],
                izin_hizmet_yurtdisi_3_4=izin_hizmet['yurtdisi_3_4'],
                izin_hizmet_yurtdisi_tum=izin_hizmet['yurtdisi_tum'],
                izin_hizmet_diger_hizmet=izin_hizmet['diger_hizmet'],
                izin_hizmet_ssk_2_3=izin_hizmet['ssk_2_3'],
                izin_hizmet_ssk_3_4=izin_hizmet['ssk_3_4'],
                izin_hizmet_ssk_kamu=izin_hizmet['ssk_kamu'],
                izin_hizmet_fahri_gorev=izin_hizmet['fahri_gorev'],
                izin_hizmet_yurtdisi_egitim=izin_hizmet['yurtdisi_egitim']
            )
        }


class HizmetSureleri():

    personel = None

    def __init__(self,personel=None,tckn=None):
        if personel:
            self.personel = personel
        elif tckn:
            self.personel = Personel.objects.filter(tckn=tckn)[0]

    def fiili_hizmet_getir(self):
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn,sgk_nevi__in=[3, 7, 4, 1,2, 6 ])

        sure = 0
        for hizmet in hizmetler:
            sure += hizmet.sure
        sure += self._emekli_sandigi_hesapla()

        return sure
        return self._emekli_sandigi_hesapla() + self._bagkur_tum_hesapla() \
                + self._diger_hizmet_hesapla() + self._yurtdisi_tum_hesapla() \
                + self._fiili_hizmet_hesapla() + self._ssk_tum_hesapla() \
                + self._askerlik_hesapla() + self._ucretsiz_izin_hesapla() \
                + self._fahri_gorev_hesapla() + self._yurtdisi_egitim_hesapla()

    def fiili_hizmet_ayrinti(self):
        return { "emekli_sandigi": self._emekli_sandigi_hesapla(), "bagkur_tum": self._bagkur_tum_hesapla(),
                "diger_hizmet": self._diger_hizmet_hesapla(), "yurtdisi_tum": self._yurtdisi_tum_hesapla(),
                "fiili_hizmet": self._fiili_hizmet_hesapla(), "ssk_tum": self._ssk_tum_hesapla(),
                "askerlik_hesapla": self._askerlik_hesapla(), "ucretsiz_izin": self._ucretsiz_izin_hesapla(),
                "fahri_gorev": self._fahri_gorev_hesapla(), "yurtdisi_egitim": self._yurtdisi_egitim_hesapla()
            }

    def kidem_hizmet_getir(self):
        return self._emekli_sandigi_hesapla() + self._askerlik_hesapla() \
                + self._ssk_tum_hesapla() + self._bagkur_tum_hesapla() \
                + self._yurtdisi_tum_hesapla() + self._diger_hizmet_hesapla() \
                + self._fahri_gorev_hesapla() + self._yurtdisi_egitim_hesapla()

    def kidem_hizmet_ayrinti(self):
        return { "emekli_sandigi": self._emekli_sandigi_hesapla(), "askerlik_hesapla": self._askerlik_hesapla(),
                 "ssk_2_3" : self._ssk_2_3_hesapla(), "ssk_3_4" : self._ssk_3_4_hesapla(),
                 "ssk_kamu" : self._ssk_kamu_hesapla(), "bagkur_2_3" : self._bagkur_2_3_hesapla(),
                 "bagkur_3_4" : self._bagkur_3_4_hesapla(), "yurtdisi_2_3": self._yurtdisi_2_3_hesapla(),
                "yurtdisi_3_4": self._yurtdisi_3_4_hesapla(), "yurtdisi_tum": self._yurtdisi_tum_hesapla(),
                "diger_hizmet": self._diger_hizmet_hesapla(), "fahri_gorev": self._fahri_gorev_hesapla(),
                 "yurtdisi_egitim": self._yurtdisi_egitim_hesapla()
            }

    def izin_hizmet_getir(self):
        return self._emekli_sandigi_hesapla() + self._askerlik_hesapla() \
               + self._ssk_tum_hesapla() + self._bagkur_tum_hesapla() \
               + self._yurtdisi_tum_hesapla() + self._diger_hizmet_hesapla() \
               + self._fahri_gorev_hesapla() + self._yurtdisi_egitim_hesapla()

    def izin_hizmet_ayrinti(self):
        return {"emekli_sandigi": self._emekli_sandigi_hesapla(), "askerlik_hesapla": self._askerlik_hesapla(),
                "ssk_2_3": self._ssk_2_3_hesapla(), "ssk_3_4": self._ssk_3_4_hesapla(),
                "ssk_kamu": self._ssk_kamu_hesapla(), "bagkur_2_3": self._bagkur_2_3_hesapla(),
                "bagkur_3_4": self._bagkur_3_4_hesapla(), "yurtdisi_2_3": self._yurtdisi_2_3_hesapla(),
                "yurtdisi_3_4": self._yurtdisi_3_4_hesapla(), "yurtdisi_tum": self._yurtdisi_tum_hesapla(),
                "diger_hizmet": self._diger_hizmet_hesapla(), "fahri_gorev": self._fahri_gorev_hesapla(),
                "yurtdisi_egitim": self._yurtdisi_egitim_hesapla()
                }

    """
    Aşağıdaki fonksiyonlar yanlızca bu class içinde kullanılacaktır. İhtiyaç olan yerlerde
    üstteki fonksiyonlar çağırılacaktır.

    """

    def _emekli_sandigi_hesapla(self):
        hizmetler = HizmetKayitlari.objects.filter(tckn=self.personel.tckn).order_by("order_date")

        baslangic = None
        sure = 0

        for hizmet in hizmetler:
            if hizmet.sebep_kod.nevi == 1:
                baslangic = hizmet.baslama_tarihi
            elif hizmet.sebep_kod.nevi == 2:
                sure += (hizmet.bitis_tarihi - baslangic).days

        if baslangic:
            sure += (date.today() - baslangic).days

        return sure

    def _diger_hizmet_hesapla(self):
        return 0

    def _yurtdisi_2_3_hesapla(self):
        # sgk_nevi = 4 / Yurt Dışı Hizmetleri / kha_durum = 1 - 2/3
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[4], kha_durum=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _yurtdisi_3_4_hesapla(self):
        # sgk_nevi = 4 / Yurt Dışı Hizmetleri / kha_durum = 2 - 3/4
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[4],kha_durum=2)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _yurtdisi_tum_hesapla(self):
        # sgk_nevi = 4 / Yurt Dışı Hizmetleri
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[4])

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _fiili_hizmet_hesapla(self):
        return 0

    def _ssk_2_3_hesapla(self):
        # sgk_nevi = 1 / SSK Kamu - 2 / SSK Özel - 12 / SSK FHZ (01/10/2008 Sonrası İçin)
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[1, 2, 12],kha_durum=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _ssk_3_4_hesapla(self):
        # sgk_nevi = 1 / SSK Kamu - 2 / SSK Özel - 12 / SSK FHZ (01/10/2008 Sonrası İçin)
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[1, 2, 12],kha_durum=2)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _ssk_kamu_hesapla(self):
        # sgk_nevi = 1 / SSK Kamu
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _ssk_tum_hesapla(self):
        # sgk_nevi = 1 / SSK Kamu - 2 / SSK Özel - 12 / SSK FHZ (01/10/2008 Sonrası İçin)
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[1, 2, 12])

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _bagkur_2_3_hesapla(self):
        # sgk_nevi = 3 / Bağ-Kur
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[3],kha_durum=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _bagkur_3_4_hesapla(self):
        # sgk_nevi = 3 / Bağ-Kur
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[3],kha_durum=2)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _bagkur_tum_hesapla(self):
        # sgk_nevi = 3 / Bağ-Kur
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[3])

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _askerlik_hesapla(self):
        return 0

    def _fahri_gorev_hesapla(self):
        return 0

    def _yurtdisi_egitim_hesapla(self):
        return 0

    def _ucretsiz_izin_hesapla(self):
        return 0