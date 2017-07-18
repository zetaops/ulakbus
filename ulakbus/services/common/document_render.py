# -*- coding: utf-8 -*-

from zato.server.service import Service
import time
import requests
import io
import json
from boto.s3.connection import S3Connection as s3
from boto.s3.key import Key


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
        self.S3_PROXY_URL = self.user_config.zetaops.zetaops3s.S3_PROXY_URL
        self.S3_ACCESS_KEY = self.user_config.zetaops.zetaops3s.S3_ACCESS_KEY
        self.S3_SECRET_KEY = self.user_config.zetaops.zetaops3s.S3_SECRET_KEY
        self.S3_PUBLIC_URL = self.user_config.zetaops.zetaops3s.S3_PUBLIC_URL
        self.S3_PROXY_PORT = self.user_config.zetaops.zetaops3s.S3_PROXY_PORT
        self.S3_BUCKET_NAME = self.user_config.zetaops.zetaops3s.S3_BUCKET_NAME

        # Standart render process
        resp = self.render_document(payload=self.request.payload)

        wants_pdf = 'pdf' in self.request.payload
        if wants_pdf:
            file_desc = self.make_file_like_object(resp.data['download_url'])
            pdf_resp = self.create_pdf(file_desc)
            resp = self.prepare_response(pdf_resp['status'], pdf_resp['download_url'])
        else:
            resp = self.prepare_response('finished', resp.data['download_url'])

        self.response.payload = resp

    @staticmethod
    def prepare_response(status, url):
        """ Prepare a response for client
        :param status: Message of status
        :param url: Download_url, It can be None or URL
        :return: type: <dict>
        """
        resp = {"status": status, "download_url": url}
        return resp

    def render_document(self, payload):
        """ Render ODT file.
        :param payload:
        :return:
        """
        self.logger.info('{} :: Document render service called'.format(time.ctime()))

        renderer = self.outgoing.plain_http.get('document.renderer')
        headers = {'X-App-Name': 'Zato', 'Content-Type': 'application/json'}

        resp = renderer.conn.send(self.cid, data=payload, headers=headers)
        return resp

    @staticmethod
    def make_file_like_object(data, download_token=1):
        """  Make file-like object from url.
        :param data: URL or Value
        :param download_token: Will the
        :return: BytesIO object
        """
        file_desc = None
        if download_token == 1:
            s3_resp = requests.get(data)
            file_desc = io.BytesIO(s3_resp.content)
        else:
            file_desc = io.BytesIO(data)
        file_desc.seek(0)
        return file_desc

    def create_pdf(self, file_desc):
        """ ODF to PDF
        :param file_desc: File-like object
        :return:
        """
        self.logger.info('{} :: Docsbox service called'.format(time.ctime()))
        # Get outgoing way.
        pdf_writer = self.outgoing.plain_http.get('docsbox.out')

        # Add to queue
        files = {'file':file_desc}
        headers = {'Content-Type': 'multipart/form-data'}

        result = pdf_writer.conn.post(self.cid, files=files)
        task_info = json.loads(result.text)

        task_id = task_info['id'].encode('utf-8')

        # Chect the queue for 3 seconds.
        task_queue_status = self.check_the_status(request_period=3,
                                                  task_id=task_id)
        # Send back to client
        if task_queue_status['status'] == 'finished':

            pdf_file = self.download_pdf_file(task_queue_status['result_url'])
            # Save PDF file to S3 Server
            s3_url = self.save_document(pdf_file)
            task_queue_status['download_url'] = "{0}{1}".format(self.S3_PUBLIC_URL, s3_url)
            return task_queue_status
        else:
            return '{"status":"Error!", "download_url":"None"}'

    def download_pdf_file(self, result_url):
        """ Download pdf file from Docsbox service
        :param result_url: URL of pdf file.
        :return: PDF file, type: <BytesIO>
        """
        # Get outgoing connection of zato.
        download_pdf = self.outgoing.plain_http.get('download_pdf')
        params = {"req_param": result_url}
        headers = {'Content-Type': 'multipart/form-data'}
        # Make request to download pdf file with params and headers.
        download_pdf_result = download_pdf.conn.get(self.cid, params=params, headers=headers)
        # Make a BytesIO object of DOCSBOX result_url.
        pdf_file = self.make_file_like_object(download_pdf_result._content, download_token=0)

        return pdf_file

    def check_the_status(self, request_period, task_id):
        """ Check the status of task_id according to given request_period
        :param request_period:
        :param task_id:
        :return:
        """
        pdf_writer_queue = self.outgoing.plain_http.get('docsbox.out.queue')
        self.logger.info('ATTR : {}'.format(pdf_writer_queue.__dict__))
        start_time = time.time()
        now_time = 0.0
        while True:
            params = {'task_id': '{}'.format(task_id)}

            queue_info = pdf_writer_queue.conn.get(self.cid, params)
            queue_info = json.loads(queue_info.text)

            if queue_info['status'] == 'finished':
                break
            now_time = time.time()
            if (now_time - start_time) >= request_period:
                break
        self.logger.info('Elapsed time : {}'.format(now_time-start_time))
        return queue_info

    def s3_connect(self):
        """ Connect to 3S server
        :return:
        """
        if self.s3connect:
            return

        conn = s3(aws_access_key_id=self.S3_ACCESS_KEY,
                  aws_secret_access_key=self.S3_SECRET_KEY,
                  proxy=self.S3_PROXY_URL,
                  proxy_port=self.S3_PROXY_PORT,
                  is_secure=False)
        self.bucket = conn.get_bucket(self.S3_BUCKET_NAME)
        self.s3connect = True

    def save_document(self, pdf_file):
        """
        Save document to S3 bucket
        Args:
            pdf_file: file-like object, BytesIO
        Returns:
            (str) key of file
        """
        self.s3_connect()
        k = Key(self.bucket)
        k.set_contents_from_string(pdf_file.getvalue())
        self.bucket.set_acl('public-read', k.key)
        return k.key


class DocumentCache:
    def __init__(self, zato_service):
        self.zato_service = zato_service

    def key_from_context(self):
        """ Sort and convert string of request.payload. Make key, from context data
        :return: produced key. type: <str>
        """
        context = self.zato_service.request.payload['context']
        context = json.loads(context)
        key = "".join(["{}{}".format(k, v) for k, v in sorted(context.items())])
        return key

    def check_context(self):
        key = self.key_from_context()
        val_of_context = self.zato_service.kvdb.conn.get(key)
        if val_of_context is not None:
            pass

