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
	version="1.8.0",
	description="The free sport tracking center",
	long_description="Pytrainer is a tool to log all your sport excursion coming from GPS devices (with a focus on ForeRunner 205, 305 and 405) or GPX (http://www.topografix.com) files. Pytrainer supports GPS track files and displays it in graphs, maps... ",
	author="Fiz Vazquez, John Blance, David Garcia Granda, Arnd Zapletal, Nathan Jones",
	maintainer_email="pytrainer-devel@lists.sourceforge.net",
	url="http://sourceforge.net/projects/pytrainer/",
	license="GNU General Public License (GPL)",
	packages=[	'pytrainer',
			'pytrainer.gui',
			'pytrainer.extensions',
			'pytrainer.lib'
			],

	data_files=[
		('share/pytrainer/glade/',glob("glade/*.glade")),
		('share/pytrainer/glade/',glob("glade/*.png")),
		('share/pytrainer/glade/',glob("glade/*.jpg")),
		('share/pytrainer/schemas/',glob("schemas/*.xsd")),
		('share/pytrainer/import/',glob("import/*.py")),
		('share/pytrainer/import/',glob("import/*.xsl")),
		('share/pytrainer/',glob("*.style")),
		install_plugin("garmin-gpx"),
		install_plugin("garmin-hr"),
		install_plugin("garmin-hr-file"),
		install_plugin("garmin-tcxv2"),
		install_plugin("googleearth"),
		install_plugin("garmintools"),
		install_plugin("garmintools_full"),
		install_extension("wordpress"),
		install_extension("openstreetmap"),
		install_extension("fixelevation"),
		(install_locale("ca")),
		(install_locale("cs")),
		(install_locale("da")),
		(install_locale("de")),
		(install_locale("es")),
		(install_locale("eu")),
		(install_locale("fr")),
		(install_locale("no")),
		(install_locale("pl")),
		(install_locale("ru")),
		(install_locale("sv")),
		('share/pixmaps/',['pytrainer.png']),
		('share/applications/',['pytrainer.desktop'])
		],
	scripts=['bin/pytrainer'] 
)
