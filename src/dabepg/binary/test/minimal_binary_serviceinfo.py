#===============================================================================
# Python DAB EPG API - Serialize/Deserialize To/From objects to XML/Binary as per
# ETSI specifications TS 102 818 (XML Specification for DAB EPG) and TS 102 
# 371 (Transportation and Binary Encoding Specification for EPG).
# 
# Copyright (C) 2012 Global Radio
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

from dabepg import * 
from dabepg.bands import BAND_5A

info = ServiceInfo()
ensemble = Ensemble(ContentId('e1', 'cfff'))
info.ensembles.append(ensemble)
ensemble.frequencies.append(BAND_5A)
ensemble.names.append(ShortName('Demo'))
ensemble.names.append(MediumName('Demo Mux'))

# Service
service = Service(ContentId('e1', 'cfff', 'c0fe', '0'))
service.names.append(ShortName('Service'))
service.names.append(MediumName('Service'))
service.media.append(Multimedia('32x32.png', Multimedia.LOGO_COLOUR_SQUARE))
service.media.append(Multimedia('112x32.png', Multimedia.LOGO_COLOUR_RECTANGLE))
service.media.append(Multimedia('128x128.png', Multimedia.LOGO_UNRESTRICTED, width=128, height=128))
service.media.append(Multimedia('http://www.capitalfm.com/logos/320x240.png', Multimedia.LOGO_UNRESTRICTED, width=320, height=240))
ensemble.services.append(service)

from dabepg.binary import marshall
print marshall(info)
