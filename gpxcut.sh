#! /bin/bash


#get the origin gpx
echo $1

#prepare some variables
gpxinit="<?xml version='1.0'?><gpx version='1.0' creator='GPSBabel - http://www.gpsbabel.org' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns='http://www.topografix.com/GPX/1/0' xsi:schemaLocation='http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd'><trk><name>1</name><trkseg>"

gpxend="</trkseg></trk></gpx>"
count=0
oldtime=""
file="/tmp/reg0.gpx"

#scan it line by line looking at the data:
cat /tmp/reg.gpx | while read line; do
	trkptline=$(echo ${line} | grep "lat=")
	eleline=$(echo ${line} | grep "ele")
	timeline=$(echo ${line} | grep "time")
	notrkptline=$(echo ${line} | grep "/trkpt")
	if [ "$trkptline" != "" ]; then
		trkpt=$trkptline
	fi
	if [ "$eleline" != "" ]; then
		ele=$eleline
	fi
	if [ "$timeline" != "" ]; then
		time=$timeline
		lasttime=$(echo $time | cut -d ">" -f 2 | cut -d "T" -f 1)
	fi
	if [ "$notrkptline" != "" ]; then
		if [ "$lasttime" != "$oldtime" ]; then
			echo $gpxend >> $file
			let count=$count+1
			file="/tmp/reg$count.gpx"
			echo "creamos nuevo file $file"
			echo $gpxinit > $file
			echo $trkpt >> $file
			echo $ele >> $file
			echo $time >> $file
			echo "</trkpt>\n" >> $file
			oldtime=$lasttime
		else
			echo $trkpt >> $file
			echo $ele >> $file
			echo $time >> $file
			echo "</trkpt>\n" >> $file
		fi
	fi
	trkptline=""
	eleline=""
	timeline=""
	notrkptline=""
done

echo $gpxend >> $file

