default:
	msgfmt pytrainer_da.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_da.po pytrainer_da.po_new > pytrainer_da.po.tmp
	mv pytrainer_da.po.tmp pytrainer_da.po
	rm pytrainer_da.po_new
