default:
	msgfmt pytrainer_pl.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_pl.po pytrainer_pl.po_new > pytrainer_pl.po.tmp
	mv pytrainer_pl.po.tmp pytrainer_pl.po
	rm pytrainer_pl.po_new
