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
import xml.dom.minidom
from elementtree.ElementTree import parse
import isodate
from xml.dom import XML_NAMESPACE

EPG_NS = 'http://www.worlddab.org/schemas/epgDataTypes/14'
SCHEDULE_NS = 'http://www.worlddab.org/schemas/epgSchedule/14'
SERVICEINFO_NS = 'http://www.worlddab.org/schemas/epgSI/14'
TYPES_NS = 'http://www.worlddab.org/schemas/epgDataTypes/14'
XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'
SCHEDULE_SCHEMA_LOCATION = '%s epgSchedule_14.xsd' % SCHEDULE_NS
SERVICEINFO_SCHEMA_LOCATION = '%s epgSI_14.xsd' % SERVICEINFO_NS

class MarshallListener:
    
    def on_element(self, doc, object, element):
        pass
    
def marshall(obj, listener=MarshallListener(), **kwargs):
    if isinstance(obj, ServiceInfo): return marshall_serviceinfo(obj, listener, **kwargs)
    elif isinstance(obj, Epg): return marshall_epg(obj, listener, **kwargs)
    else: raise ValueError('neither a ServiceInfo nor an Epg be')
    
def marshall_serviceinfo(info, listener=MarshallListener(), **kwargs):
    
    doc = xml.dom.minidom.Document()
    
    # service info
    info_element = doc.createElement('serviceInformation')
    info_element.namespaceURI = SCHEDULE_NS
    if info.version > 1: info_element.setAttribute('version', str(info.version))
    info_element.setAttribute('creationTime', info.created.isoformat())
    if info.originator is not None:
        info_element.setAttribute('originator', info.originator)
    if info.provider is not None:
        info_element.setAttribute('serviceProvider', info.provider)   
    info_element.setAttribute('system', info.type)
    doc.appendChild(info_element)
    
    # fudge the namespaces in there
    info_element.setAttribute('xmlns', SCHEDULE_NS)
    info_element.setAttribute('xmlns:epg', TYPES_NS)
    info_element.setAttribute('xmlns:xsi', XSI_NS)
    info_element.setAttribute('xsi:schemaLocation', SERVICEINFO_SCHEMA_LOCATION)
    info_element.setAttribute('xml:lang', 'en')

    # ensemble
    for ensemble in info.ensembles:
        ensemble_element = doc.createElement('ensemble')
        ensemble_element.setAttribute('id', str(ensemble))
        if ensemble.version > 1: ensemble_element.setAttribute('version', str(ensemble.version))
        for name in ensemble.names:
            ensemble_element.appendChild(build_name(doc, name))
        for frequency in ensemble.frequencies:
            frequency_element = doc.createElement('frequency')
            if len(ensemble_element.getElementsByTagName('frequency')) == 0:
                frequency_element.setAttribute('type', 'primary')
            else:
                frequency_element.setAttribute('type', 'secondary')
            frequency_element.setAttribute('kHz', str(frequency))
            ensemble_element.appendChild(frequency_element)
            
        # service
        for service in ensemble.services:
            service_element = doc.createElement('service')
            if service.version > 1: service_element.setAttribute('version', str(service.version))
            service_element.setAttribute('format', service.format)
            service_id_element = doc.createElement('serviceID')
            service_id_element.setAttribute('id', str(service.id))
            service_element.appendChild(service_id_element)
            if service.bitrate is not None: 
                service_element.setAttribute('bitrate', str(service.bitrate))
            # names
            for name in service.names:
                service_element.appendChild(build_name(doc, name))
            # media
            for media in service.media:
                service_element.appendChild(build_mediagroup(doc, media)) 
            # genre
            for genre in service.genres:
                service_element.appendChild(build_genre(doc, genre))    
            # links
            for link in service.links:
                service_element.appendChild(build_link(doc, link))                    
            # keywords
            if len(service.keywords) > 0:
                keywords_element = doc.createElement('keywords')
                service_element.appendChild(keywords_element)
                keywords_element.appendChild(doc.createCDATASection(', '.join(service.keywords)))
                
            listener.on_element(doc, service, service_element)
            ensemble_element.appendChild(service_element)
                
        listener.on_element(doc, ensemble, ensemble_element)
        info_element.appendChild(ensemble_element)
        
    listener.on_element(doc, info, info_element)
        
    if kwargs.has_key('indent'):
        return doc.toprettyxml(indent=kwargs['indent'], encoding='UTF-8')
    else:
        return doc.toxml('UTF-8')

