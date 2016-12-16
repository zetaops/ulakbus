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


class S3FileManager(object):
    def __init__(self):
        self.conn = s3(aws_access_key_id=settings.S3_ACCESS_KEY,
                       aws_secret_access_key=settings.S3_SECRET_KEY,
                       proxy=settings.S3_PROXY_URL,
                       proxy_port=settings.S3_PROXY_PORT,
                       is_secure=False)

    def store_file(self, **kwargs):
        bucket = self.conn.get_bucket(settings.S3_BUCKET_NAME)
        content = kwargs['content']
        k = Key(bucket)
        filename = None
        if 'name' in kwargs:
            filename, extension = os.path.splitext(kwargs['name'])
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
        bucket.set_acl('public-read', k.key)
        return k.key

    @staticmethod
    def get_url(key):
        return "%s%s" % (settings.S3_PUBLIC_URL, key)
