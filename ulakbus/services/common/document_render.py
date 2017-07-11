# -*- coding: utf-8 -*-

from zato.server.service import Service
import time


class RenderDocument(Service):
    """ The submitted template is rendered with the context data and the download link is sent back.

    ::: Requirements :::
        - template : It can be base64 encoded data or URL
        - context  : Have to be a dict.

    :::   Response   :::
        - download_url : The URL of the rendered template

    :::    Client    :::
        >>> curl localhost:3002/v1 -X POST -i -H "Content-Type: application/json" -d '{"template": "http://example.com/sample_template.odt", "context": {"name": "ali"}}'
        --- The service will download the template and render with context data.

        >>> curl localhost:3002/v1 -X POST -i -H "Content-Type: application/json" -d "{\"template\": \"`base64 -w 0 template.odt`\", \"context\": {\"name\": \"ali\"}}"
        --- The service will decode the template and render with context data.

        ::: On Success :::
            {"download_url": "http://example.com/sample_rendered.odt"}
    """

    HAS_CHANNEL = True

    def handle(self):
        self.logger.info('{} :: Document render service called'.format(time.ctime()))

        renderer = self.outgoing.plain_http.get('DocumentRenderer')

        headers = {'X-App-Name': 'Zato', 'Content-Type': 'application/json'}
        resp = renderer.conn.send(self.cid, data=self.request.payload, headers=headers)

        self.response.payload = resp.data
