from dabepg.binary import unmarshall
import logging

logging.basicConfig(level=logging.DEBUG)


epg = unmarshall(open('epg.dat', 'rb').read())
print epg