import argparse
import configparser
import time
import sys

from xmlrpc.client import Fault
from xmlrpc.client import ServerProxy

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--section', help='Config section.')
parser.add_argument('-d', '--domain', help='Domain to check.')
parser.add_argument('--handle', help='Handle to use.')
args = parser.parse_args()

config = configparser.ConfigParser({
    'endpoint': 'https://rpc.gandi.net/xmlrpc/',
})
config.read('.gandibot')


def getvalue(key, default=None):
    if getattr(args, key):
        return getattr(args, key)
    else:
        return section.get(key, default)

section = config[args.section]
endpoint = section['endpoint']
apikey = section['apikey']

domain = getvalue('domain', 'er.tl')
api = ServerProxy(endpoint)
handle = getvalue('handle')

# Make sure that the handle provided exists
try:
    api.contact.info(apikey, handle)
except Fault as e:
    print("Cannot get contact info: %s" % e)
    sys.exit(1)

print('Registering domain %s with handle %s' % (domain, handle))

domain_spec = {
    'owner': handle,
    'admin': handle,
    'bill': handle,
    'tech': handle,
    'nameservers': ['a.dns.gandi-ote.net', 'b.dns.gandi-ote.net',
                    'c.dns.gandi-ote.net'],
    'duration': 1,
}


# get domain status
result = api.domain.available(apikey, [domain])
while result[domain] == 'pending':
    time.sleep(0.7)  # magic number in the gandi docs
    result = api.domain.available(apikey, [domain])

if result.get(domain) == 'available':
    print('Domain is available')
    op = api.domain.create(apikey, domain, domain_spec)
    print(op)
else:
    print('Domain is %s' % result.get(domain))
