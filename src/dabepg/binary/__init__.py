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

logger = logging.getLogger("dabepg.binary")

class Element:
    
    def __init__(self, tag, attributes=None, children=None, cdata=None):
        self.tag = tag
        self.attributes = (attributes if attributes is not None else [])
        self.children = (children if children is not None else [])
        self.cdata = cdata
        logger.debug('created new element: %s', self)
        
    def tobytes(self):
        logger.debug('rendering element: %s', self)
        data = bitarray()
        for attribute in self.attributes: 
            try: data += attribute.tobytes()
            except: 
                logger.exception('error rendering attribute %s of %s', attribute, self)
                raise
        for child in self.children: 
            try: data += child.tobytes()
            except: 
                logger.exception('error rendering child %s of %s', child, self)
                raise
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
    
    def __iter__(self):
        return iter(self.children)
    
    def has_child(self, tag):
        return len(self.get_children(tag))
    
    def get_children(self, tag=None):
        if tag is not None:
            return [x for x in self.children if x.tag == tag]
        return self.children
    
    def has_attribute(self, tag):
        return len(self.get_attributes(tag))
    
    def get_attributes(self, tag=None):
        if tag is not None:
            return [x for x in self.attributes if x.tag == tag]
        return self.attributes    
    
    @staticmethod
    def frombits(bits):
        
        # b0-b7: element tag
        tag = int(bits[0:8].to01(), 2)
        if tag < 0x02 or tag > 0x30: raise ValueError('invalid value for tag: 0x%02x' % tag)
               
        # b8-15: element data length (0-253 bytes)
        # b16-31: extended element length (256-65536 bytes)
        # b16-39: extended element length (65537-16777216 bytes)
        datalength = int(bits[8:16].to01(), 2)
        start = 16
        if datalength == 0xfe:
            datalength = int(bits[16:32].to01(), 2)
            start = 32
        elif datalength == 0xff:
            datalength = int(bits[16:40].to01(), 2)
            start = 40
        data = bits[start : start + (datalength * 8)]
                
        i = 0
        e = Element(tag)
        logger.debug('parsing data of length %d bytes for element with tag 0x%02x', datalength, tag)
        while i < data.length():
            
            child_tag = int(data[i:i+8].to01(), 2)            
            child_datalength = int(data[i+8:i+16].to01(), 2)
            logger.debug('child tag 0x%02x for parent 0x%02x has data length of %d bytes', child_tag, tag, child_datalength)
            start = 16
            if child_datalength == 0xfe:
                child_datalength = int(data[i+16:i+32].to01(), 2)
                start = 32
            elif child_datalength == 0xff: 
                child_datalength = int(bits[i+16:i+40].to01(), 2)
                start = 40
            end = i + start + (child_datalength * 8)
 
            child_data = data[i + start : i + start + (child_datalength * 8)] 
            #logger.debug('child tag 0x%02x has data: %s', child_tag, bitarray_to_hex(child_data))
                
            # attributes
            if child_tag >= 0x80 and child_tag <= 0x87:
                attribute = Attribute.frombits(tag, data[i:end])
                e.attributes.append(attribute)
            # token table
            elif child_tag == 0x04:
                tokens = decode_tokentable(child_data)
                e.tokens = tokens
                logger.debug('parsed token table: %s', tokens)
            # default content ID
            elif child_tag == 0x05:
                default_contentid = decode_contentid(child_data)
                e.default_contentid = default_contentid
            # default language
            elif child_tag == 0x06: 
                pass               
            # children
            elif child_tag >= 0x02 and child_tag <= 0x30:
                child = Element.frombits(data[i:end])
                child.parent = e
                e.children.append(child)
            # cdata
            elif child_tag == 0x01:
                cdata = CData.frombits(data[i:end])
                e.cdata = cdata
            else:
                raise ValueError('unknown element 0x%02x under parent 0x%02x' % (child_tag, tag))
            
            i = end
            
        return e
        
    def __str__(self):
        return 'tag=0x%02X, attributes=%s, children=%s, cdata=%s' % (self.tag, self.attributes, self.children, self.cdata)
    
    def __repr__(self):
        return '<Element: 0x%02X>' % self.tag
        
