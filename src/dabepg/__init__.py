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


import datetime
import locale
import re
from dateutil.tz import tzlocal

MAX_SHORTCRID = 16777215
TRIGGER_PATTERN = '[0-9a-fA-F]{8}'

class Bearer:  
    
    def __init__(self, id, trigger=None):
        if isinstance(id, str): id = ContentId.fromstring(id)
        self.id = id
        self.trigger = trigger
        if trigger is not None and re.match(TRIGGER_PATTERN, trigger) is None:
            raise ValueError('trigger does not match the following pattern ' + TRIGGER_PATTERN)
        
    def __eq__(self, other):
        if isinstance(other, Bearer):
            return self.id == other.id and self.trigger == other.trigger            
        
    def __str__(self):
        return '%s' % self.id
    
    def __repr__(self):
        return '<Bearer: %s>' % str(self)
        

CONTENTID_PATTERN = '([0-9a-fA-F]{2})\\.([0-9a-fA-F]{4})(\\.([0-9a-fA-F]{4,8})\\.([0-9a-fA-F]{1})){0,1}'

class ContentId:
    
    def __init__(self, ecc, eid, sid=None, scids=None, xpad=None):
        """Values can be passed in as hex string or integers"""
        self.sid = sid
        self.scids = scids
        self.xpad = xpad
        
        # ECC    
        if isinstance(ecc, int): self.ecc = ecc
        else: self.ecc = int(ecc, 16)
        
        # EId
        if isinstance(eid, int): self.eid = eid
        else: self.eid = int(eid, 16)
            
        # SId
        if sid:
            if isinstance(sid, int): self.sid = sid
            else: self.sid = int(sid, 16)
                  
        # SCIdS
        if scids:
            if isinstance(scids, int): self.scids = scids
            else: self.scids = int(scids, 16)                      

        # XPAD
        if xpad:
            if isinstance(xpad, int): self.xpad = xpad
            else: self.xpad = int(xpad, 16)  
        
    @classmethod
    def fromstring(cls, string):
        pattern = re.compile(CONTENTID_PATTERN)
        matcher = pattern.search(string)
        ecc = matcher.group(1)
        eid = matcher.group(2)
        sid = None
        scids = None
        if len(matcher.groups()) > 2:
            sid = matcher.group(4)
            scids = matcher.group(5)
        return ContentId(ecc, eid, sid, scids)
    
    def __str__(self):
        id = '%x.%x' % (self.ecc, self.eid)
        if self.sid is not None and self.scids is not None:
            id += '.%x.%x' % (self.sid, self.scids)
        return id
    
    def __repr__(self):
        return '<ContentId: %s>' % str(self)
    
    def __eq__(self, other):
        return str(self) == str(other)
            
        
CRID_PATTERN = 'crid://([^\\/]+)/([^\\/]+)'
        
class Crid:
    
    def __init__(self, authority, data):
        self.authority = authority
        self.data = data
        
    @classmethod
    def fromstring(cls, string):
        pattern = re.compile(CRID_PATTERN)
        matcher = pattern.search(string)
        authority = matcher.group(0)
        data = matcher.group(1)
        return Crid(authority, data)
        
    def __str__(self):
        return 'crid://%s/%s' % (self.authority, self.data)
    
    
class Ensemble:
    
    def __init__(self, id, version=1):
        self.id = id
        self.names = []
        self.media = []
        self.keywords = []
        self.links = []
        self.services = []
        self.frequencies = []
        self.ca = None
        self.version = version
        
    def __str__(self):
        return str(self.id)
    
    def __repr__(self):
        return '<Ensemble: %s>' % str(self)
    
    
class Epg:
    
    DAB="DAB"
    DRM="DRM"
    
    def __init__(self, schedule, type=DAB):
        self.type = type
        self.schedule = schedule if schedule is not None else Schedule()
    
class Link:
    
    def __init__(self, url, mimetype=None, description=None, expiry=None, locale=locale.getlocale()):
        self.url = url
        self.mimetype = mimetype
        self.description = description
        self.expiry = expiry
        self.locale = locale
        
    def __str__(self):
        return self.url
        
        
class Location:
    
    def __init__(self, times=None, bearers=None):
        self.times = times if times is not None else []
        self.bearers = [] if bearers is None else map(lambda x: x if isinstance(x, ContentId) else ContentId.fromstring(str(x)), bearers)
        
    def __str__(self):
        return str(dict(times=self.times, bearers=self.bearers))
    
    def __repr__(self):
        return '<Location: %s>' % str(self)
        
        
