#/bin/sh

if test -d /usr/lib/xulrunner-1.8.1.4
then
LD_LIBRARY_PATH=/usr/lib/xulrunner-1.8.1.4 MOZILLA_FIVE_HOME=/usr/lib/firefox python pytrainer.py

elif test -d /usr/lib/xulrunner-1.8.5-test
then
#LD_LIBRARY_PATH=/usr/lib/xulrunner-1.8.5
echo 1.8.5 exists replace this test with other relevant test....
else
echo neither directory exists, sorry!
fi

