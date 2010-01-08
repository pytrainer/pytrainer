default:
	msgfmt pytrainer_no.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_no.po pytrainer_no.po_new > pytrainer_no.po.tmp
	mv pytrainer_no.po.tmp pytrainer_no.po
	rm pytrainer_no.po_new
