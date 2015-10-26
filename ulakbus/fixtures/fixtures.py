import json
import os
import riak
from ulakbus import settings

client = riak.RiakClient(protocol=settings.RIAK_PROTOCOL, host=settings.RIAK_SERVER, port=settings.RIAK_PROTOCOL)
fixture_bucket = client.bucket_type('models').bucket('ulakbus_fixtures')

FIXTURES_FILE = os.environ.get('FIXTURES_FILE',
                               '/'.join([os.path.dirname(os.path.realpath("__file__")), 'settings.json']))

try:
    with open(FIXTURES_FILE, "r") as fixtures_file:
        try:
            fixtures = json.load(fixtures_file)
            for fix in fixtures:
                f = fixture_bucket.get(fix)
                f.data = fixtures[fix]
                print "%s: %s stored.." % (fix, fixtures[fix])
                f.store()
        except ValueError as e:
            print "please validate your json file: %s" % e
except IOError:
    print "file not found: %" % FIXTURES_FILE