def marshall_epg(epg, listener=MarshallListener(), **kwargs):
    
    doc = xml.dom.minidom.Document()
    
    schedule = epg.schedule
    
    # epg
    epg_element = doc.createElement('epg')
    epg_element.namespaceURI = SCHEDULE_NS
    doc.appendChild(epg_element)
    
    # fudge the namespaces in there
    epg_element.setAttribute('xmlns', SCHEDULE_NS)
    epg_element.setAttribute('xmlns:epg', TYPES_NS)
    epg_element.setAttribute('xmlns:xsi', XSI_NS)
    epg_element.setAttribute('xsi:schemaLocation', SCHEDULE_SCHEMA_LOCATION)
    epg_element.setAttribute('xml:lang', 'en')
    
    epg_element.setAttribute('system', epg.type)
    
    # schedule
    schedule_element = doc.createElement('schedule')
    epg_element.appendChild(schedule_element)
    schedule_element.setAttribute('version', str(schedule.version))
    schedule_element.setAttribute('creationTime', schedule.created.isoformat())
    if schedule.originator is not None:
        schedule_element.setAttribute('originator', schedule.originator)
        
    # scope
    scope = schedule.get_scope()
    if scope is not None:
        scope_element = doc.createElement('scope')
        scope_element.setAttribute('startTime', scope.start.isoformat())
        scope_element.setAttribute('stopTime', scope.end.isoformat())
        for service in scope.services:
            service_scope_element = doc.createElement('serviceScope')
            service_scope_element.setAttribute('id', str(service))
            scope_element.appendChild(service_scope_element)
            listener.on_element(doc, service, service_scope_element)
        listener.on_element(doc, scope, scope_element)
        schedule_element.appendChild(scope_element)
    
    # programmes
    for programme in schedule.programmes:
        programme_element = doc.createElement('programme')
        programme_element.setAttribute('shortId', str(programme.shortcrid))
        if programme.crid is not None:
            programme_element.setAttribute('id', str(programme.crid))
        if programme.version is not None:
            programme_element.setAttribute('version', str(programme.version))
        if programme.recommendation:
            programme_element.setAttribute('recommendation', 'yes')
        if not programme.onair:
            programme_element.setAttribute('broadcast', 'off-air')
        if programme.bitrate is not None:
            programme_element.setAttribute('bitrate', str(programme.bitrate)) 
        # names
        for name in programme.names:
            child = build_name(doc, name)
            listener.on_element(doc, name, child)
            programme_element.appendChild(child)
        # locations
        for location in programme.locations:
            child = build_location(doc, location, listener)
            listener.on_element(doc, location, child)
            programme_element.appendChild(child)    
        # media
        for media in programme.media:
            child = build_mediagroup(doc, media, 'epg')
            listener.on_element(doc, media, child)
            programme_element.appendChild(child)     
        # genre
        for genre in programme.genres:
            child = build_genre(doc, genre)
            listener.on_element(doc, genre, child)
            programme_element.appendChild(child)    
        # membership
        for membership in programme.memberships:
            child = build_membership(doc, membership)
            listener.on_element(doc, membership, child)
            programme_element.appendChild(child)    
        # link
        for link in programme.links:
            child = build_link(doc, link)
            listener.on_element(doc, link, child)
            programme_element.appendChild(child)      
        # events
        for event in programme.events:
            child = build_programme_event(doc, event, listener)
            listener.on_element(doc, event, child)
            programme_element.appendChild(child) 
            
        schedule_element.appendChild(programme_element)
            
        listener.on_element(doc, programme, programme_element)
        
    listener.on_element(doc, epg, epg_element)
        
    if kwargs.has_key('indent'):
        return doc.toprettyxml(indent=kwargs['indent'], encoding='UTF-8')
    else:
        return doc.toxml('UTF-8')
    
def build_name(doc, name):
    name_element = None
    if isinstance(name, ShortName):
        name_element = doc.createElement('epg:shortName')
    elif isinstance(name, MediumName):
        name_element = doc.createElement('epg:mediumName')
    elif isinstance(name, LongName):
        name_element = doc.createElement('epg:longName')
    name_element.appendChild(doc.createTextNode(name.text))
    return name_element
    
