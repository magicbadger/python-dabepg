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
import datetime

class Test(unittest.TestCase):


    def test_build_xml_serviceinfo(self):
        info = ServiceInfo(version=2, originator='BBC', provider='BBC', created=datetime.datetime(2001, 02, 28, 0, 0, 0, 0))
        ensemble = Ensemble(ContentId('e1', 'ce15'))
        info.ensembles.append(ensemble)
        ensemble.frequencies.append(225648)
        ensemble.names.append(ShortName('BBC'))
        ensemble.names.append(MediumName('BBC National'))
        ensemble.media.append(ShortDescription('Digital Radio from the BBC'))
        ensemble.media.append(Multimedia('http://www.bbc.co.uk/radio1/images/bbclogo.png', Multimedia.LOGO_COLOUR_RECTANGLE))
        ensemble.media.append(Multimedia('http://www.bbc.co.uk/radio/bbclogo_large.png', Multimedia.LOGO_UNRESTRICTED, 'image/png', 200, 200))
        ensemble.keywords.append('Radio1')
        ensemble.keywords.append('Radio2')
        ensemble.keywords.append('Radio3')
        ensemble.keywords.append('Radio4')
        ensemble.keywords.append('Radio5 Live')
        ensemble.links.append(Link('http://www.bbc.co.uk/radio/', 'text/html', 'BBC Radio homepage'))
        
        # Radio 1
        radio1 = Service(ContentId('e1', 'ca15', 'c221', '0'), bitrate=160)
        radio1.names.append(ShortName('Radio 1'))
        radio1.names.append(MediumName('BBC Radio 1'))
        radio1.media.append(ShortDescription('Rock and pop music from the BBC.'))
        radio1.media.append(Multimedia('http://www.bbc.co.uk/radio1/images/r1logo.png', Multimedia.LOGO_COLOUR_SQUARE))
        radio1.genres.append(Genre('urn:tva:metadata:cs:ContentCS:2002:3.6.7', 'Rap/Hip Hop/Reggae'))
        radio1.genres.append(Genre('urn:tva:metadata:cs:ContentCS:2002:3.6.8', 'Electronic/Club/Urban/Dance'))
        radio1.genres.append(Genre('urn:tva:metadata:cs:ContentCS:2002:2.5.0', 'ARTISTIC PERFORMANCE'))
        radio1.genres.append(Genre('urn:tva:metadata:cs:ContentCS:2002:1.1.0', 'ENTERTAINMENT'))
        radio1.keywords.append('music')
        radio1.keywords.append('pop')
        radio1.keywords.append('rock')
        radio1.keywords.append('dance')
        radio1.keywords.append('hip-hop')
        radio1.keywords.append('soul')
        radio1.links.append(Link('http://www.bbc.co.uk/radio1', 'text/html'))
        ensemble.services.append(radio1)

        # Radio 2
        radio2 = Service(ContentId('e1', 'ca15', 'c222', '0'))
        radio2.names.append(ShortName('Radio 2'))
        radio2.names.append(MediumName('BBC Radio 2'))
        ensemble.services.append(radio2)
        
        # Radio 3
        radio3 = Service(ContentId('e1', 'ca15', 'c223', '0'))
        radio3.names.append(ShortName('Radio 3'))
        radio3.names.append(MediumName('BBC Radio 3'))
        ensemble.services.append(radio3)
        
        # Radio 4
        radio4 = Service(ContentId('e1', 'ca15', 'c224', '0'))
        radio4.names.append(ShortName('Radio 4'))
        radio4.names.append(MediumName('BBC Radio 4'))
        ensemble.services.append(radio4)
        
        # Radio 5
        radio5 = Service(ContentId('e1', 'ca15', 'c225', '0'))
        radio5.names.append(ShortName('Radio 5'))
        radio5.names.append(MediumName('BBC Radio 5'))
        ensemble.services.append(radio5)

        print marshall(info)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()