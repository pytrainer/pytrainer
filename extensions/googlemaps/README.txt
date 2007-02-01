GOOGLEMAPS INTEGRATED EXTENSION
===============================

This extension allows you to draw your pytrainer records in
a pytrainer googlemaps integrated window. If you want use 
this extension you need attach a gpx (GPS extandar file format)
file at your records. 

CONFIGURATION
=============
Yo need configure two values in order to use this extension:

* googlekey: 
You can get a googlekey from here
http://www.google.com/apis/maps/signup.html

* Trackdistance:
With this option you can specific the minimal distance (in meters)
between track points drawed in the googlemaps window. Googlemaps 
is not very efficient. If you draw too much track points googlemaps
will be slow. 

If your tracks are 100km long, i recomend you use a 
trackdistance=200 

If your tracks are 30km long, i recomend you use a 
trackdistance=50

LAUNCHING PYTRAINER WITH GOOGLEMAPS EXTENSION
=============================================
In order to use pytrainer with googlemaps extension
you must edit your enviroment global LD_LIBRARY_PATH.

use:

LD_LIBRARY_PATH=/usr/lib/firefox pytrainer

LICENCE
=======
If you want know more about googlemaps licence see this:

http://www.google.com/apis/maps/terms.html