def build_location(doc, location, listener):
    location_element = doc.createElement('epg:location')
    for time in location.times:
        if isinstance(time, Time):
            time_element = doc.createElement('epg:time')
            location_element.appendChild(time_element)
            time_element.setAttribute('time', time.billed_time.isoformat())
            time_element.setAttribute('duration', get_iso_period(time.billed_duration))
            listener.on_element(doc, time, time_element)
        elif isinstance(time, RelativeTime):
            time_element = doc.createElement('epg:relativeTime')
            location_element.appendChild(time_element)
            time_element.setAttribute('time', get_iso_period(time.billed_offset))
            time_element.setAttribute('duration', get_iso_period(time.billed_duration)) 
            listener.on_element(doc, time, time_element)
    for bearer in location.bearers:
        bearer_element = doc.createElement('epg:bearer')
        location_element.appendChild(bearer_element)
        bearer_element.setAttribute('id', str(bearer))  
        listener.on_element(doc, bearer, bearer_element)
    return location_element  
    
def build_mediagroup(doc, media, namespace=None):
    namespace = namespace + ':' if namespace is not None else ''
    mediagroup_element = doc.createElement('%smediaDescription' % namespace)
    if isinstance(media, ShortDescription):
        media_element = doc.createElement('epg:shortDescription')
        mediagroup_element.appendChild(media_element)
        media_element.appendChild(doc.createCDATASection(media.text))
    elif isinstance(media, LongDescription):
        media_element = doc.createElement('epg:longDescription')
        mediagroup_element.appendChild(media_element)
        media_element.appendChild(doc.createCDATASection(media.text))    
    elif isinstance(media, Multimedia):
        media_element = doc.createElement('epg:multimedia')
        mediagroup_element.appendChild(media_element)
        media_element.setAttribute('url', media.url)
        media_element.setAttribute('type', media.type)
        if media.type == Multimedia.LOGO_UNRESTRICTED:
            media_element.setAttribute('height', str(media.height))
            media_element.setAttribute('width', str(media.width))
    return mediagroup_element
    
def build_genre(doc, genre):
    genre_element = doc.createElement('epg:genre')
    genre_element.setAttribute('href', genre.href)
    if genre.name is not None:
        genre_name_element = doc.createElement('epg:name')
        genre_element.appendChild(genre_name_element)
        genre_name_element.appendChild(doc.createCDATASection(genre.name))
    return genre_element    
    
def build_membership(doc, membership):
    membership_element = doc.createElement('memberOf')
    membership_element.setAttribute('shortId', str(membership.shortcrid))
    if membership.crid is not None:
        membership_element.setAttribute('crid', membership.crid)
    if membership.index is not None: 
        membership_element.setAttribute('index', str(membership.index))
    return membership_element  
    
def build_link(doc, link):
    link_element = doc.createElement('link')
    link_element.setAttribute('url', link.url)
    if link.description is not None:
        link_element.setAttribute('description', link.description)
    if link.mimetype is not None:
        link_element.setAttribute('mimeType', link.mimetype)
    if link.expiry is not None:
        link_element.setAttribute('expiryTime', link.expiry.isoformat())
    return link_element   

def build_programme_event(doc, event, listener):
    event_element = doc.createElement('epg:programmeEvent')
    if event.shortcrid is not None:
        event_element.setAttribute('shortId', str(event.shortcrid))
    if event.crid is not None:
        event_element.setAttribute('id', str(event.crid))
    if event.version is not None:
        event_element.setAttribute('version', str(event.version))
    if event.recommendation is not False:
        event_element.setAttribute('recommendation', 'yes')
    if not event.onair is not None:
        event_element.setAttribute('broadcast', 'off-air')
    if event.bitrate is not None:
        event_element.setAttribute('bitrate', str(event.bitrate))
     # names
    for name in event.names:
        event_element.appendChild(build_name(doc, name))
    # locations
    for location in event.locations:
        event_element.appendChild(build_location(doc, location, listener))    
    # media
    for media in event.media:
        event_element.appendChild(build_mediagroup(doc, media, 'epg'))       
    # genre
    for genre in event.genres:
        event_element.appendChild(build_genre(doc, genre)) 
    # membership
    for membership in event.memberships:
        event_element.appendChild(build_membership(doc, membership))  
    # link
    for link in event.links:
        event_element.appendChild(build_link(doc, link))   
             
    return event_element
    
