#!/bin/sh
LOCALE_BASE_PATH="locale"
cd ../
echo -n "Extracting translatable strings... "
xgettext glade/*.ui -o ./messages.pot
find ./ -iname "*.py" -exec xgettext -k_ -j -o ./messages.pot {} \;
echo "OK"

for LANGUAGE in `ls -l $LOCALE_BASE_PATH | awk {'print $9'}`; do
    echo -n "Creating new $LANGUAGE po file... "
    msginit --no-translator -i ./messages.pot -l $LANGUAGE -o ./locale/$LANGUAGE/LC_MESSAGES/pytrainer_$LANGUAGE.po_new
    echo -n "Merging with old po file... "
    cd ./$LOCALE_BASE_PATH/$LANGUAGE/LC_MESSAGES/
    msgmerge -q pytrainer_$LANGUAGE.po pytrainer_$LANGUAGE.po_new > pytrainer_$LANGUAGE.po.tmp
    echo "OK"
    mv pytrainer_$LANGUAGE.po.tmp pytrainer_$LANGUAGE.po
    rm pytrainer_$LANGUAGE.po_new
    echo -n "Statistics for $LANGUAGE: "
    msgfmt --statistics pytrainer_$LANGUAGE.po -o ./pytrainer.mo
    cd ../../../
done
