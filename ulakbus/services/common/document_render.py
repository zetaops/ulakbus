# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zato.server.service import Service
import time
import requests
import io
import json
import hashlib
import copy
import base64
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
            # >>> curl localhost:11223/render/document -X POST -i -H "Content-Type: application/json" \
             - d '{"template": "http://example.com/sample_template.odt", \
             "context": {"name": "ali", "pdf":"1"}, "modify_date": "[hash_value_of_template]"}'

            --- The service will download the template and render with context data.
                Download rendred template and convert pdf file.

            # >>> curl localhost:11223/render/document -X POST -i -H "Content-Type: application/json" \
            -d "{\"template\": \"`base64 -w 0 template.odt`\", \"context\": {\"name\": \"ali\"}, \
             "modify_date": "[hash_value_of_template]"}"

            --- The service will decode the template and render with context data.

            The response is compatible with Zato-Wrapper.
            ::: On Success :::
                {"status": "finished", "result": "http://example.com/sample_rendered.odt"}
                {"status": "finished", "result": "http://example.com/sample.pdf"}

            :::   On Fail  :::
                {"status": "Error!", "result": "None"}
        """

    HAS_CHANNEL = True

    def handle(self):
        # Load the 3S configuration from ZATO.
        self.s3connect = False
        self.S3_PROXY_URL = self.user_config.zetaops.zetaops3s.S3_PROXY_URL
        self.S3_ACCESS_KEY = self.user_config.zetaops.zetaops3s.S3_ACCESS_KEY
        self.S3_SECRET_KEY = self.user_config.zetaops.zetaops3s.S3_SECRET_KEY
        self.S3_PUBLIC_URL = self.user_config.zetaops.zetaops3s.S3_PUBLIC_URL
        self.S3_PROXY_PORT = self.user_config.zetaops.zetaops3s.S3_PROXY_PORT
        self.S3_BUCKET_NAME = self.user_config.zetaops.zetaops3s.S3_BUCKET_NAME

        self.wants_pdf = self.request.payload.get('pdf', False)

        self.document_cache = DocumentCache(payload=self.request.payload,
                                            kvdb_conn=self.kvdb.conn,
                                            wants_pdf=self.wants_pdf,
                                            logger=self.logger)

        cache_stat = self.document_cache.check_the_cache()

        if cache_stat is None:
            self.logger.info("STANDART RENDERING PROCESS STARTED")
            resp = self.standard_process(payload=self.request.payload)

        else:
            # `cache_stat` can be context_value or template_value.
            value = self.get_value_from_cache(cache_stat=cache_stat)

            # if `value` is `template`. Use content of `template` on Redis.
            if value == self.document_cache.template:
                self.logger.info("NO NEED TO DOWNLOAD TEMPLATE")

                new_payload = self.create_new_payload()
                resp = self.standard_process(payload=new_payload)
            else:
                self.logger.info("NO ACTION WASN'T REQUIRED, SENDED URL")
                resp = self.prepare_response('ok', value)

        self.response.status_code = 200
        self.response.payload = resp

    def create_new_payload(self):
        """
        Create a new payload for no download the `template`
        Returns:
            dict: New payload.
        """
        new_payload = copy.copy(self.request.payload)
        new_payload['template'] = self.document_cache.template['content']
        return new_payload

    def get_value_from_cache(self, cache_stat):
        """
        Get URL on returned value from `DocumentCache`.
        Args:
            cache_stat (dict): Redis value.
        Returns:
            str: URL
            dict: `template` value on Redis.
        """
        def check_is_none(url, cache_stat):
            """
            Check url. If it's None, return `template`.
            Args:
                url (str):
                cache_stat (dict):
            Returns:
                str: URL
                dict: `template` value on Redis.
            """
            url_val = cache_stat.get(url, None)
            if url_val is None:
                return self.document_cache.template
            else:
                return url_val

        if self.wants_pdf:
            return check_is_none('pdf_url', cache_stat)

        else:
            return check_is_none('odt_url', cache_stat)

    def standard_process(self, payload):
        """
        It's a standard render process. The lead is shaped according to payload.
        Args:
            payload (dict)

        Returns:
            dict: Response.

        """
        resp = self.render_document(payload=payload)
        self.document_cache.add_rendered_doc(odt_url=resp.data['download_url'])

        if self.wants_pdf:
            file_desc = self.make_file_like_object(resp.data['download_url'], download_token=1)
            pdf_resp = self.create_pdf(file_desc)
            self.document_cache.add_rendered_pdf_doc(pdf_url=pdf_resp['download_url'])
            resp = self.prepare_response(pdf_resp['status'], pdf_resp['download_url'])
        else:
            resp = self.prepare_response('ok', resp.data['download_url'])
        return resp

    def render_document(self, payload):
        """
        Render ODT template file with context data.

        Args:
            payload (dict): Context data is variable of Jinja.

        Returns:
             response : Response object.

        """
        self.logger.info('{} :: DOCUMENT RENDER SERVICE CALLED '.format(time.ctime()))

        renderer = self.outgoing.plain_http.get('document.renderer')
        headers = {'X-App-Name': 'Zato', 'Content-Type': 'application/json'}

        resp = renderer.conn.send(self.cid, data=payload, headers=headers)
        return resp

    def create_pdf(self, file_desc):
        """
        Process of ODF to PDF. It's uses DocsBox Service.

        Args:
            file_desc (File or BytesIO): File or file-like object.

        Returns:
            dict: Status of process and download_url of pdf file.

        """
        self.logger.info('{} :: DOCSBOX SERVICE CALLED'.format(time.ctime()))
        # Get outgoing way.
        pdf_writer = self.outgoing.plain_http.get('docsbox.out')

        # Add to queue
        files = {'file': file_desc}

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
            return {"status": "error", "download_url": "None"}

    def check_the_status(self, request_period, task_id):
        """
        Check the status of task_id according to given request_period

        Args:
            request_period (int): How many times in second.
            task_id (str): ID of task.

        Returns:
            dict: return queue stats of task id.

        """
        pdf_writer_queue = self.outgoing.plain_http.get('docsbox.out.queue')
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
        self.logger.info('ELAPSED TIME : {}'.format(now_time - start_time))
        return queue_info

    def download_pdf_file(self, result_url):
        """
        Download pdf file from DocsBox Service. It has own channel.
        Args:
            result_url (str): This will be downloaded.

        Returns:
             BytesIO: PDF file.

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

    def s3_connect(self):
        """
        Connect to 3S server.
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

    def save_document(self, file_desc):
        """
        Save document to 3S bucket.

        Args:
            file_desc (File or BytesIO): File or file-like object.

        Returns:
             str: Key of saved file.

        """
        self.s3_connect()
        k = Key(self.bucket)
        k.set_contents_from_string(file_desc.getvalue())
        self.bucket.set_acl('public-read', k.key)
        return k.key

    @staticmethod
    def make_file_like_object(data, download_token=1):
        """
        Make the data file-like object.

        Args:
            data (bytes or str): If you send bytes, download_token must be 0.
            download_token (int): optional

        Returns:
            BytesIO: File-like object.

        """
        if download_token == 1:
            resp = requests.get(data)
            data = resp.content

        file_desc = io.BytesIO(data)
        file_desc.seek(0)

        return file_desc

    @staticmethod
    def prepare_response(status, url):
        """
        Prepare response for client. It's compatible with Zato-Wrapper.

        Args:
            status (str): Status of process.
            url (str): Download url of produced document.

        Returns:
            dict: Response for client.

        """
        resp = {"status": status, "result": url}
        return resp


class DocumentCache(object):
    """

        Caching mechanism. Add and get request and template from redis.

        ::: Scenario 1
            - If we have performed the request and modify_date of template on redis is equal
              the request modify_date send user the ODT or PDF URL.

        ::: Scenario 2
            - If we have performed the request and modify_date isn't equal the redis value.
              send base64 content of template. Or, We have the template but context isn't equal
              the redis value, don't download the template. Send base64 content of template

        """

    def __init__(self, payload, kvdb_conn, wants_pdf, logger):
        """
        Args:
            payload (dict): received request.
            kvdb_conn (object) : redis connection object.
            wants_pdf (bool):
        """
        self.kvdb_conn = kvdb_conn
        self.payload = payload
        self.wants_pdf = wants_pdf
        self.logger = logger

        self.context_key = self.key_from_context(context=self.payload['context'])
        self.template_key = self.key_from_template(template=self.payload['template'])

        self.context_value = None
        self.template_value = None

        self.template = None

    def key_from_context(self, context):
        """
        Sort and hash the `payload` data. It's the key of redis.
        Args:
            context (dict): Jinja2 variables.
        Returns:
            str: Sorted and hashed data.
        """
        key = "".join(["{}{}".format(k, v) for k, v in sorted(context.items())])
        key = self.hashing(key.encode())
        return key

    def key_from_template(self, template):
        """
        Take the hash of the template.
        If template is base64 encoded data, before decode it.

        Args:
            template (str): base64 encoded bytes or url

        Returns:
            str: Key format for redis. Hashed template.
        """

        if not template.startswith('http'):
            template = base64.b64decode(template)

        return self.hashing(template)

    def is_template_newest(self):
        """
        Check the `modify_date` are equal?
        Returns:
            bool:
        """
        if self.template_value is not None:
            return self.template_value['modify_date'] == self.payload['modify_date']

    def context_and_template_compatible(self):
        """
        Check `template` of `context_value` is equal to `template_key`
        Compare two entries on Redis.
        Returns:
            Bool: Is equal, returns True.
            None:
        """
        if self.context_value is not None:
            return self.context_value['template'] == self.template_key

    def check_the_cache(self):
        """
        Check the cache for the request processed before?

        Returns:
            dict: Template, context or None

        """
        self.context_value = self.get_value(self.context_key)
        self.template_value = self.get_value(self.template_key)

        if self.is_template_newest():
            self.template = self.template_value

        if self.template:
            if self.context_value and self.context_and_template_compatible():
                return self.context_value

        return self.template

    def get_value(self, key):
        """
        Get value of the `key` from redis.
        Args:
            key (str): Redis key.

        Returns:
            dict: Redis value or None.
        """
        value = self.kvdb_conn.get(key)

        if value is not None:
            return json.loads(value)

    def set_value(self, key, value):
        """
        Set key-value pair to Redis
        Args:
            key (str):
            value (object): This will dump with JSON.
        """
        value = json.dumps(value)
        self.kvdb_conn.set(key, value)

    def add_rendered_doc(self, odt_url):
        """
        Add rendered document url to Redis.
        Args:
            odt_url (str): S3 url of rendered ODT document.
        """

        # Add first entry to Redis. This is `context`.

        context_value = {"template": self.template_key,
                         "odt_url": odt_url,
                         "pdf_url": None}

        self.set_value(self.context_key, context_value)

        self.logger.info("CONTEXT VALUE ADDED TO REDIS")

        # If template is empty, we need to add second entry to Redis. This is `template`.

        if self.template is None:

            template_content = self.payload['template']
            if self.payload['template'].startswith('http'):
                self.logger.info("TEMPLATE IS DOWNLOADED and ADDED TO REDIS")
                file_desc = self.download_template(self.payload['template'])
                template_content = base64.b64encode(file_desc.getvalue())

            template_value = {"modify_date": self.payload['modify_date'],
                              "content": template_content}

            self.set_value(self.template_key, template_value)

    def add_rendered_pdf_doc(self, pdf_url):
        """
        Update value of `context` key.
        Args:
            pdf_url (str):
        """
        context_value = self.get_value(self.context_key)

        if context_value is not None:
            self.logger.info("PDF URL ADDING TO REDIS")
            context_value['pdf_url'] = pdf_url
            self.set_value(self.context_key, context_value)

    @staticmethod
    def download_template(template_url):
        """
        Args:
            template_url: (string) url of template file
        Returns:
            return downloaded file
        """
        response = requests.get(template_url)
        file_desc = io.BytesIO(response.content)
        return file_desc

    @staticmethod
    def hashing(data):
        """
        Returns hashed value of the param `data`.

        Args:
            data (str): Encoded bytes

        Returns:
            str: Hashed data.

        """
        return hashlib.sha256(data).hexdigest()
