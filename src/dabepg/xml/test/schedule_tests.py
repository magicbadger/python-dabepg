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


class Test(unittest.TestCase):


    def test_long_running_show(self):
        """
        Testing the splitting and restrictions of long running shows.
        
        The XML specification does not allow for the full use of ISO8601 Periods, such 
        that Hours are the largest allowable unit.
        
        The binary specification has a limit of 18h on a show, due to the field used to 
        encode duration
        """
        
        schedule = Schedule()
        epg = Epg(schedule=schedule)
        
        programme = Programme(123456)
        
        programme.names.append(MediumName('Long Show'))
        programme.names.append(LongName('This is a very long show indeed'))
        
        location = Location()
        location.times.append(Time(datetime.datetime(2014, 11, 14, 0, 0, 0, 0), datetime.timedelta(days=7)))
        location.bearers.append(Bearer('e1.ce00.c000.0'))
        programme.locations.append(location)
        
        schedule.programmes.append(programme)
        
        from dabepg.xml import marshall as marshall_xml
        from dabepg.binary import marshall as marshall_binary
        print marshall_xml(epg, indent='   ')
        
        print marshall_binary(epg)
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()