class Attribute:
    
    def __init__(self, tag, value, bitlength=None):
        self.tag = tag
        self.value = value
        self.bitlength = bitlength
        logger.debug('created new attribute: %s', self)
    
    def tobytes(self):

        # encode data
        data = None
        if isinstance(self.value, int) or isinstance(self.value, long): # integer
            if self.bitlength is None: raise ValueError('attribute with int value has no bitlength specification: %s' % self)
            logger.debug('encoding attribute %s as int with %d bits', self, self.bits)
            data = int_to_bitarray(self.value, self.bits)
        elif isinstance(self.value, datetime.timedelta): # duration
            data = int_to_bitarray(self.value.seconds, 16)
            logger.debug('encoding attribute %s as duration', self)
        elif isinstance(self.value, Crid): # CRID
            data = bitarray()
            data.fromstring(str(self.value))
            logger.debug('encoding attribute %s as CRID', self)
        elif isinstance(self.value, Genre): # genre
            data = encode_genre(self.value)
            logger.debug('encoding attribute %s as genre', self)
        elif isinstance(self.value, datetime.datetime): # time
            data = encode_timepoint(self.value)
            logger.debug('encoding attribute %s as timepoint', self)
        elif isinstance(self.value, str): # string
            data = bitarray()
            data.fromstring(self.value)
            logger.debug('encoding attribute %s as string', self)
        elif isinstance(self.value, Bearer):
            data = encode_contentid(self.value.id)
            logger.debug('encoding attribute %s as content ID from bearer', self)
        elif isinstance(self.value, ContentId):
            data = encode_contentid(self.value)
            logger.debug('encoding attribute %s as content ID', self)
        else:
            raise ValueError('dont know how to encode this type: %s = %s' % (self.value.__class__.__name__, str(self.value)))
        data.fill()
        
        # b0-b7: tag
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
    
    @staticmethod
    def frombits(parent, bits):
        # b0-b7: attribute tag
        tag = int(bits[0:8].to01(), 2)
        
        # b8-15: attribute data length (0-253 bytes)
        # b16-31: extended attribute length (256-65536 bytes)
        # b16-39: extended attribute length (65537-16777216 bytes)
        datalength = int(bits[8:16].to01(), 2)
        start = 16
        if datalength >= 254 and datalength <= 1<<16:
            datalength = int(bits[16:32].to01(), 2)
            start = 32
        elif datalength > 1<<16 and datalength <= 1<<24: 
            datalength = int(bits[16:40].to01(), 2)
            start = 40
        elif datalength > 1<<24:
            raise ValueError('attribute data length exceeds the maximum allowed by the extended attribute length (24bits): %s > %s' + datalength + " > " + (1<<24))
        data = bits[start:start+(datalength * 8)]
                
        # decode data
        if isinstance(parent, Element): parent_tag = parent.tag
        else: parent_tag = int(parent)
        if (parent_tag, tag) in [
                (0x02, 0x80), (0x21, 0x80), (0x23, 0x80), (0x23, 0x81), (0x23, 0x82), (0x23, 0x84), (0x25, 0x80),
                (0x1c, 0x81), (0x1c, 0x82), (0x1c, 0x87), (0x17, 0x81), (0x17, 0x82), (0x03, 0x80), (0x26, 0x81)
        ]: # integer
            logger.debug('decoding tag/attribute 0x%02x/0x%02x as int', parent_tag, tag)
            value = int(data.to01(), 2)
        elif (parent_tag, tag) in [(0x2c, 0x81), (0x2c, 0x83)]: # duration
            logger.debug('decoding tag/attribute 0x%02x/0x%02x as duration', parent_tag, tag)
            value = datetime.timedelta(seconds=int(data.to01(), 2))
        elif (parent_tag, tag) in [(0x20, 0x80), (0x1c, 0x80), (0x17, 0x80)]: # CRID
            logger.debug('decoding tag/attribute 0x%02x/0x%02x as CRID', parent_tag, tag)
            value = Crid.fromstring(data.tostring())
        elif (parent_tag, tag) in []: # genre
            logger.debug('decoding tag/attribute 0x%02x/0x%02x as genre', parent_tag, tag)
            value = decode_genre(data)
        elif (parent_tag, tag) in [(0x20, 0x81), (0x21, 0x81), (0x24, 0x80), (0x24, 0x81), (0x2c, 0x80), (0x2c, 0x82),
                                   (0x03, 0x81)]: # time
            logger.debug('decoding tag/attribute 0x%02x/0x%02x as timepoint', parent_tag, tag)
            value = decode_timepoint(data)
        elif (parent_tag, tag) in [(0x20, 0x82), (0x03, 0x82), (0x03, 0x83)]: # string
            logger.debug('decoding tag/attribute 0x%02x/0x%02x as string', parent_tag, tag)
            value = data.tostring()
        elif (parent_tag, tag) in [(0x25, 0x80), (0x26, 0x80), (0x29, 0x80)]: # content ID
            logger.debug('decoding tag/attribute 0x%02x/0x%02x as ContentId', parent_tag, tag)
            value = decode_contentid(data)
        elif (parent_tag, tag) in [(0x1c, 0x83), (0x1c, 0x84), (0x03, 0x84)]:
            try:
                value = decode_enum(parent_tag, tag, data)
            except:
                logger.warning('error decoding enum for parent 0x%02x from tag: 0x%02x - IGNORING for now' % (parent_tag, tag))
                value = data
        else:
            raise ValueError('dont know how to decode attribute value for parent 0x%02x from tag: 0x%02x' % (parent_tag, tag))
        
        return Attribute(tag, value)
    
    def __str__(self):
        return str('0x%x' % self.tag)
    
    def __repr__(self):
        return '<Attribute: tag=%s, value=%s>' % (str(self), self.value)
    
