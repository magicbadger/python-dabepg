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
    
class Content:
    
    class NonFiction(Genre):
         
        def __init__(self):
             Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1', 'NON-FICTION/INFORMATION')
             
        class News(Genre):
             
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.1', 'News')
                 
    
             Daily_News = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.1', 'Daily news')
             Special_News = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.2', 'Special news/edition')
             Special_Report = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.3', 'Special Report')
             Commentary = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.4', 'Commentary')
             Periodical = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.5', 'Periodical')
             National_Politics = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.6', 'National politics/National assembly')
             Economy = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.7', 'Economy/Market/Financial/Business')
             International = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.8', 'Foreign/International')
             Sports = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.9', 'Sports')
             
             class Cultural(Genre):
                 
                 def __init__(self):
                     Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.1.10', 'Cultural')
                     
                 Arts = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.10.1', 'Arts')
                 Entertainment = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.10.2', 'Entertainment')
                 Film = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.10.3', 'Film')
                 Music = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.10.4', 'Music')
                 Radio = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.10.5', 'Radio')
                 TV = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.10.6', 'TV')
                 
             Local = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.11', 'Local/Regional')
             Traffic = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.12', 'Traffic')
             Weather = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.13', 'Weather forecasts')
             Service_information = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.14', 'Service information')
             Public_affairs = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.15', 'Public affairs')
             Current_affairs = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.16', 'Current affairs')
             Consumer_affairs = Genre('urn:tva:metadata:cs:ContentCS:2009:3.1.1.17', 'Consumer affairs')

        class Religion(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.2', 'Religion/Philosophies')
                 
        class General(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.3', 'General non-fiction')
                 
        class Arts(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.4', 'Arts')     
                 
        class Humanities(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.5', 'Humanities')     
                 
        class Sciences(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.6', 'Sciences')    
                 
        class Human_interest(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.7', 'Human interest')        
                 
        class Transport_and_Communications(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.8', 'Transport and Communications')    
                 
        class Events(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.9', 'Events')                    
                 
        class Media(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.10', 'Media')    
                 
        class Listings(Genre):
         
             def __init__(self):
                 Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.1.11', 'Listings')      
                 
                 
    class Sports(Genre):
     
         def __init__(self):
             Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.2', 'SPORTS')   
                           
             
    class Drama(Genre):
     
         def __init__(self):
             Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.4', 'FICTION/DRAMA') 
             
             
    class Entertainment(Genre):
     
         def __init__(self):
             Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.5', 'AMUSEMENT/ENTERTAINMENT')         
             
             
    class Music(Genre):
     
        def __init__(self):
            Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6', 'Music')                   
             
        class Classical(Genre):
         
            def __init__(self):
                Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.1', 'Classical music')
                 
            class Early(Genre):
             
                def __init__(self):
                    Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.1.1', 'Early')        
                    
        class Jazz(Genre):
         
            def __init__(self):
                Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.2', 'Jazz')    
                
        class Background(Genre):
         
            def __init__(self):
                Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.3', 'Background music')   
                
        class PopRock(Genre):
         
            def __init__(self):
                Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.4', 'Pop-rock')      
                
        class Blues_Soul(Genre):
         
            def __init__(self):
                Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.5', 'Blues/Rhythm and Blues/Soul/Gospel')
                
        class Country(Genre):
         
            def __init__(self):
                Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.6', 'Country and Western')          
                
        class Hiphop(Genre):
         
            def __init__(self):
                Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.7', 'Rap/Hip Hop/Reggae')  
                
        class Electronic(Genre):

            def __init__(self):
                Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.8', 'Electronic/Club/Urban/Dance')
                
        class World(Genre):
         
            def __init__(self):
                Genre.__init__(self, 'urn:tva:metadata:cs:ContentCS:2009:3.6.9', 'World/Traditional/Ethnic/Folk music')                                                                                                                                                                
             
