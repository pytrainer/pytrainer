default:
	msgfmt pytrainer_cs.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_cs.po pytrainer_cs.po_new > pytrainer_cs.po.tmp
	mv pytrainer_cs.po.tmp pytrainer_cs.po
	rm pytrainer_cs.po_new
