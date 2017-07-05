# -*-  coding: utf-8 -*-

from datetime import timedelta, date, datetime

from ulakbus.models.hitap.hitap import HizmetKayitlari, HizmetBirlestirme
from ulakbus.models import Personel, Izin, AskerlikKayitlari, UcretsizIzin
from ulakbus.models import HizmetOkul, HizmetKurs
from zengine.views.crud import CrudView
from pyoko.exceptions import ObjectDoesNotExist
from collections import OrderedDict

class HizmetSureleriView(CrudView):

    class Meta:
        model = 'Personel'

    def sure_gosterim_duzenle(self, sure):
        """
        parametre olarak girilen gün sayısını yıl ay gün formatına çevirir.
        Örnek:
            2127 integer değeri parametre olarak verilirse, metod
            '5 Yıl 10 Ay 27 Gün' string değerini return eder.
        Args:
            sure: integer

        Returns:

        """
        if sure == 0:
            return 0
        else:
            yildan_kalan = sure % 360
            sure -= yildan_kalan
            yil = sure / 360
            aydan_kalan = yildan_kalan % 30
            yildan_kalan -= aydan_kalan
            ay = yildan_kalan / 30
            return "{yil} Yıl {ay} Ay {gun} Gun".format(
                yil = yil,
                ay = ay,
                gun = aydan_kalan
            )

    def goster(self):
        """
        Hizmet sürelerini bir tablo halinde ekrana basan metoddur.
        Returns:

        """
        p = self.object
        self.output['object_title'] = "Personel: {0} {1} Hizmet Süreleri".format(p.ad, p.soyad)

        hs = HizmetSureleri(personel=p)
        fiili_hizmet = hs.fiili_hizmet_ayrinti()
        kidem_hizmet = hs.kidem_hizmet_ayrinti()
        izin_hizmet = hs.izin_hizmet_ayrinti()

        output = [{0: (u'Fiili Hizmet'),
                   1: (u'Kıdem Hizmeti'),
                   2: (u'İzin Hizmeti')}]

        self.current.output['objects'] = output

        hesaplanan_fiili_hizmet = """
        Emekli Sandığı: {fiili_hizmet_emekli_sandigi}

        Bağkur(Tüm): {fiili_hizmet_bagkur_tum}

        Diğer Hizmetler:  {fiili_hizmet_diger_hizmet}

        Yurtdışı (Tüm): {fiili_hizmet_yurtdisi_tum}

        Fiili İtibar: {fiili_hizmet_fiili_hizmet}

        SSK (Tüm): {fiili_hizmet_ssk_tum}

        Askerlik: {fiili_hizmet_askerlik_hesapla}

        Ücretsiz İzin: {fiili_hizmet_ucretsiz_izin}

        Fahri Görev: {fiili_hizmet_fahri_gorev}

        Yurtdışı Eğitim: {fiili_hizmet_yurtdisi_egitim}
        """.format(
            fiili_hizmet_emekli_sandigi=self.sure_gosterim_duzenle(fiili_hizmet['emekli_sandigi']),
            fiili_hizmet_bagkur_tum=self.sure_gosterim_duzenle(fiili_hizmet['bagkur_tum']),
            fiili_hizmet_diger_hizmet=self.sure_gosterim_duzenle(fiili_hizmet['diger_hizmet']),
            fiili_hizmet_yurtdisi_tum=self.sure_gosterim_duzenle(fiili_hizmet['yurtdisi_tum']),
            fiili_hizmet_fiili_hizmet=self.sure_gosterim_duzenle(fiili_hizmet['fiili_hizmet']),
            fiili_hizmet_ssk_tum=self.sure_gosterim_duzenle(fiili_hizmet['ssk_tum']),
            fiili_hizmet_askerlik_hesapla=self.sure_gosterim_duzenle(fiili_hizmet['askerlik_hesapla']),
            fiili_hizmet_ucretsiz_izin=self.sure_gosterim_duzenle(fiili_hizmet['ucretsiz_izin']),
            fiili_hizmet_fahri_gorev=self.sure_gosterim_duzenle(fiili_hizmet['fahri_gorev']),
            fiili_hizmet_yurtdisi_egitim=self.sure_gosterim_duzenle(fiili_hizmet['yurtdisi_egitim'])
        )

        hesaplanan_kidem_hizmeti = """
        Emekli Sandığı: {kidem_hizmet_emekli_sandigi}

        Bağkur(2/3): {kidem_hizmet_bagkur_2_3}

        Bağkur(3/4): {kidem_hizmet_bagkur_3_4}

        Yurtdışı (2/3): {kidem_hizmet_yurtdisi_2_3}

        Yurtdışı (3/4): {kidem_hizmet_yurtdisi_3_4}

        Yurtdışı (Tüm): {kidem_hizmet_yurtdisi_tum}

        Diğer Hizmetler:  {kidem_hizmet_diger_hizmet}

        SSK (2/3): {kidem_hizmet_ssk_2_3}

        SSK (3/4): {kidem_hizmet_ssk_3_4}

        SSK (Kamu): {kidem_hizmet_ssk_kamu}

        Askerlik: {kidem_hizmet_askerlik_hesapla}

        Fahri Görev: {kidem_hizmet_fahri_gorev}

        Yurtdışı Eğitim: {kidem_hizmet_yurtdisi_egitim}
        """.format(
            kidem_hizmet_emekli_sandigi=self.sure_gosterim_duzenle(kidem_hizmet['emekli_sandigi']),
            kidem_hizmet_bagkur_2_3=self.sure_gosterim_duzenle(kidem_hizmet['bagkur_2_3']),
            kidem_hizmet_bagkur_3_4=self.sure_gosterim_duzenle(kidem_hizmet['bagkur_3_4']),
            kidem_hizmet_yurtdisi_2_3=self.sure_gosterim_duzenle(kidem_hizmet['yurtdisi_2_3']),
            kidem_hizmet_yurtdisi_3_4=self.sure_gosterim_duzenle(kidem_hizmet['yurtdisi_3_4']),
            kidem_hizmet_yurtdisi_tum=self.sure_gosterim_duzenle(kidem_hizmet['yurtdisi_tum']),
            kidem_hizmet_diger_hizmet=self.sure_gosterim_duzenle(kidem_hizmet['diger_hizmet']),
            kidem_hizmet_ssk_2_3=self.sure_gosterim_duzenle(kidem_hizmet['ssk_2_3']),
            kidem_hizmet_ssk_3_4=self.sure_gosterim_duzenle(kidem_hizmet['ssk_3_4']),
            kidem_hizmet_ssk_kamu=self.sure_gosterim_duzenle(kidem_hizmet['ssk_kamu']),
            kidem_hizmet_askerlik_hesapla=self.sure_gosterim_duzenle(kidem_hizmet['askerlik_hesapla']),
            kidem_hizmet_fahri_gorev=self.sure_gosterim_duzenle(kidem_hizmet['fahri_gorev']),
            kidem_hizmet_yurtdisi_egitim=self.sure_gosterim_duzenle(kidem_hizmet['yurtdisi_egitim'])
        )

        hesaplanan_izin_hizmeti = """
        Emekli Sandığı: {izin_hizmet_emekli_sandigi}

        Bağkur(2/3): {izin_hizmet_bagkur_2_3}

        Bağkur(3/4): {izin_hizmet_bagkur_3_4}

        Yurtdışı (2/3): {izin_hizmet_yurtdisi_2_3}

        Yurtdışı (3/4): {izin_hizmet_yurtdisi_3_4}

        Yurtdışı (Tüm): {izin_hizmet_yurtdisi_tum}

        Diğer Hizmetler:  {izin_hizmet_diger_hizmet}

        SSK (2/3): {izin_hizmet_ssk_2_3}

        SSK (3/4): {izin_hizmet_ssk_3_4}

        SSK (Kamu): {izin_hizmet_ssk_kamu}

        Fahri Görev: {izin_hizmet_fahri_gorev}

        Yurtdışı Eğitim: {izin_hizmet_yurtdisi_egitim}
        """.format(
            izin_hizmet_emekli_sandigi=self.sure_gosterim_duzenle(izin_hizmet['emekli_sandigi']),
            izin_hizmet_bagkur_2_3=self.sure_gosterim_duzenle(izin_hizmet['bagkur_2_3']),
            izin_hizmet_bagkur_3_4=self.sure_gosterim_duzenle(izin_hizmet['bagkur_3_4']),
            izin_hizmet_yurtdisi_2_3=self.sure_gosterim_duzenle(izin_hizmet['yurtdisi_2_3']),
            izin_hizmet_yurtdisi_3_4=self.sure_gosterim_duzenle(izin_hizmet['yurtdisi_3_4']),
            izin_hizmet_yurtdisi_tum=self.sure_gosterim_duzenle(izin_hizmet['yurtdisi_tum']),
            izin_hizmet_diger_hizmet=self.sure_gosterim_duzenle(izin_hizmet['diger_hizmet']),
            izin_hizmet_ssk_2_3=self.sure_gosterim_duzenle(izin_hizmet['ssk_2_3']),
            izin_hizmet_ssk_3_4=self.sure_gosterim_duzenle(izin_hizmet['ssk_3_4']),
            izin_hizmet_ssk_kamu=self.sure_gosterim_duzenle(izin_hizmet['ssk_kamu']),
            izin_hizmet_fahri_gorev=self.sure_gosterim_duzenle(izin_hizmet['fahri_gorev']),
            izin_hizmet_yurtdisi_egitim=self.sure_gosterim_duzenle(izin_hizmet['yurtdisi_egitim'])
        )
        bilgiler = OrderedDict([(0, hesaplanan_fiili_hizmet), (1, hesaplanan_kidem_hizmeti),
                                (2, hesaplanan_izin_hizmeti)])
        item = {
            "type": "table-multiRow",
            "fields": bilgiler,
            "actions": False
        }

        self.current.output['objects'].append(item)


