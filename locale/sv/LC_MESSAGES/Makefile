default:
	msgfmt pytrainer_sv.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_sv.po pytrainer_sv.po_new > pytrainer_sv.po.tmp
	mv pytrainer_sv.po.tmp pytrainer_sv.po
	rm pytrainer_sv.po_new
