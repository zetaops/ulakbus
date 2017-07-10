# -*- coding: utf-8 -*-

from zato.server.service import Service


class RenderDocuments(Service):
    def handle(self):
        self.logger.info('Request: {}'.format(self.request.payload))
        self.logger.info('Request-Type: {}'.format(type(self.request.payload)))

        renderer = self.outgoing.plain_http.get('DocumentRenderer')

        headers = {'X-App-Name': 'Zato', 'Content-Type': 'application/json'}

        resp = renderer.conn.send(self.cid, data=self.request.payload, headers=headers)

        self.logger.info('Response: {}'.format(resp))
        self.logger.info('Response-Type: {}'.format(type(resp)))

        self.response.payload = resp.data

