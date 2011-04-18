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

from dabepg import *
from bitarray import bitarray, bits2bytes
import math
import datetime, pytz
import logging

log = logging.getLogger("dabepg.binary")

class Element:
    
    def __init__(self, tag, attributes=None, children=None, cdata=None):
        self.tag = tag
        self.attributes = (attributes if attributes is not None else [])
        self.children = (children if children is not None else [])
        self.cdata = cdata
        log.debug('created new element: %s', self)
        
    def tobytes(self):
        log.debug('rendering element: %s', self)
        data = bitarray()
        for attribute in self.attributes: data += attribute.tobytes()
        for child in self.children: data += child.tobytes()
        if self.cdata is not None: data += self.cdata.tobytes()
        
        # b0-b7: element tag
        bits = int_to_bitarray(self.tag, 8)
  
        # b8-15: element data length (0-253 bytes)
        # b16-31: extended element length (256-65536 bytes)
        # b16-39: extended element length (65537-16777216 bytes)
        datalength = bits2bytes(data.length())
        if datalength <= 253:
            tmp = int_to_bitarray(datalength, 8)
            bits += tmp
        elif datalength >= 254 and datalength <= 1<<16:
            tmp = bitarray()
            tmp.fromstring('\xfe')
            bits += tmp
            tmp = int_to_bitarray(datalength, 16)
            bits += tmp
        elif datalength > 1<<16 and datalength <= 1<<24: 
            tmp = bitarray()
            tmp.fromstring('\xff')
            bits += tmp
            tmp = int_to_bitarray(datalength, 24)
            bits += tmp
        else: raise ValueError('element data length exceeds the maximum allowed by the extended element length (24bits): %s > %s' + datalength + " > " + (1<<24))
                
        bits += data
        return bits
    
    def __str__(self):
        return 'tag=0x%02X, attributes=%s, children=%s, cdata=%s' % (self.tag, self.attributes, self.children, self.cdata)
    
    def __repr__(self):
        return '<Element: 0x%02X>' % self.tag
    
class Attribute:
    
    def __init__(self, tag, value, bits=None):
        self.tag = tag
        self.value = value
        self.bits = bits
    
    def tobytes(self):

        # encode data
        data = None
        if isinstance(self.value, int) or isinstance(self.value, long): # integer
            if self.bits is None: raise ValueError('attribute with int value has no bitlength specification: %s' % self)
            log.debug('encoding attribute %s as int with %d bits', self, self.bits)
            data = int_to_bitarray(self.value, self.bits)
        elif isinstance(self.value, datetime.timedelta): # duration
            data = int_to_bitarray(self.value.seconds, 16)
            log.debug('encoding attribute %s as duration', self)
        elif isinstance(self.value, Crid): # CRID
            data = bitarray()
            data.fromstring(str(self.value))
            log.debug('encoding attribute %s as CRID', self)
        elif isinstance(self.value, Genre): # genre
            data = encode_genre(self.value)
            log.debug('encoding attribute %s as genre', self)
        elif isinstance(self.value, datetime.datetime): # time
            data = encode_timepoint(self.value)
            log.debug('encoding attribute %s as timepoint', self)
        elif isinstance(self.value, str): # string
            data = bitarray()
            data.fromstring(self.value)
            log.debug('encoding attribute %s as string', self)
        elif isinstance(self.value, Bearer):
            data = encode_contentid(self.value.id)
            log.debug('encoding attribute %s as content ID from bearer', self)
        elif isinstance(self.value, ContentId):
            data = encode_contentid(self.value)
            log.debug('encoding attribute %s as content ID', self)
        else:
            raise ValueError('dont know how to encode this type: %s = %s' % (self.value.__class__.__name__, str(self.value)))
        data.fill()
        
        # b0-b7: element tag
        bits = int_to_bitarray(self.tag, 8)
  
        # b8-15: element data length (0-253 bytes)
        # b16-31: extended element length (256-65536 bytes)
        # b16-39: extended element length (65537-16777216 bytes)
        datalength = bits2bytes(data.length())
        if datalength <= 253:
            bits += int_to_bitarray(datalength, 8)
        elif datalength >= 254 and datalength <= 1<<16:
            tmp = bitarray()
            tmp.fromstring('\xfe')
            bits += tmp
            bits += int_to_bitarray(datalength, 16)
        elif datalength > 1<<16 and datalength <= 1<<24: 
            tmp = bitarray()
            tmp.fromstring('\xff')
            bits += tmp
            bits += int_to_bitarray(datalength, 24)
        else: raise ValueError('element data length exceeds the maximum allowed by the extended element length (24bits): %s > %s' + datalength + " > " + (1<<24))
                
        bits += data
        return bits
    
    def __str__(self):
        return str('0x%x' % self.tag)
    
    def __repr__(self):
        return '<Attribute: tag=%s, value=%s>' % (str(self), self.value)
    
