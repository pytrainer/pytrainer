<?xml version="1.0"?>

<!-- note defining a namespace for TrainingCenterDatabase as the translation does not seem to work with a default namespace -->
<xsl:stylesheet version="1.0"
xmlns:t="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>
<xsl:output  method="xml" indent="yes" omit-xml-declaration="no"/> 

<!-- this is a bit of a messy way to get whitespace into the output - but it works -->
<xsl:variable name="newline"><xsl:text>
</xsl:text></xsl:variable>

<xsl:template match="/">
    <gpx xmlns="http://www.topografix.com/GPX/1/1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
    creator="pytrainer http://sourceforge.net/projects/pytrainer" version="1.1"
    xsi:schemaLocation="http://www.topografix.com/GPX/1/1
    http://www.topografix.com/GPX/1/1/gpx.xsd
    http://www.cluetrust.com/XML/GPXDATA/1/0
    http://www.cluetrust.com/Schemas/gpxdata10.xsd">

    <xsl:value-of select="$newline"/>
    <xsl:variable name="sport">"Run"</xsl:variable>
    <xsl:variable name="time"><xsl:value-of select="t:Track/t:Trackpoint/t:Time"/></xsl:variable>
    <xsl:variable name="name"><xsl:value-of select="$sport"/><xsl:value-of  select="substring($time, 1,10)"/></xsl:variable>
    <metadata><xsl:value-of select="$newline"/>
    <name><xsl:value-of select="$name"/></name><xsl:value-of select="$newline"/>
    <link href="http://sourceforge.net/projects/pytrainer"/><xsl:value-of select="$newline"/>
    <time><xsl:value-of select="$time"/></time><xsl:value-of select="$newline"/>
    </metadata><xsl:value-of select="$newline"/>
    <trk><xsl:value-of select="$newline"/>
    <xsl:for-each select="t:Track">
        <trkseg><xsl:value-of select="$newline"/>
        <xsl:for-each select="t:Trackpoint">
            <!-- only output a trkpt if a position exists -->
            <xsl:if test="t:Position">
                <xsl:variable name="lat"><xsl:value-of select="t:Position/t:LatitudeDegrees"/></xsl:variable>
                <xsl:variable name="lon"><xsl:value-of select="t:Position/t:LongitudeDegrees"/></xsl:variable>
                <trkpt lat="{$lat}" lon="{$lon}"><xsl:value-of select="$newline"/>
                <ele><xsl:value-of select="t:AltitudeMeters"/></ele><xsl:value-of select="$newline"/>
                <time><xsl:value-of select="t:Time"/></time><xsl:value-of select="$newline"/>
				<xsl:if test="t:HeartRateBpm">
	                <extensions><xsl:value-of select="$newline"/>
    	            <gpxdata:hr><xsl:value-of select="t:HeartRateBpm"/></gpxdata:hr><xsl:value-of select="$newline"/>
    	            </extensions><xsl:value-of select="$newline"/>
				</xsl:if>
                </trkpt><xsl:value-of select="$newline"/>
            </xsl:if>
        </xsl:for-each>
        <xsl:value-of select="$newline"/>        
        </trkseg><xsl:value-of select="$newline"/>
    </xsl:for-each>
    </trk><xsl:value-of select="$newline"/>
    </gpx><xsl:value-of select="$newline"/>
</xsl:template>
</xsl:stylesheet>