genre_map = dict(
    IntentionCS=1,
    FormatCS=2,
    ContentCS=3, # what happened to 4?!
    OriginationCS=5,
    ContentAlertCS=6,
    MediaTypeCS=7,
    AtmosphereCS=8
)
    
def encode_genre(genre):
    
    segments = genre.href.split(':')
    if len(segments) < 6: raise ValueError('genre is incorrectly formatted: %s' % genre)
    
    bits = bitarray(4)
    bits.setall(False)
    
    # b0-3: RFU(0)
    # b4-7: CS
    cs = segments[4]
    if cs in genre_map.keys(): cs_val = genre_map[cs]
    else: raise ValueError('unknown CS in genre: %s' % cs)
    bits += int_to_bitarray(cs_val, 4)
    
    # optional schema levels
    if len(segments) >= 6:
        levels = segments[6].split('.')
        for level in levels:
            bits += int_to_bitarray(int(level), 8)
        
    return bits

def decode_genre(bits):
    
    # b4-7: CS
    cs_val = int(bits[4:8].to01(), 2)
    if cs_val in genre_map.values(): cs = [x[0] for x in genre_map.items() if x[1] == cs_val]
    else: raise ValueError('unknown CS value for genre: %d' % cs_val)
    
    level = '%d' % cs_val
    
    # optional schema levels
    if bits.length() > 8:
        i = 8
        while i < bits.length():
            sublevel = int(bits[i:i+8].to01(), 2)
            level += '.%d' % sublevel
            i += 8
    
    return Genre('urn:tva:metadata:cs:ContentCS:2002:%s' % level)
    
