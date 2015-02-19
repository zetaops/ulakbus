import os

__author__ = 'Evren Esat Ozkan'


def get_worfklow_path(wf_name):
    return "%s/workflows/%s.zip" % (os.path.dirname(os.path.realpath(__file__)), wf_name)
