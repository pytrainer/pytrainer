this little extension runs a script of your choice and uses some data of the
current workout as arguments. I use it to tweet. with these settings:
it builds the command like this: <script> "<argument>" "<string>"

to tweet, use something like this:
script: /usr/bin/twidge
argument: upate
script: "I was %s %d in %T (%p) %c #pytrainer"
this runs twidge ( you have configure it first with "twidge update") with the
command "update" and a some data of your current workout:
Output would look like this:
/usr/bin/twidge update "I was Running 11.02 km in 1:02:13 (5.38 min/km) it was nice #pytrainer"

The string is a pseudo-printf like argument this gets replaced by the actual values:
%t title
%s sport
%D date
%T time
%d distance
%p pace
%S speed
%b beats
%c comments
%C calories
%mS maxSpeed
%mp maxpace
%mb maxbeats