def get_iso_period(duration):
    if isinstance(duration, int): duration = datetime.timedelta(seconds=duration)
    days = duration.days
    hours = duration.seconds / (60 * 60)
    minutes = (duration.seconds - hours * 60 * 60) / 60
    seconds = (duration.seconds - hours * 60 * 60 - minutes * 60)
    result = 'P'
    if days > 0: result +='%dD' % days
    result += 'T'
    if hours > 0: result += '%dH' % hours
    if minutes > 0: result += '%dM' % minutes
    if seconds > 0: result += '%dS' % seconds
    if hours == 0 and minutes == 0 and seconds == 0: result += '0S'
    return result

def get_schedule_filename(date, id):
    return '%s_%s_%s_%s_%s_PI.xml' % (date.strftime('%Y%m%d'), id.ecc, id.eid, id.sid, id.scids)

def get_serviceinfo_filename(date, channel):
    
    # try to get a unique 8 character identifier
    channel = re.sub(r'\W+', '', channel.upper())[:8]

    return '%s_%s_SI.xml' % (date.strftime('%Y%m%d'), channel) 

def parse_serviceinfo(root):
    service_info = ServiceInfo()
    if root.attrib.has_key('creationTime'): service_info.created = isodate.parse_datetime(root.attrib['creationTime'])
    if root.attrib.has_key('version'): service_info.version = int(root.attrib['version'])
    if root.attrib.has_key('originator'): service_info.originator = root.attrib['originator']
    if root.attrib.has_key('serviceProvider'): service_info.provider = root.attrib['serviceProvider']
    if root.attrib.has_key('system') and root.attrib['system'] == 'DRM': raise Exception('parser only supports DAB EPG')
    if not root.attrib.has_key('{%s}lang' % XML_NAMESPACE): raise Exception('no xml:lang attribute declaration')
    
    for ensembleElement in root.findall("{%s}ensemble" % SERVICEINFO_NS):
        service_info.ensembles.append(parse_ensemble(ensembleElement))
    
    return service_info

def parse_epg(doc):
    pass

def parse_name(nameElement):
    if nameElement.tag == '{%s}shortName' % EPG_NS:
        return ShortName(nameElement.text)
    elif nameElement.tag == '{%s}mediumName' % EPG_NS:
        return MediumName(nameElement.text)
    elif nameElement.tag == '{%s}longName' % EPG_NS:
        return LongName(nameElement.text)
    else:
        raise ValueError('unknown name element: %s' % nameElement)
    
def parse_description(descriptionElement):
    if descriptionElement.tag == '{%s}shortDescription' % EPG_NS:
        return ShortDescription(descriptionElement.text)
    elif descriptionElement.tag == '{%s}longDescription' % EPG_NS:
        return LongDescription(descriptionElement.text)   
    else:
        raise ValueError('unknown description element: %s' % descriptionElement)
    
def parse_multimedia(multimediaElement):
    multimedia = Multimedia(multimediaElement.attrib['url'])
    if multimediaElement.attrib.has_key('type'):
        type = multimediaElement.attrib['type']
        if type == 'logo_colour_square': multimedia.type = Multimedia.LOGO_COLOUR_SQUARE
        if type == 'logo_colour_rectangle': multimedia.type = Multimedia.LOGO_COLOUR_RECTANGLE
        if type == 'logo_mono_rectangle': multimedia.type = Multimedia.LOGO_MONO_RECTANGLE
        if type == 'logo_mono_square': multimedia.type = Multimedia.LOGO_MONO_SQUARE
        if type == 'logo_unrestricted': 
            multimedia.type = Multimedia.LOGO_UNRESTRICTED
            if not multimediaElement.attrib.has_key('mimetype') or not multimediaElement.attrib.has_key('width') or not multimediaElement.attrib.has_key('height'):
                raise ValueError('must specify mimetype, width and height for unrestricted logo')
    if multimediaElement.attrib.has_key('mimetype'): multimedia.mime = multimediaElement.attrib['mimetype']
    if multimediaElement.attrib.has_key('width'): multimedia.width = int(multimediaElement.attrib['width'])
    if multimediaElement.attrib.has_key('height'): multimedia.width = int(multimediaElement.attrib['height'])  
    return multimedia      
    