def encode_timepoint(timepoint):
    
    bits = bitarray(1)
    bits.setall(False)
    
    # b0: RFA(0)
        
    # b1-17: Date
    a = (14 - timepoint.month) / 12
    y = timepoint.year + 4800 - a
    m = timepoint.month + (12 * a) - 3
    jdn = timepoint.day + ((153 * m) + 2) / 5 + (365 * y) + (y / 4) - (y / 100) + (y / 400) - 32045
    jd = jdn + (timepoint.hour - 12) / 24 + timepoint.minute / 1440 + timepoint.second / 86400
    mjd = (int)(jd - 2400000.5)
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

def decode_timepoint(bits):
    
    if not bits.any(): return None # NOW
    
    mjd = int(bits[1:18].to01(), 2)
    date = datetime.datetime.fromtimestamp((mjd - 40587) * 86400)
    timepoint = datetime.datetime.combine(date, datetime.time())

    if bits[20]:
        timepoint = timepoint.replace(hour=int(bits[21:26].to01(), 2),
                                      minute=int(bits[26:32].to01(), 2),
                                      second=int(bits[32:38].to01(), 2),
                                      microsecond=int(bits[38:48].to01(), 2) * 1000)
    else:
        timepoint = timepoint.replace(hour=int(bits[21:26].to01(), 2), 
                                      minute=int(bits[26:32].to01(), 2))
    return timepoint

def encode_contentid(id):

    if id.sid and id.scids:
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
        bits += int_to_bitarray(id.scids, 4)
        
        # optional next 8 bits: ECC
        if id.ecc is not None:
            bits += int_to_bitarray(id.ecc, 8)
        
        # optional next 16 bits: EId
        if id.eid is not None:
            bits += int_to_bitarray(id.eid, 16)
        
        # next 16/32 bits: SId
        bits += int_to_bitarray(id.sid, 16)
        
        # optional next 8 bits: X-PAD extension
        if id.xpad is not None:
            bits += int_to_bitarray(id.xpad, 8)

    else: # we have an ensemble id. probably.
        bits = bitarray()
        
        # b0: ECC
        bits += int_to_bitarray(id.ecc, 8)

        # b8: EId
        bits += int_to_bitarray(id.eid, 16)
        
    return bits

def decode_contentid(bits):
    """decodes a ContentId from a bitarray"""
    
    # b0: RFA(0)
    
    # b1: Ensemble Flag. Indicates whether ECC and EId are contained with the
    # Content ID.
    # 0 = ECC and EId are not present. The service that is referenced within the
    # contentID is transmitted on the same ensemble as this EPG service
    # 1 = ECC and EId are present.
    ecc = None
    eid = None
    sid = None
    scids = None
    xpad = None

    
    try:
        if bits.length() == 24: # EnsembleId
            # ECC, EId
            ecc = int(bits[0:8].to01(), 2)
            eid = int(bits[8:24].to01(), 2)
            
        else:    
            ensemble_flag = bits[1]
            xpad_flag = bits[2]
            sid_flag = bits[3]
            
            # SCIdS
            scids = int(bits[4:8].to01(), 2)
            
            # ECC, EId
            i = 8
            if ensemble_flag:
                ecc = int(bits[8:16].to01(), 2)
                eid = int(bits[16:32].to01(), 2)
                i = 32
            
            # SId
            if not sid_flag:
                sid = int(bits[i:i+16].to01(), 2)
                i += 16
            elif sid_flag:
                sid = int(bits[i:i+32].to01(), 2)
                i += 32
                
            # XPAD
            if xpad_flag:
                xpad = int(bits[i+3:i+8].to01(), 2)
    except:
        raise ValueError('error parsing ContentId from data: %s', bitarray_to_hex(bits))
        
        
    return ContentId(ecc, eid, sid, scids, xpad)   

def decode_tokentable(bits):
    
    tokens = {}
    
    i = 0 
    while i < bits.length():
        tag = int(bits[i:i+8].to01(), 2)
        length = int(bits[i+8:i+16].to01(), 2)
        data = bits[i+16:i+16+(length*8)].tostring()
        tokens[tag] = data
        i += 16 + (length * 8)
    return tokens

