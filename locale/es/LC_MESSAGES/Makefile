default:
	msgfmt pytrainer_es.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_es.po pytrainer_es.po_new > pytrainer_es.po.tmp
	mv pytrainer_es.po.tmp pytrainer_es.po
	rm pytrainer_es.po_new
	
