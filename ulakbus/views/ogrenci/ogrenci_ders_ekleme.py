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
        ders_zamani = fields.String('Dersin Zamanı ve Yeri')
        ders_tipi = fields.String('Ders Tipi')

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


class DersAramaFormu(JsonForm):
    """
    Öğrenci ders ekleme iş akışı için kullanılan formdur.

    """

    class Dersler(ListNode):
        key = fields.String(hidden=True)
        ders_adi = fields.String('Dersin Zamanı ve Yeri')

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
    def derslerin_kredilerini_keylerini_bul(subeler):
        """
        Returns:
            Seçilen derslerin zamanlarını,kredileri ve keylerini
        """

        derslerin_keyleri = []
        derslerin_kredileri = []
        for item in subeler:
            try:
                if item['secim']:
                    sube = Sube.objects.get(item['key'])
                    derslerin_keyleri.append(sube.ders.key)
                    derslerin_kredileri.append(sube.ders.yerel_kredisi)
            except KeyError:
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
        def ders_etkinliklerinin_zamanlarini_bul(ders_etkinligi):
            baslangic = int("%s%s" % (ders_etkinligi.baslangic_saat, ders_etkinligi.baslangic_dakika))
            bitis = int("%s%s" % (ders_etkinligi.bitis_saat, ders_etkinligi.bitis_dakika))
            return baslangic, bitis

        def indices(mylist, gun):
            return [i for i, x in enumerate(mylist) if x == gun]

        def zamanlari_karsilastir(*args):

            _items = []
            values = args[0].values()
            keys = args[0].keys()
            for i in range(len(values)):
                aralik = range(len(values))
                aralik.remove(i)
                for y in aralik:
                    value_1 = values[i][0] < values[y][0] and values[i][1] <= values[y][0]
                    value_2 = values[i][0] >= values[y][1] and values[i][1] > values[y][1]
                    if not (value_1 or value_2):
                            _items.append(keys[i])

            return _items

        _ders_etkinlikleri = []
        _ders_etkinliklerin_gunleri = []
        for sube_dict in subeler:
            try:
                if sube_dict['secim']:
                    sube = Sube.objects.get(sube_dict['key'])
                    _etkinlik = [ders_etkinligi.ders_etkinligi
                                 for ders_etkinligi in sube.ders_etkinligi_set]
                    _ders_etkinlikleri.extend(_etkinlik)
                    _gunler = [ders_etkinligi.ders_etkinligi.get_gun_display()
                               for ders_etkinligi in sube.ders_etkinligi_set]
                    _ders_etkinliklerin_gunleri.extend(_gunler)
            except KeyError:
                sube = Sube.objects.get(sube_dict['key'])
                _etkinlik = [ders_etkinligi.ders_etkinligi
                             for ders_etkinligi in sube.ders_etkinligi_set]
                _ders_etkinlikleri.extend(_etkinlik)
                _gunler = [ders_etkinligi.ders_etkinligi.get_gun_display()
                           for ders_etkinligi in sube.ders_etkinligi_set]
                _ders_etkinliklerin_gunleri.extend(_gunler)
        zaman = []
        for gun in set(_ders_etkinliklerin_gunleri):
            _indices = indices(_ders_etkinliklerin_gunleri, gun)
            _zaman = collections.OrderedDict()
            if len(_indices) > 1:
                for i in _indices:
                    dez = ders_etkinliklerinin_zamanlarini_bul(_ders_etkinlikleri[i])
                    if dez not in _zaman:
                        _zaman[_ders_etkinlikleri[i]] = dez
                    else:
                        continue
            cakisan_dersler = zamanlari_karsilastir(_zaman)
            if cakisan_dersler:
                zaman.append(cakisan_dersler)
            else:
                continue
        return zaman

    def degistirilen_derslerden_secim_yap(self):
        """
        Danışman tarafından değiştirilen derslerden seçim yapılır.

        """

        _form = DersSecimForm(title='Ders Seçiniz', current=self.current)
        for sube_ders in self.current.task_data["onaylanan_dersler"]:
            sube = Sube.objects.get(sube_ders['key'])
            _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube)
            try:
                _form.Dersler(key=sube_ders['key'], ders_zamani=_zaman,
                              ders_tipi=sube_ders['ders_tipi'], ders_adi=sube_ders['ders_adi'])
            except KeyError:
                _form.Dersler(key=sube_ders['key'], ders_zamani=_zaman,
                              ders_tipi="Bölüm", ders_adi=sube.ders_adi)
        toplam_kredi = OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(
            self.current.task_data["onaylanan_dersler"])
        _text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz." % \
                sum(toplam_kredi[1])
        _form.help_text = _text
        self.form_out(_form)
        self.sube_secim_form_inline_edit()
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

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

        yeni_donem_basarisiz_zorunlu_dersler, basarili_zorunlu_dersler = \
            OgrenciDersEkleme.yeni_donem_acilan_basarisiz_zorunlu_dersleri_bul(ogrenci_program)
        yeni_donem_basarisiz_zorunlu_secmeli_dersler = OgrenciDersEkleme.yeni_donem_acilan_basarisiz_secmeli_dersleri_bul(
            ogrenci_program)
        self.current.task_data["alttan_ders_yoksa"] = ""
        if yeni_donem_basarisiz_zorunlu_secmeli_dersler or yeni_donem_basarisiz_zorunlu_dersler:
            _form = DersSecimForm(title='Alttan Kalan Zorunlu Dersler', current=self.current)
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
            if "secim_yoksa_help_text" in self.current.task_data:
                _form.help_text = self.current.task_data['secim_yoksa_help_text']
                del self.current.task_data['secim_yoksa_help_text']
            elif "d_k_help_text" in self.current.task_data:
                _form.help_text = self.current.task_data["d_k_help_text"]
                del self.current.task_data["d_k_help_text"]
            elif "c_d_help_text" in self.current.task_data:
                _form.help_text = self.current.task_data["c_d_help_text"]
                del self.current.task_data["c_d_help_text"]
            elif "a_k_help_text" in self.current.task_data:
                _form.help_text = self.current.task_data["a_k_help_text"]
                del self.current.task_data["a_k_help_text"]
            else:
                _form.help_text = "Seçim yapabileceğiniz minimum krediniz 30'dur, maximum krediniz 45'dir."
            self.form_out(_form)
            self.current.output["meta"]["allow_actions"] = False
            self.current.output["meta"]["allow_add_listnode"] = False

        else:
            self.current.task_data["alttan_ders_yoksa"] = "guncel_donemden_zorunlu_ders_sec"

    def is_akisi_adimina_karar_ver(self):
        """
        Öğrencinin seçimini ilk kez yapıp yapmadığına karar verir.

        """

        if 'degistirilen_dersler' in self.current.task_data:
            self.current.task_data['is_akisi_adimi'] = "degistirilen_dersler"
        else:
            self.current.task_data['is_akisi_adimi'] = "alttan_ders_secimlerini_kontrol_et"

    def alttan_ders_secimlerini_kontrol_et(self):
        """
        Alttan seçilen derslere ait birden fazla şube olup olmadığını ve toplam kredinin 45 geçmemesi
        şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.

        """

        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['ak_ders_subeleri'] = subeler
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(subeler)
        self.current.task_data['ak_derslerin_kredileri'] = sum(derslerin_kredileri)
        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        if not subeler:
            self.current.task_data[
                'secim_yoksa_help_text'] = "Alttan kalan derslerinizden yapmadınız, lütfen ders seçimi yapınız!"
            self.current.task_data['alttan_ders'] = 'alttan_kalan_ders_sec'
        elif any(1 != i for i in d_key.values()):
            dersler = [Ders.objects.get(key).ad for key in d_key if d_key[key] > 1]
            self.current.task_data["d_k_help_text"] = "----".join(
                dersler) + "  adlı derslere ait birden fazla şube seçimiz yaptınız!!!"
            self.current.task_data['alttan_ders'] = 'alttan_kalan_ders_sec'

        elif sum(derslerin_kredileri) > 45:
            text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz" % \
                   sum(derslerin_kredileri)
            self.current.task_data["a_k_help_text"] = text
            self.current.task_data['alttan_ders'] = 'alttan_kalan_ders_sec'
        elif cakisan_dersler:
            sube_keyleri = {ders_etkinligi.sube.key for ders_etkinligi_lst in cakisan_dersler for ders_etkinligi in ders_etkinligi_lst}
            self.current.task_data["c_d_help_text"] = "-----".join(
                [Sube.objects.get(key).__unicode__() for key in sube_keyleri]) \
                                                      + "  dersleri  çakışmaktadır."
            self.current.task_data['alttan_ders'] = 'alttan_kalan_ders_sec'
        else:
            self.current.task_data['alttan_ders'] = "guncel_donemden_zorunlu_ders_sec"

    def guncel_donemden_zorunlu_ders_sec(self):
        """
        Güncel dönemin zorunlu dersleri listelenir.

        """

        _form = DersSecimForm(title='Mevcut Dönemin Zorunlu Dersleri', current=self.current)
        toplam_kredi = OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(self.current.input['form']['Dersler'])
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

        if "d_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["d_k_help_text"]
            del self.current.task_data["d_k_help_text"]
        elif "c_d_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["c_d_help_text"]
            del self.current.task_data["c_d_help_text"]
        elif "a_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["a_k_help_text"]
            del self.current.task_data["a_k_help_text"]
        else:
            text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz." % \
                   sum(toplam_kredi[1])
            _form.help_text = text
        _form.alttan_ders_sec = fields.Button("Alttan Ders Seç", cmd="alttan_kalan_ders_sec")
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def guncel_donemden_zorunlu_ders_secimlerini_kontrol_et(self):
        """
        Güncel dönemden  seçilen  zorunlu derslere ait birden fazla şube olup olmadığını ve toplam kredinin 45 geçmemesi
        şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.

        """

        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['gdz_derslerin_subeleri'] = [sube for sube in self.current.input['form']['Dersler'] if
                                                            sube['secim']]
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(self.current.input['form']['Dersler'])
        self.current.task_data['gdz_derslerinin_kredileri'] = sum(derslerin_kredileri)
        toplam_kredi = self.current.task_data['ak_derslerin_kredileri'] + self.current.task_data[
            'gdz_derslerinin_kredileri']
        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        subeler.extend(self.current.task_data['ak_ders_subeleri'])
        cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        if any(1 != i for i in d_key.values()):
            for key in d_key:
                if d_key[key] > 1:
                    ders = Ders.objects.get(key)
                    self.current.task_data["d_k_help_text"] = "%s dersine ait %s şube seçtiniz!!" % (
                        ders.ad, d_key[key])
                    self.current.task_data["zorunlu_ders"] = "guncel_donemden_zorunlu_ders_sec"

        elif cakisan_dersler:
            sube_keyleri = {ders_etkinligi.sube.key for ders_etkinligi_lst in cakisan_dersler for ders_etkinligi in ders_etkinligi_lst}
            self.current.task_data["c_d_help_text"] = "-----".join(
                [Sube.objects.get(key).__unicode__() for key in sube_keyleri]) \
                                                      + "  dersleri  çakışmaktadır."
            self.current.task_data["zorunlu_ders"] = "guncel_donemden_zorunlu_ders_sec"

        elif toplam_kredi > 45:
            text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz" % \
                   toplam_kredi
            self.current.task_data["a_k_help_text"] = text
            self.current.task_data["zorunlu_ders"] = "guncel_donemden_zorunlu_ders_sec"
        else:
            self.current.task_data["zorunlu_ders"] = "guncel_donemin_zorunlu_secmeli_derslerini_sec"

    def guncel_donemin_zorunlu_secmeli_derslerini_sec(self):
        """
        Güncel dönemin zorunlu teknik seçmeli dersleri seçilir.

        """
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        toplam_kredi = self.current.task_data['ak_derslerin_kredileri'] + self.current.task_data[
            'gdz_derslerinin_kredileri']
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
        _form.help_text = 'Minumum seçmeniz gereken seçmeli sayısı %s, Maximum seçmeniz gereken seçmeli sayısı %s' % (
            secmeli_ders.min_sayi, secmeli_ders.max_sayi)
        for ders in secmeli_ders.Dersler:
            if ders.zorunlu_secmeli:
                for sube in ders.ders.sube_set:
                    _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube.sube)
                    _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                                  ders_zamani=_zaman,
                                  ders_tipi='Seçmeli')
        if "d_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["d_k_help_text"]
            del self.current.task_data["d_k_help_text"]
        elif "c_d_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["c_d_help_text"]
            del self.current.task_data["c_d_help_text"]
        elif "a_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["a_k_help_text"]
            del self.current.task_data["a_k_help_text"]
        elif "s_d_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["s_d_help_text"]
            del self.current.task_data["s_d_help_text"]
        else:
            text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz." % \
                   toplam_kredi
            _form.help_text = text
        _form.alttan_ders_sec = fields.Button("Alttan Ders Seç", cmd="alttan_kalan_ders_sec")
        _form.gdz_sec = fields.Button("Güncel Dönemden Zorunlu Ders Seç", cmd="guncel_donemden_zorunlu_ders_sec")
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def guncel_donemin_zorunlu_secmelilerini_kontrol_et(self):
        """
        Güncel dönemden seçilen zorunlu teknik derslere ait birden fazla şube olup olmadığını
        ve toplam kredinin 45 geçmemesi şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.

        """

        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['gdz_secmeli_derslerinin_subeleri'] = [sube for sube in
                                                                      self.current.input['form']['Dersler'] if
                                                                      sube['secim']]
        secmeli_ders = SecmeliDersGruplari.objects.get(self.current.task_data["secmeli_ders_key"])
        count = 0
        for ders in self.current.input['form']['Dersler']:
            if ders['secim']:
                count += 1
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(self.current.input['form']['Dersler'])
        self.current.task_data['gdz_secmelilerin_kredileri'] = sum(derslerin_kredileri)
        toplam_kredi = self.current.task_data['gdz_secmelilerin_kredileri'] + \
                       self.current.task_data['ak_derslerin_kredileri'] + \
                       self.current.task_data['gdz_derslerinin_kredileri']

        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        subeler.extend(self.current.task_data['ak_ders_subeleri'])
        cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        if any(1 != i for i in d_key.values()):
            for key in d_key:
                if d_key[key] > 1:
                    ders = Ders.objects.get(key)
                    self.current.task_data["d_k_help_text"] = "%s dersine ait %s şube seçtiniz!!" % (
                        ders.ad, d_key[key])
                    self.current.task_data["zorunlu_secmeli"] = "guncel_donemin_secmeli_derslerini_sec"
        elif cakisan_dersler:
            sube_keyleri = {ders_etkinligi.sube.key for ders_etkinligi_lst in cakisan_dersler for ders_etkinligi in ders_etkinligi_lst}
            self.current.task_data["c_d_help_text"] = "-----".join(
                [Sube.objects.get(key).__unicode__() for key in sube_keyleri]) \
                                                      + "  dersleri  çakışmaktadır."
            self.current.task_data["zorunlu_secmeli"] = "guncel_donemin_secmeli_derslerini_sec"
        elif toplam_kredi > 45:
            text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz" % \
                   toplam_kredi
            self.current.task_data["a_k_help_text"] = text
            self.current.task_data["zorunlu_secmeli"] = "guncel_donemin_secmeli_derslerini_sec"
        elif count < secmeli_ders.min_sayi or count > secmeli_ders.max_sayi:
            text = "Seçmeli ders seçimleriniz sayısı %s'dir.Seçmeli ders seçimleriniz minimum sayısı %s, " \
                   "maximum ise %s olmalıdır." % (count, secmeli_ders.min_sayi, secmeli_ders.max_sayi)
            self.current.task_data["s_d_help_text"] = text
            self.current.task_data["zorunlu_secmeli"] = "guncel_donemin_secmeli_derslerini_sec"
        else:
            ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
            aktif_donem_durumu = 3 <= ogrenci_program.aktif_donem <= 6
            if ogrenci_program.genel_ortalama >= 3.00 and aktif_donem_durumu and \
                            self.current.task_data["alttan_ders_yoksa"] == "guncel_donemden_zorunlu_ders_sec":
                self.current.task_data["zorunlu_secmeli"] = "ustten_ders_secimini_onayla"
            else:
                self.current.task_data["zorunlu_secmeli"] = "butun_bolumlerden_ders_sec"

    def ustten_ders_secimini_onayla(self):
        """
        Öğrencinin genel not ortalaması 3.00  ya da 3.00 üstündeyse üstten ders seçimi yapıp
        yapmak istemediği sorulur.

        """

        _form = JsonForm(title='Üstten Ders Seçimi Onay')
        _form.help_text = "Üstten Ders Seçmek İstiyor musunuz?"
        _form.evet = fields.Button("Evet", flow="ustten_ders_sec")
        _form.hayir = fields.Button("Hayır", flow="farkli_bolumlerden_ders_sec")
        self.form_out(_form)

    def ustten_ders_sec(self):
        """
        Üstten seçilebilecek dersler listelenilir.

        """

        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        aktif_donem = ogrenci_program.aktif_donem
        dersler = Ders.objects.filter(program_donemi=aktif_donem + 2, donem=Donem.guncel_donem(),
                                      program=ogrenci_program.program)
        toplam_kredi = self.current.task_data['gdz_secmelilerin_kredileri'] + \
                       self.current.task_data['ak_derslerin_kredileri'] + \
                       self.current.task_data['gdz_derslerinin_kredileri']
        _form = DersSecimForm(title='Üstten Ders Seçimi', current=self.current)
        for ders in dersler:
            for sube in ders.sube_set:
                _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube.sube)
                _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                              ders_zamani=_zaman,
                              ders_tipi='Üstten')

        if "d_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["d_k_help_text"]
            del self.current.task_data["d_k_help_text"]
        elif "c_d_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["c_d_help_text"]
            del self.current.task_data["c_d_help_text"]
        elif "a_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["a_k_help_text"]
            del self.current.task_data["a_k_help_text"]
        elif 'ua_help_text' in self.current.task_data:
            _form.help_text = self.current.task_data['ua_help_text']
            del self.current.task_data['ua_help_text']
        else:
            _text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz." % \
                    toplam_kredi
            _form.help_text = _text
        _form.alttan_ders_sec = fields.Button("Alttan Ders Seç", cmd="alttan_kalan_ders_sec")
        _form.gdz_sec = fields.Button("Güncel Dönemden Zorunlu Ders Seç", cmd="guncel_donemden_zorunlu_ders_sec")
        _form.gdzs_sec = fields.Button("Güncel Dönemden Zorunlu Seçmeli Ders Seç",
                                       cmd="guncel_donemin_zorunlu_secmeli_derslerini_sec")
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def ustten_alinan_dersleri_kontrol_et(self):
        """
        Üstten seçilen derslere ait birden fazla şube olup olmadığını ve toplam kredinin 45 geçmemesi
        şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.

        """

        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['ua_derslerin_subeleri'] = [sube for sube in self.current.input['form']['Dersler'] if
                                                           sube['secim']]
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(self.current.input['form']['Dersler'])
        self.current.task_data['ua_derslerin_kredileri'] = sum(derslerin_kredileri)
        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        subeler.extend(self.current.task_data['ak_ders_subeleri'])
        subeler.extend(self.current.task_data['gdz_derslerin_subeleri'])
        subeler.extend(self.current.task_data['gdz_secmeli_derslerinin_subeleri'])
        cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        toplam_kredi = self.current.task_data['gdz_secmelilerin_kredileri'] + \
                       self.current.task_data['ak_derslerin_kredileri'] + \
                       self.current.task_data['gdz_derslerinin_kredileri'] + \
                       self.current.task_data['ua_derslerin_kredileri']

        if any(1 != i for i in d_key.values()):
            for key in d_key:
                if d_key[key] > 1:
                    ders = Ders.objects.get(key)
                    self.current.task_data["d_k_help_text"] = "%s dersine ait %s şube seçtiniz!!" % (
                        ders.ad, d_key[key])
                    self.current.task_data['ustten_ders'] = "ustten_ders_sec"

        elif toplam_kredi > 45:
            text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz" % \
                   toplam_kredi
            self.current.task_data["a_k_help_text"] = text
            self.current.task_data['ustten_ders'] = "ustten_ders_sec"

        elif self.current.task_data['ua_derslerin_kredileri'] > 9:
            self.current.task_data['ua_help_text'] = "Üstten seçilen derslerin toplam kredisi maximum 9 olmalıdır."
            self.current.task_data['ustten_ders'] = "ustten_ders_sec"

        elif cakisan_dersler:
            sube_keyleri = {ders_etkinligi.sube.key for ders_etkinligi_lst in cakisan_dersler for ders_etkinligi in ders_etkinligi_lst}
            self.current.task_data["c_d_help_text"] = "-----".join(
                [Sube.objects.get(key).__unicode__() for key in sube_keyleri]) \
                                                      + "  dersleri  çakışmaktadır."
            self.current.task_data['ustten_ders'] = "ustten_ders_sec"

        else:
            self.current.task_data['ustten_ders'] = "farkli_bolumlerden_ders_sec"

    def butun_bolumlerden_ders_sec(self):
        """
        Öğrenci bütün bölümlerden ders seçmesine olanak sağlar.

        """
        if "ua_derslerin_kredileri" in self.current.task_data:
            toplam_kredi = self.current.task_data['gdz_secmelilerin_kredileri'] + \
                           self.current.task_data['ak_derslerin_kredileri'] + \
                           self.current.task_data['gdz_derslerinin_kredileri'] + \
                           self.current.task_data['ua_derslerin_kredileri']
        else:
            toplam_kredi = self.current.task_data['gdz_secmelilerin_kredileri'] + \
                           self.current.task_data['ak_derslerin_kredileri'] + \
                           self.current.task_data['gdz_derslerinin_kredileri']

        _form = DersAramaFormu(title='Bütün Bölümlerden Ders Seçimi', current=self.current)
        if "d_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["d_k_help_text"]
            del self.current.task_data["d_k_help_text"]
        elif "c_d_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["c_d_help_text"]
            del self.current.task_data["c_d_help_text"]
        elif "a_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["a_k_help_text"]
            del self.current.task_data["a_k_help_text"]
        else:
            _text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz." % \
                    toplam_kredi
            _form.help_text = _text
        _form.alttan_ders_sec = fields.Button("Alttan Ders Seç", cmd="alttan_kalan_ders_sec")
        _form.gdz_sec = fields.Button("Güncel Dönemden Zorunlu Ders Seç", cmd="guncel_donemden_zorunlu_ders_sec")
        _form.gdzs_sec = fields.Button("Güncel Dönemden Zorunlu Seçmeli Ders Seç",
                                       cmd="guncel_donemin_zorunlu_secmeli_derslerini_sec")
        _form.ustten_ders_sec = fields.Button("Üstten Ders Seç", cmd="ustten_ders_sec")
        self.form_out(_form)
        self.sube_secim_form_inline_edit()

    def butun_dersleri_kontrol_et(self):
        """
        Bölümlerden  seçilen derslere ait birden fazla şube olup olmadığını ve bütün seçilen derslerin toplam kredisinin
        45 geçmemesi şartlarını kontrol eder.
        Yukarıda tanımlı şartların sağlanmaması iş akışı önceki adıma geri döner.
        Şartlar sağlandığında ise danışamana bilgi verecek iş akışı adımına gider.

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

        subeler = butun_derslerin_sube_keyleri + self.current.input['form']['Dersler']
        self.current.task_data['butun_derslerin_subeleri'] = subeler
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(subeler)
        toplam_kredi = sum(derslerin_kredileri)
        
        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        if any(1 != i for i in d_key.values()):
            for key in d_key:
                if d_key[key] > 1:
                    ders = Ders.objects.get(key)
                    self.current.task_data["d_k_help_text"] = "%s dersine ait %s şube seçtiniz!!" % (
                        ders.ad, d_key[key])
                self.current.task_data["butun_bolumler"] = "butun_bolumlerden_ders_sec"
        # or toplam_kredi < 30 eklenecek
        elif toplam_kredi > 45:
            text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz" % \
                   toplam_kredi
            self.current.task_data["a_k_help_text"] = text
            self.current.task_data["butun_bolumler"] = "butun_bolumlerden_ders_sec"

        elif cakisan_dersler:
            sube_keyleri = {ders_etkinligi.sube.key for ders_etkinligi_lst in cakisan_dersler for ders_etkinligi in ders_etkinligi_lst}
            self.current.task_data["c_d_help_text"] = "-----".join(
                [Sube.objects.get(key).__unicode__() for key in sube_keyleri]) \
                                                      + "  dersleri  çakışmaktadır."
            self.current.task_data["butun_bolumler"] = "butun_bolumlerden_ders_sec"
        else:
            self.current.task_data["butun_bolumler"] = "butun_secilen_dersleri_listele"

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
        subelerin_keyleri = list(butun_derslerin_sube_keyleri)
        subelerin_keyleri.extend(self.current.input['form']['Dersler'])
        toplam_kredi = OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(subelerin_keyleri)
        text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz." % \
               sum(toplam_kredi[1])
        _form.help_text = text
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def bilgi_ver(self):
        """
        Danışmana, öğrencinin ders seçimi yaptığına dair mesaj gönderirilir.

        """

        msg = {
            "title": 'Ders Seçimi',
            "body": ' Ders seçiminiz kaydedilip danışmanıza onay için gönderilmiştir.'}
        self.current.task_data['LANE_CHANGE_MSG'] = msg
        self.current.task_data['lane_change_invite'] = {'title': 'Ders Onay',
                                                        'body': 'Öğrencinin Ders Seçimlerini Onaylayınız'}
        if 'onaylanan_dersler' in self.current.task_data:
            self.current.task_data['subeler'] = self.current.input['form']['Dersler']
        else:
            self.current.task_data['subeler'] = self.current.task_data['butun_derslerin_subeleri']

    def ogrenci_dersleri_onayla(self):
        """
        Öğrenci tarafından seçilen derslerden bazıları
        """
        _form = DersOnayForm(title="Ders Seçimini Onayla", current=self.current)
        if "secimi_kabul_edilen_dersler" not in self.current.task_data:
            for sube_ders in self.current.task_data['subeler']:
                sube = Sube.objects.get(sube_ders['key'])
                _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube)
                try:
                    _form.Dersler(key=sube_ders['key'], ders_zamani=_zaman,
                                  ders_tipi=sube_ders['ders_tipi'], ders_adi=sube_ders['ders_adi'])
                except KeyError:
                    _form.Dersler(key=sube_ders['key'], ders_zamani=_zaman,
                                  ders_tipi="Bölüm", ders_adi=sube.ders_adi)
        else:
            for sube_ders in self.current.task_data['secimi_kabul_edilen_dersler']:
                sube = Sube.objects.get(sube_ders['key'])
                _zaman = OgrenciDersEkleme.ders_zamanini_bul(sube)
                try:
                    _form.Dersler(key=sube_ders['key'], ders_zamani=_zaman,
                                  ders_tipi=sube_ders['ders_tipi'], ders_adi=sube_ders['ders_adi'])
                except KeyError:
                    _form.Dersler(key=sube_ders['key'], ders_zamani=_zaman,
                                  ders_tipi="Bölüm", ders_adi=sube.ders_adi)
            del self.current.task_data['secimi_kabul_edilen_dersler']
            del self.current.task_data['eklenen_ders']
        try:
            # Bu kısmı gözden geçir, krediyi basarken hata veriyor.
            subeler = list(self.current.task_data['subeler'])
            subeler.extend(self.current.input['form']['Dersler'])
            toplam_kredi = OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(subeler)
        except KeyError:
            toplam_kredi = OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(self.current.task_data['subeler'])

        text = "Öğrenci tarafından seçilen derslerin toplam kredisi %s'dir, " \
               "minumum 30 kredi seçebilirsiniz,maximum ise 45 kredi seçebilirsiniz." % sum(toplam_kredi[1])
        _form.help_text = text
        self.form_out(_form)
        self.current.output["meta"]["allow_add_listnode"] = False

    def kontrol(self):
        """
        
        """
        sube_keyleri = [s['key'] for s in self.current.input['form']['Dersler']]
        _sube_keyleri = [sube_dict[key] for sube_dict in self.current.task_data['subeler'] for key in sube_dict if
                         key == "key"]
        for s_key in _sube_keyleri:
            if s_key not in sube_keyleri:
                self.current.task_data['cmd'] = 'ogrenciye_bilgi_ver'

    def ogrenciye_ders_ekle(self):
        if "eklenen_ders" not in self.current.task_data:
            self.current.task_data['secimi_onaylanan_dersler'] = list(self.current.input['form']['Dersler'])
        toplam_kredi = OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(self.current.task_data['secimi_onaylanan_dersler'])
        _form = DersAramaFormu(title='Ders Seçiniz', current=self.current)
        if "d_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["d_k_help_text"]
            del self.current.task_data["d_k_help_text"]
        elif "c_d_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["c_d_help_text"]
            del self.current.task_data["c_d_help_text"]
        elif "a_k_help_text" in self.current.task_data:
            _form.help_text = self.current.task_data["a_k_help_text"]
            del self.current.task_data["a_k_help_text"]
        else:
            text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz." % \
                   sum(toplam_kredi[1])
            _form.help_text = text
        _form.ders_secimini_onayla = fields.Button("Ders Seçimi Onayla Ekranına Geri Dön", cmd="ogrenci_dersleri_onayla")
        self.form_out(_form)
        self.sube_secim_form_inline_edit()
        self.current.output["meta"]["allow_add_listnode"] = False

    def eklenen_dersleri_kontrol_et(self):
        subeler = list(self.current.task_data['secimi_onaylanan_dersler'])
        subeler.extend(self.current.input['form']['Dersler'])
        derslerin_keyleri, derslerin_kredileri = \
            OgrenciDersEkleme.derslerin_kredilerini_keylerini_bul(subeler)
        d_key = OgrenciDersEkleme.birden_fazla_secilen_subeleri_bul(derslerin_keyleri)
        cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(subeler)
        if any(1 != i for i in d_key.values()):
            for key in d_key:
                if d_key[key] > 1:
                    ders = Ders.objects.get(key)
                    self.current.task_data["d_k_help_text"] = "%s dersine ait %s şube seçtiniz!!" % (
                        ders.ad, d_key[key])
                self.current.task_data["eklenen_ders"] = "ogrenciye_ders_ekle"
        # or sum(derslerin_kredileri) < 30 eklenecek
        elif sum(derslerin_kredileri) > 45:
            text = "Toplam krediniz %s'dir,minumum 30 kredi seçebilirsiniz, maximum ise 45 kredi seçebilirsiniz" % \
                   sum(derslerin_kredileri)
            self.current.task_data["a_k_help_text"] = text
            self.current.task_data["eklenen_ders"] = "ogrenciye_ders_ekle"

        elif cakisan_dersler:
            sube_keyleri = {ders_etkinligi.sube.key for ders_etkinligi_lst in cakisan_dersler for ders_etkinligi in ders_etkinligi_lst}
            self.current.task_data["c_d_help_text"] = "-----".join(
                [Sube.objects.get(key).__unicode__() for key in sube_keyleri]) \
                                                      + "  dersleri  çakışmaktadır."
            self.current.task_data["eklenen_ders"] = "ogrenciye_ders_ekle"
        else:
            self.current.task_data['secimi_onaylanan_dersler'].extend(self.current.input['form']['Dersler'])
            self.current.task_data['secimi_kabul_edilen_dersler'] = subeler
            self.current.task_data["eklenen_ders"] = "ogrenci_dersleri_onayla"

    def ogrenciye_bilgi_ver(self):
        msg = {
            "title": 'Ders Seçimi',
            "body": 'Seçilen derslerde yapılan değişiklik bilgisi öğrenciye aktarıldı.'}
        self.current.task_data['LANE_CHANGE_MSG'] = msg
        self.current.task_data['lane_change_invite'] = {'title': 'Ders Değişikliği',
                                                        'body': 'Danışmanınız tarafından dersleriniz değiştirilmiştir.'}
        self.current.task_data["onaylanan_dersler"] = self.current.input['form']['Dersler']

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
        if self.output['forms']['schema']['properties']['Dersler']['schema'][0]['type'] == "checkbox":
            self.output['forms']['schema']['properties']['Dersler']['schema'][0]['default'] = True
        self.output['forms']['schema']['properties']['Dersler']['quick_add'] = True
        self.output['forms']['schema']['properties']['Dersler']['quick_add_field'] = "ders_adi"
        self.output['forms']['schema']['properties']['Dersler']['quick_add_view'] = "sube_arama"
