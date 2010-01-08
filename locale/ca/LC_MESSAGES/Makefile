default:
	msgfmt pytrainer_ca.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_ca.po pytrainer_ca.po_new > pytrainer_ca.po.tmp
	mv pytrainer_ca.po.tmp pytrainer_ca.po
	rm pytrainer_ca.po_new
