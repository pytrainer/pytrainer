#!/bin/sh

NO_LANGUAGE='None (generate .pot)'

LANGUAGE=$(zenity --list --text="Select your language" --radiolist --column "Pick" --column "Language" TRUE "$NO_LANGUAGE" FALSE "ca" FALSE "cs" FALSE "da" FALSE "de" FALSE "es" FALSE "eu" FALSE "fr" FALSE "gl" FALSE "no" FALSE "pl" FALSE "pt" FALSE "ru" FALSE "sv")
if [ $? != 0 ]; then exit ; fi

cd ../

echo "Extracting translatable strings from input files"
xgettext glade/*.ui -o ./messages.pot
if [ $? != 0 ]; then echo "WARNING: xgettext not found. Please install gettext package"; exit; fi
find ./ -iname "*.py" -exec xgettext -k_ -j -o ./messages.pot {} \;

CWD=$(pwd)
echo "Generated $CWD/messages.pot"

if test "$LANGUAGE" = "$NO_LANGUAGE"; then exit; fi

echo "Initializing translations for desired language"
msginit -i ./messages.pot -l $LANGUAGE -o ./locale/$LANGUAGE/LC_MESSAGES/pytrainer_$LANGUAGE.po_new

cd ./locale/$LANGUAGE/LC_MESSAGES/
echo "Merging old po file with newly generated one"
make merge

SOFTWARE=$(zenity --list --text="Select your translation software" --radiolist --column "Pick" --column "Software" TRUE "gtranslator" FALSE "kbabel" FALSE "poedit" FALSE "virtaal")
if [ $? != 0 ]; then exit ; fi

# Editing our new gettext catalog (.po file)
$SOFTWARE pytrainer_$LANGUAGE.po
if [ $? != 0 ]; then echo "WARNING: $SOFTWARE not found"; exit ; fi

echo "Compiling new message catalog"
make
