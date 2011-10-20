default:
	msgfmt pytrainer_pt.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_pt.po pytrainer_pt.po_new > pytrainer_pt.po.tmp
	mv pytrainer_pt.po.tmp pytrainer_pt.po
	rm pytrainer_pt.po_new
	
