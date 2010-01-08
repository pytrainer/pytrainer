default:
	msgfmt pytrainer_ru.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_ru.po pytrainer_ru.po_new > pytrainer_ru.po.tmp
	mv pytrainer_ru.po.tmp pytrainer_ru.po
	rm pytrainer_ru.po_new
