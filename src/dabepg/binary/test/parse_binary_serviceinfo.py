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

si = unmarshall(f)
print 'ServiceInformation', si
print
for ensemble in si.ensembles: 
    print 'Ensemble', ensemble
    for service in ensemble.services:
        print '\t', service.get_name()
        print '\t\t', service.ids
