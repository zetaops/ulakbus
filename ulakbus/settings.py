# -*-  coding: utf-8 -*-
"""project settings"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.settings import *
import os.path

__author__ = 'Evren Esat Ozkan'

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Localization/Internationalization settings defaults
DEFAULT_LANG = 'tr'
DEFAULT_LOCALIZATION_FORMAT = 'tr_TR'
# Available translations
TRANSLATIONS = ['tr', 'en']
# Locale options that should be given to the users for formatting of dates, numbers etc.
LOCALIZATION_FORMATS = ['en_US', 'en_GB', 'tr_TR']
# The directory containing the translations
TRANSLATIONS_DIR = os.path.join(BASE_DIR, 'locale')
# The language of messages in Ulakbus
TRANSLATION_DOMAINS['messages'] = 'tr'

# Default mail address
MAIL_ADDRESS = 'postmaster@mg.ulakbus.net'
# Demo main url
DEMO_URL = 'http://dev.zetaops.io'

# path of the activity modules which will be invoked by workflow tasks
ACTIVITY_MODULES_IMPORT_PATHS.extend(['ulakbus.views', 'ulakbus.tasks'])
# absolute path to the workflow packages
WORKFLOW_PACKAGES_PATHS.append(os.path.join(BASE_DIR, 'diagrams'))

SERVICE_PACKAGES_PATH = os.path.join(BASE_DIR, 'services')

LOG_FILE = os.environ.get('LOG_FILE', './ulakbus.log')

AUTH_BACKEND = 'ulakbus.models.auth.AuthBackend'

WF_INITIAL_VALUES = 'ulakbus.lib.view_helpers.WFValues'

PERMISSION_MODEL = 'ulakbus.models.auth.Permission'
USER_MODEL = 'ulakbus.models.auth.User'
ROLE_MODEL = 'ulakbus.models.auth.Role'
UNIT_MODEL = 'ulakbus.models.auth.Unit'
ABSTRACT_ROLE_MODEL = 'ulakbus.models.auth.AbstractRole'

# # left blank to use StreamHandler aka stderr
# LOG_HANDLER = os.environ.get('LOG_HANDLER', 'file')
#
# # logging dir for file handler
# LOG_DIR = os.environ.get('LOG_DIR', '/tmp/')

# DEFAULT_CACHE_EXPIRE_TIME = 99999999  # seconds

# diagrams that does not require logged in user
ANONYMOUS_WORKFLOWS.extend(['login', 'logout', 'parolami_unuttum', 'yeni_parola_belirle'])

#: Ortak kullanılan workflowlar
COMMON_WORKFLOWS.extend(['profil_sayfasi_goruntuleme', 'e_posta_degistir', 'kullanici_adi_degistir',
                         'parola_degistir'])

# #PYOKO SETTINGS
DEFAULT_BUCKET_TYPE = os.environ.get('DEFAULT_BUCKET_TYPE', 'models')

DATE_DEFAULT_FORMAT = "%d.%m.%Y"
DATETIME_DEFAULT_FORMAT = "%d.%m.%Y %H:%M:%S"

DEFAULT_WF_CATEGORY_NAME = 'Genel'
DEFAULT_OBJECT_CATEGORY_NAME = 'Seçime Uygun Görevler'

OBJECT_MENU = {
    # 'personel|ogrenci|personeller|ogrenciler': [{'name':'ModelName',
    #                                             'field':'field_name',
    #                                             'verbose_name': 'verbose_name',
    #                                             'category': 'Genel'
    #                                             'wf':'crud'}]
    # 'field' defaults to 'personel' or 'ogrenci'
    # verbose_name can be specified to override the model's verbose_name_plural
    'other': [
        {'name': 'Personel', 'category': 'Genel'},
        {'name': 'Ogrenci', 'category': 'Genel'},
        {'name': 'Okutman', 'category': 'Genel'},
        {'name': 'HariciOkutman', 'category': 'Genel'},
        {'name': 'Donem', 'category': 'Genel'},
        {'name': 'Program', 'category': 'Genel'},
        {'name': 'Ders', 'category': 'Genel'},
        {'name': 'Campus', 'category': 'Genel'},
        {'name': 'Building', 'category': 'Genel'},
        {'name': 'Room', 'category': 'Genel'},
        # {'name': 'AkademikTakvim', 'category': 'Genel'},
        {'name': 'OgrenciProgram', 'category': 'Genel'},
    ],
    'personel': [
        {'name': 'Personel', 'wf': 'kimlik_ve_iletisim_bilgileri',
         'verbose_name': 'Kimlik ve Iletisim Bilgileri', 'field': 'personel_id'},

        {'name': 'Izin', 'wf': 'izin', 'verbose_name': 'İzin İşlemleri', 'field': 'personel_id'},

        {'name': 'UcretsizIzin', 'wf': 'ucretsiz_izin', 'verbose_name': 'Ücretsiz İzin İşlemleri',
         'field': 'personel_id'},

        {'name': 'KurumDisiGorevlendirmeBilgileri', 'field': 'personel_id'},

        {'name': 'KurumIciGorevlendirmeBilgileri', 'field': 'personel_id'},

        {'name': 'AdresBilgileri', 'verbose_name': 'Adres Bilgileri', 'field': 'personel_id'},

        {'name': 'Atama', 'verbose_name': 'Atama İşlemleri', "wf": 'personel_atama',
         'field': 'personel_id'},

        {'name': 'Izin', 'verbose_name': 'İzin Başvuru', 'wf': 'izin_basvuru',
         'field': 'personel_id'},

        {'name': 'Personel', 'verbose_name': 'Akademik Personel Görev Süresi Uzatma',
         'wf': 'gorev_suresi_uzatma', 'field': 'personel_id'},

        {'name': 'Personel', 'verbose_name': 'Görevlendirme', 'wf': 'gorevlendirme',
         'field': 'personel_id'},

        {'name': 'Personel', 'verbose_name': 'Personel İşten Ayrılma', 'field': 'personel_id',
         'wf': 'personel_isten_ayrilma'},

        # Hitap İşlemleri
        {'name': 'HizmetKayitlari', 'verbose_name': 'Hizmet Cetveli', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'personel_hizmet_cetveli'},

        {'name': 'HizmetKurs', 'verbose_name': 'Kurs Bilgileri', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'HizmetOkul', 'verbose_name': 'Okul Bilgileri', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'HizmetMahkeme', 'verbose_name': 'Mahkeme Bilgileri', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'HizmetBirlestirme', 'verbose_name': 'Hizmet Birleştirme', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'HizmetTazminat', 'verbose_name': 'Tazminat Bilgileri', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'HizmetUnvan', 'verbose_name': 'Ünvan', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'HizmetAcikSure', 'verbose_name': 'Açık Süre Bilgileri', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'HizmetBorclanma', 'verbose_name': 'Borçlanma Bilgileri', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'HizmetIHS', 'verbose_name': 'İtibari Hizmet', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'HizmetIstisnaiIlgi', 'verbose_name': 'İstisnai İlgi', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},

        {'name': 'AskerlikKayitlari', 'verbose_name': 'Askerlik Kayıtları', 'field': 'personel_id',
         'category': 'Hitap İşlemleri', 'wf': 'crud_hitap'},
    ],
    'ogrenci': [
        {'name': 'Borc', 'verbose_name': 'Harç Bilgileri', 'field': 'ogrenci_id'},
        {'name': 'OgrenciProgram', 'verbose_name': 'Öğrenci Mezuniyet', 'wf': 'ogrenci_mezuniyet',
         'field': 'ogrenci_id'},
        {'name': 'DegerlendirmeNot', 'field': 'ogrenci_id'},
        {'name': 'OgrenciDersi', 'field': 'ogrenci_id'},
        {'name': 'Ogrenci', 'field': 'object_id', 'wf': 'ogrenci_kimlik_bilgileri',
         'verbose_name': 'Kimlik Bilgileri'},
        {'name': 'Ogrenci', 'field': 'object_id', 'wf': 'ogrenci_iletisim_bilgileri',
         'verbose_name': 'İletişim Bilgileri'},
        {'name': 'OncekiEgitimBilgisi', 'verbose_name': 'Önceki Eğitim Bilgileri',
         'field': 'ogrenci_id'},
        # {'name': 'OgrenciProgram', 'field': 'ogrenci_id', 'wf': 'ders_ekle',
        #  'verbose_name': 'Ders Ekle'},
        {'name': 'OgrenciProgram', 'field': 'ogrenci_id', 'wf': 'danisman_atama',
         'verbose_name': 'Danışman Atama'},
        {'name': 'DondurulmusKayit', 'verbose_name': 'Kayıt Dondurma', 'wf': 'kayit_dondur',
         'field': 'ogrenci_id'},
        {'name': 'OgrenciProgram', 'verbose_name': 'Mazaretli Öğrenci',
         'wf': 'mazeretli_ders_kaydi', 'field': 'ogrenci_id'},
        {'name': 'DegerlendirmeNot', 'verbose_name': 'Not Düzenleme',
         'wf': 'ogrenci_isleri_not_duzenleme',
         'field': 'ogrenci_id'},
        {'name': 'OgrenciProgram', 'verbose_name': 'Kayıt Sil', 'wf': 'kayit_sil',
         'field': 'ogrenci_id'},
        {'name': 'OgrenciDersi', 'verbose_name': 'Ders Ekle', 'wf': 'ogrenci_ders_atama',
         'field': 'ogrenci_id'}
    ],
}

AUTO_IMPORT_MODULES.extend([
    'ulakbus.views.system',
])

ZATO_SERVER = os.environ.get('ZATO_SERVER', 'http://localhost:11223')

ENABLE_SIMPLE_CRUD_MENU = False

ALLOWED_ORIGINS += [
    'http://ulakbus.net',
    'http://www.ulakbus.net',
    'http://dev.zetaops.io',
    'http://nightly.zetaops.io',
    'http://nightly.ulakbus.net'
]

UID = 173500

FILE_MANAGER = 'ulakbus.lib.s3_file_manager.S3FileManager'
ALLOWED_FILE_TYPES = {
    'png': ('image/png', 'png'),
    'txt': ('text/plain', 'txt'),
    'jpg': ('image/jpeg', 'jpg'),
    'jpeg': ('image/jpeg', 'jpg'),
    'pdf': ('application/pdf', 'pdf'),
    'doc': ('application/msword', 'doc'),
    'xls': ('application/vnd.ms-excel', 'xls'),
    'ppt': ('application/vnd.ms-powerpoint', 'ppt'),
    'pptx': ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'pptx'),
    'xlsx': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx'),
    'docx': ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx'),
}

S3_PROXY_URL = os.environ.get('S3_PROXY_URL')
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
S3_PUBLIC_URL = os.environ.get('S3_PUBLIC_URL')
S3_PROXY_PORT = os.environ.get('S3_PROXY_PORT', '80')
S3_BUCKET_NAME = 'ulakbus'

QUICK_MENU = [
    'kadro_islemleri',
    # 'izin',
    'akademik_takvim',
    'ders_hoca_sube_atama',
    'ders_ekle',
    'Birim',
    'Ders',
    'Program'
]

MAX_NUM_DROPDOWN_LINKED_MODELS = 20

PERMISSION_PROVIDER = 'ulakbus.models.auth.ulakbus_permissions'

ERROR_MESSAGE_500 = "DEMO Sisteminde güncelleme nedeniyle kesinti ve hata olabilir." \
                    "Şimdi bunlardan birini görüyorsunuz. Lütfen daha sonra tekrar deneyiniz"

SICIL_PREFIX = "KON"

#: User search method of messaging subsystem will work on these fields
MESSAGING_USER_SEARCH_FIELDS = ['name', 'surname']

#: Unit search method of messaging subsystem will work on these fields
MESSAGING_UNIT_SEARCH_FIELDS = ['name', ]

MESSAGES = {
    'lane_change_invite_title': 'Etkinlik gerekiyor!',
    'lane_change_invite_body': 'Bir iş akışı sizin etkinliğinizi gerektiriyor, '
                               'lütfen aşağıdaki bağlantıya tıklayarak akışa katılın:',
    'lane_change_message_title': 'Teşekkürler!',
    'lane_change_message_body': 'Bu iş akışında şuan için gerekli adımları tamamladınız. '
                                'İlgili kişiler, iş akışına katılmaları için haberdar edildiler.',

}
