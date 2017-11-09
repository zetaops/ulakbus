#-*- coding: utf-8 -*-
from ulakbus.models import Personel, HizmetBirlestirme, HizmetKayitlari
from ulakbus.models import AskerlikKayitlari, HizmetOkul, UcretsizIzin
from datetime import date, datetime, timedelta
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models.personel import Ceza


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


def sicil_terfi_kazanan_personel_listesi():
    def sure_hesapla(ui):
        basla, bitis = ui.baslama_bitis_tarihleri()
        delta = bitis - basla
        return delta.days

    def sicil_not_kontrol(p):
        if not p.SicilNotu:
            return True

        for s in p.SicilNotu:
            if s.yil in [2009, 2010] and s.puan < 80:
                return False

        return True

    istifa_ucretsiz_izin_sebep_kodlari = [267, 268, 270, ]
    today = date.today()
    sekiz_yil_once = today - timedelta(days=8 * 365)

    terfi_alacaklar = []
    terfi_almislar = []
    hic_hizmet_kaydi_olmayanlar = []
    sicil_notu_kotu_olanlar = []
    ceza_almislar = []
    for p in Personel.objects.all():
        sekiz_yillik_terfi = HizmetKayitlari.objects.order_by('-order_date').filter(personel=p, sebep_kod__in=[93, 278])
        son_8_yillik_terfi = None
        if sekiz_yillik_terfi:
            son_8_yillik_terfi = sekiz_yillik_terfi[0].baslama_tarihi or sekiz_yillik_terfi[0].bitis_tarihi
        else:
            hk = HizmetKayitlari.objects.order_by('order_date').filter(personel=p)
            if hk:
                son_8_yillik_terfi = hk[0].baslama_tarihi or hk[0].bitis_tarihi
            else:
                hic_hizmet_kaydi_olmayanlar.append(p)
                continue

        if son_8_yillik_terfi > sekiz_yil_once:
            terfi_almislar.append(p)
            continue

        if son_8_yillik_terfi.year <= 2010:
            sicil_not = sicil_not_kontrol(p)
            if sicil_not is False:
                sicil_notu_kotu_olanlar.append(p)
                continue

        ceza = Ceza.objects.filter(personel=p, baslama_tarihi__gt=son_8_yillik_terfi).count()
        if ceza:
            ceza_almislar.append(p)
            continue

        cikarilacak_sure = 0

        cikarilacak_kayitlar = HizmetKayitlari.objects.filter(sebep_kod__in=istifa_ucretsiz_izin_sebep_kodlari,
                                                              kurum_onay_tarihi__gt=son_8_yillik_terfi)

        cikarilacak_sure += sum([sure_hesapla(ui) for ui in cikarilacak_kayitlar])

        terfi_suresi = today - son_8_yillik_terfi
        net_sure = terfi_suresi.days - cikarilacak_sure

        if net_sure >= 365 * 8:
            terfi_alacaklar.append((p, net_sure, cikarilacak_sure))

    return terfi_alacaklar, terfi_almislar, hic_hizmet_kaydi_olmayanlar, sicil_notu_kotu_olanlar
