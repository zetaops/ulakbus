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
            form = {
                'sec': 1,
            }
            if loop == 1:
                form['tur_id'] = 'NHOloQ0kAy3Reb03aSlrfEnnlJb'
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
                assert 'ProjeTurForm' in self.client.current.task_data
                assert 'RevizyonGerekceForm' in self.client.current.task_data
                assert 'UniversiteDisiDestekForm' in self.client.current.task_data
                assert 'UniversiteDisiUzmanForm' in self.client.current.task_data
                assert 'YurutucuTecrubesiForm' in self.client.current.task_data
                assert 'GerceklestirmeGorevlisiForm' in self.client.current.task_data


                self.client.post(form={'devam': 1})
            else:
                form['tur_id'] = 'Kvu9MRWA52accYwKfWKegtZr2BA'
                user = User.objects.get(username='ogretim_uyesi_1')
                self.prepare_client('/bap_proje_basvuru', user=user)
                self.client.post()

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

            resp = self.client.post(form={'arastirma_olanaklari': 1, 'ProjeBelgeleri': []})

            assert resp.json['forms']['model']['form_name'] == 'ArastirmaOlanaklariForm'

            if loop == 0:
                olanak = resp.json['forms']['model']['Olanak']
                # Lab ekleme ekranına gidilir
                resp = self.client.post(cmd='lab', form={'lab_ekle': 1,
                                                         'Olanak': olanak if olanak else []})

                assert resp.json['forms']['model']['form_name'] == 'LabEkleForm'

                # Lab eklenir
                resp = self.client.post(cmd='ekle', form={'lab': "6Jy9r5e05DwsnkPGOesSvG9v6T8",
                                                          'lab_ekle': 1})

                olanak = resp.json['forms']['model']['Olanak']

                assert resp.json['forms']['model']['form_name'] == 'ArastirmaOlanaklariForm'

                assert len(resp.json['forms']['model']['Olanak']) == 1

                # Personel ekleme ekranına gidilir
                resp = self.client.post(cmd='personel', form={'personel_ekle': 1,
                                                              'Olanak': olanak})

                assert resp.json['forms']['model']['form_name'] == 'PersonelEkleForm'

                # Personel eklenir
                resp = self.client.post(cmd='ekle', form={'personel': "L6j4ZvGts0XY5PKEiRPUiWxdTvy",
                                                          'personel_ekle': 1})

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
            form = {
                'Isler': [{'ad': 'test_is_ekleme',
                           'baslama_tarihi': '2017-04-11T21:00:00.000Z',
                           'bitis_tarihi': '2017-04-15T21:00:00.000Z'}],
                'ad': 'test_is_paketi_hazirlama',
                'baslama_tarihi': '10.04.2017',
                'bitis_tarihi': '24.04.2017',
                'kaydet': 1
            }

            # yeni is paketi ekleme adimi baslatilir
            self.client.post(cmd='add_edit_form', form={'yeni_paket': 1})

            # yeni eklenicek is paketi datalari gonderilip kaydedilir.
            self.client.post(form=form)

            # is paketi duzenleme adimi baslatilir
            resp = self.client.post(cmd='duzenle_veya_sil', form={'duzenle': 1})

            # yeni kaydettigimiz is paketinin id si bulunup is_paketi_id degiskenine atanir.
            tittle_map = resp.json['forms']['form'][1]['titleMap']
            is_paketi_id = ''
            for item in tittle_map:
                if item['name'] == form['ad']:
                    is_paketi_id = item['value']
                    break

            # duzenlenecek is paketi secilir
            resp = self.client.post(form={'ilerle': 1, 'is_paketi': is_paketi_id})

            assert resp.json['forms']['model']['ad'] == form['ad']

            form['bitis_tarihi'] = '29.04.2017'

            # Düzenlenen iş paketini kaydet.
            self.client.post(form=form)

            # is paketi silme adimi baslatilir.
            self.client.post(cmd='duzenle_veya_sil', form={'sil': 1})

            # silinecek is paketi secilir
            resp = self.client.post(form={'ilerle': 1, 'is_paketi': is_paketi_id})

            assert resp.json['forms']['form'][0]['helpvalue'] == "test_is_paketi_hazirlama " \
                                                                 "iş paketini silmek istiyor musunuz?"

            # silme islemi gerceklestirilir.
            self.client.post(cmd='delete', form={'evet': 1})

            # baslangic tarihi bitis tarihinden buyuk bir is paketi eklenmeye calisilir.
            self.client.post(cmd='add_edit_form', form={'yeni_paket': 1})
            form['baslama_tarihi'] = '30.04.2017'
            resp = self.client.post(form=form)

            assert resp.json['msgbox']['title'] == 'Kayıt Başarısız Oldu!'
            assert resp.json['msgbox']['msg'] == 'Bitiş tarihi, başlangıç tarihinden küçük olamaz'

            form['kaydet'] = ''
            form['iptal'] = 1

            self.client.post(cmd='iptal', form=form)
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

            destek = resp.json['forms']['model']['Destek']

            resp = self.client.post(form={'ileri': 1, 'Destek': destek if destek else []})
            assert resp.json['forms']['model']['form_name'] == 'YurutucuTecrubesiForm'
            akademik_faaliyet = resp.json['forms']['model']['AkademikFaaliyet']

            resp = self.client.post(form={'ileri': 1,
                                          'AkademikFaaliyet': akademik_faaliyet if
                                          akademik_faaliyet else []})

            assert resp.json['forms']['model']['form_name'] == 'YurutucuProjeForm'
            proje = resp.json['forms']['model']['Proje']

            resp = self.client.post(cmd='ileri', form={'ileri': 1,
                                                       'Proje': proje if proje else []})

            # Proje Gerçekleştiricisi
            proje = BAPProje.objects.get(self.client.current.task_data['bap_proje_id'])
            if loop == 0:
                assert "Gerçekleştirme Görevlisi" in resp.json['forms']['schema']['title']
                resp = self.client.post(wf='bap_proje_basvuru',
                                        form={'gerceklestirme_gorevlisi_id': None, 'sec': 1})
                assert resp.json['msgbox']['title'] == "Gerçekleştirme Görevlisi Seçimi Hatası"
                assert "Gerçekleştirme Görevlisi" in resp.json['forms']['schema']['title']
                self.client.post(wf='bap_proje_basvuru',
                                 form={'gerceklestirme_gorevlisi_id': "DFAhsiUW9rhz0bhmM5C9WOacorI",
                                       'sec': 1})
                proje.reload()
                assert proje.gerceklestirme_gorevlisi.key == "DFAhsiUW9rhz0bhmM5C9WOacorI"

            if loop == 1:
                proje.reload()
                assert proje.gerceklestirme_gorevlisi.user == self.client.current.user

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
