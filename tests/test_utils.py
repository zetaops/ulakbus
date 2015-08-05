import os
import threading
from time import sleep

__author__ = 'Evren Esat Ozkan'


def get_worfklow_path(wf_name):
    return "%s/workflows/%s.zip" % (os.path.dirname(os.path.realpath(__file__)), wf_name)


import requests
from pprint import pprint
import json


class Request(object):
    def __init__(self, wfname):
        self.wfname = wfname

    def request(self, **data):
        threading.Thread(target=self._request, args=(self.wfname,), kwargs=data).start()

    def _request(wfname, data):
        url = 'http://localhost:9001/%s/' % wfname
        sleep(0.1)
        r = requests.post(url, data=json.dumps(data))
        pprint(r.headers)
        print(r.content)

