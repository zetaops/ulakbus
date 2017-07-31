# -*- coding: utf-8 -*-

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
        # >>> curl localhost:11223/render/document -X POST -i -H "Content-Type: application/json" -d '{"template": "http://example.com/sample_template.odt", "context": {"name": "ali", "pdf":"1"}, "modify_date": "[hash_value_of_template]"}'
        --- The service will download the template and render with context data. Download rendred template and convert pdf file.

        # >>> curl localhost:11223/render/document -X POST -i -H "Content-Type: application/json" -d "{\"template\": \"`base64 -w 0 template.odt`\", \"context\": {\"name\": \"ali\"}, "modify_date": "[hash_value_of_template]"}"
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

        self.s3connect = False
        # Load the 3S configuration from ZATO.
        self.S3_PROXY_URL = self.user_config.zetaops.zetaops3s.S3_PROXY_URL
        self.S3_ACCESS_KEY = self.user_config.zetaops.zetaops3s.S3_ACCESS_KEY
        self.S3_SECRET_KEY = self.user_config.zetaops.zetaops3s.S3_SECRET_KEY
        self.S3_PUBLIC_URL = self.user_config.zetaops.zetaops3s.S3_PUBLIC_URL
        self.S3_PROXY_PORT = self.user_config.zetaops.zetaops3s.S3_PROXY_PORT
        self.S3_BUCKET_NAME = self.user_config.zetaops.zetaops3s.S3_BUCKET_NAME

        self.logger.info("PAYLOAD CONTENT : {}".format(self.request.payload))

        if 'pdf' in self.request.payload:
            if self.request.payload['pdf'] == True:
                self.wants_pdf = True
            else:
                self.wants_pdf = False
        self.document_cache = DocumentCache(self, self.wants_pdf)
        # Check the request in the cache
        cache_stat = self.document_cache.check_the_cache()

        if cache_stat is not None:
            # No action required
            if 'odt_url' in cache_stat:
                if self.wants_pdf:
                    self.logger.info("NO ACTION WASN'T REQUIRED, SENDED PDF URL")
                    resp = self.prepare_response('ok', cache_stat['pdf_url'])
                else:
                    resp = self.prepare_response('ok', cache_stat['odt_url'])
                    self.logger.info("NO ACTION WASN'T REQUIRED, SENDED ODT URL")
            # No need to download template
            elif 'modify_date' in cache_stat:
                self.logger.info("NO NEED TO DOWNLOAD TEMPLATE")
                new_payload = copy.copy(self.request.payload)
                new_payload['template'] = cache_stat['template']
                resp = self.standard_process(new_payload)
            # Standard rendering process
        else:
            self.logger.info("STANDARD RENDERING PROCESS")
            resp = self.standard_process(self.request.payload)

        self.response.status_code = 200
        self.response.payload = resp

    def standard_process(self, payload):
        """
        It's a standard render process. The lead is shaped according to payload.
        Args:
            payload: type: <dict>

        Returns: Response. type: <dict>

        """
        file_name = payload['template']
        if payload['template'].startswith('http'):
            template_file = self.download_template(payload['template'])
            payload['template'] = base64.b64encode(template_file.getvalue())

        file_content = payload['template']

        self.logger.info("TYPE : {}, CONTENT : {}".format(type(payload), payload))

        resp = self.render_document(payload=payload)

        self.document_cache.add_rendered_doc(file_name=file_name,
                                             odt_url=resp.data['download_url'],
                                             file_content=file_content)

        if self.wants_pdf:
            file_desc = self.make_file_like_object(resp.data['download_url'])
            pdf_resp = self.create_pdf(file_desc)
            self.document_cache.add_rendered_pdf_doc(file_name=file_name,
                                                     pdf_url=pdf_resp['download_url'],
                                                     odt_url=resp.data['download_url'])

            resp = self.prepare_response("ok", pdf_resp['download_url'])
        else:
            resp = self.prepare_response('ok', resp.data['download_url'])
        return resp

    @staticmethod
    def prepare_response(status, url):
        """
        Prepare response for client. It's compatible with Zato-Wrapper.

        Args:
            status: Status of process. type: <str>
            url: Download url of produced document. type: <str>

        Returns: type: <dict>

        """
        resp = {"status": status, "result": url}
        return resp

    def render_document(self, payload):
        """
        Render ODT template file with context data.

        Args:
            payload: Context data is variable of Jinja.

        Returns: Response object.

        """
        self.logger.info('{} :: Document render service called'.format(time.ctime()))

        renderer = self.outgoing.plain_http.get('document.renderer')
        headers = {'X-App-Name': 'Zato', 'Content-Type': 'application/json'}

        resp = renderer.conn.send(self.cid, data=payload, headers=headers)
        return resp

    @staticmethod
    def make_file_like_object(data, download_token=1):
        """
        Make the data file-like object.

        Args:
            data: type: <bytes>, but you must assign download_token to 0.
                  It can be <str>
            download_token: <optional> type: <int>

        Returns: BytesIO object.

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
        """
        Process of ODF to PDF. It's uses DocsBox Service.

        Args:
            file_desc: File or file-like object.

        Returns: type: <dict>

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
            return {"status":"Error!", "download_url":"None"}

    def download_pdf_file(self, result_url):
        """
        Download pdf file from DocsBox Service. It has own channel.
        Args:
            result_url: This will be downloaded.

        Returns: PDF file, type: <BytesIO>

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
        """
        Check the status of task_id according to given request_period

        Args:
            request_period: type: <int>
            task_id: type: <str>

        Returns: type: <dict>

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
        """
        Connect to 3S server.

        Returns: None

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
        Save document to 3S bucket.

        Args:
            pdf_file: file-like object. type: <BytesIO>

        Returns: key of file.

        """
        self.s3_connect()
        k = Key(self.bucket)
        k.set_contents_from_string(pdf_file.getvalue())
        self.bucket.set_acl('public-read', k.key)
        return k.key

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