def encode_genre(genre):
    
    segments = genre.href.split(':')
    if len(segments) < 6: raise ValueError('genre is incorrectly formatted: %s' % genre)
    
    bits = bitarray(4)
    bits.setall(False)
    
    # b0-3: RFU(0)
    
    # b4-7: CS
    cs = segments[4]
    if cs == 'IntentionCS':
        cs_val = 1
    elif cs == 'FormatCS':
        cs_val = 2
    elif cs == 'ContentCS':
        cs_val = 3
    elif cs == 'IntendedAudienceCS':
        cs_val = 4
    elif cs == 'OriginationCS':
        cs_val = 5
    elif cs == 'ContentAlertCS':
        cs_val = 6
    elif cs == 'MediaTypeCS':
        cs_val = 7
    elif cs == 'AtmosphereCS':
        cs_val = 8
    else:
        raise ValueError('unknown CS in genre: %s' % cs)
    bits += int_to_bitarray(cs_val, 4)
    
    # optional schema levels
    if len(segments) >= 6:
        levels = segments[6].split('.')
        for level in levels:
            bits += int_to_bitarray(int(level), 8)
        
    return bits
    
    
def encode_timepoint(timepoint):
    
    bits = bitarray(1)
    bits.setall(False)
    
    # b0: RFA(0)
        
    # b1-17: Date
    a = (14 - timepoint.month) / 12;
    y = timepoint.year + 4800 - a;
    m = timepoint.month + (12 * a) - 3;
    jdn = timepoint.day + ((153 * m) + 2) / 5 + (365 * y) + (y / 4) - (y / 100) + (y / 400) - 32045;
    jd = jdn + (timepoint.hour - 12) / 24 + timepoint.minute / 1440 + timepoint.second / 86400;
    mjd = (int)(jd - 2400000.5);
    bits += int_to_bitarray(mjd, 17)
        
    # b18: RFA(0)
    bits += bitarray('0')
        
    # b19: LTO Flag
    if timepoint.tzinfo is None or timepoint.tzinfo is pytz.timezone('UTC'):
        bits += bitarray('0')
    else:
        bits += bitarray('1')
        
    # b20: UTC Flag
    # b21: UTC - 11 or 27 bits depending on the form
    if timepoint.second > 0:
        bits += bitarray('1')
        bits += int_to_bitarray(timepoint.hour, 5)
        bits += int_to_bitarray(timepoint.minute, 6)
        bits += int_to_bitarray(timepoint.second, 6)
        bits += bitarray('0' * 10)
    else:
        bits += bitarray('0')
        bits += int_to_bitarray(timepoint.hour, 5)
        bits += int_to_bitarray(timepoint.minute, 6)
        
    # b32/48: LTO
    if timepoint.tzinfo is not None and timepoint.tzinfo is not pytz.timezone('UTC'):
            bits += bitarray('00') # b49-50: RFA(0)
            offset = (timepoint.utcoffset().days * 86400 + timepoint.utcoffset().seconds) + (timepoint.dst().days * 86400 + timepoint.dst().days)
            bits += bitarray('0' if offset > 0 else '1') # b51: LTO sign
            bits += int_to_bitarray(offset / (60 * 60) * 2, 5) # b52-56: Half hours
            
    return bits

