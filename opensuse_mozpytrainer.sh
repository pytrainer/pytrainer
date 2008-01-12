#/bin/sh

if test -L /usr/lib/xulrunner-1.8.1
then
echo using the symlink to the current directory
LD_LIBRARY_PATH=/usr/lib/xulrunner-1.8.1 MOZILLA_FIVE_HOME=/usr/lib/firefox python pytrainer.py
elif test -d /usr/lib/xulrunner-1.8.1.4
then
LD_LIBRARY_PATH=/usr/lib/xulrunner-1.8.1.4 MOZILLA_FIVE_HOME=/usr/lib/firefox python pytrainer.py

elif test -d /usr/lib/xulrunner-1.8.10
then
LD_LIBRARY_PATH=/usr/lib/xulrunner-1.8.1.10 MOZILLA_FIVE_HOME=/usr/lib/firefox python pytrainer.py
else
echo neither directory exists. Try looking in /usr/lib for "xulrunner-something" and amend this script
echo to look for that directory too.
echo You are also encouraged to improve this script so it automatically detects the correct directory...
fi

