# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje
from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase
from time import sleep


class TestCase(BaseTestCase):

    def test_bap_proje_basvuru(self):

        for loop in range(2):
            if loop == 1:
                sleep(1)
                token, user = self.get_user_token('ogretim_uyesi_1')
                self.prepare_client('/bap_proje_basvuru', user=user, token=token)
                resp = self.client.post()
                assert resp.json['forms']['form'][0][
                           'helpvalue'] == "#### Revizyon Gerekçeleri:\n" + \
                                           "Bu bir revizyon gerekçesi."

                assert 'ArastirmaOlanaklariForm' in self.client.current.task_data
                assert 'GenelBilgiGirForm' in self.client.current.task_data
                assert 'GerekliBelgeForm' in self.client.current.task_data
                assert 'LabEkleForm' in self.client.current.task_data
                assert 'PersonelEkleForm' in self.client.current.task_data
                assert 'ProjeBelgeForm' in self.client.current.task_data
                assert 'ProjeCalisanlariForm' in self.client.current.task_data
                assert 'ProjeDetayForm' in self.client.current.task_data
                assert 'ProjeIncelemeForm' in self.client.current.task_data
                assert 'ProjeTurForm' in self.client.current.task_data
                assert 'RevizyonGerekceForm' in self.client.current.task_data
                assert 'UniversiteDisiDestekForm' in self.client.current.task_data
                assert 'UniversiteDisiUzmanForm' in self.client.current.task_data
                assert 'YurutucuTecrubesiForm' in self.client.current.task_data

                self.client.post(form={'devam': 1})
            else:
                user = User.objects.get(username='ogretim_uyesi_1')
                self.prepare_client('/bap_proje_basvuru', user=user)
                self.client.post()

            form = {
                'sec': 1,
                'tur_id': 'Kvu9MRWA52accYwKfWKegtZr2BA'
            }

            sleep(1)

            resp = self.client.post(cmd='kaydet_ve_kontrol', form=form)

            sleep(1)
            if loop == 0:
                assert len(resp.json['forms']['model']['BelgeForm']) == 1

            resp = self.client.post(cmd='genel', form={'belgelerim_hazir': 1})

            assert resp.json['forms']['model']['form_name'] == 'GenelBilgiGirForm'

            form = {
                'ad': "Proje1",
                'anahtar_kelimeler': "proje, bap, bilimsel, araştırma",
                'detay_gir': 1,
                'sure': 12,
                'teklif_edilen_baslama_tarihi': "28.04.2017",
                'teklif_edilen_butce': 1234
            }

            resp = self.client.post(form=form)

            assert resp.json['forms']['model']['form_name'] == 'ProjeDetayForm'

            form = {
                'b_plani': "asd",
                'basari_olcutleri': "asd",
                'hedef_ve_amac': "asd",
                'konu_ve_kapsam': "asd",
                'literatur_ozeti': "asd",
                'ozgun_deger': "asd",
                'proje_belgeleri': 1,
                'yontem': "asd",
            }

            resp = self.client.post(form=form)

            assert resp.json['forms']['model']['form_name'] == 'ProjeBelgeForm'

            resp = self.client.post(form={'arastirma_olanaklari': 1})

            assert resp.json['forms']['model']['form_name'] == 'ArastirmaOlanaklariForm'

            if loop == 0:
                # Lab ekleme ekranına gidilir
                resp = self.client.post(cmd='lab', form={'lab_ekle': 1})

                assert resp.json['forms']['model']['form_name'] == 'LabEkleForm'

                # Lab eklenir
                resp = self.client.post(form={'lab': "6Jy9r5e05DwsnkPGOesSvG9v6T8", 'lab_ekle': 1})

                assert resp.json['forms']['model']['form_name'] == 'ArastirmaOlanaklariForm'

                assert len(resp.json['forms']['model']['Olanak']) == 1

                # Personel ekleme ekranına gidilir
                resp = self.client.post(cmd='personel', form={'personel_ekle': 1})

                assert resp.json['forms']['model']['form_name'] == 'PersonelEkleForm'

                # Personel eklenir
                resp = self.client.post(form={'personel': "L6j4ZvGts0XY5PKEiRPUiWxdTvy", 'personel_ekle': 1})

                assert resp.json['forms']['model']['form_name'] == 'ArastirmaOlanaklariForm'

                assert len(resp.json['forms']['model']['Olanak']) == 2

            resp = self.client.post(cmd='ilerle', form={'ileri': 1})

            assert resp.json['forms']['model']['form_name'] == 'ProjeCalisanlariForm'

            if loop == 0:
                form = {
                    'Calisan': [
                        {
                            'ad': "Orhan",
                            'soyad': "Veli",
                            'nitelik': "Şair",
                            'calismaya_katkisi': "Şiir"
                        }
                    ],
                    'ileri': 1
                }
                # Calisan eklenir
                self.client.post(cmd='ileri', form=form)
            else:
                self.client.post(cmd='ileri')

            # İş paketi ekranı
            self.client.post(cmd='bitir', form={'bitir': 1})

            # Bütçe planı ekranı
            resp = self.client.post(cmd='bitir', form={'bitir': 1})

            assert resp.json['forms']['model']['form_name'] == 'UniversiteDisiUzmanForm'

            if loop == 0:
                form = {
                    'Uzman': [
                        {
                            'ad': "Osman",
                            'eposta': "osman@zops.com",
                            'faks': "2324568",
                            'kurum': "Zetaops",
                            'soyad': "Uyar",
                            'tel': "2324567",
                            'unvan': "Geliştirici"
                        }
                    ],
                    'ileri': 1
                }

                resp = self.client.post(form=form)
            else:
                resp = self.client.post()

            sleep(1)
            assert resp.json['forms']['model']['form_name'] == 'UniversiteDisiDestekForm'

            resp = self.client.post(form={'ileri': 1})
            assert resp.json['forms']['model']['form_name'] == 'YurutucuTecrubesiForm'

            resp = self.client.post(form={'ileri': 1})
            assert resp.json['forms']['model']['form_name'] == 'YurutucuProjeForm'

            # Görüntüle
            self.client.post(cmd='ileri', form={'ileri': 1})

            # Onaya gönder
            resp = self.client.post(cmd='onay', form={'onay': 1})

            assert 'msgbox' in resp.json

            sleep(1)

            token, user = self.get_user_token('bap_koordinasyon_birimi_1')
            self.prepare_client('/bap_proje_basvuru', user=user, token=token)
            self.client.post()

            self.client.post(cmd='karar_ver', form={'karar_ver': 1})
            if loop == 1:
                self.client.post()
            else:
                self.client.post(cmd='revizyon', form={'revizyon': 1})
                form = {
                    'gonder': 1,
                    'revizyon_gerekce': "Bu bir revizyon gerekçesi."
                }

                self.client.post(cmd='gonder', form=form)
                resp = self.client.post(cmd='revizyon', form={'tamam': 1})
                assert 'msgbox' in resp.json

        BAPProje.objects.get(self.client.current.task_data['bap_proje_id']).blocking_delete()





















