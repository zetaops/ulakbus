# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import OgrenciProgram, DegerlendirmeNot, OgrenciDersi

from ulakbus.lib.ogrenci import HarfNotu
from zengine.views.crud import CrudView

__author__ = 'zops5'


class BasariDurum(CrudView):
    class Meta:
        model = "OgrenciProgram"

    def doneme_bazli_not_tablosu(self):

        # unit = self.current.role.unit
        # program = Program.objects.get(birim=unit)

        ogrenci = self.current.role.get_user().ogrenci
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci)
        donemler = [d.donem for d in ogrenci_program.OgrenciDonem]
        # donemler = sorted(donemler, key=lambda donem: donem.baslangic_tarihi)
        # donemler = ogrenci_program.tarih_sirasiyla_donemler()

        donem_tablosu = list()

        for donem in donemler:
            donem_basari_durumu = [
                ['Ders Kodu', 'Ders Adi', 'Ogretim Elemani', 'Sinav Notlari', 'Ortalama', 'Not',
                 'Durum']
            ]
            ogrenci_dersler = OgrenciDersi.objects.filter(donem=donem,
                                                          ogrenci_program=ogrenci_program)
            for d in ogrenci_dersler:
                dersler = list()
                dersler.append(d.ders.kod)
                dersler.append("""**%s**
                \n**TU:** %s - **Krd:** %s - **AKTS:** %s""" % (
                    d.ders_adi(), str(d.ders.teori_saati) + '-'
                    + str(d.ders.uygulama_saati), str(d.ders.yerel_kredisi),
                    str(d.ders.ects_kredisi)))
                degerlendirmeler = DegerlendirmeNot.objects.filter(
                    ogrenci_no=ogrenci_program.ogrenci_no, donem=donem.ad, ders=d.ders)
                notlar = [(deg.sinav.get_tur_display(),
                           deg.puan,
                           deg.sinav.sube_ortalamasi,
                           deg.sinav.tarih) for deg in degerlendirmeler]
                dersler.append('Ogretim Elemani')
                if len(notlar) > 0:
                    dersler.append(''.join(["""**%s:** %s, **Ort:** %s, **Tarih:** %s
                    \n""" % (sinav, puan, ort, tarih) for sinav, puan, ort, tarih in notlar]))
                    notlar = list(zip(*notlar)[1])
                    ortalama = sum(notlar) / len(notlar)
                    dersler.append("{0:.2f}".format(ortalama))
                    dersler.append(HarfNotu.puan_harf_notu(puan=ortalama))
                    dersler.append('Gecti' if ortalama > HarfNotu.CC.get_100()  else 'Kaldi')
                else:
                    dersler.append('')
                    dersler.append('')
                    dersler.append('')
                    dersler.append('')
                donem_basari_durumu.append({"fields": dersler})
            donem_tablosu.append(
                {
                    "key": donem.ad,
                    "selected": donem.guncel,
                    "objects": donem_basari_durumu
                }
            )

            self.output['objects'] = donem_tablosu
            self.output['meta']['selective_listing'] = True
            self.output['meta']['selective_listing_label'] = "Dönem Seçiniz"
            self.output['meta']['allow_actions'] = False