class BaseTime:
    
    def get_billed_time(self, base):
        raise ValueError('not implemented')
        
    def get_billed_duration(self):
        raise ValueError('not implemented')
        
    def get_actual_time(self, base):
        raise ValueError('not implemented')
        
    def get_actual_duration(self):
        raise ValueError('not implemented')
    
    
class RelativeTime(BaseTime):
    
    def __init__(self, billed_offset, billed_duration, actual_offset=None, actual_duration=None):
        self.actual_offset = actual_offset
        self.actual_duration = actual_duration
        self.billed_offset = billed_offset
        self.billed_duration = billed_duration
    
    def get_billed_time(self, base):
        if self.billed_offset is None: return None
        return base + self.billed_offset
        
    def get_billed_duration(self):
        return self.billed_duration
        
    def get_actual_time(self, base):
        if self.actual_offset is None: return None
        return base + self.actual_offset
        
    def get_actual_duration(self):
        return self.actual_duration
    
    def __str__(self):
        return 'offset=%s, duration=%s' % (str(self.billed_offset), str(self.billed_duration))
    
    def __repr__(self):
        return '<RelativeTime: %s>' % str(self)

        
class Time(BaseTime):
    
    def __init__(self, billed_time, billed_duration, actual_time=None, actual_duration=None):
        self.actual_time = actual_time
        self.actual_duration = actual_duration
        self.billed_time = billed_time
        self.billed_duration = billed_duration
    
    def get_billed_time(self, base=None):
        return self.billed_time
        
    def get_billed_duration(self):
        return self.billed_duration
        
    def get_actual_time(self, base=None):
        return self.actual_time
        
    def get_actual_duration(self):
        return self.actual_duration

    def __str__(self):
        return 'time=%s, duration=%s' % (str(self.billed_time), str(self.billed_duration))
    
    def __repr__(self):
        return '<Time: %s>' % str(self)

    
class Text:
    
    def __init__(self, text, max_length, locale=locale.getdefaultlocale()):
        if len(text) > max_length: raise ValueError('text length exceeds the maximum: %d>%d' % (len(text), max_length))
        self.max_length = max_length
        self.text = text
        
    def __str__(self):
        return self.text

    def __repr__(self):
        return '<Text[%d]: %s>' % (self.max_length, self.text)
    
class LongDescription(Text):
    
    max_length = 1800
    
    def __init__(self, text, locale=locale.getdefaultlocale()):
        Text.__init__(self, text, 1800, locale)

class ShortDescription(Text):
    
    max_length = 180
    
    def __init__(self, text, locale=locale.getdefaultlocale()):
        Text.__init__(self, text, 180, locale)
        
class LongName(Text):
    
    max_length = 128
    
    def __init__(self, text, locale=locale.getdefaultlocale()):
        Text.__init__(self, text, 128, locale)

class MediumName(Text):
    
    max_length = 16
    
    def __init__(self, text, locale=locale.getdefaultlocale()):
        Text.__init__(self, text, 16, locale)
        
class ShortName(Text):
    
    max_length = 8
    
    def __init__(self, text, locale=locale.getdefaultlocale()):
        Text.__init__(self, text, 8, locale)    
        
def suggest_names(names):     
    result = []
    for name in names:
        if len(name) > MediumName.max_length:
            result.append(MediumName(name[0:MediumName.max_length-1]))
            result.append(LongName(name))
        elif len(name) > ShortName.max_length:
            result.append(ShortName(name[0:ShortName.max_length-1]))
            result.append(MediumName(name))
            result.append(LongName(name))
        else:
            result.append(ShortName(name))
            result.append(MediumName(name))
            result.append(LongName(name))            
    return result
        
       
class Membership:
    
    def __init__(self, shortcrid, crid=None, index=None):
        self.shortcrid = shortcrid
        self.crid = crid
        self.index = index 
        
    def __str__(self):
        return str(self.shortcrid)
    
    def __repr__(self):
        return '<Membership: shortcrid=%d, crid=%s, index=%s>' % (self.shortcrid, self.crid, str(self.index))
    
class Multimedia:
    
    LOGO_UNRESTRICTED ="logo_unrestricted"    
    LOGO_MONO_SQUARE = "logo_mono_square"
    LOGO_COLOUR_SQUARE = "logo_colour_square"
    LOGO_MONO_RECTANGLE = "logo_mono_rectangle"
    LOGO_COLOUR_RECTANGLE = "logo_colour_rectangle"
    
    def __init__(self, url, type=LOGO_UNRESTRICTED, mimetype=None, height=None, width=None, locale=locale.getdefaultlocale()):
        self.url = url
        self.type = type
        self.mimetype = mimetype
        self.height = height
        self.width = width
        
        
