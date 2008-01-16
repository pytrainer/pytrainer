install:
	xgettext glade/pytrainer.glade -o ./messages.pot
	find ./ -iname "*.py" -exec xgettext -k_ -j -o ./messages.pot ./pytrainer/main.py {}  \;
	make locale_es
	make locale_eu
	make locale_ca
	make locale_fr
	make locale_da
	make locale_de
	make locale_no
	make locale_cs
	make locale_ru
	make locale_pl

locale_es:
	msginit -i ./messages.pot -l es -o ./locale/es/LC_MESSAGES/pytrainer_es.pot
locale_eu:
	msginit -i ./messages.pot -l eu -o ./locale/eu/LC_MESSAGES/pytrainer_eu.pot
locale_ca:
	msginit -i ./messages.pot -l ca -o ./locale/ca/LC_MESSAGES/pytrainer_ca.pot
locale_fr:
	msginit -i ./messages.pot -l fr -o ./locale/fr/LC_MESSAGES/pytrainer_fr.pot
locale_da:
	msginit -i ./messages.pot -l da -o ./locale/de/LC_MESSAGES/pytrainer_da.pot
locale_de:
	msginit -i ./messages.pot -l de -o ./locale/de/LC_MESSAGES/pytrainer_de.pot
locale_pl:
	msginit -i ./messages.pot -l pl -o ./locale/pl/LC_MESSAGES/pytrainer_pl.pot
locale_no:
	msginit -i ./messages.pot -l no -o ./locale/no/LC_MESSAGES/pytrainer_no.pot
locale_cs:
	msginit -i ./messages.pot -l cs -o ./locale/cs/LC_MESSAGES/pytrainer_cs.pot
locale_ru:
	msginit -i ./messages.pot -l ru -o ./locale/ru/LC_MESSAGES/pytrainer_ru.pot
locale_pl:
	msginit -i ./messages.pot -l pl -o ./locale/ru/LC_MESSAGES/pytrainer_pl.pot
