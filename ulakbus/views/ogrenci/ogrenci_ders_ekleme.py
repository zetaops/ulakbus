# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import collections

from pyoko import ListNode
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models import Ogrenci, OgrenciDersi, Program, OgrenciProgram, Ders, Donem, Sube, SecmeliDersGruplari, \
    OgretimYili
from zengine.forms import fields, JsonForm
from zengine.views.crud import CrudView


def sube_arama(current):
    q = current.input.get('query')
    sube_lst = []
    subeler = Sube.objects.search_on(*['ders_adi'], contains=q).filter(donem=Donem.guncel_donem())
    for sube in subeler:
        sube_lst.append((sube.key, "%s - %s" % (
            sube.__unicode__(), OgrenciDersEkleme.ders_zamanini_bul(sube))))
    current.output['objects'] = sube_lst


class DersOnayForm(JsonForm):
    """
    Öğrenci ders ekleme iş akışı için kullanılan formdur.

    """

    class Dersler(ListNode):
        key = fields.String(hidden=True)
        ders_adi = fields.String('Ders')
        ders_baslangic_saati = fields.String('Dersin Başlangıç Saati')
        ders_bitis_saati = fields.String('Ders Bitiş Saati')
        ders_saati = fields.Integer('Ders Saati')
        ders_gunu = fields.String('Ders Günü')

    onayla = fields.Button("Onayla", cmd="kontrol")
    ders_ekle = fields.Button("Ders Ekle", cmd="ogrenciye_ders_ekle")


class DersSecimForm(JsonForm):
    """
    Öğrenci ders ekleme iş akışı için kullanılan formdur.

    """
    class Meta:
        inline_edit = ['secim']

    class Dersler(ListNode):
        secim = fields.Boolean("Seçim", type="checkbox")
        key = fields.String(hidden=True)
        ders_adi = fields.String('Ders')
        ders_zamani = fields.String('Dersin Zamanı ve Yeri')
        ders_tipi = fields.String('Ders Tipi')

    onayla = fields.Button("Onayla")


