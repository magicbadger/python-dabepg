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

from dabepg import Genre

class Intention:
    
    ENTERTAIN = Genre('urn:tva:metadata:cs:IntentionCS:2005:1.1', 'ENTERTAIN')
    INFORM = Genre('urn:tva:metadata:cs:IntentionCS:2005:1.2', 'INFORM')
    Infotainment = Genre('urn:tva:metadata:cs:IntentionCS:2005:1.2.3', 'Infotainment')
    Advice = Genre('urn:tva:metadata:cs:IntentionCS:2005:1.2.4', 'Advice')
    EDUCATE = Genre('urn:tva:metadata:cs:IntentionCS:2005:1.3"', 'EDUCATE')
    ENRICH = Genre('urn:tva:metadata:cs:IntentionCS:2005:1.8', 'ENRICH')
    Inspirational_enrichment = Genre('urn:tva:metadata:cs:IntentionCS:2005:1.8.2', 'Inspirational enrichment')
    
