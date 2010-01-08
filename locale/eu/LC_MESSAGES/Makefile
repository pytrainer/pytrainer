default:
	msgfmt pytrainer_eu.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_eu.po pytrainer_eu.po_new > pytrainer_eu.po.tmp
	mv pytrainer_eu.po.tmp pytrainer_eu.po
	rm pytrainer_eu.po_new
