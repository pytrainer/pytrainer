default:
	msgfmt pytrainer_dk.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_dk.po pytrainer_dk.po_new > pytrainer_dk.po.tmp
	mv pytrainer_de.pk.tmp pytrainer_dk.po
	rm pytrainer_dk.po_new
