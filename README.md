# Description

A python implementation of the ETSI DAB EPG XML standard (ETSI TS 102 818 v1.5), incorporating an XML and binary marshaller conforming to ETSI TS 102 371. 

This can be used by broadcasters for producing or parsing EPG data to a DAB multiplex for broadcast, or for general schedule interfacing. It can also be used for producing data based around the DAB EPG standard, such as for [http://www.radioplayer.co.uk UK Radioplayer].

# TODO

The library generally ignore GI files, and there may be some shortcuts taken when marshalling/unmarshalling, e.g. not supporting DRM in any way.

There is no profiling split in the binary marshaller.

# Usage

## Programme Information

Semantically equivalent to the example given in ETSI TS 102 818 section 4.3.1

```
<?xml version="1.0" encoding="UTF-8"?>
<epg system="DAB">
    <schedule creationTime="2009-02-09T14:52:49.263Z" originator="BBC" version="1">
        <scope startTime="2001-03-01T00:00:00.000Z" stopTime="2001-03-02T18:00:00.000Z">
            <serviceScope id="e1.ce15.c221.0"/>
            <serviceScope id="e1.ce15.c224.0"/>
        </scope>
        <programme id="crid://www.bbc.co.uk;dab/BC81123456a" recommendation="yes" shortId="213456">
            <mediumName xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" xmlns="http://www.worlddab.org/schemas/epg">Gilles Peterson</mediumName>
            <longName xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" xmlns="http://www.worlddab.org/schemas/epg">Gilles Peterson: Worldwide</longName>
            <location>
                <time actualDuration="PT2H" actualTime="2003-12-18T00:00:00.000Z" duration="PT2H" time="2003-12-18T00:00:00.000Z"/>
                <bearer id="e1.ce15.c221.0"/>
            </location>
            <mediaDescription>
                <shortDescription xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" xmlns="http://www.worlddab.org/schemas/epg"><![CDATA[Gilles Peterson brings you two hours of global beats and the best of cool. Including the Worldwide family. KV5 are live from Maida Value with special guests.]]></shortDescription>
            </mediaDescription>
            <mediaDescription/>
            <genre href="urn:tva:metadata:cs:ContentCS:2005:3.6.7">
                <name xmlns="http://www.worlddab.org/schemas/epg"><![CDATA[Rap/Hip Hop/Reggae]]></name>
            </genre>
            <genre href="urn:tva:metadata:cs:ContentCS:2005:3.6.8">
                <name xmlns="http://www.worlddab.org/schemas/epg"><![CDATA[Electronic/Club/Urban/Dance]]></name>
            </genre>
            <genre href="urn:tva:metadata:cs:FormatCS:2005:2.5">
                <name xmlns="http://www.worlddab.org/schemas/epg"><![CDATA[ARTISTIC PERFORMANCE]]></name>
            </genre>
            <genre href="urn:tva:metadata:cs:IntentionCS:2005:1.1">
                <name xmlns="http://www.worlddab.org/schemas/epg"><![CDATA[ENTERTAINMENT]]></name>
            </genre>
            <genre href="urn:tva:metadata:cs:ContentCS:2005:3.6.9">
                <name xmlns="http://www.worlddab.org/schemas/epg"><![CDATA[World/Traditional/Ethnic/Folk music]]></name>
            </genre>
            <memberOf id="crid://www.bbc.co.uk/WorldwideGroup" shortId="1000"/>
            <link description="Email:" xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" url="mailto:gilles.peterson@bbc.co.uk"/>
            <link description="Web:" xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" url="http://www.bbc.co.uk/radio1/urban/peterson"/>
            <keywords xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en"></keywords>
            <programmeEvent shortId="6353">
                <shortName xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" xmlns="http://www.worlddab.org/schemas/epg">Herbert</shortName>
                <mediumName xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" xmlns="http://www.worlddab.org/schemas/epg">Herbert Live</mediumName>
                <longName xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" xmlns="http://www.worlddab.org/schemas/epg">Live session from Herbert</longName>
                <location>
                    <relativeTime duration="PT15M" time="PT45M"/>
                </location>
                <mediaDescription>
                    <shortDescription xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" xmlns="http://www.worlddab.org/schemas/epg"><![CDATA[Live session from Herbert, recorded at Cargo on 24/2/01]]></shortDescription>
                </mediaDescription>
                <mediaDescription/>
            </programmeEvent>
        </programme>
        <programme shortId="59033">
            <mediumName xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en" xmlns="http://www.worlddab.org/schemas/epg">PM</mediumName>
            <location>
                <time duration="PT1H" time="2003-12-18T17:00:00.000Z"/>
                <bearer id="e1.ce15.c224.0"/>
            </location>
            <keywords xmlns:ns0="http://www.w3.org/XML/2001/namespace" ns0:lang="en"></keywords>
        </programme>
    </schedule>
</epg>
```

The code to generate this is:

```
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
```

## Service Information

Semantically equivalent to the example given in ETSI TS 102 818 Section X

```
<?xml version="1.0" encoding="UTF-8"?>
<serviceInformation creationTime="2001-02-28T00:00:00"
	originator="BBC" serviceProvider="BBC" system="DAB" version="2"
	xml:lang="en" xmlns="http://www.worlddab.org/schemas/epgSI/14"
	xmlns:epg="http://www.worlddab.org/schemas/epgDataTypes/14" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://www.worlddab.org/schemas/epgSI/14 epgSI_14.xsd">
	<ensemble id="e1.ce15">
		<epg:shortName>BBC</epg:shortName>
		<epg:mediumName>BBC National</epg:mediumName>
		<frequency kHz="225648" type="primary" />
		<service bitrate="160" format="audio">
			<serviceID id="e1.ca15.c221.0" />
			<epg:shortName>Radio 1</epg:shortName>
			<epg:mediumName>BBC Radio 1</epg:mediumName>
			<mediaDescription>
				<epg:shortDescription><![CDATA[Rock and pop music from the BBC.]]></epg:shortDescription>
			</mediaDescription>
			<mediaDescription>
				<epg:multimedia type="logo_colour_square"
					url="http://www.bbc.co.uk/radio1/images/r1logo.png" />
			</mediaDescription>
			<epg:genre href="urn:tva:metadata:cs:ContentCS:2002:3.6.7">
				<epg:name><![CDATA[Rap/Hip Hop/Reggae]]></epg:name>
			</epg:genre>
			<epg:genre href="urn:tva:metadata:cs:ContentCS:2002:3.6.8">
				<epg:name><![CDATA[Electronic/Club/Urban/Dance]]></epg:name>
			</epg:genre>
			<epg:genre href="urn:tva:metadata:cs:ContentCS:2002:2.5.0">
				<epg:name><![CDATA[ARTISTIC PERFORMANCE]]></epg:name>
			</epg:genre>
			<epg:genre href="urn:tva:metadata:cs:ContentCS:2002:1.1.0">
				<epg:name><![CDATA[ENTERTAINMENT]]></epg:name>
			</epg:genre>
			<link mimeType="text/html" url="http://www.bbc.co.uk/radio1" />
			<keywords><![CDATA[music, pop, rock, dance, hip-hop, soul]]></keywords>
		</service>
		<service format="audio">
			<serviceID id="e1.ca15.c222.0" />
			<epg:shortName>Radio 2</epg:shortName>
			<epg:mediumName>BBC Radio 2</epg:mediumName>
		</service>
		<service format="audio">
			<serviceID id="e1.ca15.c223.0" />
			<epg:shortName>Radio 3</epg:shortName>
			<epg:mediumName>BBC Radio 3</epg:mediumName>
		</service>
		<service format="audio">
			<serviceID id="e1.ca15.c224.0" />
			<epg:shortName>Radio 4</epg:shortName>
			<epg:mediumName>BBC Radio 4</epg:mediumName>
		</service>
		<service format="audio">
			<serviceID id="e1.ca15.c225.0" />
			<epg:shortName>Radio 5</epg:shortName>
			<epg:mediumName>BBC Radio 5</epg:mediumName>
		</service>
	</ensemble>
</serviceInformation>
```

The code to generate this is:

```

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

        print marshall(info, indent='   ')
```

## Element Listener

A listener is applied to most elements when serializing, and can be passed in during the XML marshalling phase:

```
xml = marshall(epg, listener=augmenter)
```

Where `schedule_augmenter` is a class implementing the `dabepg.xml.MarshallListener` interface:

```
class MarshallListener:
    
    def on_element(self, doc, object, element):
        pass
```

Where `doc` is the DOM document object, `object` is the originating API object that is being serialized, and `element` is the resultant element that can be modified.

Additional elements can be added, or generated elements and attributes modified to suit.