"""Map of possible num values and their binary equivalents.
   Note that not all the values are currently implemented, which will
   cause the decoder to skip over their details"""
enum_values = {
    (0x02, 0x80, 0x01) : Epg.DAB,
    (0x02, 0x80, 0x02) : Epg.DRM,
    (0x1c, 0x83, 0x01) : False,
    (0x1c, 0x83, 0x02) : True,
    (0x1c, 0x84, 0x01) : "on-air",
    (0x1c, 0x84, 0x02) : "off-air"
}

def decode_enum(parent_tag, tag, bits):
    
    if bits.length() != 8: raise ValueError('enum data for parent/attribute 0x%02x/0x%02x is of incorrect length: %d bytes' % (parent_tag, tag, bits.length()/8))
    
    value = int(bits.to01(), 2)
    key = (parent_tag, tag, value)
    if key in enum_values.keys():
        return enum_values.get(key)
    else:
        raise NotImplementedError('enum for parent/attribute 0x%02x/0x%02x not implemented' % (parent_tag, tag))
    
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
    
    @staticmethod
    def frombits(bits):
                
        # b0-b7: element tag
        tag = int(bits[0:8].to01(), 2)
        if tag != 0x01: raise ValueError('CData does not have the correct tag: 0x%02x != 0x01', tag)
        
        # b8-15: element data length (0-253 bytes)
        # b16-31: extended element length (256-65536 bytes)
        # b16-39: extended element length (65537-16777216 bytes)
        datalength = int(bits[8:16].to01(), 2)
        start = 16
        if datalength >= 254 and datalength <= 1<<16:
            datalength = int(bits[16:32].to01(), 2)
            start = 32
        elif datalength > 1<<16 and datalength <= 1<<24: 
            datalength = int(bits[16:40].to01(), 2)
            start = 40
        elif datalength > 1<<24:
            raise ValueError('element data length exceeds the maximum allowed by the extended element length (24bits): %s > %s' + datalength + " > " + (1<<24))
        data = bits[start:start+(datalength * 8)]
        
        return CData(data.tostring())

def marshall(obj):
    """Marshalls an :class:Epg or :class:ServiceInfo to its binary document"""    
    if isinstance(obj, ServiceInfo): return marshall_serviceinfo(obj)
    elif isinstance(obj, Epg): return marshall_epg(obj)
    
def marshall_serviceinfo(info):
 
    if info.type == ServiceInfo.DRM: raise Exception("DRM not yet supported");

    # serviceInformation
    info_element = Element(0x03)
    if info.version > 1: info_element.attributes.append(Attribute(0x80, info.version, 16)) 
    if info.created: info_element.attributes.append(Attribute(0x81, info.created))
    if info.originator: info_element.attributes.append(Attribute(0x82, info.originator))
    if info.provider: info_element.attributes.append(Attribute(0x83, info.provider))

    # only one ensemble per file
    if len(info.ensembles) == 0: raise ValueError("You must specify an ensemble in this binary encoded Service Information file")
    if len(info.ensembles) > 1: raise ValueError("Cannot have more than one ensemble per binary encoded Service Information file")

    # ensemble
    ensemble = info.ensembles[0]
    ensemble_element = build_ensemble(ensemble)

    info_element.children.append(ensemble_element)

    return info_element.tobytes().tostring()

def marshall_epg(epg):
    
    schedule = epg.schedule
    
    # epg (default type is DAB, so no need to encode)
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
            programme_element.attributes.append(Attribute(0x83, 0x02, 8)) # hardcoded to 'yes'
        if not programme.onair:
            programme_element.attributes.append(Attribute(0x84, 0x02, 8)) # hardcoded to 'on-air'
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
        # TODO language
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
        event_element.children.append(build_link(link))   
             
    return event_element