class HizmetSureleri():
    """
        Hizmet süreleri hesabı metodlarını içeren class'dır.
    """

    personel = None

    def __init__(self,personel=None,tckn=None):
        if personel:
            self.personel = personel
        elif tckn:
            self.personel = Personel.objects.filter(tckn=tckn)[0]

    def fiili_hizmet_getir(self):
        """
        Memuriyet öncesi hizmetleride dahil personelin tüm hizmetlerini hesaplar.
        Returns:

        """
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
        """
        Personelin fiili hizmet ayrıntılarını dict formatında return eder.
        Returns:

        """
        return { "emekli_sandigi": self._emekli_sandigi_hesapla(), "bagkur_tum": self._bagkur_tum_hesapla(),
                "diger_hizmet": self._diger_hizmet_hesapla(), "yurtdisi_tum": self._yurtdisi_tum_hesapla(),
                "fiili_hizmet": self._fiili_hizmet_hesapla(), "ssk_tum": self._ssk_tum_hesapla(),
                "askerlik_hesapla": self._askerlik_hesapla(), "ucretsiz_izin": self._ucretsiz_izin_hesapla(),
                "fahri_gorev": self._fahri_gorev_hesapla(), "yurtdisi_egitim": self._yurtdisi_egitim_hesapla()
            }

    def kidem_hizmet_getir(self):
        """
        Personelin kıdem hizmeti toplamını return eder.
        Returns:

        """
        return self._emekli_sandigi_hesapla() + self._askerlik_hesapla() \
                + self._ssk_tum_hesapla() + self._bagkur_tum_hesapla() \
                + self._yurtdisi_tum_hesapla() + self._diger_hizmet_hesapla() \
                + self._fahri_gorev_hesapla() + self._yurtdisi_egitim_hesapla()

    def kidem_hizmet_ayrinti(self):
        """
        Personelin kıdem hizmet bilgisi ayrıntılarını dict formatında return eder.
        Returns:

        """
        return { "emekli_sandigi": self._emekli_sandigi_hesapla(), "askerlik_hesapla": self._askerlik_hesapla(),
                 "ssk_2_3" : self._ssk_2_3_hesapla(), "ssk_3_4" : self._ssk_3_4_hesapla(),
                 "ssk_kamu" : self._ssk_kamu_hesapla(), "bagkur_2_3" : self._bagkur_2_3_hesapla(),
                 "bagkur_3_4" : self._bagkur_3_4_hesapla(), "yurtdisi_2_3": self._yurtdisi_2_3_hesapla(),
                "yurtdisi_3_4": self._yurtdisi_3_4_hesapla(), "yurtdisi_tum": self._yurtdisi_tum_hesapla(),
                "diger_hizmet": self._diger_hizmet_hesapla(), "fahri_gorev": self._fahri_gorev_hesapla(),
                 "yurtdisi_egitim": self._yurtdisi_egitim_hesapla()
            }

    def izin_hizmet_getir(self):
        """
        Personelin izin hizmet toplamını hesaplar
        Returns:

        """
        return self._emekli_sandigi_hesapla() + self._askerlik_hesapla() \
               + self._ssk_tum_hesapla() + self._bagkur_tum_hesapla() \
               + self._yurtdisi_tum_hesapla() + self._diger_hizmet_hesapla() \
               + self._fahri_gorev_hesapla() + self._yurtdisi_egitim_hesapla()

    def izin_hizmet_ayrinti(self):
        """
        Personelin izin hizmet bilgisi ayrıntılarını dict formatında return eder.
        Returns:

        """
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

    def tarih_fark_hesapla(self, baslangic, bitis):
        """
        SGK bir ay'ı 30 gün olarak kabul ettiği için hizmet süreleri hesabında
        iki tarih arasındaki gün farkı hesaplanırken aylar 30'ar gün olarak
        hesaba katılır. Burada da bir ay 30 gün olarak kabul edilerek parametre
        olarak girilen iki tarih arasındaki fark gün sayısı olarak hesaplanıp
        return edilmektedir.
        Args:
            baslangic: datetime
            bitis: datetime

        Returns:

        """
        sure = (bitis.year - baslangic.year) * 360
        if bitis.month > baslangic.month:
            sure += (bitis.month - baslangic.month) * 30
        elif bitis.month < baslangic.month:
            sure -= (baslangic.month - bitis.month) * 30

        if bitis.day > baslangic.day:
            sure += bitis.day - baslangic.day
        elif bitis.day < baslangic.day:
            sure -= baslangic.day - bitis.day

        return sure

    def _emekli_sandigi_hesapla(self):
        """
        Personelin emekli sandığı hizmet süresinı hesaplayan metod.
        Returns:

        """
        hizmetler = HizmetKayitlari.objects.filter(tckn=self.personel.tckn).order_by("-order_date")

        baslangic = None
        sure = 0

        for hizmet in hizmetler:
            if hizmet.sebep_kod.nevi == 1:
                baslangic = hizmet.baslama_tarihi
            elif hizmet.sebep_kod.nevi == 2:
                sure += self.tarih_fark_hesapla(baslangic, hizmet.bitis_tarihi)
                baslangic = None

        if baslangic:
            sure += self.tarih_fark_hesapla(baslangic, date.today())

        return sure

    def _diger_hizmet_hesapla(self):
        return 0

    def _yurtdisi_2_3_hesapla(self):
        """
        Personelin yurt dışı (2/3) hizmetini hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 4 / Yurt Dışı Hizmetleri / kha_durum = 1 - 2/3
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[4], kha_durum=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _yurtdisi_3_4_hesapla(self):
        """
        Personelin yurt dışı (3/4) hizmetini hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 4 / Yurt Dışı Hizmetleri / kha_durum = 2 - 3/4
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[4],kha_durum=2)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _yurtdisi_tum_hesapla(self):
        """
        Personelin yurt dışı toplam hizmetini hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 4 / Yurt Dışı Hizmetleri
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[4])

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _fiili_hizmet_hesapla(self):
        return 0

    def _ssk_2_3_hesapla(self):
        """
        Personelin ssk (2/3) hizmetini hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 1 / SSK Kamu - 2 / SSK Özel - 12 / SSK FHZ (01/10/2008 Sonrası İçin)
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[1, 2, 12],kha_durum=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _ssk_3_4_hesapla(self):
        """
        Personelin ssk (3/4) hizmetini hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 1 / SSK Kamu - 2 / SSK Özel - 12 / SSK FHZ (01/10/2008 Sonrası İçin)
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[1, 2, 12],kha_durum=2)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _ssk_kamu_hesapla(self):
        """
        Personelin ssk kamu hizmetini hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 1 / SSK Kamu
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _ssk_tum_hesapla(self):
        """
        Personelin ssk hizmet toplamını hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 1 / SSK Kamu - 2 / SSK Özel - 12 / SSK FHZ (01/10/2008 Sonrası İçin)
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[1, 2, 12])

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _bagkur_2_3_hesapla(self):
        """
        Personelin Bağ-Kur (2/3) hizmetini hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 3 / Bağ-Kur
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[3],kha_durum=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _bagkur_3_4_hesapla(self):
        """
        Personelin Bağ-Kur (3/4) hizmetini hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 3 / Bağ-Kur
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[3],kha_durum=2)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _bagkur_tum_hesapla(self):
        """
        Personelin Bağ-Kur hizmet toplamını hesaplayan metoddur.
        Returns:

        """
        # sgk_nevi = 3 / Bağ-Kur
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[3])

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _askerlik_hesapla(self):
        """
        Personelin askerlik süresini hesaplayan metoddur
        Returns:

        """
        try:
            askerlik = AskerlikKayitlari.objects.get(tckn=self.personel.tckn)
            sure = self.tarih_fark_hesapla(askerlik.baslama_tarihi, askerlik.bitis_tarihi)
        except ObjectDoesNotExist:
            sure = 0
        return sure

    def _fahri_gorev_hesapla(self):
        return 0

    def _yurtdisi_egitim_hesapla(self):
        """
        Personelin yurt dışı eğitim süresini hesaplayan metoddur.
        Returns:

        """
        egitim_bilgileri = HizmetOkul.objects.filter(ogrenim_yeri=2, tckn=self.personel.tckn)
        sure = 0
        for egitim in egitim_bilgileri:
            sure += egitim.ogrenim_suresi * 360
        return sure

    def _ucretsiz_izin_hesapla(self):
        """
        Personelin kullandığı toplam ücretsiz izin süresini hesaplayan metoddur.
        Returns:

        """
        ucretsiz_izinler = UcretsizIzin.objects.filter(personel=self.personel)
        sure = 0

        for izin in ucretsiz_izinler:
            sure += self.tarih_fark_hesapla(izin.baslangic, izin.bitis)
            #sure += (izin.bitis - izin.baslangic).days

        return sure