def encode_contentid(id):

    bits = bitarray(4)
    bits.setall(False)
    
    # b0: RFA(0)
        
    # b1: Ensemble Flag. Indicates whether ECC and EId are contained with the
    # Content ID.
    # 0 = ECC and EId are not present. The service that is referenced within the
    # contentID is transmitted on the same ensemble as this EPG service
    # 1 = ECC and EId are present.
    if id.ecc is not None and id.eid is not None: bits[1] = True

    # b2: X-PAD flag. Indicates whether the addressed component is carried in an
    # X-PAD channel.
    # 0 = Is not carried in an X-PAD channel.
    # 1 = Is carried in an X-PAD channel.
    if id.xpad is not None: bits[2] = True
        
    # b3: SId encoding flag
    # 0 = Audio service (SId is 16bit)
    # 1 = Data service (SId is 32bit)
    # no audio support right now
        
    # b4-7: SCIdS
    bits += int_to_bitarray(int(id.scids, 16), 4)
        
    # optional next 8 bits: ECC
    if id.ecc is not None:
        bits += int_to_bitarray(int(id.ecc, 16), 8)
        
    # optional next 16 bits: EId
    if id.eid is not None:
        bits += int_to_bitarray(int(id.eid, 16), 16)
        
    # next 16/32 bits: SId
    bits += int_to_bitarray(int(id.sid, 16), 16)
        
    # optional next 8 bits: X-PAD extension
    if id.xpad is not None:
        bits += int_to_bitarray(int(id.xpad, 16), 8)
        
    return bits
    
class CData:
    
    def __init__(self, value):
        self.value = value
        
    def tobytes(self):
        # b0-b7: element tag
        bits = bitarray()
        bits.fromstring('\x01')
  
        # b8-15: element data length (0-253 bytes)
        # b16-31: extended element length (256-65536 bytes)
        # b16-39: extended element length (65537-16777216 bytes)
        datalength = len(self.value)
        if datalength <= 253:
            tmp = int_to_bitarray(datalength, 8)
            bits += tmp
        elif datalength >= 254 and datalength <= 1<<16:
            tmp = bitarray()
            tmp.fromstring('\xfe')
            bits += tmp
            tmp = int_to_bitarray(datalength, 16)
            bits += tmp
        elif datalength > 1<<16 and datalength <= 1<<24: 
            tmp = bitarray()
            tmp.fromstring('\xff')
            bits += tmp
            tmp = int_to_bitarray(datalength, 24)
            bits += tmp
        else: raise ValueError('element data length exceeds the maximum allowed by the extended element length (24bits): %s > %s' + datalength + " > " + (1<<24))
        stringbits = bitarray()
        stringbits.fromstring(str(self.value))
        bits += stringbits
        
        return bits

def marshall(obj):
    if isinstance(obj, ServiceInfo): return marshall_serviceinfo(obj)
    elif isinstance(obj, Epg): return marshall_epg(obj)
    
def marshall_serviceinfo(info):
    pass

