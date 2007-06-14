#!/usr/bin/env python
#
# setup.py for gnuConcept

from distutils.core import setup
from glob import glob

def install_locale(lang):
	return "share/locale/%s/LC_MESSAGES" %lang, glob("locale/%s/LC_MESSAGES/*.mo" %lang)

def install_plugin(plugin_name):
	return "share/pytrainer/plugins/%s"%plugin_name, glob("plugins/%s/*"%plugin_name) 

def install_extension(extension_name):
	return "share/pytrainer/extensions/%s"%extension_name, glob("extensions/%s/*"%extension_name) 

setup( 	name="pytrainer",
	version="1.4.1",
	author="Fiz Vazquez",
	author_email="vud1@sindominio.net",
	url="http://pytrainer.e-oss.net",
	license="GNU General Public License(GPL)",
	packages=[	'pytrainer',
			'pytrainer.gui',
			'pytrainer.extensions',
			'pytrainer.lib'
			],

	data_files=[
		('share/pytrainer/glade/',glob("glade/*.glade")),
		('share/pytrainer/glade/',glob("glade/*.png")),
		('share/pytrainer/',glob("*.style")),
		install_plugin("garmin301"),
		install_plugin("googleearth"),
		install_extensions("wordpress"),
		(install_locale("es")),
		(install_locale("ca")),
		(install_locale("fr")),
		(install_locale("de")),
		(install_locale("pl")),
		('share/pixmaps/',['pytrainer.png']),
		('share/applications/',['pytrainer.desktop'])
		],
	scripts=['bin/pytrainer'] 
)	
