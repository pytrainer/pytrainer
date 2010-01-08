default:
	msgfmt pytrainer_de.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_de.po pytrainer_de.po_new > pytrainer_de.po.tmp
	mv pytrainer_de.po.tmp pytrainer_de.po
	rm pytrainer_de.po_new