def parse_media(mediaElement):
    media = []
    for descriptionElement in mediaElement.findall("{%s}shortDescription" % EPG_NS): media.append(parse_description(descriptionElement))    
    for descriptionElement in mediaElement.findall("{%s}longDescription" % EPG_NS): media.append(parse_description(descriptionElement)) 
    for multimediaElement in mediaElement.findall("{%s}multimedia" % EPG_NS): media.append(parse_multimedia(multimediaElement))
    return media

def parse_genre(genreElement):
    genre = Genre(genreElement.attrib['href'])
    genre.name = genreElement.findtext('{%s}name' % EPG_NS)
    return genre  

def parse_link(linkElement):
    link = Link(linkElement.attrib['url'])
    if linkElement.attrib.has_key('description'):
        link.description = linkElement.attrib['description']
    if linkElement.attrib.has_key('mimeType'):
        link.mimetype = linkElement.attrib['mimeType']    
    if linkElement.attrib.has_key('expiryTime'):
        link.expiry = isodate.parse_datetime(linkElement.attrib['expiryTime']) 
    return link
        
def parse_keywords(keywordsElement):
    return map(lambda x: x.strip(), keywordsElement.text.split(','))
    
def parse_service(serviceElement):
    id = ContentId.fromstring(serviceElement.find("{%s}serviceID" % SERVICEINFO_NS).attrib['id'])
    service = Service(id)
    
    # attributes
    if serviceElement.attrib.has_key('version'): service.version = int(serviceElement.attrib['version'])
    if serviceElement.attrib.has_key('bitrate'): service.bitrate = int(serviceElement.attrib['bitrate'])
    
    # subelements
    for nameElement in serviceElement.findall("{%s}shortName" % EPG_NS): service.names.append(parse_name(nameElement))
    for nameElement in serviceElement.findall("{%s}mediumName" % EPG_NS): service.names.append(parse_name(nameElement))
    for nameElement in serviceElement.findall("{%s}longName" % EPG_NS): service.names.append(parse_name(nameElement))
    for mediaElement in serviceElement.findall("{%s}mediaDescription" % SERVICEINFO_NS): service.media.extend(parse_media(mediaElement))
    for genreElement in serviceElement.findall("{%s}genre" % EPG_NS): service.genres.append(parse_genre(genreElement))
    for linkElement in serviceElement.findall("{%s}link" % SERVICEINFO_NS): service.links.append(parse_link(linkElement))
    for keywordsElement in serviceElement.findall("{%s}keywords" % SERVICEINFO_NS): service.keywords.extend(parse_keywords(keywordsElement))
    
    return service

def parse_ensemble(ensembleElement):
    ensemble = Ensemble(ContentId.fromstring(ensembleElement.attrib['id']))
    for nameElement in ensembleElement.findall("{%s}shortName" % SCHEDULE_NS): ensemble.names.append(parse_name(nameElement))
    for nameElement in ensembleElement.findall("{%s}mediumName" % SCHEDULE_NS): ensemble.names.append(parse_name(nameElement))
    for nameElement in ensembleElement.findall("{%s}longName" % SCHEDULE_NS): ensemble.names.append(parse_name(nameElement))
    
    for frequencyElement in ensembleElement.findall("{%s}frequency" % SERVICEINFO_NS):
        ensemble.frequencies.append(int(frequencyElement.attrib['kHz']))
        
    for serviceElement in ensembleElement.findall("{%s}service" % SERVICEINFO_NS):
        ensemble.services.append(parse_service(serviceElement))
    return ensemble

def unmarshall(i):
    
    # read data
    import StringIO
    d = i if isinstance(i, file) else StringIO.StringIO(i)
    
    doc = parse(d)
    root = doc.getroot()
    
    if root.tag == '{%s}serviceInformation' % SERVICEINFO_NS:
        return parse_serviceinfo(root)
    elif root.tag == '{%s}epg' % SCHEDULE_NS:
        return parse_epg(root)
    else:
        raise Exception('Arrgh! this be neither serviceInformation nor epg - to Davy Jones\' locker with ye!')   
    