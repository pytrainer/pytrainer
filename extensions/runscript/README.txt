this little extension runs a script of your choice and uses some data of the
current workout as arguments. I use it to tweet.

to tweet, use something like this:
 /usr/bin/twidge update "I was %s %d in %T (%p) %c #pytrainer"

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

Be careful to escape the input correctly or use " around the input.
