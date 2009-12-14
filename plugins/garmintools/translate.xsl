<?xml version="1.0"?>

<!-- note defining a namespace for TrainingCenterDatabase as the translation does not seem to work with a default namespace -->
<xsl:stylesheet version="1.0"
xmlns:t="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>
<xsl:output  method="xml" indent="yes" omit-xml-declaration="no"/> 

<!-- this is a bit of a messy way to get whitespace into the output - but it works -->
<xsl:variable name="newline"><xsl:text>
</xsl:text></xsl:variable>

<xsl:template match="/">
    <gpx creator="pytrainer http://sourceforge.net/projects/pytrainer" version="1.1" 
	xmlns="http://www.topografix.com/GPX/1/1"
    xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" >

    <xsl:value-of select="$newline"/>
    <xsl:variable name="sport"><xsl:value-of select="root/run/@sport"/></xsl:variable>
    <xsl:variable name="time"><xsl:value-of select="root/point/@time"/></xsl:variable>
    <xsl:variable name="name"><xsl:value-of select="$sport"/><xsl:value-of  select="substring($time, 1,10)"/></xsl:variable>
    <metadata><xsl:value-of select="$newline"/>
    <name><xsl:value-of select="$name"/></name><xsl:value-of select="$newline"/>
    <link href="http://sourceforge.net/projects/pytrainer"/><xsl:value-of select="$newline"/>
    <time><xsl:value-of select="$time"/></time><xsl:value-of select="$newline"/>
    </metadata><xsl:value-of select="$newline"/>
    <trk><xsl:value-of select="$newline"/>
        <trkseg><xsl:value-of select="$newline"/>
        <!-- <xsl:variable name="calories"><xsl:value-of select="t:Calories"/></xsl:variable> -->
        <xsl:for-each select="root/point">
				<xsl:if test="@lat"> <!-- only write trkpt if lat/lon exist -->
	                <xsl:variable name="lat"><xsl:value-of select="@lat"/></xsl:variable>
    	            <xsl:variable name="lon"><xsl:value-of select="@lon"/></xsl:variable>
    	            <trkpt lat="{$lat}" lon="{$lon}"><xsl:value-of select="$newline"/>
    	            <ele><xsl:value-of select="@alt"/></ele><xsl:value-of select="$newline"/>
    	            <time><xsl:value-of select="@time"/></time><xsl:value-of select="$newline"/>
					<xsl:if test="@hr">
		                <extensions><xsl:value-of select="$newline"/>
    		            <gpxdata:hr><xsl:value-of select="@hr"/></gpxdata:hr><xsl:value-of select="$newline"/>
    		            </extensions><xsl:value-of select="$newline"/>
					</xsl:if>
    	            </trkpt><xsl:value-of select="$newline"/>
				</xsl:if> 
        </xsl:for-each>
        <xsl:value-of select="$newline"/>        
        </trkseg><xsl:value-of select="$newline"/>
    </trk><xsl:value-of select="$newline"/>

<!-- Lap Data -->
	<xsl:value-of select="$newline"/>
	<extensions><xsl:value-of select="$newline"/>
    <xsl:for-each select="root/lap">
    <xsl:variable name="vIndex">
    <xsl:number count="lap"/>
    </xsl:variable>
		<gpxdata:lap><xsl:value-of select="$newline"/>
			<gpxdata:index><xsl:value-of select="$vIndex"/></gpxdata:index><xsl:value-of select="$newline"/>
            <xsl:variable name="stlat"><xsl:value-of select="begin_pos/@lat"/></xsl:variable>
            <xsl:variable name="stlon"><xsl:value-of select="begin_pos/@lon"/></xsl:variable>
            <gpxdata:startPoint lat="{$stlat}" lon="{$stlon}"/><xsl:value-of select="$newline"/>
            <xsl:variable name="endlat"><xsl:value-of select="end_pos/@lat"/></xsl:variable>
            <xsl:variable name="endlon"><xsl:value-of select="end_pos/@lon"/></xsl:variable>
            <gpxdata:endPoint lat="{$endlat}" lon="{$endlon}"/><xsl:value-of select="$newline"/>
			<gpxdata:startTime><xsl:value-of select="@start"/></gpxdata:startTime><xsl:value-of select="$newline"/>
			<gpxdata:elapsedTime><xsl:value-of select="@duration"/></gpxdata:elapsedTime><xsl:value-of select="$newline"/> <!-- Needs converting to seconds -->
			<gpxdata:calories><xsl:value-of select="calories"/></gpxdata:calories><xsl:value-of select="$newline"/>
			<gpxdata:distance><xsl:value-of select="@distance"/></gpxdata:distance><xsl:value-of select="$newline"/>
			<gpxdata:summary><xsl:value-of select="$newline"/>
				<MaximumSpeed kind="max"><xsl:value-of select="max_speed"/></MaximumSpeed><xsl:value-of select="$newline"/>
				<AverageHeartRateBpm kind="avg"><xsl:value-of select="avg_hr"/></AverageHeartRateBpm><xsl:value-of select="$newline"/>
				<MaximumHeartRateBpm kind="max"><xsl:value-of select="max_hr"/></MaximumHeartRateBpm><xsl:value-of select="$newline"/>
			</gpxdata:summary><xsl:value-of select="$newline"/> 
			<gpxdata:trigger><xsl:value-of select="@trigger"/></gpxdata:trigger><xsl:value-of select="$newline"/>
			<gpxdata:intensity><xsl:value-of select="intensity"/></gpxdata:intensity><xsl:value-of select="$newline"/>
		</gpxdata:lap><xsl:value-of select="$newline"/>
    </xsl:for-each>
    </extensions><xsl:value-of select="$newline"/>

    </gpx><xsl:value-of select="$newline"/>
</xsl:template>
</xsl:stylesheet>