def build_service(service):
    service_element = Element(0x28)

    # version
    if service.version > 1: service_element.attributes.append(Attribute(0x80, service.version, 16)) 

    # format
    # TODO 

    # bitrate
    if service.bitrate: service_element.attributes.append(Attribute(0x83, service.bitrate * 10, 16))

    # service ID - TODO signal secondary ID
    serviceid_element = Element(0x29)
    serviceid_element.attributes.append(Attribute(0x80, service.id))    
    service_element.children.append(serviceid_element)

    # simulcast TODO

    # names
    for name in service.names:
        service_element.children.append(build_name(name))

    # media
    if len(service.media) > 0:
        service_element.children.append(build_mediagroup(service.media))

    # genre
    for genre in service.genres:
        service_element.children.append(build_genre(genre))

    # language TODO

    # CA TODO

    # keywords 
    if len(service.keywords):
        service_element.children.append(build_keywords(service.keywords))    

    # links TODO

    return service_element

def build_keywords(keywords):
    keywords_element = Element(0x16) # TODO set non-english locale
    keywords_element.cdata = CData(",".join(keywords))
    return keywords_element

def build_ensemble(ensemble):
    ensemble_element = Element(0x26)

    ensemble_element.attributes.append(Attribute(0x80, ensemble.id))
    if ensemble.version > 1: ensemble_element.attributes.append(Attribute(0x81, ensemble.version, 16))

    # names
    for name in ensemble.names:
        ensemble_element.children.append(build_name(name))

    # frequencies
    if not len(ensemble.frequencies):
        raise ValueError('At least one frequency must be defined for this ensemble')
    for frequency in ensemble.frequencies:
        frequency_element = Element(0x27)
        frequency_element.attributes.append(Attribute(0x81, frequency, 24))
        ensemble_element.children.append(frequency_element)

    # media
    if len(ensemble.media) > 0:
        ensemble_element.children.append(build_mediagroup(ensemble.media))

    # keywords

    # links

    # services
    for service in ensemble.services:
        service_element = build_service(service) 
        ensemble_element.children.append(service_element)

    return ensemble_element

token_table_pattern = re.compile('([\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\x0b\\x0c\\x0e\\x0f\\x10\\x11\\x12\\x13])')
def apply_token_table(val, e):
    x = e
    while x:
        if hasattr(x, 'tokens'):
            tokens = x.tokens
            matcher = re.findall(token_table_pattern, val)
            if matcher:
                for group in matcher: 
                    logger.debug('replacing 0x%02x with %s', ord(group), tokens[ord(group)])
                    val = val.replace(group, tokens[ord(group)])
            matcher = re.search(token_table_pattern, val)
            if matcher: 
                logger.warning('%d tokens (%s) still remain in string "%s" from table: %s', len(matcher.groups()), matcher.groups(), val, tokens)
            break
        elif hasattr(x, 'parent'):
            x = x.parent
        else:
            break
    return val        

def print_info(e):

    print e.attributes
    print e.children
    print e.cdata

def parse_time(e):
    
    billed_time = e.get_attributes(0x80)[0].value
    billed_duration = e.get_attributes(0x81)[0].value
    actual_time = None
    if e.has_attribute(0x82): actual_time = e.get_attributes(0x82)[0].value
    actual_duration = None
    if e.has_attribute(0x82): actual_duration = e.get_attributes(0x83)[0].value
    time = Time(billed_time, billed_duration, actual_time, actual_duration)
    return time

def parse_bearer(e):
    
    id = e.get_attributes(0x80)[0].value
    bearer = Bearer(id)
    return bearer
    

def parse_location(e):
    
    location = Location()
    
    # times
    for c in e.get_children(0x2c):
        location.times.append(parse_time(c))
        
    # bearer
    for c in e.get_children(0x2d):
        location.bearers.append(parse_bearer(c)) 
    
    # apply a default content ID
    if not len(location.bearers):
        x = e
        while x:
            if hasattr(x, 'default_contentid'):
                default_contentid = x.default_contentid
                location.bearers.append(default_contentid)
                break
            elif hasattr(x, 'parent'):
                x = x.parent
            else:
                break   
    if not len(location.bearers):
        raise ValueError('location has no bearers and no default content ID is defined')
    
    return location

