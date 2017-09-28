# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje
from ulakbus.models import Demirbas
from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase
from time import sleep

DUMMY_TEXT = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula " \
             "eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient " \
             "montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, " \
             "pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla " \
             "vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, " \
             "venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer " \
             "tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend " \
             "tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. " \
             "Aliquam lorem ante, dapibus in, viverra quis, feugiat a,"

pdf_belge = {u'belge': {
    u'file_content': u"""data:application/pdf;base64,JVBERi0xLjEKJcKlwrHDqwoKMSAwIG9iagogIDw8IC9UeX
    BlIC9DYXRhbG9nCiAgICAgL1BhZ2VzIDIgMCBSCiAgPj4KZW5kb2JqCgoyIDAgb2JqCiAgPDwgL1R5cGUgL1BhZ2VzCiAgI
    CAgL0tpZHMgWzMgMCBSXQogICAgIC9Db3VudCAxCiAgICAgL01lZGlhQm94IFswIDAgMzAwIDE0NF0KICAPgplbmRvYmoKC
    jMgMCBvYmoKICA8PCAgL1R5cGUgL1BhZ2UKICAgICAgL1BhcmVudCAyIDAgUgogICAgICAvUmVzb3VyY2VzCiAgICAgICA8
    PCAvRm9udAogICAgICAgICAgIDw8IC9GMQogICAgICAgICAgICAgICA8PCAvVHlwZSAvRm9udAogICAgICAgICAgICAgICA
    gICAvU3VidHlwZSAvVHlwZTEKICAgICAgICAgICAgICAgICAgL0Jhc2VGb250IC9UaW1lcy1Sb21hbgogICAgICAgICAgIC
    AgICAPgogICAgICAgICAgID4CiAgICAgICAPgogICAgICAvQ29udGVudHMgNCAwIFIKICAPgplbmRvYmoKCjQgMCBvYmoKI
    CA8PCAvTGVuZ3RoIDU1ID4CnN0cmVhbQogIEJUCiAgICAvRjEgMTggVGYKICAgIDAgMCBUZAogICAgKEhlbGxvIFdvcmxkK
    SBUagogIEVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxOCAwMDAw
    MCBuIAowMDAwMDAwMDc3IDAwMDAwIG4gCjAwMDAwMDAxNzggMDAwMDAgbiAKMDAwMDAwMDQ1NyAwMDAwMCBuIAp0cmFpbGV
    yCiAgPDwgIC9Sb290IDEgMCBSCiAgICAgIC9TaXplIDUKICAPgpzdGFydHhyZWYKNTY1CiUlRU9GCg==""",
    u'file_name': u'pdf_trial.pdf', u'isImage': False}, u'aciklama': u'pdf denemesi'}