class DocumentCache:
    """

    Caching mechanism. Add and get request and template from redis.

    ::: Scenario 1
        - If we have performed the request and modify_date of template on redis is equal the request modify_date
          send user the ODT or PDF URL.

    ::: Scenario 2
        - If we have performed the request and modify_date isn't equal the redis value. Send base64 content of template
          Or, We have the template but context isn't equal the redis value, don't download the template. Send base64
          content of template

    """
    def __init__(self, zato_service, wants_pdf):
        """
        Constructor of caching mechanism.

        Args:
            zato_service: It's a ZatoService. i.e DocumentRender.
            wants_pdf: type: <Boolean>
        """
        self.zato_service = zato_service
        self.wants_pdf = wants_pdf

    @staticmethod
    def hashing(data):
        """
        Hash the data of param.

        Args:
            data: Encoded bytes data.

        Returns: Hashed data. type: <str>

        """
        return hashlib.sha256(data).hexdigest()

    def key_from_context(self):
        """
        Sort and hash the context data. It's a key of redis.

        Returns: Sorted and hashed data. type: <str>

        """
        context = self.zato_service.request.payload['context']
        key = "".join(["{}{}".format(k, v) for k, v in sorted(context.items())])
        key = self.hashing(key.encode())
        return key

    def value_of_context(self, file_name, pdf_url, odt_url):
        """
        Make dict. The produced data will be used for redis value of context key.

        Args:
            file_name: Encoded bytes
            pdf_url: <str>
            odt_url: <str>

        Returns:
            Return value of context key. type: <dict>

        """
        # Hash value of template.
        template = self.key_hash_template(payload=file_name)
        return {"template": template, "odt_url": odt_url, "pdf_url": pdf_url}

    def value_of_template(self, file_content):
        """
        Make dict. The produced data will be used for redis value of template key.

        Args:
            file_content: base64 encoded data

        Returns: Value of template key on redis. type: <dict>

        """

        modify_date = self.zato_service.request.payload['modify_date']
        template_content = file_content
        return {'modify_date': modify_date, 'template': template_content}

    def key_hash_template(self, payload):
        """
        Take the hash of the template.
        If template is base64 encoded data, before decode it.

        Args:
            payload: Encoded bytes

        Returns: Key format for redis. Hashed template. type: <str>
        """

        if payload.startswith('http'):
            template = self.hashing(payload)
        else:
            template = base64.b64decode(payload)
            template = self.hashing(template)
        return template

    def add_rendered_doc(self, file_name, odt_url, file_content):
        """
        Add to redis that rendered document. PDF url is null, because it hasn't produced yet.
        It will add 2 rows to redis.
        First; Key: Context. Value: PDF_URL, ODT_URL and TEMPLATE_KEY
        Second, Key: TEMPLATE_KEY. Value: modify_date and TEMPLATE. TEMPLATE is base64 encoded.
        Args:
            file_name: key on redis.
            odt_url: rendered odt file url. type: <str>
            file_content: base64 encoded data of rendered document.

        Returns: None.

        """
        self.zato_service.logger.info("ADD_RENDERED_DOC method is runining..")
        key = self.key_from_context()
        value = self.value_of_context(file_name=file_name, odt_url=odt_url, pdf_url=None)

        value = json.dumps(value)
        self.zato_service.kvdb.conn.set(key, value)

        template_key = self.key_hash_template(file_name)
        template_value = self.value_of_template(file_content)

        template_value = json.dumps(template_value)
        self.zato_service.kvdb.conn.set(template_key, template_value)

    def add_rendered_pdf_doc(self, file_name=None, pdf_url=None, odt_url=None):
        """
        Get context key from redis and update pdf_url

        Args:
            file_name:
            pdf_url:
            odt_url:

        Returns: None

        """
        self.zato_service.logger.info("add_rendered_pdf_doc cagirildi")
        key = self.key_from_context()
        template_key = self.key_hash_template(file_name)

        value = self.zato_service.kvdb.conn.get(key)
        value = json.loads(value)

        if value['template'] == template_key:
            self.zato_service.logger.info("template ile template_key karşılaştırıldı ve pdf_url güncelleniyor.")
            value['pdf_url'] = pdf_url

            value = json.dumps(value)
            self.zato_service.kvdb.conn.set(key, value)

    def get_context(self):
        """
        Convert context to key format. (Sorted and hashed)
        Get key from redis.

        Returns: If redis has the key, return value. type: <dict>
                 If redis hasn't the key, return None. type: <NoneType>

        """
        key = self.key_from_context()
        val_of_context = self.zato_service.kvdb.conn.get(key)

        if val_of_context is None:
            return None

        val_of_context = json.loads(val_of_context)
        return val_of_context

    def get_template(self):
        """
        Convert template to key format. (Hashed)
        Get key from redis.

        Returns: If redis has the key, return value. type: <dict>
                 If redis hasn't the key, return None. type: <NoneType>

        """
        key = self.key_hash_template(self.zato_service.request.payload['template'])
        value = self.zato_service.kvdb.conn.get(key)

        if value is None:
            return None

        value = json.loads(value)
        return value

    def check_the_cache(self):
        """
        Check the request for we have already performed the request.
        Get context and template from redis.

        Returns: If we have performed the request, return value of redis. type: <dict>
                 If we haven't performed the request, return None. type: <NoneType>

        """
        val_context = self.get_context()
        val_template = self.get_template()

        key_template = self.key_hash_template(self.zato_service.request.payload['template'])
        modify_date = self.zato_service.request.payload['modify_date']


        # This request wasn't proceded before.
        if val_context is None:
            # So Should we download template file?

            if val_template is None:
                # No, this request hasn't seen before.
                return None
            else:
                # We have the template, but is it newest?
                if val_template['modify_date'] == modify_date:
                    return val_template
                else:
                    return None

        else:
            # Check the context. Is it newest?
            if val_context['template'] == key_template and val_template['modify_date'] == modify_date:
                # PDF wants?
                if self.wants_pdf:
                    # We have the pdf url, return context.
                    if val_context['pdf_url'] is not None:
                        return val_context
                    else:
                        return val_template
                else:
                    return val_context
            else:
                return None

