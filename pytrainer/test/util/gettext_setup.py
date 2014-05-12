import gettext, gtk.glade

def gettext_setup():
	'''Need to set this stuff up so that the translation functions work.  Seems like
	the module that needs translation ought to have some way of setting this up.'''
	DIR = "../../locale"
	gettext.bindtextdomain("pytrainer", DIR)
	gtk.glade.bindtextdomain("pytrainer", DIR)
	gtk.glade.textdomain("pytrainer")
	gettext.textdomain("pytrainer")
	gettext.install("pytrainer", DIR, unicode=1)