class TestCase(BaseTestCase):
    def test_bap_proje_basvuru(self):

        for loop in range(2):
            form = {
                'sec': 1,
            }
            if loop == 1:
                form['tur'] = 'NHOloQ0kAy3Reb03aSlrfEnnlJb'
                sleep(1)
                token, user = self.get_user_token('ogretim_uyesi_1')
                self.prepare_client('/bap_proje_basvuru', user=user, token=token)
                # Süresi geçen rapor var mı kontrolü yapılır.
                self.client.post()
                # Süresi geçen raporun olmadığı kabul edilir.
                resp = self.client.post(form={kontrol: False})

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
                form['tur'] = 'Kvu9MRWA52accYwKfWKegtZr2BA'
                user = User.objects.get(username='ogretim_uyesi_1')
                self.prepare_client('/bap_proje_basvuru', user=user)
                # Süresi geçen rapor var mı kontrolü yapılır.
                self.client.post()
                # Süresi geçen raporun olmadığı kabul edilir.
                resp = self.client.post(form={kontrol: False})

            sleep(1)

            resp = self.client.post(cmd='kaydet_ve_kontrol', form=form)

            sleep(1)
            if loop == 0:
                assert len(resp.json['forms']['model']['BelgeForm']) == 1

            resp = self.client.post(cmd='genel', form={'belgelerim_hazir': 1})

            assert resp.json['forms']['model']['form_name'] == 'GenelBilgiGirForm'

            if loop == 0:
                self.client.post(cmd='daha_sonra_devam_et')
                token, user = self.get_user_token('ogretim_uyesi_1')
                self.prepare_client('/bap_proje_basvuru', user=user, token=token)
                self.client.post()
                self.client.post(cmd='kaydet_ve_kontrol')
                resp = self.client.post(cmd='genel')
                assert resp.json['forms']['model']['form_name'] == 'GenelBilgiGirForm'

            form = {
                'ad': "Proje1",
                'anahtar_kelimeler': "proje, bap, bilimsel, araştırma",
                'detay_gir': 1,
                'sure': 12,
                'teklif_edilen_butce': 1234
            }

            resp = self.client.post(form=form, cmd='detay_gir')

            assert resp.json['forms']['model']['form_name'] == 'ProjeDetayForm'

            form = {
                'b_plani': DUMMY_TEXT,
                'basari_olcutleri': DUMMY_TEXT,
                'hedef_ve_amac': DUMMY_TEXT,
                'konu_ve_kapsam': DUMMY_TEXT,
                'literatur_ozeti': DUMMY_TEXT,
                'ozgun_deger': DUMMY_TEXT,
                'proje_belgeleri': 1,
                'yontem': DUMMY_TEXT,
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
                resp = self.client.post(cmd='ekle', form={'lab_id': "6Jy9r5e05DwsnkPGOesSvG9v6T8"})

                olanak = resp.json['forms']['model']['Olanak']

                assert resp.json['forms']['model']['form_name'] == 'ArastirmaOlanaklariForm'

                assert len(resp.json['forms']['model']['Olanak']) == 1

                # Personel ekleme ekranına gidilir
                resp = self.client.post(cmd='personel', form={'personel_ekle': 1,
                                                              'Olanak': olanak})

                assert resp.json['forms']['model']['form_name'] == 'PersonelEkleForm'

                # Personel eklenir
                resp = self.client.post(cmd='ekle',
                                        form={'personel_id': "L6j4ZvGts0XY5PKEiRPUiWxdTvy",
                                              'personel_ekle': 1})

                assert resp.json['forms']['model']['form_name'] == 'ArastirmaOlanaklariForm'

                assert len(resp.json['forms']['model']['Olanak']) == 2

                # Demirbas ekleme ekranına gidilir
                resp = self.client.post(cmd='demirbas')

                assert resp.json['forms']['schema']['title'] == "Makine, Teçhizat Ekle"

                resp = self.client.post(cmd='devam')

                assert resp.json['forms']['model']['form_name'] == 'MakineTechizatAraForm'

                resp = self.client.post(form={'ad': 'masa'}, cmd='ara')

                count = Demirbas.objects.all().search_on(
                    'ad', 'teknik_ozellikler', 'etiketler', contains='masa').count()
                dem = Demirbas.objects.all().search_on(
                    'ad', 'teknik_ozellikler', 'etiketler', contains='masa').values_list('key')[0]
                assert len(resp.json['objects']) == count + 1

                resp = self.client.post(object_id=dem, cmd='listeye_ekle')

                assert len(resp.json['forms']['model']['Olanak']) == 3

            resp = self.client.post(cmd='ilerle', form={'ileri': 1})

            assert resp.json['forms']['model']['form_name'] == 'ProjeCalisanlariForm'

            if loop == 0:
                form = {
                    'Calisan': [
                        {
                            'ad': "Orhan",
                            'soyad': "Veli",
                            'nitelik': "Şair",
                            'calismaya_katkisi': "Şiir",
                            'kurum': 'Ölü Ozanlar Derneği'
                        }
                    ],
                    'ileri': 1
                }
                # Calisan eklenir
                resp = self.client.post(cmd='ileri', form=form)
            else:
                resp = self.client.post(cmd='ileri')

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

                resp = self.client.post(cmd='ileri', form=form)
            else:
                resp = self.client.post(cmd='ileri')

            assert resp.json['forms']['schema']['title'] == "Bap İş Paketi Takvimi"

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
            resp = self.client.post(cmd='bitir', form={'bitir': 1})

            assert resp.json['forms']['model']['form_name'] == 'UniversiteDisiDestekForm'

            if loop == 0:
                form = {
                    'Destek': [
                        {
                            'destek_belgesi': pdf_belge,
                            'destek_belgesi_aciklamasi': "asd",
                            'destek_miktari': "asd",
                            'kurulus': "asd",
                            'sure': 12,
                            'tur': "asd",
                            'verildigi_tarih': "2017-07-17T21:00:00.000Z"
                        }
                    ],
                    'ileri': 1
                }
                resp = self.client.post(form=form)
            else:
                resp = self.client.post()

            assert resp.json['forms']['schema']['title'] == "Proje1 projesi için Bütçe Planı"

            # Bütçe planı ekranı
            resp = self.client.post(cmd='bitir', form={'bitir': 1})

            assert resp.json['forms']['model']['form_name'] == 'YurutucuTecrubesiForm'
            akademik_faaliyet = resp.json['forms']['model']['AkademikFaaliyet']

            resp = self.client.post(form={'ileri': 1,
                                          'AkademikFaaliyet': akademik_faaliyet if
                                          akademik_faaliyet else []}, cmd='ileri')

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
