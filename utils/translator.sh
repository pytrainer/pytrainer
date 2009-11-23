#!/bin/sh

SOFTWARE=$(zenity --list --text="Select your translation software" --radiolist --column "Pick" --column "Software" TRUE "gtranslator" FALSE "kbabel" FALSE "poedit")
if [ $? != 0 ]; then exit ; fi

LANGUAGE=$(zenity --list --text="Select your language" --radiolist --column "Pick" --column "Language" TRUE "es" FALSE "eu" FALSE "ca" FALSE "fr" FALSE "da" FALSE "de" FALSE "pl" FALSE "no" FALSE "cs" FALSE "ru" FALSE "pl")
if [ $? != 0 ]; then exit ; fi

cd ../

xgettext glade/pytrainer.glade -o ./messages.pot
if [ $? != 0 ]; then echo "WARNNING: xgettext not found. Please, install gettext package"; exit; fi
find ./ -iname "*.py" -exec xgettext -k_ -j -o ./messages.pot ./pytrainer/main.py {} \;

msginit -i ./messages.pot -l $LANGUAGE -o ./locale/$LANGUAGE/LC_MESSAGES/pytrainer_$LANGUAGE.pot

cd ./locale/$LANGUAGE/LC_MESSAGES/
make merge
$SOFTWARE pytrainer_$LANGUAGE.po
if [ $? != 0 ]; then echo "WARNNING: $SOFTWARE not found"; exit ; fi
make

