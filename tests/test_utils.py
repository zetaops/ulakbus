# -*-  coding: utf-8 -*-
import os
from werkzeug.test import Client
import json
from zengine.dispatcher import app

__author__ = 'Evren Esat Ozkan'


def get_worfklow_path(wf_name):
    return "%s/workflows/%s.zip" % (
        os.path.dirname(os.path.realpath(__file__)), wf_name)


from pprint import pprint
import json


class TestClient(object):
    def __init__(self, workflow):
        self.workflow = workflow
        self._client = Client(app)
        self.headers = {}

    def set_workflow(self, workflow):
        self.workflow = workflow

    def post(self, **data):
        """
        by default data dict encoded as json and
        content type set as application/json
        :param data: post data,
        :return: tuple with 3 items :
            [response_content as list],
            response_code,
            {response_headers as dict}
        """

        make_json = not data.pop('no_json', False)
        if make_json:
            self.headers.update({'Content-Type': 'application/json'})
        if 'headers' in data:
            self.headers.update(data.pop('headers'))
        if '_data' in data:
            post_data = data.pop('_data')
        else:
            post_data = data
        if make_json:
            post_data = json.dumps(post_data)
        resp = type('resp',(object,),{})
        (resp.content,
         resp.code,
         resp.headers) = self._client.post(self.workflow,
                                           data=data,
                                           headers=self.headers)
        resp.content = list(resp.content)
        resp.json = json.loads(resp.content[0])
        return resp


class BaseTestCase:
    client = None

    @classmethod
    def prepare_client(self, workflow_name):
        if not self.client:
            self.client = TestClient(workflow_name)
