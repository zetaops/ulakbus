# -*-  coding: utf-8 -*-
"""project settings"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
__author__ = 'Evren Esat Ozkan'
from zengine.settings import *
import os.path

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

DEFAULT_LANG = 'tr'

# path of the activity modules which will be invoked by workflow tasks
ACTIVITY_MODULES_IMPORT_PATHS.extend(['ulakbus.views', 'ulakbus.tasks'])
# absolute path to the workflow packages
WORKFLOW_PACKAGES_PATHS.append(os.path.join(BASE_DIR, 'diagrams'))

AUTH_BACKEND = 'ulakbus.models.auth.AuthBackend'

PERMISSION_MODEL = 'ulakbus.models.auth.Permission'
USER_MODEL = 'ulakbus.models.auth.User'
ROLE_MODEL = 'ulakbus.models.auth.Role'
# # left blank to use StreamHandler aka stderr
# LOG_HANDLER = os.environ.get('LOG_HANDLER', 'file')
#
# # logging dir for file handler
# LOG_DIR = os.environ.get('LOG_DIR', '/tmp/')

# DEFAULT_CACHE_EXPIRE_TIME = 99999999  # seconds

# diagrams that does not require logged in user
ANONYMOUS_WORKFLOWS = ['login', ]

# #PYOKO SETTINGS
DEFAULT_BUCKET_TYPE = os.environ.get('DEFAULT_BUCKET_TYPE', 'models')

DATE_DEFAULT_FORMAT = "%d.%m.%Y"
DATETIME_DEFAULT_FORMAT = "%d.%m.%Y %H:%s"

CRUD_MENUS = {
    # 'personel|ogrenci|personeller|ogrenciler': [{'name':'ModelName',
    #                                             'field':'field_name',
    #                                             'verbose_name': 'verbose_name',
    #                                             'category': 'Genel'
    #                                             'wf':'crud'}]
    # 'field' defaults to 'personel' or 'ogrenci'
    # verbose_name can be specified to override the model's verbose_name_plural
    'personel': [
        {'name': 'Personel', 'field':'object_id', 'wf': 'kimlik_ve_iletisim_bilgileri', 'verbose_name': 'Kimlik ve Iletisim Bilgileri'},
        {'name': 'KurumDisiGorevlendirmeBilgileri'},
        {'name': 'KurumIciGorevlendirmeBilgileri'},
        {'name': 'AdresBilgileri'},
        {'name': 'HizmetKurs'},
        {'name': 'HizmetOkul'},
        {'name': 'HizmetMahkeme'},
        {'name': 'HizmetBirlestirme'},
        {'name': 'HizmetTazminat'},
        {'name': 'HizmetUnvan'},
        {'name': 'HizmetAcikSure'},
        {'name': 'HizmetBorclanma'},
        {'name': 'HizmetIHS'},
        {'name': 'HizmetIstisnaiIlgi'},
        {'name': 'HizmetKayitlari'},
        {'name': 'AskerlikKayitlari'},
        {'name': 'Atama'},
        {'name': 'Kadro'},
        {'name': 'Izin'},
        {'name': 'UcretsizIzin'},
    ],
    'ogrenci': [
        {'name': 'DersKatilimi'},
        {'name': 'Borc'},
        {'name': 'DegerlendirmeNot'},
        {'name': 'OgrenciDersi'},
        {'name': 'Ogrenci', 'field':'object_id', 'wf':'ogrenci_kimlik_bilgileri', 'verbose_name': 'Kimlik Bilgileri'},
    ],
}
ADMIN_MENUS = [
    {'kategori': 'Admin', 'model': 'User', 'wf': 'crud', 'param': 'id', 'text': 'Kullanıcı'},
    {'kategori': 'Admin', 'model': 'Role', 'wf': 'crud', 'param': 'id', 'text': 'Rol'},
    {'kategori': 'Admin', 'model': 'Permission', 'wf': 'crud', 'param': 'id', 'text': 'Yetki'},
    {'kategori': 'Admin', 'model': 'Personel', 'wf': 'crud', 'param': 'id', 'text': 'Personel'},
    {'kategori': 'Admin', 'model': 'Ogrenci', 'wf': 'crud', 'param': 'id', 'text': 'Öğrenci'},
    {'kategori': 'Admin', 'model': 'Okutman', 'wf': 'crud', 'param': 'id', 'text': 'Okutman'},

]

VIEW_URLS.extend([
    # ('falcon URI template', 'python path to view method/class')
    ('/ara/ogrenci/{query}', 'ulakbus.views.system.SearchStudent'),
    ('/ara/personel/{query}', 'ulakbus.views.system.SearchPerson'),
    ('/notify/', 'ulakbus.views.system.Notification'),
])

ZATO_SERVER = os.environ.get('ZATO_SERVER', 'http://localhost:11223')

ENABLE_SIMPLE_CRUD_MENU = False
