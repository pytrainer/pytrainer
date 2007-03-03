If you want launch pytrainer with googlemaps embed you
need have installed mozilla-firefox. You need, too, have 
propierly configured the shared library.

You can launch pytrainer in this way:

LD_LIBRARY_PATH=/usr/lib/firefox python pytrainer.py

or add /usr/lib/firefox (or the direcory where 
libgtkmozembed.so is installed in) to the /etc/ld.so.conf.d file