def marshall_epg(epg):
    
    schedule = epg.schedule
    
    # epg
    epg_element = Element(0x02)
    
    # schedule
    schedule_element = Element(0x21)
    epg_element.children.append(schedule_element)
    if schedule.version is not None and schedule.version > 1:
        schedule_element.attributes.append(Attribute(0x80, schedule.version, 16))
    schedule_element.attributes.append(Attribute(0x81, schedule.created))
    if schedule.originator is not None:
        schedule_element.attributes.append(Attribute(0x82, schedule.originator))
        
    # schedule scope
    scope = schedule.get_scope()
    if scope is not None:
        schedule_element.children.append(build_scope(scope))
    
    # programmes
    for programme in schedule.programmes:
        programme_element = Element(0x1c)
        programme_element.attributes.append(Attribute(0x81, programme.shortcrid, 24))
        if programme.crid is not None:
            programme_element.attributes.append(Attribute(0x80, programme.crid))
        if programme.version is not None:
            programme_element.attributes.append(Attribute(0x82, programme.version, 16))
        if programme.recommendation:
            programme_element.attributes.append(Attribute(0x83, 0x02, 8))
        if not programme.onair:
            programme_element.attributes.append(Attribute(0x84, 0x02, 8))
        if programme.bitrate is not None:
            programme_element.attributes.append(Attribute(0x87, math.ceil(programme.bitrate), 16))
        # names
        for name in programme.names:
            child = build_name(name)
            programme_element.children.append(child)
        # locations
        for location in programme.locations:
            child = build_location(location)
            programme_element.children.append(child)
        # media
        if len(programme.media) > 0:
            child = build_mediagroup(programme.media)
            programme_element.children.append(child)
        # genre
        for genre in programme.genres:
            child = build_genre(genre)
            programme_element.children.append(child)
        # membership
        for membership in programme.memberships:
            child = build_membership(membership)
            programme_element.children.append(child)    
        # link
        for link in programme.links:
            child = build_link(link)
            programme_element.children.append(child)      
        # events
        for event in programme.events:
            child = build_programme_event(event)
            programme_element.children.append(child) 
            
        schedule_element.children.append(programme_element)
     
    return epg_element.tobytes().tostring()
    
def build_scope(scope):
    scope_element = Element(0x24)
    scope_element.attributes.append(Attribute(0x80, scope.start))
    scope_element.attributes.append(Attribute(0x81, scope.end))
    for service in scope.services:
        service_scope_element = Element(0x25)
        service_scope_element.attributes.append(Attribute(0x80, service))
        scope_element.children.append(service_scope_element)
    return scope_element
    
def build_name(name):
    name_element = None
    if isinstance(name, ShortName): name_element = Element(0x10)
    elif isinstance(name, MediumName): name_element = Element(0x11)
    elif isinstance(name, LongName): name_element = Element(0x12)
    name_element.cdata = CData(name.text)
    return name_element
    
def build_location(location):
    location_element = Element(0x19)
    for time in location.times:
        location_element.children.append(build_time(time))                
    for bearer in location.bearers:
        bearer_element = Element(0x2d)
        bearer_element.attributes.append(Attribute(0x80, bearer))
        location_element.children.append(bearer_element)       
    return location_element  

def build_time(time):
    time_element = None
    if isinstance(time, Time):
        time_element = Element(0x2c)
        time_element.attributes.append(Attribute(0x80, time.billed_time))
        if time.actual_time is not None:
            time_element.attributes.append(Attribute(0x82, time.actual_time))
        if time.actual_duration is not None:
            time_element.attributes.append(Attribute(0x83, time.actual_duration))            
        time_element.attributes.append(Attribute(0x81, time.billed_duration))
    elif isinstance(time, RelativeTime):
        time_element = Element(0x2f)
        time_element.attributes.append(Attribute(0x80, time.billed_offset))
        time_element.attributes.append(Attribute(0x81, time.billed_duration))
        if time.actual_offset is not None:
            time_element.attributes.append(Attribute(0x82, time.actual_offset))
        if time.actual_duration is not None:
            time_element.attributes.append(Attribute(0x83, time.actual_duration))
    return time_element   
    