def parse_media(e):
    
    media = []
    
    # descriptions
    for c in e.get_children(0x1a):
        val = apply_token_table(c.cdata.value, e)
        media.append(ShortDescription(val))
    for c in e.get_children(0x1b):
        val = apply_token_table(c.cdata.value, e)
        media.append(LongDescription(val))
        
    return media

def parse_programme(e):    
    
    shortid = e.get_attributes(0x81)[0].value
    programme = Programme(shortid)
    
    # names
    for c in e.get_children(0x10):
        val = apply_token_table(c.cdata.value, e)
        programme.names.append(ShortName(val))
    for c in e.get_children(0x11):
        val = apply_token_table(c.cdata.value, e)
        programme.names.append(MediumName(val))
    for c in e.get_children(0x12):
        val = apply_token_table(c.cdata.value, e)
        programme.names.append(LongName(val))  
        
    # media
    for c in e.get_children(0x13):
        media = parse_media(c)
        programme.media.extend(media)              
    
    # location
    for c in e.get_children(0x19):
        programme.locations.append(parse_location(c))
    
    return programme
 
def parse_schedule(e):
    
    schedule = Schedule()
    
    # programmes
    programme_elements = e.get_children(0x1c)
    for p in programme_elements: 
        programme = parse_programme(p)
        schedule.programmes.append(programme)
        
    return schedule

def parse_epg(e):
    schedule = parse_schedule(e.get_children(0x21)[0])
    return Epg(schedule, type)

def parse_service(e):
    
    id = e.get_children(0x29)[0].get_attributes(0x80)[0].value
    service = Service(id)
    
    # names
    for c in e.get_children(0x10):
        val = apply_token_table(c.cdata.value, e)
        service.names.append(ShortName(val))
    for c in e.get_children(0x11):
        val = apply_token_table(c.cdata.value, e)
        service.names.append(MediumName(val))
    for c in e.get_children(0x12):
        val = apply_token_table(c.cdata.value, e)
        service.names.append(LongName(val)) 
    return service
    

def parse_ensemble(e):    
    id = e.get_attributes(0x80)[0].value
    ensemble = Ensemble(id)
    
    # names
    for c in e.get_children(0x10):
        val = apply_token_table(c.cdata.value, e)
        ensemble.names.append(ShortName(val))
    for c in e.get_children(0x11):
        val = apply_token_table(c.cdata.value, e)
        ensemble.names.append(MediumName(val))
    for c in e.get_children(0x12):
        val = apply_token_table(c.cdata.value, e)
        ensemble.names.append(LongName(val)) 
        
    # services
    for c in e.get_children(0x28):
        ensemble.services.append(parse_service(c))
    
    return ensemble 

def parse_service_information(e):
    service_info = ServiceInfo()
    ensemble = parse_ensemble(e.get_children(0x26)[0])
    service_info.ensembles.append(ensemble)
    return service_info
    
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
      
def unmarshall(i):
    """Unmarshalls a PI or SI binary file to its respective :class:Epg or :class:ServiceInfo object
    
    :param i: String or File object to read binary from
    :type i: str, file
    """    
    
    logger.debug('unmarshalling object of type: %s', type(i))
    
    b = bitarray()
    if isinstance(i, file):
        logger.debug('object is a file')
        b.fromfile(i)
    else:
        logger.debug('object is a string of %d bytes', len(str(i)))
        b.fromstring(str(i))
        
    e = Element.frombits(b)
    logger.debug('unmarshalled element %s', e)
    if e.tag == 0x03:
        si = parse_service_information(e)
        return si
    elif e.tag == 0x02:
        epg = parse_epg(e)
        return epg
    else:
        raise Exception('Arrgh! this be neither serviceInformation nor epg - to Davy Jones\' locker with ye!')    
