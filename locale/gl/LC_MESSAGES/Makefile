default:
	msgfmt pytrainer_gl.po -o ./pytrainer.mo

merge:
	msgmerge pytrainer_gl.po pytrainer_gl.po_new > pytrainer_gl.po.tmp
	mv pytrainer_gl.po.tmp pytrainer_gl.po
	rm pytrainer_gl.po_new
	
