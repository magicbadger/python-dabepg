from dabepg.binary import unmarshall
import logging
import sys

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('dabepg').setLevel(logging.INFO)

def usage():
    print "USAGE: parse_binary_schedule.py [filename] (or expects stdin)"""

args = sys.argv[1:]
if len(args):
    filename = args[0]
    print 'decoding from', filename
    f = open(filename, 'rb')
else:
    f = sys.stdin

epg = unmarshall(f)
print 'EPG, scope:', epg.schedule.get_scope()
print
for programme in epg.schedule.programmes:
    print programme.get_name(), ['%s/%s' % (x[0].isoformat(), (x[0] + x[1]).isoformat()) for x in programme.get_times()]
    print '\t', programme.get_description()
