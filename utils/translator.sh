#!/bin/sh

SOFTWARE=$(zenity --list --text="Select your translation software" --radiolist --column "Pick" --column "Software" TRUE "gtranslator" FALSE "kbabel" FALSE "poedit")
if [ $? != 0 ]; then exit ; fi

LANGUAGE=$(zenity --list --text="Select your language" --radiolist --column "Pick" --column "Language" TRUE "es" FALSE "eu" FALSE "ca" FALSE "fr" FALSE "da" FALSE "de" FALSE "pl" FALSE "no" FALSE "cs" FALSE "ru" FALSE "pl" FALSE "sv" FALSE "gl")
if [ $? != 0 ]; then exit ; fi

cd ../

# Extract translatable strings from input files
xgettext glade/*.glade -o ./messages.pot
if [ $? != 0 ]; then echo "WARNING: xgettext not found. Please install gettext package"; exit; fi
find ./ -iname "*.py" -exec xgettext -k_ -j -o ./messages.pot {} \;

# Initializing translations for desired language
msginit -i ./messages.pot -l $LANGUAGE -o ./locale/$LANGUAGE/LC_MESSAGES/pytrainer_$LANGUAGE.po_new
rm ./messages.pot

cd ./locale/$LANGUAGE/LC_MESSAGES/
# Merging old po file with the one generated as a result of current script
make merge

# Editing our new gettext catalog (.po file)
$SOFTWARE pytrainer_$LANGUAGE.po
if [ $? != 0 ]; then echo "WARNING: $SOFTWARE not found"; exit ; fi

# Compiling our new message catalog into binary files ready for distribution
make
