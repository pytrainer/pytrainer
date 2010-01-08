default:
	msgfmt pytrainer_fr.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_fr.po pytrainer_fr.po_new > pytrainer_fr.po.tmp
	mv pytrainer_fr.po.tmp pytrainer_fr.po
	rm pytrainer_fr.po_new
