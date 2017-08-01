# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import base64
import os
from uuid import uuid4
from boto.s3.connection import S3Connection as s3
from boto.s3.key import Key
from pyoko.conf import settings
import zipfile
from ulakbus.lib.common import get_file_url
from io import BytesIO


class S3FileManager(object):
    def __init__(self):
        self.conn = s3(aws_access_key_id=settings.S3_ACCESS_KEY,
                       aws_secret_access_key=settings.S3_SECRET_KEY,
                       proxy=settings.S3_PROXY_URL,
                       proxy_port=settings.S3_PROXY_PORT,
                       is_secure=False)
        self.bucket = self.conn.get_bucket(settings.S3_BUCKET_NAME)

    def store_file(self, **kwargs):
        content = kwargs['content']
        k = Key(self.bucket)
        filename = None
        if 'name' in kwargs:
            filename, extension = os.path.splitext(kwargs['name'])
            filename = filename.replace(" ", "")
            extension = extension.replace('.', '')
        if 'ext' in kwargs:
            extension = kwargs['ext']
        typ, ext = settings.ALLOWED_FILE_TYPES[extension]
        if "type" in kwargs:
            typ = kwargs['type']
        if 'random_name' in kwargs:
            filename = None
        k.key = "%s.%s" % (filename or uuid4().hex, ext)
        k.content_type = typ
        try:
            content = base64.decodestring(content.split('base64,')[1])
        except IndexError:
            content = base64.decodestring(content)

        k.set_contents_from_string(content)
        self.bucket.set_acl('public-read', k.key)
        return k.key

    def download_files_as_zip(self, keys, zip_name):
        """
        Args:
            keys(list): s3'e kaydedilen dosyaların key'lerinden oluşan list
            zip_name(str): oluşturulacak zip dosyasının adı

        Returns:
            Oluşturulan zip dosyasının url'i döndürülür.

        """
        zip_name = "%s.zip" % zip_name
        temp_zip_file = BytesIO()
        zip_file = zipfile.ZipFile(temp_zip_file, mode='w', compression=zipfile.ZIP_DEFLATED)
        for file_key in keys:
            temp_file = BytesIO()
            self.bucket.get_key(file_key).get_contents_to_file(temp_file)
            zip_file.writestr(file_key, temp_file.getvalue())
        zip_file.close()
        content = base64.b64encode(temp_zip_file.getvalue())
        key = self.store_file(name=zip_name, content=content, type='application/zip', ext='zip')
        return get_file_url(key)

    def get_last_modified_date(self, key):
        """

        Args:
            key(str): s3 key

        Returns (str):
            last modified datetime of object

        """
        k = self.bucket.get_key(key)
        return k.last_modified
