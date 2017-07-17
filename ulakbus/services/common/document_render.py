# -*- coding: utf-8 -*-

from zato.server.service import Service
import time
import requests
import io
import json
from boto.s3.connection import S3Connection as s3
from boto.s3.key import Key

"""
S3_PROXY_URL = os.environ.get('S3_PROXY_URL')
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
S3_PUBLIC_URL = os.environ.get('S3_PUBLIC_URL')
S3_PROXY_PORT = os.environ.get('S3_PROXY_PORT', '80')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'my_bucket')
MAX_UPLOAD_TEMPLATE_SIZE = os.environ.get('MAX_UPLOAD_TEMPLATE_SIZE',
                                          False) or 3 * 1024 * 1024  # 3MB
"""

class RenderDocument(Service):
    """ The submitted template is rendered with the context data and the download link is sent back.
        If context data includes 'pdf', rendered document is converted to pdf.

    ::: Requirements :::
        - template : It can be base64 encoded data or URL
        - context  : Have to be a dict.
            - pdf  : Rendered document is converted to pdf.

    :::   Response   :::
        - status       : Status of request.
        - download_url : The URL of the rendered template

    :::    Client    :::
        # >>> curl localhost:11223/render/document -X POST -i -H "Content-Type: application/json" -d '{"template": "http://example.com/sample_template.odt", "context": {"name": "ali", "pdf":"1"}}'
        --- The service will download the template and render with context data. Download rendred template and convert pdf file.

        # >>> curl localhost:11223/render/document -X POST -i -H "Content-Type: application/json" -d "{\"template\": \"`base64 -w 0 template.odt`\", \"context\": {\"name\": \"ali\"}}"
        --- The service will decode the template and render with context data.

        ::: On Success :::
            {"status": "finished", "download_url": "http://example.com/sample_rendered.odt"}
            {"status": "finished", "download_url": "http://example.com/sample.pdf"}

        :::   On Fail  :::
            {"status": "Error!", "download_url": "None"}
    """

    HAS_CHANNEL = True

    def handle(self):

        self.s3connect = False
        # Load the 3S configuration from ZATO.
        self.DOSBOX_URL = self.user_config.zetaops.zetaops3s.DOCSBOX_URL
        self.S3_PROXY_URL = self.user_config.zetaops.zetaops3s.S3_PROXY_URL
        self.S3_ACCESS_KEY = self.user_config.zetaops.zetaops3s.S3_ACCESS_KEY
        self.S3_SECRET_KEY = self.user_config.zetaops.zetaops3s.S3_SECRET_KEY
        self.S3_PUBLIC_URL = self.user_config.zetaops.zetaops3s.S3_PUBLIC_URL
        self.S3_PROXY_PORT = self.user_config.zetaops.zetaops3s.S3_PROXY_PORT
        self.S3_BUCKET_NAME = self.user_config.zetaops.zetaops3s.S3_BUCKET_NAME
        self.MAX_UPLOAD_TEMPLATE_SIZE = 3 * 1024 * 1024

        self.logger.info('{} :: Document render service called'.format(time.ctime()))

        renderer = self.outgoing.plain_http.get('document.renderer')
        headers = {'X-App-Name': 'Zato', 'Content-Type': 'application/json'}

        resp = renderer.conn.send(self.cid, data=self.request.payload, headers=headers)

        # If client wants a pdf, send pdf download_url to client
        if 'pdf' in self.request.payload:
            self.logger.info('{} :: create_pdf method called'.format(time.ctime()))
            pdf_resp = self.create_pdf(resp.data['download_url'])
            resp = {"status": pdf_resp['status'], "download_url": pdf_resp['download_url']}
            self.response.payload = resp

        # Just send download_url to client
        else:
            r = {"status":"finished", "download_url":resp.data['download_url']}
            self.response.payload = r

    @staticmethod
    def make_file_like_object(download_url):
        """  Make file-like object from url.
        :param download_url:
        :return: BytesIO object
        """
        s3_resp = requests.get(download_url)
        file_desc = io.BytesIO(s3_resp.content)
        file_desc.seek(0)
        return file_desc

    