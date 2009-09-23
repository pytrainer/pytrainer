#/bin/sh
# First arg is log level, e.g. -d for DEBUG

export LD_LIBRARY_PATH=/usr/lib/firefox
# Building xulrunner path to avoid problems when upgrading
PATH_XULRUNNER=/usr/lib
XULRUNNER_VERSION=`ls "$PATH_XULRUNNER" | grep xulrunner`
export MOZILLA_FIVE_HOME=$PATH_XULRUNNER/$XULRUNNER_VERSION
rm /home/johnb/.pytrainer/log.out
python pytrainer.py -d
