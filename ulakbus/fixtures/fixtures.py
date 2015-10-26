import json
import os
import riak
from ulakbus import settings

client = riak.RiakClient(protocol=settings.RIAK_PROTOCOL, host=settings.RIAK_SERVER, port=settings.RIAK_PROTOCOL)
fix_bucket = client.bucket_type('models').bucket('ulakbus_fixtures')
FIXTURES_FILE = os.environ.get('FIXTURES_FILE',
                               '/'.join([os.path.dirname(os.path.realpath("__file__")), 'settings.json']))

with open("settings.json", "r") as fixtures_file:
    fixtures = json.load(fixtures_file)
    for fix in fixtures:
        f = fix_bucket.get(fix)
        f.data = fixtures[fix]
        print "%s: %s kaydediliyor" % (fix, fixtures[fix])
        f.store()
