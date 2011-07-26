#===============================================================================
# Python DAB EPG API - Serialize/Deserialize To/From objects to XML/Binary as per
# ETSI specifications TS 102 818 (XML Specification for DAB EPG) and TS 102 
# 371 (Transportation and Binary Encoding Specification for EPG).
# 
# Copyright (C) 2010 Global Radio
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#===============================================================================

import unittest

from dabepg import *
from dabepg.xml import marshall


class Test(unittest.TestCase):


    def test_build_xml_schedule(self):
        schedule = Schedule(version=2, originator='Global Radio')
        epg = Epg(schedule=schedule)
        
        programme = Programme(213456, crid='crid://bbc.co.uk/4969758988')
        
        programme.names.append(MediumName('Gilles Peterson'))
        programme.names.append(LongName('Gilles Peterson: Worldwide'))
        
        location = Location()
        location.times.append(Time(datetime.datetime(2003, 12, 18, 0, 0, 0, 0), datetime.timedelta(hours=2), actual_time=datetime.datetime(2003, 12, 18, 0, 0, 0, 0), actual_duration=datetime.timedelta(hours=2)))
        location.bearers.append(Bearer('e1.ce15.c221.0'))
        programme.locations.append(location)
        
        programme.media.append(ShortDescription('Gilles Peterson brings you two hours of global beats and the best of cool. Including the Worldwide family. KV5 are live from Maida Value with special guests.'))
        
        programme.genres.append(Genre('urn:tva:metadata:cs:ContentCS:2002:3.6.7', name='Rap/Hip Hop/Reggae'))
        
        programme.memberships.append(Membership(1000, crid='crid://www.bbc.co.uk/WorldwideGroup'))
        
        programme.links.append(Link('mailto:gilles.peterson@bbc.co.uk', description='Email:'))
        
        event1 = ProgrammeEvent(6353, crid='crid://www.bbc.co.uk;dab/BC81123456a', recommendation=True)
        event1.names.append(ShortName('Herbert'))
        event1.names.append(MediumName('Herbert Live'))
        event1.names.append(LongName('Live session from Herbert'))
        event_location = Location(times=[RelativeTime(45 * 60, 15 * 60)])
        event1.locations.append(event_location)
        event1.media.append(ShortDescription('Live session from Herbert, recorded at Cargo on 24/2/01'))
        programme.events.append(event1)
        
        event2 = ProgrammeEvent(59033)
        event2.names.append(MediumName('PM'))
        event2.locations.append(Location(times=[Time(datetime.datetime(2003, 12, 18, 17, 0, 0, 0), datetime.timedelta(hours=1))], bearers=[Bearer('e1.ce15.c224.0')]))
        programme.events.append(event2)
        
        schedule.programmes.append(programme)
        print marshall(epg)
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()