class OgrenciDersEkleme(CrudView):
    class Meta:
        model = 'Ders'

    @staticmethod
    def son_donemin_basarisiz_dersleri(dersler):
        _dersler = {}
        for d_key, kod in dersler.items():
            if kod in _dersler:
                ders = Ders.objects.get(d_key)
                if ders.donem.baslangic_tarihi > _dersler[kod].donem.baslangic_tarihi:
                    _dersler[kod] = ders
            else:
                ders = Ders.objects.get(d_key)
                _dersler[kod] = ders
        return _dersler

    @staticmethod
    def basarili_ogrenci_dersleri_bul(eski_donem_dersler, ogrenci):
        """
        Returns:
            Öğrencinin güncel dönemden önceki dönemlere ait başarılı olduğu
            derslerin kodları.
            eski dönem de açılan yerine açılan değerleri de ihmal etme

        """
        zorunlu_dersler = eski_donem_dersler[0]
        zorunlu_secmeli_dersler = eski_donem_dersler[1]
        z_ogrenci_dersleri = {}
        for _ders_kod in zorunlu_dersler:
            dersler = Ders.objects.filter(kod=_ders_kod)
            for ders in dersler:
                for _sube in ders.sube_set:
                    try:
                        ogrenci_dersi = OgrenciDersi.objects.get(ogrenci=ogrenci, sube=_sube.sube)
                        if ogrenci_dersi.harflendirilmis_not in ['DC', 'CC', 'CB', 'BB', 'BA', 'AA']:
                            z_ogrenci_dersleri[ogrenci_dersi.sube.ders.key] = ogrenci_dersi.sube.ders.kod
                    except ObjectDoesNotExist:
                        # yerine ders kafasına bak
                        pass
        s_o_dersleri = {}
        for _ders_kod in zorunlu_secmeli_dersler:
            dersler = Ders.objects.filter(kod=_ders_kod)
            for ders in dersler:
                for _sube in ders.sube_set:
                    try:
                        ogrenci_dersi = OgrenciDersi.objects.get(ogrenci=ogrenci, sube=_sube.sube)
                        if ogrenci_dersi.harflendirilmis_not in ['DC', 'CC', 'CB', 'BB', 'BA', 'AA']:
                            s_o_dersleri[ogrenci_dersi.sube.ders.key] = ogrenci_dersi.sube.ders.kod
                    except ObjectDoesNotExist:
                        pass
        zorunlu_ogrenci_dersleri = OgrenciDersEkleme.son_donemin_basarisiz_dersleri(z_ogrenci_dersleri)
        secmeli_ogrenci_dersleri = OgrenciDersEkleme.son_donemin_basarisiz_dersleri(s_o_dersleri)
        return zorunlu_ogrenci_dersleri, secmeli_ogrenci_dersleri

    @staticmethod
    def basarisiz_ogrenci_dersleri_bul(ogrenci):
        """
        Returns:
            Öğrenci başarısız olduğu derslerin kodlarını.

        """

        eski_donem_ogrenci_dersleri = []
        basarisiz_ogrenci_dersleri = OgrenciDersi.objects.search_on(*['harflendirilmis_not'], contains='F').filter(
            ogrenci=ogrenci)
        eski_donem_ogrenci_dersleri.extend(basarisiz_ogrenci_dersleri)

        basarisiz_ogrenci_dersleri = OgrenciDersi.objects.search_on(*['harflendirilmis_not'], startswith='DD').filter(
            ogrenci=ogrenci)
        eski_donem_ogrenci_dersleri.extend(basarisiz_ogrenci_dersleri)

        z_dersler = {ogrenci_dersi.sube.ders.key: ogrenci_dersi.sube.ders.kod for ogrenci_dersi in
                     eski_donem_ogrenci_dersleri if
                     ogrenci_dersi.sube.ders.zorunlu and not ogrenci_dersi.sube.ders.donem.guncel}
        zorunlu_dersler = OgrenciDersEkleme.son_donemin_basarisiz_dersleri(z_dersler)
        z_s_dersler = {}
        for ogrenci_dersi in eski_donem_ogrenci_dersleri:
            _ders = ogrenci_dersi.sube.ders()
            if _ders.secmeli_ders_gruplari_set and not _ders.donem.guncel:
                for secmeli_ders in _ders.secmeli_ders_gruplari_set:
                    for ders in secmeli_ders.secmeli_ders_gruplari.Dersler:
                        if ders.zorunlu_secmeli:
                            z_s_dersler[ders.ders.key] = ders.ders.kod
        zorunlu_secmeli_dersler = OgrenciDersEkleme.son_donemin_basarisiz_dersleri(z_s_dersler)
        return zorunlu_dersler, zorunlu_secmeli_dersler

    @staticmethod
    def yeni_donem_acilan_basarisiz_zorunlu_dersleri_bul(ogrenci_program):
        """
        Returns:
            Yeni dönemde açılan öğrencinin başarısız olduğu dersleri ve öğrencinin başarılı
            olduğu eski dönemlere ait ders kodlarını

        """
        eski_donem_dersler = OgrenciDersEkleme.basarisiz_ogrenci_dersleri_bul(ogrenci_program.ogrenci)
        basarili_zorunlu_ogrenci_dersleri = OgrenciDersEkleme.basarili_ogrenci_dersleri_bul(eski_donem_dersler,
                                                                                            ogrenci_program.ogrenci)[0]
        zorunlu_dersler = eski_donem_dersler[0]
        basarili_zorunlu_dersler = {}
        items = zorunlu_dersler.items()
        for _kod, _ders in basarili_zorunlu_ogrenci_dersleri.items():
            for kod, ders in items:
                if _kod == kod:
                    del zorunlu_dersler[kod]
                    basarili_zorunlu_dersler[_kod] = _ders
        return zorunlu_dersler, basarili_zorunlu_dersler

    @staticmethod
    def yeni_donem_acilan_basarisiz_secmeli_dersleri_bul(ogrenci_program):
        """
        Returns:
            Yeni dönemde açılan öğrencinin başarısız olduğu dersleri ve öğrencinin başarılı
            olduğu eski dönemlere ait ders kodlarını

        """
        eski_donem_dersler = OgrenciDersEkleme.basarisiz_ogrenci_dersleri_bul(
            ogrenci_program.ogrenci)
        basarili_secmeli_ogrenci_dersleri = OgrenciDersEkleme.basarili_ogrenci_dersleri_bul(eski_donem_dersler,
                                                                                            ogrenci_program.ogrenci)[1]
        secmeli_dersler = eski_donem_dersler[1]
        items = secmeli_dersler.items()
        for _kod, _ders in basarili_secmeli_ogrenci_dersleri.items():
            for kod, ders in items:
                if _kod == kod:
                    if _ders.donem.baslangic_tarihi > ders.donem.baslangic_tarihi:
                        del secmeli_dersler[kod]
        return secmeli_dersler

    @staticmethod
    def yeni_donem_zorunlu_dersleri_bul(ogrenci_program, yeni_donem_basarisiz_dersler, basarili_zorunlu_dersler):
        """
        Returns:
            Güncel dönemde açılan öğrencinin alması gereken zorunlu dersleri.

        """

        programa_kayitli_zorunlu_dersler = Ders.objects.filter(program=ogrenci_program.program,
                                                               donem=Donem.guncel_donem(),
                                                               zorunlu=True)
        yeni_donem_basarisiz_ders_kodlari = [kod for kod in yeni_donem_basarisiz_dersler]
        zorunlu_dersler = []
        for zorunlu_ders in programa_kayitli_zorunlu_dersler:
            if zorunlu_ders.kod not in yeni_donem_basarisiz_ders_kodlari and zorunlu_ders.kod:
                if zorunlu_ders.kod not in basarili_zorunlu_dersler:
                    zorunlu_dersler.append(zorunlu_ders)
        return zorunlu_dersler

    @staticmethod
    def dersin_kredilerini_keylerini_bul(subeler):
        """
        Returns:
            Seçilen derslerin zamanlarını,kredileri ve keylerini
        """

        derslerin_keyleri = []
        derslerin_kredileri = []
        for item in subeler:
            if item['secim']:
                sube = Sube.objects.get(item['key'])
                derslerin_keyleri.append(sube.ders.key)
                derslerin_kredileri.append(sube.ders.yerel_kredisi)
        return derslerin_keyleri, derslerin_kredileri

    @staticmethod
    def birden_fazla_secilen_subeleri_bul(derslerin_keyleri):
        """
        Returns:
            Bir derse ait sube keylerini ve keylerin sayısı dict data tipini

        """

        d_key = {}
        for ders_key in derslerin_keyleri:
            if ders_key in d_key:
                d_key[ders_key] += 1
            else:
                d_key[ders_key] = 1
        return d_key

    @staticmethod
    def ders_zamanini_bul(_sube):
        ders_zamani = ""
        for ders_etkinligi in _sube.ders_etkinligi_set:
            ders_zamani += str(ders_etkinligi.ders_etkinligi.baslangic_saat) + ':' + str(
                ders_etkinligi.ders_etkinligi.baslangic_dakika) + '-' + str(
                ders_etkinligi.ders_etkinligi.bitis_saat) + ':' + str(
                ders_etkinligi.ders_etkinligi.bitis_dakika) + '-' + \
                           str(ders_etkinligi.ders_etkinligi.get_gun_display()) + '-' + \
                           str(ders_etkinligi.ders_etkinligi.room_type)

        return ders_zamani

    @staticmethod
    def cakisan_dersleri_bul(subeler):
        _items = []

        def ders_etkinliklerinin_zamanlarini_bul(ders_etkinligi):
            baslangic = int("%s%s" % (ders_etkinligi.baslangic_saat, ders_etkinligi.baslangic_dakika))
            bitis = int("%s%s" % (ders_etkinligi.bitis_saat, ders_etkinligi.bitis_dakika))
            return baslangic, bitis

        def indices(mylist, gun):
            return [i for i, x in enumerate(mylist) if x == gun]

        # def zamanlari_karsilastir(*args):
        #     for arg in args:
        #         len_args = len(arg)
        #         i = 0
        #         while True:
        #             try:
        #                 if not ((arg[0][0] < arg[len_args - (i + 1)][0] and arg[0][1] <= arg[len_args - (i + 1)][0]) or
        #                             (arg[0][0] >= arg[len_args - (i + 1)][1] and arg[0][1] > arg[len_args - (i + 1)][1])):
        #                     _zamanlar.append(True)
        #                 else:
        #                     _zamanlar.append(False)
        #                 i += 1
        #             except IndexError:
        #                 break
        #
        # _ders_etkinlikleri = []
        # _ders_etkinliklerin_gunleri = []
        # for sube_dict in subeler:
        #     if sube_dict['secim']:
        #         sube = Sube.objects.get(sube_dict['key'])
        #         _etkinlik = [ders_etkinligi.ders_etkinligi
        #                      for ders_etkinligi in sube.ders_etkinligi_set]
        #         _ders_etkinlikleri.extend(_etkinlik)
        #         _gunler = [ders_etkinligi.ders_etkinligi.get_gun_display()
        #                    for ders_etkinligi in sube.ders_etkinligi_set]
        #         _ders_etkinliklerin_gunleri.extend(_gunler)
        # if not ((yeni_baslangic < baslangic and yeni_bitis <= baslangic) or
        #                  (yeni_baslangic >= bitis and yeni_bitis > bitis)):

        def zamanlari_karsilastir(*args):
            for arg in args:
                len_args = len(arg)
                values = arg
                for i in range(len_args):
                    for y in enumerate(range(len_args), 1):
                        if not ((values[i][1][0] < values[y][1][0] and values[i][1][1] <= values[y][1][0]) or
                                (values[i][1][0] >= values[y][1][1] and values[i][1][1] > values[y][1][1])):
                            _items.append((values[i], values[y]))

        _ders_etkinlikleri = []
        _ders_etkinliklerin_gunleri = []
        for sube_dict in subeler:
            if sube_dict['secim']:
                sube = Sube.objects.get(sube_dict['key'])
                _etkinlik = [ders_etkinligi.ders_etkinligi
                             for ders_etkinligi in sube.ders_etkinligi_set]
                _ders_etkinlikleri.extend(_etkinlik)
                _gunler = [ders_etkinligi.ders_etkinligi.get_gun_display()
                           for ders_etkinligi in sube.ders_etkinligi_set]
                _ders_etkinliklerin_gunleri.extend(_gunler)

        # _zaman = []
        # for gun in _ders_etkinliklerin_gunleri:
        #     _indices = indices(_ders_etkinliklerin_gunleri, gun)
        #     if len(_indices) > 1:
        #         for i in _indices:
        #             dez = ders_etkinliklerinin_zamanlarini_bul(_ders_etkinlikleri[i])
        #             if dez not in _zaman:
        #                 _zaman.append(dez)
        #             else:
        #                 continue
        #         zamanlari_karsilastir(_zaman)
        #

        _zaman = collections.OrderedDict()
        for gun in _ders_etkinliklerin_gunleri:
            _indices = indices(_ders_etkinliklerin_gunleri, gun)
            if len(_indices) > 1:
                for i in _indices:
                    dez = ders_etkinliklerinin_zamanlarini_bul(_ders_etkinlikleri[i])
                    if dez not in _zaman:
                        _zaman[_ders_etkinlikleri[i]] = dez
                    else:
                        continue
                zamanlari_karsilastir(_zaman)

        return _items

    def degistirilen_derslerden_secim_yap(self):
        """
        Danışman tarafından değiştirilen derslerden seçim yapılır.

        """

        _form = DersSecimForm(title='Ders Seçiniz', current=self.current)
        for item in self.current.task_data['degistirilen_dersler']:
            sube = Sube.objects.get(item['key'])
            for ders_programi in sube.ders_programi_set:
                _form.Dersler(key=sube.key, ders_adi=sube.ders_adi,
                              ders_saati=ders_programi.ders_programi.saat,
                              ders_gunu=ders_programi.ders_programi.gun, ders_tipi=item['ders_tipi'], secim=True)
        self.form_out(_form)
        self.sube_secim_form_inline_edit()

    def alttan_kalan_ders_sec(self):
        """
        Öğrencinin alttan alması gereken dersleri listeler.

        """

        p = Program.objects.get(bolum=self.current.role.unit)
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        self.current.task_data['ogrenci_key'] = ogrenci.key
        ogrenci_program = OgrenciProgram.objects.get(program=p, ogrenci=ogrenci)
        self.current.task_data['danisman_key'] = ogrenci_program.danisman.key
        self.current.task_data['ogrenci_program_key'] = ogrenci_program.key
        _form = DersSecimForm(title='Alttan Kalan Zorunlu Dersler', current=self.current)
        yeni_donem_basarisiz_zorunlu_dersler, basarili_zorunlu_dersler = \
            OgrenciDersEkleme.yeni_donem_acilan_basarisiz_zorunlu_dersleri_bul(ogrenci_program)
        yeni_donem_basarisiz_zorunlu_secmeli_dersler = OgrenciDersEkleme.yeni_donem_acilan_basarisiz_secmeli_dersleri_bul(
            ogrenci_program)
        for kod in yeni_donem_basarisiz_zorunlu_dersler.keys():
            y_ders = Ders.objects.get(kod=kod, donem=Donem.guncel_donem())
            for sube in y_ders.sube_set:
                _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube.sube)
                _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                              ders_zamani=_zaman, ders_tipi='Zorunlu')

        for kod in yeni_donem_basarisiz_zorunlu_secmeli_dersler.keys():
            y_ders = Ders.objects.get(kod=kod, donem=Donem.guncel_donem())
            for sube in y_ders.sube_set:
                _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube.sube)
                _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                              ders_zamani=_zaman, ders_tipi='Seçmeli')
        _form.help_text = "Mininum Krediniz 30, Maximum Krediniz 45dir."
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def is_akisi_adimina_karar_ver(self):
        """
        Öğrencinin seçimini ilk kez yapıp yapmadığına karar verir.

        """

        if 'degistirilen_dersler' in self.current.task_data:
            self.current.task_data['cmd'] = "degistirilen_dersler"
        else:
            self.current.task_data['cmd'] = "alttan_ders_secimlerini_kontrol_et"

    def alttan_ders_secimlerini_kontrol_et(self):
        """
        Alttan seçilen derslere ait birden fazla şube olup olmadığını ve toplam kredinin 45 geçmemesi
        şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.

        """

        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['ak_ders_subeleri'] = subeler
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.dersin_kredilerini_keylerini_bul(self.current.task_data['ak_ders_subeleri'])
        self.current.task_data['ak_derslerin_kredileri'] = sum(derslerin_kredileri)
        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        # cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        for key in d_key:
            if d_key[key] > 1 or self.current.task_data['ak_derslerin_kredileri'] > 45:
                self.current.task_data['alttan_ders_cmd'] = 'alttan_kalan_ders_sec'

            else:
                self.current.task_data['alttan_ders_cmd'] = "guncel_donemden_zorunlu_ders_sec"

    def guncel_donemden_zorunlu_ders_sec(self):
        """
        Güncel dönemin zorunlu dersleri listelenir.

        """

        _form = DersSecimForm(title='Mevcut Dönemin Zorunlu Dersleri', current=self.current)
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        yeni_donem_basarisiz_dersler, basarili_zorunlu_dersler = \
            OgrenciDersEkleme.yeni_donem_acilan_basarisiz_zorunlu_dersleri_bul(ogrenci_program)
        zorunlu_dersler = OgrenciDersEkleme.yeni_donem_zorunlu_dersleri_bul(ogrenci_program,
                                                                            yeni_donem_basarisiz_dersler,
                                                                            basarili_zorunlu_dersler)
        for ders in zorunlu_dersler:
            for sube in ders.sube_set:
                _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube.sube)
                _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                              ders_zamani=_zaman,
                              ders_tipi='Zorunlu')
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def guncel_donemden_zorunlu_ders_secimlerini_kontrol_et(self):
        """
        Güncel dönemden  seçilen  zorunlu derslere ait birden fazla şube olup olmadığını ve toplam kredinin 45 geçmemesi
        şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.

        """

        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['gdz_derslerin_subeleri'] = subeler
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.dersin_kredilerini_keylerini_bul(self.current.input['form']['Dersler'])
        self.current.task_data['gdz_derslerinin_kredileri'] = sum(derslerin_kredileri)
        toplam_kredi = self.current.task_data['ak_derslerin_kredileri'] + self.current.task_data[
            'gdz_derslerinin_kredileri']
        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        # cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        if d_key:
            for key in d_key:
                if d_key[key] > 1 or toplam_kredi > 45:
                    self.current.task_data["zorunlu_ders_cmd"] = "guncel_donemden_zorunlu_ders_sec"
                    break
                else:
                    self.current.task_data["zorunlu_ders_cmd"] = "guncel_donemin_zorunlu_secmeli_derslerini_sec"
        else:
            self.current.task_data["zorunlu_ders_cmd"] = "guncel_donemin_zorunlu_secmeli_derslerini_sec"

    def guncel_donemin_zorunlu_secmeli_derslerini_sec(self):
        """
        Güncel dönemin zorunlu teknik seçmeli dersleri seçilir.

        """

        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        guncel_donem = Donem.guncel_donem()
        if 'Güz' in guncel_donem.ad:
            yil = guncel_donem.baslangic_tarihi.year
        else:
            yil = guncel_donem.baslangic_tarihi.year - 1
        ogretim_yili = OgretimYili.objects.get(yil=yil)
        # Bir yılın, bir programın ve bir donemin  bir tane seçmeli ders grubu olur
        secmeli_ders = SecmeliDersGruplari.objects.get(program=ogrenci_program.program, ogretim_yili=ogretim_yili,
                                                       donem=ogrenci_program.aktif_donem)
        self.current.task_data['secmeli_ders_key'] = secmeli_ders.key
        _form = DersSecimForm(title='Mevcut Dönemin Zorunlu Seçmeli Dersleri ', current=self.current)
        # _form.help_text = 'Minumum seçmeniz gereken seçmeli sayısı %s, Maximum seçmeniz gereken seçmeli sayısı %s' % (
        #     secmeli_ders.min_sayi, secmeli_ders.max_sayi)
        for ders in secmeli_ders.Dersler:
            if ders.zorunlu_secmeli:
                for sube in ders.ders.sube_set:
                    _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube.sube)
                    _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                                  ders_zamani=_zaman,
                                  ders_tipi='Seçmeli')
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def guncel_donemin_zorunlu_secmelilerini_kontrol_et(self):
        """
        Güncel dönemden seçilen zorunlu teknik derslere ait birden fazla şube olup olmadığını
        ve toplam kredinin 45 geçmemesi şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.

        """

        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['gdz_secmeli_derslerinin_subeleri'] = subeler
        secmeli_ders = SecmeliDersGruplari.objects.get(self.current.task_data["secmeli_ders_key"])
        count = 0
        for ders in self.current.input['form']['Dersler']:
            if ders['secim']:
                count += 1
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.dersin_kredilerini_keylerini_bul(self.current.input['form']['Dersler'])
        self.current.task_data['gdz_secmelilerin_kredileri'] = sum(derslerin_kredileri)
        toplam_kredi = self.current.task_data['gdz_secmelilerin_kredileri'] + \
                       self.current.task_data['ak_derslerin_kredileri'] + \
                       self.current.task_data['gdz_derslerinin_kredileri']

        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        if d_key:
            for key in d_key:
                if d_key[key] > 1 or secmeli_ders.max_sayi < count or secmeli_ders.min_sayi > count or toplam_kredi > 45 \
                        or cakisan_dersler:
                    self.current.task_data["zorunlu_secmeli_cmd"] = "guncel_donemin_secmeli_derslerini_sec"
                    break
                else:
                    self.current.task_data["zorunlu_secmeli_cmd"] = "ustten_ders_secimini_onayla"
        else:
            self.current.task_data["zorunlu_secmeli_cmd"] = "ustten_ders_secimini_onayla"

    def ustten_ders_secimini_onayla(self):
        """
        Öğrencinin genel not ortalaması 3.00  ya da 3.00 üstündeyse üstten ders seçimi yapıp
        yapmak istemediği sorulur.

        """

        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        if ogrenci_program.genel_ortalama >= 3.00 and ogrenci_program.aktif_donem >= 3:
            _form = JsonForm(title='Üstten Ders Seçimi Onay')
            _form.help_text = "Üstten Ders Seçmek İstiyor musunuz?"
            _form.evet = fields.Button("Evet", flow="ustten_ders_sec")
            _form.hayir = fields.Button("Hayır", flow="farkli_bolumlerden_ders_sec")
            self.form_out(_form)
        else:
            self.current.task_data['flow'] = "farkli_bolumlerden_ders_sec"

    def ustten_ders_sec(self):
        """
        Üstten seçilebilecek dersler listelenilir.

        """

        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        aktif_donem = ogrenci_program.aktif_donem
        dersler = Ders.objects.filter(program_donemi=aktif_donem + 2, donem=Donem.guncel_donem(),
                                      program=ogrenci_program.program)
        _form = DersSecimForm(title='Üstten Seçilebilecek Dersler', current=self.current)
        for ders in dersler:
            for sube in ders.sube_set:
                _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube.sube)
                _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                              ders_zamani=_zaman,
                              ders_tipi='Üstten')
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def ustten_alinan_dersleri_kontrol_et(self):
        """
        Üstten seçilen derslere ait birden fazla şube olup olmadığını ve toplam kredinin 45 geçmemesi
        şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.

        """

        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['ua_derslerin_subeleri'] = subeler
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.dersin_kredilerini_keylerini_bul(self.current.input['form']['Dersler'])
        self.current.task_data['ua_derslerin_kredileri'] = sum(derslerin_kredileri)
        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        toplam_kredi = self.current.task_data['gdz_secmelilerin_kredileri'] + \
                       self.current.task_data['ak_derslerin_kredileri'] + \
                       self.current.task_data['gdz_derslerinin_kredileri'] + \
                       self.current.task_data['ua_derslerin_kredileri']
        if d_key:
            for key in d_key:
                if d_key[key] > 1 or toplam_kredi > 45 or self.current.task_data['ua_derslerin_kredileri'] > 9 \
                        or True in cakisan_dersler:
                    self.current.task_data['secim_command'] = "ustten_ders_sec"
                    break
                else:
                    self.current.task_data['secim_command'] = "farkli_bolumlerden_ders_sec"
        else:
            self.current.task_data['secim_command'] = "farkli_bolumlerden_ders_sec"

    def butun_bolumlerden_ders_sec(self):
        """
        Öğrenci bütün bölümlerden ders seçmesine olanak sağlar.

        """

        _form = DersSecimForm(title='Ders Seçiniz', current=self.current)
        self.form_out(_form)
        self.sube_secim_form_inline_edit()

    def butun_secilen_dersleri_listele(self):
        """
        Seçilen bütün dersler listelenir.

        """
        if 'ua_derslerin_subeleri' in self.current.task_data:
            butun_derslerin_sube_keyleri = self.current.task_data['ua_derslerin_subeleri'] + \
                                           self.current.task_data['gdz_secmeli_derslerinin_subeleri'] + \
                                           self.current.task_data['gdz_derslerin_subeleri'] + \
                                           self.current.task_data['ak_ders_subeleri']
        else:
            butun_derslerin_sube_keyleri = self.current.task_data['gdz_secmeli_derslerinin_subeleri'] + \
                                           self.current.task_data['gdz_derslerin_subeleri'] + \
                                           self.current.task_data['ak_ders_subeleri']

        _form = DersSecimForm(title='Seçilen Bütün Dersler', current=self.current)
        for item in butun_derslerin_sube_keyleri:
            sube = Sube.objects.get(item['key'])
            _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube)
            _form.Dersler(key=sube.key, ders_adi=sube.ders_adi,
                          ders_zamani=_zaman,
                          ders_tipi='Zorunlu', secim=True)
        for sube in self.current.input['form']['Dersler']:
            sube = Sube.objects.get(sube['key'])
            _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube)
            _form.Dersler(key=sube.key, ders_adi=sube.ders_adi,
                          ders_zamani=_zaman,
                          secim=True, ders_tipi="Bölüm")
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def butun_dersleri_kontrol_et(self):
        """
        Bölümlerden  seçilen derslere ait birden fazla şube olup olmadığını ve bütün seçilen derslerin toplam kredisinin
        45 geçmemesi şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.
        Şartlar sağlandığında ise danışamana bilgi verecek iş akışı adımına gider.

        """

        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['butun_derslerin_subeleri'] = subeler
        count = 0
        for ders in self.current.input['form']['Dersler']:
            if ders['secim']:
                count += 1
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.dersin_kredilerini_keylerini_bul(self.current.input['form']['Dersler'])
        self.current.task_data['secilen_derslerin_kredileri'] = sum(derslerin_kredileri)
        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        for key in d_key:
            if d_key[key] > 1 or self.current.task_data['secilen_derslerin_kredileri'] > 45:
                self.current.task_data["cmd"] = "butun_bolumlerden_ders_sec"
                break
            else:
                self.current.task_data["cmd"] = "bilgi_ver"

    def bilgi_ver(self):
        """
        Danışmana, öğrencinin ders seçimi yaptığına dair mesaj gönderirilir.

        """

        msg = {
            "title": 'Ders Seçimi',
            "body": ' Ders seçiminiz kaydedilip danışmanıza gönderilmiştir.'}
        self.current.task_data['LANE_CHANGE_MSG'] = msg
        self.current.task_data['lane_change_invite'] = {'title': 'Ders Onay',
                                                        'body': 'Öğrencinin Ders Seçimlerini Onaylayınız'}
        if 'degistirilen_dersler' in self.current.task_data:
            self.current.task_data['subeler'] = self.current.input['form']['Dersler']
        else:
            self.current.task_data['subeler'] = self.current.task_data['butun_derslerin_subeleri']

    def ogrenci_dersleri_onayla(self):
        """
        Öğrenci tarafından seçilen derslerden bazıları
        """
        _form = DersOnayForm(title="Ders Seçim Onayla", current=self.current)
        for sube_ders in self.current.task_data['subeler']:
            _form.Dersler(key=sube_ders['key'], ders_zamani=sube_ders['ders_zamani'],
                          ders_tipi=sube_ders['ders_tipi'], ders_adi=sube_ders['ders_adi'])
        self.form_out(_form)

    def kontrol(self):
        """
        
        """
        if len(self.current.task_data['subeler']) > len(self.current.input['form']['Dersler']):
            self.current.task_data['cmd'] = 'ogrenci_bilgi_ver'
            self.current.task_data['degistirilen_desler'] = self.current.input['form']['Dersler']
        else:
            self.current.task_data['cmd'] = 'ogrenci_derslerini_kaydet'

        def ogrenciye_ders_ekle(self):
            self.current.task_data['degistirilen_dersler'] = self.current.input['form']['Dersler']
            _form = DersSecimForm(title='Ders Seçiniz', current=self.current)
            self.form_out(_form)
            self.sube_secim_form_inline_edit()

    def ogrenciye_bilgi_ver(self):
        msg = {
            "title": 'Ders Seçimi',
            "body": 'Seçilen derslerde yapılan değişiklik bilgisi öğrenciye aktarıldı.'}
        self.current.task_data['LANE_CHANGE_MSG'] = msg
        self.current.task_data['lane_change_invite'] = {'title': 'Ders Değişikliği',
                                                        'body': 'Danışmanınız tarafından dersleriniz değiştirilmiştir.'}

    def ogrenci_derslerini_kaydet(self):
        for sube_key in self.current.input['form']['Dersler']:
            sube = Sube.objects.get(sube_key['key'])
            ogrenci_dersi = OgrenciDersi()
            ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_key'])
            ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
            ogrenci_dersi.sube = sube
            ogrenci_dersi.ogrenci = ogrenci
            ogrenci_dersi.ogrenci_program = ogrenci_program
            ogrenci_dersi.save()
            ogrenci_dersi.delete()
            self.current.output['msgbox'] = {
                'type': 'info', "title": 'Mesaj Iletildi',
                "msg": 'Öğrencinin dersleri başarıyla kaydedilmiştir.'}

    def sube_secim_form_inline_edit(self):
        self.output['forms']['schema']['properties']['Dersler']['schema'][0]['type'] = 'model'
        self.output['forms']['schema']['properties']['Dersler']['schema'][0]['model_name'] = "Ders"
        self.output['forms']['schema']['properties']['Dersler']['quick_add'] = True
        self.output['forms']['schema']['properties']['Dersler']['quick_add_field'] = "ders_adi"
        self.output['forms']['schema']['properties']['Dersler']['quick_add_view'] = "sube_arama"
