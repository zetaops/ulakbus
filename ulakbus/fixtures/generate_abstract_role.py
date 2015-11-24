# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Ali Riza Keles'

bolum_roller = ['bolum baskani', 'bolum kurulu baskani', 'bolum kurulu uyesi']
ana_bilim_dali_roller = ['ana bilim dali baskani', 'ana bilim dali uyesi']
bilim_dali_roller = ['bilim dali baskani', 'bilim dali uyesi']

on_lisans_program_roller = ['on lisans ogrencisi']
lisans_program_roller = ['lisans ogrencisi']
yuksek_lisans_program_roller = ['yuksek lisans ogrencisi']
doktora_program_roller = ['doktora ogrencisi']

fakulte_roller = ['fakulte dekani',
                  'fakulte dekan yardimcisi',
                  'fakulte kurulu baskani',
                  'fakulte kurulu uyesi',
                  'fakulte sekreteri',
                  'fakulte ogrenci isleri personeli',
                  'fakulte ogrenci isleri sefi',
                  'fakulte yonetim kurulu baskani',
                  'fakulte yonetim kurulu uyesi']

tip_fakultesi_extra_roller = ['etik kurulu baskani',
                              'etik kurulu uyesi',
                              'bas koordinator',
                              'bas koordinator yardimcisi',
                              'donem koordinatoru',
                              'egitim komisyonu baskani',
                              'egitim komisyonu uyesi']
dis_hekimligi_fakultesi_extra_roller = ['etik kurulu baskani',
                                        'etik kurulu uyesi']

enstitu_roller = ['enstitu mudur',
                  'enstitu mudur yardimcisi',
                  'enstitu kurulu baskani',
                  'enstitu kurulu uyesi',
                  'enstitu yonetim kurulu baskani',
                  'enstitu yonetim kurulu uyesi',
                  'enstitu sekreteri',
                  'enstitu ogrenci isleri personeli',
                  'enstitu muhasebe isleri personeli']

yuksekokul_roller = ['yuksekokul muduru',
                     'yuksekokul mudur yardimcisi',
                     'yuksekokul kurulu baskani',
                     'yuksekokul kurulu uyesi',
                     'yuksekokul yonetim kurulu baskani',
                     'yuksekokul yonetim kurulu uyesi',
                     'yuksekokul sekreteri',
                     'yuksekokul ogrenci isleri personeli',
                     'yuksekokul ogrenci isleri sefi',
                     'yuksekokul sekreteri',
                     'yuksekokul muhasebe personeli']

yabanci_diller_yuksek_okulu_extra_roller = ['yuksekokul birim koordinatoru']

yabanci_diller_yuksek_okulu_roller = yuksekokul_roller + yabanci_diller_yuksek_okulu_extra_roller
tip_fakultesi_roller = fakulte_roller + tip_fakultesi_extra_roller
dis_hekimligi_fakultesi_roller = fakulte_roller + dis_hekimligi_fakultesi_extra_roller

abstract_roller = set(bolum_roller + ana_bilim_dali_roller + \
                      bilim_dali_roller + on_lisans_program_roller + \
                      lisans_program_roller + yuksek_lisans_program_roller + \
                      doktora_program_roller + fakulte_roller + \
                      tip_fakultesi_extra_roller + \
                      dis_hekimligi_fakultesi_extra_roller + enstitu_roller + \
                      yuksekokul_roller + yabanci_diller_yuksek_okulu_extra_roller)

roller = {
    "bolum_roller": bolum_roller,
    "ana_bilim_dali_roller": ana_bilim_dali_roller,
    "bilim_dali_roller": bilim_dali_roller,
    "on_lisans_program_roller": on_lisans_program_roller,
    "lisans_program_roller": lisans_program_roller,
    "yuksek_lisans_program_roller": yuksek_lisans_program_roller,
    "doktora_program_roller": doktora_program_roller,
    "fakulte_roller": fakulte_roller,
    "tip_fakultesi_roller": tip_fakultesi_roller,
    "dis_hekimligi_fakultesi_roller": dis_hekimligi_fakultesi_roller,
    "enstitu_roller": enstitu_roller,
    "yuksekokul_roller": yuksekokul_roller,
    "yabanci_diller_yuksek_okulu_roller": yabanci_diller_yuksek_okulu_roller,
    "tum_roller": list(abstract_roller)
}
