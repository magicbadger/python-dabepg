# Description

A python implementation of the ETSI DAB EPG standard ([http://pda.etsi.org/pda/home.asp?wki_id=hUkTWWG26f8ABCDFDRWAh ETSI TS 102 818]) incorporating an XML and binary marshaller ([http://pda.etsi.org/pda/home.asp?wki_id=-WO7ND5Wzoz_.%27,-28nGw ETSI TS 102 371]). 

This can be used by broadcasters for producing or parsing EPG data to a DAB multiplex for broadcast, or for general schedule interfacing. It can also be used for producing data based on the DAB EPG standard, such as for [http://www.radioplayer.co.uk UK Radioplayer]

The API closely follows the hierarchy of the XML specification, and hence maps well to the concepts contained within.

# Current status

It is being used in production environments for broadcasters, as well as for testing and evaluation. If you do intend to use it, please bear in mind that issues may well exist and testing should be performed to validate it for your particular use case.

I am in the process of augmenting the library with a range of tests for this purpose.

# TODO

The library generally ignore GI files, and there may be some shortcuts taken when marshalling/unmarshalling, e.g. not supporting DRM systems.

Most importantly, the library is currently missing any profiling considerations in its Binary marshaller - i.e. the splitting of the binary between Basic and Advanced profiles, as well as the combining of the two binary files upon binary unmarshalling.

# Installation

Currently, you'll have to download the source and use it locally. I'm working on making installation easier.

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

