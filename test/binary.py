import unittest

from dabepg import *
from dabepg.binary import *
import datetime

class CDataTypeTest(unittest.TestCase):

    def test_cdata(self):
        cdata = CData('This is a CDATA test')
        print 'CDATA', cdata, 'encodes as'
        bits = cdata.tobytes()
        print bitarray_to_binary(bits)
        print bitarray_to_hex(bits)
        
class LocationElementTest(unittest.TestCase):
    
    def test_location(self):
        location = Location(times=[RelativeTime(datetime.timedelta(minutes=45), datetime.timedelta(minutes=15))])
        print 'location', location, 'encodes as'
        print bitarray_to_hex(build_location(location).tobytes())
        
class MembershipElementTest(unittest.TestCase):
    
    def test_membership(self):
        membership = Membership(1000, crid='crid://www.bbc.co.uk/WorldwideGroup')
        print 'membership', repr(membership), 'encodes as'
        print bitarray_to_hex(build_membership(membership).tobytes())   
        
class ScopeElementTest(unittest.TestCase):
    
    def test_scope(self):
        start = datetime.datetime(2010, 7, 29, 0, 0, 0, 0)
        end = start + datetime.timedelta(days=1)
        services = [ContentId.fromstring('e1.c181.c2a1.0')]
        scope = Scope(start, end, services)
        print 'scope', scope, 'encodes as'
        bits = build_scope(scope).tobytes()
        print bitarray_to_binary(bits)
        print bitarray_to_hex(bits)
        
class TimepointTypeTest(unittest.TestCase):
    
    def test_encode_utc(self):
        from dabepg.binary import encode_timepoint
        from datetime import datetime
        import pytz
        
        now = datetime(2010, 7, 30, 0, 0, 0, 0)
        now = pytz.timezone('Europe/London').fromutc(now)
        now = now.astimezone(pytz.timezone('Europe/London'))
        bits = encode_timepoint(now)
        print 'timepoint', now, 'encodes as'
        print bitarray_to_binary(bits)
        print bitarray_to_hex(bits)
        
    def test_encode_lto(self):
        from dabepg.binary import encode_timepoint
        from datetime import datetime
        import pytz
        
        now = datetime(2010, 7, 30, 0, 0, 0, 0, pytz.timezone('Europe/London'))
       
        bits = encode_timepoint(now)
        print 'timeepoint', now, 'encodes as'
        print bitarray_to_binary(bits)
        print bitarray_to_hex(bits)
        
class GenreTypeTest(unittest.TestCase):
    
    def test_genre(self):
        from dabepg.binary import encode_genre
        from dabepg import Genre
        
        genre = Genre('urn:tva:metadata:cs:ContentCS:2002:3.6.9', 'World/Traditional/Ethnic/Folk Music')
        print 'genre', genre, 'encodes as'
        bits = encode_genre(genre)
        print bitarray_to_binary(bits)
        print bitarray_to_hex(bits)
        
if __name__ == "__main__":
    unittest.main()