class Programme:
    
    def __init__(self, shortcrid, crid=None, bitrate=None, onair=True, recommendation=True, version=1):
        self.shortcrid = shortcrid
        self.crid = crid
        self.version = version
        self.bitrate = bitrate
        self.onair = onair
        self.recommendation = recommendation
        self.names = []
        self.locations = []
        self.media = []
        self.genres = []
        self.keywords = []
        self.memberships = []
        self.links = []
        self.events = []
        
    def get_name(self, max_length=LongName.max_length):
        """returns the first name set with a length at or below the max_length field, which 
           defaults to the MAX_LENGTH of a LongName field"""
        for type in [ShortName, MediumName, LongName]:
            for name in [x for x in self.names if isinstance(x, type)]:
                if len(name.text) <= max_length: return name
                
    def get_times(self):
        """returns a list of (datetime, timedelta) tuples collated from the billed times of the locations
           of this programme"""
        times = []
        for location in self.locations:
            times.extend([(x.get_billed_time(), x.get_billed_duration()) for x in location.times])
        return times
        
    def __str__(self):
        return str(self.get_name())
    
    def __repr__(self):
        return '<Programme: %s>' % str(self)    
    
    
class ProgrammeEvent:
    
    def __init__(self, shortcrid, originator=None, crid=None, version=None, bitrate=None, onair=True, recommendation=False):
        self.shortcrid = shortcrid
        self.originator = originator
        self.crid = crid
        self.version = version
        self.bitrate = bitrate
        self.onair = onair
        self.recommendation = recommendation
        self.names = []
        self.locations = []
        self.media = []
        self.genres = []
        self.keywords = []
        self.memberships = []
        self.links = []
        
    def __str__(self):
        return str(self.names)
    
    def __repr__(self):
        return '<ProgrammeEvent: %s>' % str(self)
    
    
class Schedule:
    
    def __init__(self, created=datetime.datetime.now(tzlocal()), version=1, originator=None):
        self.created = created
        self.version = version
        self.originator = originator
        self.programmes = []
        
    def get_scope(self):
        start = None
        end = None
        services = []
        
        for programme in self.programmes:
            for location in programme.locations:
                for time in location.times:
                    if isinstance(time, RelativeTime): continue
                    if start is None or start > time.billed_time:
                        start = time.billed_time
                    if end is None or end < time.billed_time + time.billed_duration:
                        end = time.billed_time + time.billed_duration
                for bearer in location.bearers:
                    if isinstance(bearer, Bearer) and bearer.id not in services:
                        services.append(bearer.id) # we have a Bearer
                    elif isinstance(bearer, ContentId) and bearer not in services:
                        services.append(bearer) # we have a ContentId
                    
        if start is None or end is None: return None    
    
        return Scope(start, end, services)
        
        
class Scope:
    
    def __init__(self, start, end, services = []):
        self.start = start
        self.end = end
        self.services = services

    def __str__(self):
        return 'start=%s, end=%s, services=%s>' % (self.start, self.end, self.services)
    
    def __repr__(self):
        return '<Scope: %s>' % str(self)

                
class Service:
    
    PRIMARY = "primary"
    SECONDARY = "secondary"
    
    AUDIO = "audio"
    DLS = "DLS"
    SLIDESHOW = "MOTSlideshow"
    BWS = "MOTBWS"
    TPEG = "TPEG"
    DGPS = "DGPS"
    PROPRIETARY = "proprietary"
    
    def __init__(self, id, bitrate=None, type=PRIMARY, format=AUDIO, version=1, locale=locale.getdefaultlocale()):
        self.id = id
        self.bitrate = bitrate
        self.format = format
        self.version = version
        self.locale = locale
        self.names = []
        self.media = []
        self.genres = []
        self.links = []
        self.simulcasts = []
        self.keywords = []
        
        
class ServiceInfo:
    
    DAB='DAB'
    DRM='DRM'
    
    def __init__(self, created=datetime.datetime.now(tzlocal()), version=1, originator=None, provider=None, type=DAB):
        self.created = created
        self.version = version
        self.originator = originator
        self.provider = provider
        self.type = type
        self.ensembles = []
        
         
class Genre:
    
    def __init__(self, href, name=None):
        self.href = href
        self.name = name     
        
    def __str__(self):
        return str(self.href)
    
    def __repr__(self):
        return '<Genre: %s>' % str(self)    