def build_mediagroup(media):
    mediagroup_element = Element(0x13)
    for media in media:
        if isinstance(media, ShortDescription):
            media_element = Element(0x1a)
            media_element.cdata = CData(media.text)
            mediagroup_element.children.append(media_element)            
        elif isinstance(media, LongDescription):
            media_element = Element(0x1b)
            mediagroup_element.children.append(media_element)
            media_element.cdata = CData(media.text)  
        elif isinstance(media, Multimedia):
            media_element = Element(0x2b)
            mediagroup_element.children.append(media_element)
            if media.mimetype is not None:
                media_element.attributes.append(Attribute(0x80, media.mimetype))
            if media.language is not None:
                media_element.attributes.append(Attribute(0x81, media.language))
            if media.url is not None:
                media_element.attributes.append(Attribute(0x82, media.url))
            if media.type == Multimedia.LOGO_UNRESTRICTED:
                media_element.attributes.append(Attribute(0x83, 0x02, 8))
                media_element.attributes.append(Attribute(0x84, media.width, 16))
                media_element.attributes.append(Attribute(0x85, media.height, 16))
            if media.type == Multimedia.LOGO_MONO_SQUARE:
                media_element.attributes.append(Attribute(0x83, 0x03, 8))
            if media.type == Multimedia.LOGO_COLOUR_SQUARE:
                media_element.attributes.append(Attribute(0x83, 0x04, 8))
            if media.type == Multimedia.LOGO_MONO_RECTANGLE:
                media_element.attributes.append(Attribute(0x83, 0x05, 8))
            if media.type == Multimedia.LOGO_COLOUR_RECTANGLE:
                media_element.attributes.append(Attribute(0x83, 0x06, 8))
    return mediagroup_element
    
def build_genre(genre):
    genre_element = Element(0x14)
    genre_element.attributes.append(Attribute(0x80, genre.href))
    return genre_element    
    
def build_membership(membership):
    membership_element = Element(0x17)
    if membership.crid is not None:
        membership_element.attributes.append(Attribute(0x80, membership.crid))
    membership_element.attributes.append(Attribute(0x81, membership.shortcrid, 24))
    if membership.index is not None: 
        membership_element.attributes.append(0x82, membership.index)
    return membership_element  
    
def build_link(link):
    link_element = Element(0x18)
    link_element.attributes.append(Attribute(0x80, link.url))
    if link.description is not None:
        link_element.attributes.append(Attribute(0x83, link.description))
    if link.mimetype is not None:
        link_element.attributes.append(Attribute(0x81, link.mimetype))
    if link.expiry is not None:
        link_element.attributes.append(Attribute(0x84, link.expiry))
    return link_element   

def build_programme_event(event):
    event_element = Element(0x2e)
    if event.crid is not None:
        event_element.attributes.append(Attribute(0x80, event.crid))
    event_element.attributes.append(Attribute(0x81, event.shortcrid, 24))
    if event.version is not None and event.version > 1:
        event_element.attributes.append(Attribute(0x82, event.version, 16))
    if event.recommendation is True:
        event_element.attributes.append(Attribute(0x83, 0x02, 8))
    if not event.onair is False:
        event_element.attributes.append(Attribute(0x84, 0x02, 8))
    # names
    for name in event.names:
        event_element.children.append(build_name(name))
    # locations
    for location in event.locations:
        event_element.children.append(build_location(location))    
    # media
    if len(event.media) > 0:
        event_element.children.append(build_mediagroup(event.media))       
    # genre
    for genre in event.genres:
        event_element.children.append(build_genre(genre))
    # membership
    for membership in event.memberships:
        event_element.children.append(build_membership(membership))  
    # link
    for link in event.links:
        event_element.children(build_link(link))   
             
    return event_element
    
def int_to_bitarray(i, n):
    return bitarray(tuple((0,1)[i>>j & 1] for j in xrange(n-1,-1,-1)))

def bitarray_to_hex(bits):
    rows = []
    for i in range(0, len(bits), 256):
        rows.append(' '.join(["%02X" % ord(x) for x in bits[i:i+256].tostring()]).strip())
    return '\r\n'.join(rows)

def bitarray_to_binary(bits):
    rows = []
    for i in range(0, len(bits), 256):
        bytes = []
        for j in range(i, i+256, 8):
            bytes.append(bits[j:j+8].to01())
        rows.append(' '.join(bytes))
    return '\r\n'.join(rows)
       